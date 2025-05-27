from rest_framework.permissions import BasePermission

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_patient

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_doctor

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.patient == request.user
