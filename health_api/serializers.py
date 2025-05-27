# serializers.py - Enhanced validation

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from .models import User, HealthRecord, Annotation, Assignment
import re


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_doctor', 'is_patient', 'first_name', 'last_name']


class PatientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if not re.match("^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords don't match.")

        # Use Django's password validation
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['is_patient'] = True
        return User.objects.create(**validated_data)


class DoctorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    medical_license = serializers.CharField(max_length=50, required=True)  # Add medical license validation

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


    def validate(self, attrs):
        if attrs['password'] != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords don't match.")

        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['is_doctor'] = True
        user = User.objects.create(**validated_data)


        return user


class HealthRecordSerializer(serializers.ModelSerializer):
    annotations = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = HealthRecord
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'patient', 'annotations']
        read_only_fields = ['patient', 'created_at', 'updated_at', 'annotations']

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return value.strip()


class AnnotationSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    record_title = serializers.CharField(source='record.title', read_only=True)

    class Meta:
        model = Annotation
        fields = ['id', 'note', 'created_at', 'doctor', 'record', 'doctor_name', 'record_title']
        read_only_fields = ['doctor', 'created_at', 'doctor_name', 'record_title']

    def validate_note(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Annotation must be at least 5 characters long.")
        return value.strip()


class AssignmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'doctor', 'patient', 'created_at', 'doctor_name', 'patient_name']
        read_only_fields = ['created_at', 'doctor_name', 'patient_name']

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        patient = attrs.get('patient')

        if not doctor.is_doctor:
            raise serializers.ValidationError("Selected user is not a doctor.")

        if not patient.is_patient:
            raise serializers.ValidationError("Selected user is not a patient.")

        if Assignment.objects.filter(doctor=doctor, patient=patient).exists():
            raise serializers.ValidationError("This assignment already exists.")

        return attrs