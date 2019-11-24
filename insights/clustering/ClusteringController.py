from collections import OrderedDict
from django.conf import settings
from sqlalchemy import create_engine
import pandas as pd
# from .graph.operation import AutoAnalysis
from datetime import datetime
from graph.core import graph_parser as g_pars
from graph.core import graph_analyzer as g_ana
from graph.build.graph_builder import GraphBuilder
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ClusteringBundle:
    def __init__(self,
                 failed_result_id,
                 cluster,
                 content,
                 error_log_id,
                 execution_test_result):
        self.id = failed_result_id
        self.cluster = cluster
        self.content = content
        self.error_log_id = error_log_id
        self.execution_test_result = execution_test_result
        self.cluster_id = getattr(cluster, 'id', None)
        self.summarization = getattr(cluster, 'summarization', None)


class ClusteringController:
    def __init__(self):
        self.features = None
        self.data = {}
        self.bundles = {}
        self.docId_id_mapping = {}
        self.id_docId_mapping = {}

    def find_failed_results_execution_id(self, exe_id):
        engine = create_engine('postgres://{}:{}@{}:{}/{}'.format(settings.DATABASES['default']['USER'],
                                                                  settings.DATABASES['default']['PASSWORD'],
                                                                  settings.DATABASES['default']['HOST'],
                                                                  settings.DATABASES['default']['PORT'],
                                                                  settings.DATABASES['default']['NAME']))
        sql = """select * from test_result_log trl inner join 
        (select id as failed_result_id, error_details_id from execution_test_result 
        where execution_id = %s and status = 1 order by start_time) etr on trl.id = etr.error_details_id""" % exe_id

        start = datetime.now()
        execution_test_results = pd.read_sql(sql, con=engine)
        logger.info('Find {} failed test result within interval {}'.format(len(execution_test_results),
                                                                           datetime.now() - start))

        self.bundles = OrderedDict()
        for _, execution_test_result in execution_test_results.iterrows():
            bundle = ClusteringBundle(
                failed_result_id=execution_test_result['failed_result_id'],
                cluster=None,
                content=execution_test_result['content'],
                error_log_id=execution_test_result['error_details_id'],
                execution_test_result=execution_test_result,
            )
            self.bundles[bundle.id] = bundle

        ids = self.bundles.keys()
        self.docId_id_mapping = dict(zip(range(len(ids)), ids))
        self.id_docId_mapping = dict(zip(ids, range(len(ids))))
        return self.bundles

    def find_failed_results_within_interval(self, project_id, start_time, end_time, ka_processed=True):
        engine = create_engine('postgres://{}:{}@{}:{}/{}'.format(settings.DATABASES['default']['USER'],
                                                                  settings.DATABASES['default']['PASSWORD'],
                                                                  settings.DATABASES['default']['HOST'],
                                                                  settings.DATABASES['default']['PORT'],
                                                                  settings.DATABASES['default']['NAME']))
        if ka_processed is False:
            sql = """select * from test_result_log trl inner join 
                (select etr.id as failed_result_id, etr.error_details_id from execution_test_result etr inner join 
                (select id from execution where project_id = %s and start_time >= '%s' and end_time <= '%s') 
                exe_id on etr.execution_id = exe_id.id
                where etr.status = 1) edi on edi.error_details_id = trl.id""" % (project_id, start_time, end_time)

            start = datetime.now()
            execution_test_results = pd.read_sql(sql, con=engine)
            logger.info('Find {} failed test result within interval {}'.format(len(execution_test_results),
                                                                               datetime.now() - start))

            self.bundles = OrderedDict()
            for _, execution_test_result in execution_test_results.iterrows():
                bundle = ClusteringBundle(
                    failed_result_id=execution_test_result['failed_result_id'],
                    cluster=None,
                    content=execution_test_result['content'],
                    error_log_id=execution_test_result['error_details_id'],
                    execution_test_result=execution_test_result,
                )

                self.bundles[bundle.id] = bundle
        else:
            sql = """select * from test_result_stack_trace trst inner join 
                (select etr.id, etr.error_details_id, exe_id.start_time, exe_id.end_time 
                from execution_test_result etr inner join 
                (select id, start_time, end_time 
                from execution where project_id = %s and start_time >= '%s' and end_time <= '%s') 
                exe_id on etr.execution_id = exe_id.id) abc 
                on trst.test_result_id = abc.id""" % (project_id, start_time, end_time)

            start = datetime.now()
            execution_test_results = pd.read_sql(sql, con=engine)
            logger.info('Find {} failed test result within interval {}'.format(len(execution_test_results),
                                                                               datetime.now() - start))

            self.bundles = OrderedDict()
            for _, execution_test_result in execution_test_results.iterrows():
                bundle = ClusteringBundle(
                    failed_result_id=execution_test_result['test_result_id'],
                    cluster=None,
                    content=execution_test_result['stack_trace'],
                    error_log_id=execution_test_result['error_details_id'],
                    execution_test_result=execution_test_result,
                )

                self.bundles[bundle.id] = bundle

        ids = self.bundles.keys()
        self.docId_id_mapping = dict(zip(range(len(ids)), ids))
        self.id_docId_mapping = dict(zip(ids, range(len(ids))))
        return self.bundles

    def find_failed_results_project_id(self, project_id):
        engine = create_engine('postgres://{}:{}@{}:{}/{}'.format(settings.DATABASES['default']['USER'],
                                                                  settings.DATABASES['default']['PASSWORD'],
                                                                  settings.DATABASES['default']['HOST'],
                                                                  settings.DATABASES['default']['PORT'],
                                                                  settings.DATABASES['default']['NAME']))

        sql = """select * from test_result_stack_trace trst inner join 
        (select etr.id, etr.start_time from execution_test_result etr inner join 
        (select id from execution where project_id = %s) exe on etr.execution_id = exe.id) abc 
        on trst.test_result_id = abc.id order by start_time desc""" % project_id

        start = datetime.now()
        execution_test_results = pd.read_sql(sql, con=engine)
        logger.info('Find failed test result within interval {}'.format(datetime.now() - start))

        self.bundles = OrderedDict()
        for _, execution_test_result in execution_test_results.iterrows():
            bundle = ClusteringBundle(
                failed_result_id=execution_test_result['test_result_id'],
                cluster=None,
                content=execution_test_result['stack_trace'],
                error_log_id=execution_test_result['test_result_log_id'],
                execution_test_result=execution_test_result,
            )

            self.bundles[bundle.id] = bundle

        ids = self.bundles.keys()
        self.docId_id_mapping = dict(zip(range(len(ids)), ids))
        self.id_docId_mapping = dict(zip(ids, range(len(ids))))
        return self.bundles

    @property
    def bundles(self):
        return self.__bundles

    @bundles.setter
    def bundles(self, bundles):
        self.__bundles = bundles
        ids = self.__bundles.keys()
        self.docId_id_mapping = dict(zip(range(len(ids)), ids))
        self.id_docId_mapping = dict(zip(ids, range(len(ids))))

    @staticmethod
    def hierarchical_cluster_on_the_fly(bundles):
        assert len(bundles) > 0, "Bundles must not be empty"
        ids = [bundle.id for _id, bundle in bundles.items()]
        documents = [bundle.content for _id, bundle in bundles.items()]
        data_bundles = (ids, documents)
        graph_parser = g_pars.GraphParser(detect_ka=True)
        graph_builder = GraphBuilder(graph_parser,
                                     load_graph=False,
                                     save_graph=False).load()
        graph_builder.fit(data_bundles)
        graph_analyzer = g_ana.GraphAnalyzer(graph_builder, graph_parser)
        report = graph_analyzer.analyze_bundle(data_bundles, one_shot=True)
        return report
