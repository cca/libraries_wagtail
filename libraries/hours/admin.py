from django.contrib import admin

from .models import Library, OpenHours, Closure

# Register your models here.

for m in [Library, OpenHours, Closure]:
    admin.site.register(m)
