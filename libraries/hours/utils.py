import datetime
from hours.models import OpenHours, Library, Closure

# returns a dict of each library's open hours for a given date e.g.
# { meyer: '9-5', simpson: '9-6', materials: 'closed' }
# the home page uses this function
def get_open_hours(day=datetime.date.today()):
    # if we're passed a string, convert it to a date
    if type(day) is str:
        # @TODO validate input, must match \d{4}-\d{2}-\d{2} regex
        day = datetime.datetime.strptime(day, '%Y-%m-%d')

    weekday = day.strftime('%a').lower()

    hrs = OpenHours.objects.all()
    # filter to open hours that contain the given day
    hrs = hrs.filter(start_date__lte=day).filter(end_date__gte=day)

    closures = Closure.objects.all()
    closures = closures.filter(start_date__lte=day).filter(end_date__gte=day)
    # closures should just be a list of closed library names
    closed_libs = []
    for closure in closures:
        closed_libs.append(closure.library.name)

    output = {}
    # iterate over all Library snippets
    for lib in Library.objects.all():
        # initialize with a null fallback value
        output[lib.name] = None
        # register closures
        if lib.name in closed_libs:
            output[lib.name] = 'closed'
        else:
            # well that's some python if I've ever seen it
            output[lib.name] = hrs.filter(library=lib).values_list(weekday).first()[0]

    return output
