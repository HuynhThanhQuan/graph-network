import pandas as pd
from graph import util
from graph.core import constraint


class Evaluation:
    def __init__(self, graph_parser):
        self.graph_parser = graph_parser
        self.num_error_logs = 0
        self.num_unique_stacktrace = 0
        self.percent_unique_stacktrace = 0
        self.unique_stacktrace = None
        self.match_exactly = False
        self.representation = None

    def fit(self, error_logs):
        self.num_error_logs = len(error_logs)
        assert self.num_error_logs > 0, "No input data found"
        list_stacktrace, valid_indices, exclude = self.graph_parser.validate(error_logs)
        assert len(list_stacktrace) > 0, "Input Data is not valid"
        self.unique_stacktrace = set([' '.join(stacktrace) for stacktrace in list_stacktrace])
        self.num_unique_stacktrace = len(self.unique_stacktrace)
        self.percent_unique_stacktrace = self.num_unique_stacktrace / self.num_error_logs
        self.match_exactly = self.num_unique_stacktrace == 1
        self.representation = util.find_stacktrace_representation(list_stacktrace)

    @staticmethod
    def generate_evaluation_report(graph_parser, valid_error_logs, cluster_report):
        clusterid_docids_map = cluster_report.clusterid_docids_map
        clusterid_evaluation_map = {}
        for clusterid, docids in clusterid_docids_map.items():
            error_log_ids = cluster_report.clusterid_errorlogids_map[clusterid] if \
                cluster_report.clusterid_errorlogids_map is not None else None
            sub_error_logs = [valid_error_logs[docid] for docid in docids]
            evaluation = Evaluation(graph_parser=graph_parser)
            evaluation.fit(pd.Series(sub_error_logs))
            evaluation.docids = docids
            evaluation.error_log_ids = error_log_ids
            clusterid_evaluation_map[clusterid] = evaluation
        return clusterid_evaluation_map

    @staticmethod
    def validate(tokens_list):
        result = []
        result_indices = []
        exclude = []
        for i, tokens in enumerate(tokens_list):
            valid_tokens = [token for token in tokens if token not in constraint.Constraint.VALUES]
            if len(valid_tokens) > 0:
                result_indices.append(i)
                result.append(valid_tokens)
            else:
                exclude.append(i)
        return result, result_indices, exclude
