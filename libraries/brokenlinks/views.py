import logging

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
def brokenlinks(request):
    if not settings.BROKENLINKS_GOOGLE_SHEET_URL or not settings.BROKENLINKS_HASH:
        logger.error("brokenlinks app request but its settings are not configured")
        response = JsonResponse(
            {
                "error": "This Wagtail app needs both a BROKENLINKS_GOOGLE_SHEET_URL and BROKENLINKS_HASH in its settings to function."
            },
            status=500,
        )
        response["Access-Control-Allow-Origin"] = "*"
        return response

    # NOTE: some browser AJAX libraries send an "OPTIONS" request before POST
    # so we have to handle this case, cannot only accept POST requests
    elif request.method == "OPTIONS":
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        # note that '*' is not valid for Access-Control-Allow-Headers
        response["Access-Control-Allow-Headers"] = (
            "origin, x-csrftoken, content-type, accept"
        )
        return response

    elif request.method == "POST":
        body = QueryDict(request.body)
        data = {
            settings.BROKENLINKS_HASH["openurl"]: body.get("openurl", ""),
            settings.BROKENLINKS_HASH["permalink"]: body.get("permalink", ""),
            settings.BROKENLINKS_HASH["type"]: body.get("type", ""),
            settings.BROKENLINKS_HASH["email"]: body.get("email", ""),
            settings.BROKENLINKS_HASH["comments"]: body.get("comments", ""),
            "submit": "Submit",
        }
        r = requests.post(settings.BROKENLINKS_GOOGLE_SHEET_URL, data=data)
        logger.info("broken link reported: " + str(body.dict()))
        if r.status_code != 200:
            logger.error(
                "error submitting broken link to Google Sheets, response code: "
                + str(r.status_code)
            )
        response = JsonResponse(data, status=200)
        response["Access-Control-Allow-Origin"] = "*"
        return response

    else:
        response = JsonResponse({"error": "expected a POST request"}, status=405)
        response["Access-Control-Allow-Origin"] = "*"
        return response
