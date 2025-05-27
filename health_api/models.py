from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)  # Add email field

    def __str__(self):
        return f"{self.username} ({'Doctor' if self.is_doctor else 'Patient' if self.is_patient else 'User'})"


class HealthRecord(models.Model):
    patient = models.ForeignKey(User, related_name='records', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.patient.username}"

    class Meta:
        ordering = ['-updated_at']


class Annotation(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    record = models.ForeignKey(HealthRecord, related_name='annotations', on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Annotation by Dr. {self.doctor.username} on {self.record.title}"

    class Meta:
        ordering = ['-created_at']


class Assignment(models.Model):
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_patients'
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_doctors'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'patient')

    def __str__(self):
        return f"Dr. {self.doctor.username} -> {self.patient.username}"