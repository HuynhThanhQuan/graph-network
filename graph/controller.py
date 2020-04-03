from ki_django import audit
from datetime import datetime
from graph.build.graph_builder import GraphBuilder
from graph.core import graph_analyzer as g_ana
import json
from django.contrib import auth
from database import data_retriever as d_rtr
from graph.core import graph_parser as g_pars
# from .core import katalon_graph, graph_render
from rest_framework import response
from django import http
from graph.build import graph_configure as g_conf
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def analyze(request):
    if audit.verify_request(request):
        logger.info('================================')
        logger.info('Initiate Analyze Big Data')
        start = datetime.now()
        request_body = json.loads(request.body)
        data_config = request_body.get('data')
        logger.info('Configuration {}'.format(request_body))
        data_retriever = d_rtr.DataRetriever(data_config=data_config)
        data_bundles = data_retriever.execute()

        graph_parser = g_pars.GraphParser(detect_ka=True)

        graph_builder = GraphBuilder(graph_parser,
                                     load_graph=True,
                                     save_graph=False).load()
        graph_analyzer = g_ana.GraphAnalyzer(graph_builder, graph_parser)
        report = graph_analyzer.analyze_bundle(data_bundles)
        logger.info('Request analyze big data {}'.format(datetime.now() - start))
        return response.Response(report.cluster_docids_map)
    else:
        return http.HttpResponseForbidden('Permission denied')


def build_graph(request, rebuild=False):
    if audit.verify_request(request):
        logger.info('=======================================')
        logger.info('=============BUILD GRAPH===============')
        logger.info('=======================================')
        request_body = json.loads(request.body)
        username = request_body.get('username')
        password = request_body.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            message = 'Welcome {}. You are requesting to build Graph at {}'. \
                format(user.get_username(), datetime.now().strftime("%Y-%m-%d %H:%m:%S"))
            logger.info(message)
            data_config = request_body.get('data')
            data_retriever = d_rtr.DataRetriever(data_config=data_config)
            graph_parser = g_pars.GraphParser()
            graph_builder = GraphBuilder(graph_parser,
                                         load_graph=not rebuild,
                                         save_graph=True)
            graph_builder.build(data_retriever)
            logger.info('=======================================')
            logger.info('========BUILD GRAPH COMPLETED==========')
            logger.info('=======================================')
            return response.Response(message)
        logger.info('Client IP: "{}" - Username: "{}" - Password: "{}" - is '
                    'trying to request Build Graph but without valid authentication'.
                    format(audit.get_client_ip(request), username, password))
        logger.info('=======================================')
        logger.info('==========BUILD GRAPH FAILED===========')
        logger.info('=======================================')
        return http.HttpResponseForbidden('Permission denied')
    else:
        return http.HttpResponseForbidden('Permission denied')


def summary(request):
    if audit.verify_request(request):
        # TODO: Summary and plot graph
        pass
    else:
        return http.HttpResponseForbidden('Permission denied')
    # start = datetime.now()
    # logger.info('Analyze Performance Saver')
    # perf_saver = graph_render.PerformanceSaver(t_analysis.graph_manager)
    # logger.info('Constructing Graph objects')
    # t_ka_graph = katalon_graph.KatalonGraph(perf_saver=perf_saver)
    # t_di_graph, t_position = t_ka_graph.get_word2vector_position_3d(report.data_report.preprocessed)
    # t_ka_graph.plot_3d_network(report.data_report.preprocessed, t_position)
    # logger.info('Request analyze big data {}'.format(datetime.now() - start))


def ranking(request):
    if audit.verify_request(request):
        # TODO ranking
        pass
    else:
        return http.HttpResponseForbidden('Permission denied')
