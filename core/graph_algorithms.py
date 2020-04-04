from sklearn.feature_extraction import text
from sklearn import cluster
import numpy as np


class SparseMatrixClustering:
    def __init__(self, cluster_sim_threshold, graph_manager):
        self.cluster_sim_threshold = cluster_sim_threshold
        self.graph_manager = graph_manager
        self.score_mat = None
        self.clusterid_docids_mapping = None
        self.min_samples = 3
        self.abnormaly_detection = True
        self.labels_ = None

    def fit(self, x):
        self.score_mat = self.graph_manager.compare_ohv_stacktrace(x)
        self.clusterid_docids_mapping = self.__cluster__(self.score_mat)
        self.clusterid_docids_mapping = self.__exclude_abnormaly__(self.clusterid_docids_mapping)
        self.__relabel__(self.clusterid_docids_mapping)

    def __cluster__(self, score_mat):
        doc_ids = list(range(score_mat.shape[0]))
        clusterid = 0
        clusterid_docids_mapping = {}
        while len(doc_ids) > 0:
            pivot = doc_ids[0]
            sub = [doc_id for doc_id in doc_ids if doc_id != pivot]
            clusterid_docids_mapping[clusterid] = [pivot]
            doc_ids.remove(pivot)
            for doc_id in sub:
                if score_mat[pivot][doc_id] >= self.cluster_sim_threshold:
                    clusterid_docids_mapping[clusterid].append(doc_id)
                    doc_ids.remove(doc_id)
            clusterid += 1
        return clusterid_docids_mapping

    def __exclude_abnormaly__(self, clusterid_docids_mapping):
        if self.abnormaly_detection:
            other = []
            abnormal_keys = []
            for k, v in clusterid_docids_mapping.items():
                if len(v) <= self.min_samples:
                    other += v
                    abnormal_keys.append(k)
            for k in abnormal_keys:
                del clusterid_docids_mapping[k]
            if len(other) > 0:
                clusterid_docids_mapping['other'] = other
        return clusterid_docids_mapping

    def __relabel__(self, clusterid_docids_map):
        self.labels_ = np.zeros(self.score_mat.shape[0])
        for clusterid, docids in clusterid_docids_map.items():
            for docid in docids:
                if clusterid != 'other':
                    self.labels_[docid] = clusterid
                else:
                    self.labels_[docid] = -1


class GraphClusteringAlgorithms:
    def __init__(self, algorithms, balance_weights=False, graph_manager=None):
        self.algorithms = algorithms
        self.balanace_weights = balance_weights
        self.graph_manager = graph_manager
        self.tfidf_vec = None
        self.clusterid_docids_map = None
        self.ohv_stacktrace = None
        self.labels = None

    @staticmethod
    def preprocess(x):
        return [' '.join(stacktrace) for stacktrace in x]

    def __rebalance_weights__(self, x):
        if self.balanace_weights is True:
            self.tfidf_vec = text.TfidfVectorizer()
            return self.tfidf_vec.fit_transform(x).toarray()
        return x

    def __apply_cluster_algorithms__(self, x):
        if self.algorithms == 'k-mean':
            kmeans = cluster.KMeans(n_clusters=3)
            kmeans.fit(x)
            self.labels = kmeans.labels_
            for i, label in enumerate(kmeans.labels_):
                self.clusterid_docids_map[label] = self.clusterid_docids_map.get(label, []) + [i]
        elif self.algorithms == 'dbscan':
            dbscan = cluster.DBSCAN(eps=2, min_samples=3)
            dbscan.fit(x)
            self.labels = dbscan.labels_
            for i, label in enumerate(dbscan.labels_):
                self.clusterid_docids_map[label] = self.clusterid_docids_map.get(label, []) + [i]
        else:
            sm_cluster = SparseMatrixClustering(cluster_sim_threshold=0.8, graph_manager=self.graph_manager)
            sm_cluster.fit(x)
            self.score_mat = sm_cluster.score_mat
            self.clusterid_docids_map = sm_cluster.clusterid_docids_mapping


    def fit(self, x):
        node_pool, self.ohv_stacktrace = self.graph_manager.__convert_to_ohv__(x)
        # if self.algorithms != 'default':
        #     x = self.preprocess(x)
        #     x = self.__rebalance_weights__(x)
        self.__apply_cluster_algorithms__(self.ohv_stacktrace)
        # return x
