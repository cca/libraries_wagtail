from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

@csrf_exempt
def brokenlinks(request):
    if not settings.BROKENLINKS_GOOGLE_SHEET_KEY or not settings.BROKENLINKS_HASH:
        return JsonResponse({"error": "This Wagtail app needs both a BROKENLINKS_GOOGLE_SHEET_KEY and BROKENLINKS_HASH in its settings to function."}, status=500)
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
        response['Access-Control-Allow-Origin'] = '*'
        return response
    else:
        return JsonResponse({"error": "expected a POST request"}, status=405)
