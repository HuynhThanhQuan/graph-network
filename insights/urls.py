from django.urls import path
from insights import views

app_name = 'insights'
urlpatterns = [
    path('cluster/execution_id', views.cluster_execution_id, name='cluster_execution_id'),
    path('cluster/within_interval', views.cluster_within_interval, name='cluster_within_interval'),
    path('cluster/project_id', views.cluster_project_id, name='cluster_project_id')
]
