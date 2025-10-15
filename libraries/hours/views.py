"""JSON API View for the Hours app."""

import datetime

from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from hours.models import HoursPage, Library, get_hours_for_lib, get_open_hours


def error_response(msg):
    """Send a JSON HTTP error response to user. Don't put err object in msg.

    Parameters
    ----------
    msg : str
        Error message
    status : int
        HTTP status code

    Returns
    -------
    HTTP response

    """
    response = JsonResponse({"error": msg}, status=400)
    response["Access-Control-Allow-Origin"] = "*"
    return response


@never_cache
def hours(request):
    """Hours API view.

    Parameters
    ----------
    request : HTTP request coming from Django views

    Returns
    -------
    HTTP JsonResponse, whether error or data

    """
    if request.GET.get("format", "").lower() == "json":
        # can request hours for a given day, or library
        library = request.GET.get("library", None)
        date = request.GET.get("date", datetime.date.today())
        err = validate(library, date)
        if err is not None:
            return err

        hrs = None

        if library:
            hrs = get_hours_for_lib(library, date)
            print("library hours", hrs)

            if hrs:
                response = JsonResponse({"library": library, "hours": hrs})
                response["Access-Control-Allow-Origin"] = "*"

        # we have a date but no library, show all libraries on that date
        else:
            hrs = get_open_hours(date)
            response = JsonResponse(hrs)
            response["Access-Control-Allow-Origin"] = "*"

        # we didn't find any hours via either of the above methods
        if hrs is None:
            return error_response(
                f"No hours set found for library with name '{library}' on date '{date}'."
            )

        return response

    # redirect HTML requests to the hours page
    else:
        return redirect(HoursPage.objects.first().url)


def validate(library, date):
    """Validate input (from request query string).

    Parameters
    ----------
    library : str
        Name of a library, e.g. "Simpson".
        Libraries are Wagtail snippets.
    date : str
        Date in YYYY-MM-DD format.

    Returns
    -------
    JsonResponse | None
        If data was invalid, return value is the error JsonResponse to send to
        the user. If it was valid, the value is None.

    """
    libraries = set(library.name for library in Library.objects.all())

    # check that library is in our list
    if library and library not in libraries:
        return error_response(
            f"Library '{library}' does not exist. List of libraries: {libraries}"
        )

    # if date string is provided must be in YYYY-MM-DD form
    # check that date value is valid
    if isinstance(date, str):
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return error_response(
                f"Unable to parse provided date string '{date}'. Dates must be in YYYY-MM-DD format."
            )

    return None
