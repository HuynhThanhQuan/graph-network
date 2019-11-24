from datetime import datetime
import json
from insights.clustering.ClusteringController import ClusteringController
from insights.views_util import parse_stacktrace_report_to_json
from rest_framework import status
from django import http
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def cluster_execution_id(request):
    start = datetime.now()
    try:
        logger.info('Request cluster execution ID')
        # Read HTTP request body
        request_body = json.loads(request.body)
        execution_id = request_body['executionId']
        # Recording Clustering process
        clustering_controller = ClusteringController()
        clustering_controller.find_failed_results_execution_id(execution_id)
        if len(clustering_controller.bundles) > 0:
            logger.info('Found {} requested error logs'.format(len(clustering_controller.bundles)))
            clustering_bundles = ClusteringController.hierarchical_cluster_on_the_fly(clustering_controller.bundles)
            # Use stacktrace features
            if clustering_bundles is None:
                return http.HttpResponse("After preprocessing, data is empty",
                                         status=status.HTTP_200_OK,
                                         content_type="text/plain")
            else:
                logger.info('Returning cluster information in JSON')
                return http.JsonResponse(parse_stacktrace_report_to_json(clustering_bundles),
                                         status=status.HTTP_200_OK)
        return http.HttpResponse("Data not found in this query",
                                 status=status.HTTP_200_OK,
                                 content_type="text/plain")
    except ValueError as e:
        logger.error('Falied to cluster execution id {}'.format(e.args[0]))
        return http.HttpResponseBadRequest(e.args[0])
    finally:
        logger.info('Request cluster execution ID {}'.format(datetime.now() - start))
        logger.info('===========================================================================')


def cluster_within_interval(request):
    start = datetime.now()
    try:
        logger.info('Request cluster within interval')
        # Read HTTP request body
        request_body = json.loads(request.body)
        project_id = request_body['projectId']
        start_time = request_body['startTime']
        end_time = request_body['endTime']

        # Recording Clustering process
        clustering_controller = ClusteringController()
        clustering_controller.find_failed_results_within_interval(project_id, start_time, end_time)
        if len(clustering_controller.bundles) > 0:
            logger.info('Found {} requested error logs'.format(len(clustering_controller.bundles)))
            clustering_bundles = ClusteringController.hierarchical_cluster_on_the_fly(clustering_controller.bundles)
            # Use stacktrace features
            if clustering_bundles is None:
                return http.HttpResponse("After preprocessing, data is empty",
                                         status=status.HTTP_200_OK,
                                         content_type="text/plain")
            else:
                logger.info('Returning cluster information in JSON')
                return http.JsonResponse(parse_stacktrace_report_to_json(clustering_bundles),
                                         status=status.HTTP_200_OK)
        else:
            return http.HttpResponse("Data not found in this query",
                                     status=status.HTTP_200_OK,
                                     content_type="text/plain")
    except ValueError as e:
        logger.error('Falied to cluster within interval {}'.format(e.args[0]))
        return http.HttpResponseBadRequest(e.args[0])
    finally:
        logger.info('Request cluster within interval {}'.format(datetime.now() - start))
        logger.info('===========================================================================')


def cluster_project_id(request):
    start = datetime.now()
    try:
        logger.info('Request cluster project ID')
        # Read HTTP request body
        request_body = json.loads(request.body)
        project_id = request_body['projectId']
        # Recording Clustering process
        clustering_controller = ClusteringController()
        clustering_controller.find_failed_results_project_id(project_id)
        if len(clustering_controller.bundles) > 0:
            logger.info('Found {} requested error logs'.format(len(clustering_controller.bundles)))
            clustering_bundles = ClusteringController.hierarchical_cluster_on_the_fly(clustering_controller.bundles)
            # Use stacktrace features
            if clustering_bundles is None:
                return http.HttpResponse("After preprocessing, data is empty",
                                         status=status.HTTP_200_OK,
                                         content_type="text/plain")
            else:
                logger.info('Returning cluster information in JSON')
                return http.JsonResponse(parse_stacktrace_report_to_json(clustering_bundles),
                                         status=status.HTTP_200_OK)
        else:
            return http.HttpResponse("Data not found in this query",
                                     status=status.HTTP_200_OK,
                                     content_type="text/plain")
    except ValueError as e:
        logger.error('Falied to cluster project id {}'.format(e.args[0]))
        return http.HttpResponseBadRequest(e.args[0])
    finally:
        logger.info('Request cluster project ID {}'.format(datetime.now() - start))
        logger.info('===========================================================================')
