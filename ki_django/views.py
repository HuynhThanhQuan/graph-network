from django import http
from rest_framework.decorators import api_view
from ki_django import audit


@api_view()
def home_page(request):
    return http.HttpResponse('Welcome to Home Page') if audit.verify_request(request) else \
        http.HttpResponseForbidden('Permission denied')


@api_view()
def health_checker(request):
    return http.HttpResponse('Server is OK', status=200)
