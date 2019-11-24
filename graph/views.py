from rest_framework.decorators import api_view
from graph import controller as con


@api_view(['POST'])
def analyze(request):
    return con.analyze(request)


@api_view(['GET', 'POST'])
def summary(request):
    return con.summary(request)


@api_view(['POST'])
def build(request):
    return con.build_graph(request)


@api_view(['POST'])
def rebuild(request):
    return con.build_graph(request, rebuild=True)


@api_view(['POST'])
def ranking(request):
    return con.ranking(request)
