from django.urls import path
from graph import views

app_name = 'graph'
urlpatterns = [
    path('analyze', views.analyze, name='analyze'),
    path('summary', views.summary, name='summary'),
    path('build', views.build, name='build'),
    path('rebuild', views.rebuild, name='rebuild')
]

