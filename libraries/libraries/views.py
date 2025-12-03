"""Custom views for the libraries project."""

from django.http import HttpRequest, HttpResponse
from django_cas_ng.views import LogoutView as CASLogoutView


class LogoutView(CASLogoutView):
    """Wrapper around django_cas_ng LogoutView that supports POST requests."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Delegate POST requests to the GET handler for CAS logout."""
        return self.get(request)
