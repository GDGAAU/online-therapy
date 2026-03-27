from django.contrib import admin
from .models import Therapist, Specialty, Appointment

admin.site.register(Specialty)
admin.site.register(Therapist)
admin.site.register(Appointment)