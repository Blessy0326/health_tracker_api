from django.contrib import admin
from .models import User, HealthRecord, Annotation, Assignment

admin.site.register(User)
admin.site.register(HealthRecord)
admin.site.register(Annotation)
admin.site.register(Assignment)
