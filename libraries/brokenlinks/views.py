from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json


@csrf_exempt
def brokenlinks(request):
    if not settings.BROKENLINKS_GOOGLE_SHEET_KEY or not settings.BROKENLINKS_HASH:
        response = JsonResponse({"error": "This Wagtail app needs both a BROKENLINKS_GOOGLE_SHEET_KEY and BROKENLINKS_HASH in its settings to function."}, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    # NOTE: some browser AJAX libraries send an "OPTIONS" request before POST
    # so we have to handle this case, cannot only accept POST requests
    elif request.method == 'OPTIONS':
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        # note that '*' is not valid for Access-Control-Allow-Headers
        response["Access-Control-Allow-Headers"] = "origin, x-csrftoken, content-type, accept"
        return response
    elif request.method == 'POST':
        sheets_url = 'https://docs.google.com/a/cca.edu/forms/d/e/{0}/formResponse'.format(settings.BROKENLINKS_GOOGLE_SHEET_KEY)
        body = json.loads(request.body)
        data = {
            settings.BROKENLINKS_HASH['ipaddress']: request.META.get('REMOTE_ADDR', ''),
            settings.BROKENLINKS_HASH['openurl']: body.get('openurl', ''),
            settings.BROKENLINKS_HASH['permalink']: body.get('permalink', ''),
            settings.BROKENLINKS_HASH['type']: body.get('type', ''),
            settings.BROKENLINKS_HASH['email']: body.get('email', ''),
            settings.BROKENLINKS_HASH['comments']: body.get('comments', ''),
        }
        r = requests.post(sheets_url, data=data)
        response = JsonResponse(data, status=r.status_code)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    else:
        response = JsonResponse({"error": "expected a POST request"}, status=405)
        response["Access-Control-Allow-Origin"] = "*"
        return response
