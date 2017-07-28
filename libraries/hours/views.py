from django.shortcuts import render
from django.http import JsonResponse

# hours API
def hours(request):
    if request.GET.get('format') == 'json':
        JsonResponse({ 'format': 'json' })
