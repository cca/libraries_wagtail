import datetime

from django.shortcuts import render, redirect
from django.http import JsonResponse
from hours.models import get_open_hours, get_hours_for_lib, HoursPage

# hours API
def hours(request):
    if request.GET.get('format') == 'json':
        # can request hours for a given day, or library
        library = request.GET.get('library')
        date = request.GET.get('date', datetime.datetime.today())

        if library:
            hrs = get_hours_for_lib(library)
            if not hrs:
                return JsonResponse({
                    "error": "no library with name '%s' found" % library
                })

            # surely there is a better way but OpenHours can't serialize to JSON
            return JsonResponse({
                'library': library,
                'hours': {
                    'mon': hrs.mon,
                    'tue': hrs.tue,
                    'wed': hrs.wed,
                    'thu': hrs.thu,
                    'fri': hrs.fri,
                    'sat': hrs.sat,
                    'sun': hrs.sun,
                }
            })

        else:
            return JsonResponse(get_open_hours(date))

    # redirect HTML requests to the hours page
    else:
        return redirect(HoursPage.objects.first().url)
