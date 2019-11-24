import warnings
from django import http
from rest_framework.decorators import api_view
from insights import controller as con
from ki_django import audit
import logging
warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@api_view(['POST'])
def cluster_execution_id(request):
    return con.cluster_execution_id(request) if audit.verify_request(request) else \
        http.HttpResponseForbidden('Permission denied')


@api_view(['POST'])
def cluster_within_interval(request):
    return con.cluster_within_interval(request) if audit.verify_request(request) else \
        http.HttpResponseForbidden('Permission denied')


@api_view(['POST'])
def cluster_project_id(request):
    return con.cluster_project_id(request) if audit.verify_request(request) else \
        http.HttpResponseForbidden('Permission denied')
