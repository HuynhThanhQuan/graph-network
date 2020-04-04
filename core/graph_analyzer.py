import pandas as pd
from bigdata.core import bigdata
from graph.core import report
from datetime import datetime
from database import data_retriever
from graph import util
from graph.core import graph_algorithms as g_alg
from graph.core.graph_evaluation import Evaluation
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphAnalyzer:
    def __init__(self, graph_builder, graph_parser,
                 algorithms='default', deep_analyze=False):
        self.graph_parser = graph_parser
        self.graph_builder = graph_builder
        self.algorithms = algorithms
        self.deep_analyze = deep_analyze
        self.graph_algorithms = None

    def analyze_bundle(self, data_bundles, one_shot=False):
        if one_shot is False:
            return self.__analyze_generator__(data_bundles)
        uuid, error_logs = data_bundles
        return self.__analyze_one_shot__(uuid, error_logs)

    def __analyze_one_shot__(self, uuid, error_logs):
        # Validate error logs type must be a Series or list and length > 0
        assert error_logs is not None, "None error log is passing"
        assert isinstance(error_logs, pd.Series) or isinstance(error_logs, list), "Invalid data type, " \
                                                                                  "must be a list or pandas.Series"
        assert len(error_logs) > 0, 'Data must not be empty'
        error_logs = pd.Series(error_logs) if isinstance(error_logs, list) else error_logs
        assert uuid is None or isinstance(uuid, list) or isinstance(uuid, pd.Series), "Invalid type of UUID"
        assert len(uuid) == len(error_logs), "UUID must be same length of error logs"
        uuid = uuid.tolist() if isinstance(uuid, pd.Series) else uuid

        # Verify valid and invalid data
        list_stacktrace, valid_indices, excluded_indices = self.graph_parser.validate(error_logs)

        # Prepare Data Report
        data_report = report.DataReport(uuid=uuid, origin=error_logs)
        data_report.preprocessed = list_stacktrace
        data_report.exclude_indices = excluded_indices
        data_report.valid_indices = valid_indices
        data_report.valid_error_logs = error_logs.drop(error_logs.index[excluded_indices]).tolist()

        # Apply graph algorithms
        self.graph_algorithms = g_alg.GraphClusteringAlgorithms(algorithms=self.algorithms,
                                                                balance_weights=False,
                                                                graph_manager=self.graph_builder.graph_manager)
        self.graph_algorithms.fit(list_stacktrace)

        cluster_report = report.ClusterReport()
        cluster_report.cluster_algorithms = self.algorithms
        cluster_report.docid_uuid_map = dict(zip(range(len(error_logs)), uuid)) if uuid is not None else None
        data_report.one_hot_vector = self.graph_algorithms.ohv_stacktrace
        cluster_report.labels = self.graph_algorithms.labels
        cluster_report.clusterid_docids_map = self.graph_algorithms.clusterid_docids_map
        cluster_report.gather_report()
        cluster_report.evaluation_report = Evaluation.generate_evaluation_report(self.graph_parser,
                                                                                 data_report.valid_error_logs,
                                                                                 cluster_report)
        return report.Report(data_report=data_report,
                             cluster_report=cluster_report)

    def __analyze_generator__(self, generator):
        logger.info('STEP 1/3: LOOKUP ONE-HOT-VECTOR')
        start = datetime.now()
        assert self.graph_builder.graph_manager.get_total_node_pool() > 0, "No nodes at all, please check Graph Version"
        bigdata_cluster = bigdata.BigDataClusterring(0.8, self.graph_builder.graph_manager.get_all_node_pool())
        logger.info('Iterating over data')
        for idx, (data) in enumerate(generator):
            uuid, error_logs, static_attributes = data_retriever.DataRetriever.get_only_necessary_data(data)
            logger.info('--- Iterate chunk {}'.format(idx + 1))
            error_logs = pd.Series(error_logs) if isinstance(error_logs, list) else error_logs
            docid_uuid_map = dict(zip(range(len(error_logs)), uuid))
            list_stacktrace, valid_indices, exclude_idx = \
                Evaluation.validate(util.parse_with_regex(error_logs))
            valid_uuids = [docid_uuid_map[idx] for idx in valid_indices]
            if len(valid_uuids) == 0:
                continue
            bigdata_cluster.add(idx, valid_uuids, [self.graph_builder.graph_manager.convert_hash_stacktrace(stacktrace)
                                                   for stacktrace in list_stacktrace])
        bigdata_cluster.execute()
        bigdata_cluster.wipe_out()
        logger.info('Analyze big data within {}'.format(datetime.now() - start))
        return bigdata_cluster.bigdata_report

    def deep_analyze(self):
        if self.deep_analyze is True:
            logger.warning('Performing Deep Analyze - this can take a while')
            # deep_analysis = DeepAnalysis()
            # deep_analysis.execute(self.graph_manager)
