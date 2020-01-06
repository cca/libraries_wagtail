import datetime

from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from hours.models import get_open_hours, get_hours_for_lib, HoursPage, Library

# hours API
@never_cache
def hours(request):
    if request.GET.get('format') == 'json':
        # can request hours for a given day, or library
        library = request.GET.get('library', None)
        date = request.GET.get('date', datetime.date.today())
        success, error_response = validate(library, date)
        if success is False:
            return error_response

        hrs = None

        if library:
            hrs = get_hours_for_lib(library, date)
            print(hrs)

            if hrs:
                response = JsonResponse({
                    'library': library,
                    'hours': hrs
                })

        if date and not library:
            hrs = get_open_hours(date)
            response = JsonResponse(hrs)

        # we didn't find any hours via either of the above methods
        if hrs == None:
            response = JsonResponse({
                "error": "no hours set found for library with name '{}' on date '{}'".format(library, date)
            }, status=404)

        response["Access-Control-Allow-Origin"] = "*"
        return response

    # redirect HTML requests to the hours page
    else:
        return redirect(HoursPage.objects.first().url)


def validate(library, date):
    libraries = set(library.name for library in Library.objects.all())

    # check that library is in our list
    if library and library not in libraries:
        response = JsonResponse({
            "error": "Library '{}' does not exist. List of libraries: {}".format(library, libraries)
        }, status=400)
        response["Access-Control-Allow-Origin"] = "*"
        return False, response

    # if date string is provided must be in YYYY-MM-DD form
    # check that date value is valid
    if type(date) is str:
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError as err:
            response = JsonResponse({
                "error": "Unable to parse provided date string '{}'. ValueError: {}".format(date, err)
            }, status=400)
            response["Access-Control-Allow-Origin"] = "*"
            return False, response

    return True, None
