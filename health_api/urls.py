from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'health-records', views.HealthRecordViewSet, basename='healthrecord')
router.register(r'annotations', views.AnnotationViewSet, basename='annotation')

urlpatterns = [
    # Registration endpoints
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),

    # Assignment endpoints
    path('assign-patient/', views.assign_patient_to_doctor, name='assign_patient'),
    path('my-assignments/', views.get_my_assignments, name='my_assignments'),

    # Utility endpoints
    path('patient/<int:patient_id>/records/', views.get_patient_records, name='patient_records'),
    path('me/', views.get_current_user, name='current_user'),

    # Router endpoints
    path('', include(router.urls)),
]