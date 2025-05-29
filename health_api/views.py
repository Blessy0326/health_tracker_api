from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User, HealthRecord, Annotation, Assignment
from .serializers import (
    UserSerializer, PatientRegistrationSerializer, DoctorRegistrationSerializer,
    HealthRecordSerializer, AnnotationSerializer, AssignmentSerializer
)
from .permissions import IsPatient, IsDoctor, IsOwnerOrReadOnly
from .tasks import notify_doctor_email


# Registration Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_patient(request):
    serializer = PatientRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Patient registered successfully',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_doctor(request):
    serializer = DoctorRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Doctor registered successfully',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Health Record Views
class HealthRecordViewSet(viewsets.ModelViewSet):
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            # Patients can only see their own records
            return HealthRecord.objects.filter(patient=user)
        elif user.is_doctor:
            # Doctors can see records of their assigned patients
            assigned_patients = Assignment.objects.filter(doctor=user).values_list('patient', flat=True)
            return HealthRecord.objects.filter(patient__in=assigned_patients)
        return HealthRecord.objects.none()

    def perform_create(self, serializer):
        # Only patients can create records for themselves
        if self.request.user.is_patient:
            serializer.save(patient=self.request.user)
        else:
            raise permissions.PermissionDenied("Only patients can create health records")

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only patients can modify records
            permission_classes = [IsPatient]
        else:
            # Both patients and doctors can view (filtered by get_queryset)
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


# Annotation Views
class AnnotationViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationSerializer
    permission_classes = [IsDoctor]

    def get_queryset(self):
        user = self.request.user
        if user.is_doctor:
            # Doctors can see annotations on records of their assigned patients
            assigned_patients = Assignment.objects.filter(doctor=user).values_list('patient', flat=True)
            return Annotation.objects.filter(record__patient__in=assigned_patients)
        return Annotation.objects.none()

    def perform_create(self, serializer):
        # Verify doctor can annotate this record
        record = serializer.validated_data['record']
        if not Assignment.objects.filter(doctor=self.request.user, patient=record.patient).exists():
            raise permissions.PermissionDenied("You can only annotate records of your assigned patients")
        serializer.save(doctor=self.request.user)


# Assignment Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_patient_to_doctor(request):
    """
    Assign a patient to a doctor. Can be called by admins or the system.
    Expected data: {"doctor_id": int, "patient_id": int}
    """
    doctor_id = request.data.get('doctor_id')
    patient_id = request.data.get('patient_id')


    if not doctor_id or not patient_id:
        return Response({
            'error': 'Both doctor_id and patient_id are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        doctor = User.objects.get(id=doctor_id)
        patient = User.objects.get(id=patient_id)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid doctor or patient ID'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if assignment already exists
    if Assignment.objects.filter(doctor=doctor, patient=patient).exists():
        return Response({
            'error': 'Patient is already assigned to this doctor'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create assignment
    assignment = Assignment.objects.create(doctor=doctor, patient=patient)

    # Trigger email notification task
    if doctor.email:
        notify_doctor_email.delay(
            doctor_email=doctor.email,
            doctor_name=doctor.get_full_name() or doctor.username,
            patient_name=patient.get_full_name() or patient.username
        )

    return Response({
        'message': 'Patient assigned to doctor successfully',
        'assignment_id': assignment.id,
        'doctor': doctor.username,
        'patient': patient.username
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_assignments(request):
    """Get assignments for the current user (doctor or patient)"""
    user = request.user

    if user.is_doctor:
        assignments = Assignment.objects.filter(doctor=user).select_related('patient')
        data = [{
            'assignment_id': assignment.id,
            'patient_id': assignment.patient.id,
            'patient_username': assignment.patient.username,
            'assigned_on': assignment.created_at
        } for assignment in assignments]
        return Response({
            'role': 'doctor',
            'assignments': data
        })

    elif user.is_patient:
        assignments = Assignment.objects.filter(patient=user).select_related('doctor')
        data = [{
            'assignment_id': assignment.id,
            'doctor_id': assignment.doctor.id,
            'doctor_username': assignment.doctor.username,
            'assigned_on': assignment.created_at
        } for assignment in assignments]
        return Response({
            'role': 'patient',
            'assignments': data
        })

    return Response({
        'error': 'User must be either a doctor or patient'
    }, status=status.HTTP_400_BAD_REQUEST)


# Additional utility views
@api_view(['GET'])
@permission_classes([IsDoctor])
def get_patient_records(request, patient_id):
    """Get all records for a specific patient (for assigned doctors only)"""
    try:
        patient = User.objects.get(id=patient_id, is_patient=True)
    except User.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if doctor is assigned to this patient
    if not Assignment.objects.filter(doctor=request.user, patient=patient).exists():
        return Response({
            'error': 'You are not assigned to this patient'
        }, status=status.HTTP_403_FORBIDDEN)

    records = HealthRecord.objects.filter(patient=patient).prefetch_related('annotations')
    serializer = HealthRecordSerializer(records, many=True)

    return Response({
        'patient_id': patient.id,
        'patient_username': patient.username,
        'records': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current user info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)