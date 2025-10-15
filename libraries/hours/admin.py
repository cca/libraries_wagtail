from django.contrib import admin

from .models import Closure, Library, OpenHours

# Register your models here.

for m in [Library, OpenHours, Closure]:
    admin.site.register(m)
