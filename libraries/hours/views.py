import datetime

from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from hours.models import get_open_hours, get_hours_for_lib, HoursPage

# hours API
@never_cache
def hours(request):
    if request.GET.get('format') == 'json':
        # can request hours for a given day, or library
        library = request.GET.get('library', None)
        date = request.GET.get('date', datetime.date.today())
        hrs = None

        if library:
            hrs = get_hours_for_lib(library, date)

            if hrs:
                response = JsonResponse({
                    'library': library,
                    'hours': hrs
                })

        if date and not library:
            response = JsonResponse(get_open_hours(date))

        if hrs == None:
            response = JsonResponse({
                "error": "no hours set found for library with name '%s' on date '%s'" % (library, date)
            })

        response["Access-Control-Allow-Origin"] = "*"
        return response

    # redirect HTML requests to the hours page
    else:
        return redirect(HoursPage.objects.first().url)
