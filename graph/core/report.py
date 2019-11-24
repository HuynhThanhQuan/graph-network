class Report:
    def __init__(self, data_report, cluster_report):
        self.data_report = data_report
        self.cluster_report = cluster_report


class DataReport:
    def __init__(self, uuid, origin,
                 valid_data=None,
                 exclude_indices=None,
                 valid_indices=None,
                 preprocessed=None,
                 one_hot_vector=None):
        self.uuid = uuid
        self.origin = origin
        self.valid_data = valid_data
        self.exclude_indices = exclude_indices
        self.valid_indices = valid_indices
        self.preprocessed = preprocessed
        self.one_hot_vector = one_hot_vector


class ClusterReport:
    def __init__(self, cluster_algorithms=None,
                 docid_uuid_map=None,
                 labels=None,
                 clusterid_docids_mapping=None,
                 clusterid_errorlogids_map=None,
                 score_matrix=None,
                 evaluation_report=None):
        self.cluster_algorithms = cluster_algorithms
        self.docid_uuid_map = docid_uuid_map
        self.score_matrix = score_matrix
        self.clusterid_docids_map = clusterid_docids_mapping
        self.clusterid_errorlogids_map = clusterid_errorlogids_map
        self.labels = labels
        self.evaluation_report = evaluation_report

    def gather_report(self):
        if self.docid_uuid_map is not None:
            self.clusterid_errorlogids_map = {}
            for clusterid, docids in self.clusterid_docids_map.items():
                self.clusterid_errorlogids_map[clusterid] = [self.docid_uuid_map[docid] for docid in docids]
