import tables as tb
import numpy as np
import os
import uuid
from graph.core.matrix import MatrixCalculation
from datetime import datetime
import logging
from bigdata.build import bigdata_configure as conf
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BigDataStorageHDF5:
    TEMP_STORAGE = os.path.join(os.path.dirname(__file__), conf.BigDataEnvVar.TEMP_FOLDER)
    DOCTERM_STORAGE = os.path.join(TEMP_STORAGE, conf.BigDataEnvVar.DOC_TERM_FOLDER)
    MATRIX_STORAGE = os.path.join(TEMP_STORAGE, conf.BigDataEnvVar.MAT_CAL_FOLDER)

    def __init__(self, temporary=True):
        self.temporary = temporary
        self.uuid = uuid.uuid4()
        self.location = os.path.join(BigDataStorageHDF5.DOCTERM_STORAGE, str(self.uuid) + '.h5')
        self.file = None
        self.filters = tb.Filters(complevel=conf.BigDataEnvVar.COMPLEVEL, complib=conf.BigDataEnvVar.COMPLIB)
        self.open()

    def open(self):
        logger.info('One-hot matrix is stored at {}'.format(self.location))
        self.file = tb.open_file(self.location, 'w')

    def init_columns(self):
        self.file.create_group(self.file.root, 'uuid')
        self.file.create_group(self.file.root, 'data')

    def write_into_file(self, chunk_idx, uuids, data):
        uuid_node = self.file.get_node('/uuid')
        data_node = self.file.get_node('/data')
        chunk_index = 'chunk_' + str(chunk_idx)
        uuid_h5 = self.file.create_carray(uuid_node, chunk_index,
                                          atom=tb.Float32Atom(), shape=(len(uuids),), filters=self.filters)
        uuid_h5[:] = uuids
        matrix_h5 = self.file.create_carray(data_node, chunk_index,
                                            atom=tb.Float32Atom(), shape=data.shape, filters=self.filters)
        matrix_h5[:] = data
        return '/uuid/{}'.format(chunk_index), '/data/{}'.format(chunk_index)

    def close(self):
        self.file.close()
        size = os.path.getsize(self.location)
        logger.info('Size of temporary one-hot matrix storage {} bytes ~ {} GB'.format(size, size * (9.31 * 10 ** -10)))

    def delete(self):
        if os.path.exists(BigDataStorageHDF5.TEMP_STORAGE) and os.path.exists(BigDataStorageHDF5.DOCTERM_STORAGE):
            try:
                temp_files = os.listdir(BigDataStorageHDF5.DOCTERM_STORAGE)
                for temp_file in temp_files:
                    temp_file_path = os.path.join(BigDataStorageHDF5.DOCTERM_STORAGE, temp_file)
                    try:
                        os.remove(temp_file_path)
                    except OSError as e:
                        logger.error('Failed to delete temporary one-hot matrix storage file {}'.format(temp_file_path))
                        logger.error(e.args[0])
            except OSError as e:
                logger.warning('WARNING - Cleaning temporary one-hot matrix storage process issues. '
                               'Please contact administrator for technical support')
                logger.error(e.args[0])
            finally:
                logger.info('Cleaned temporary one-hot matrix storage process')
        else:
            os.makedirs(BigDataStorageHDF5.DOCTERM_STORAGE)
            self.delete()


class BigDataMatrixCalculation:
    def __init__(self, temporary=True):
        self.temporary = temporary
        self.uuid = uuid.uuid4()
        self.location = os.path.join(BigDataStorageHDF5.MATRIX_STORAGE, str(self.uuid) + '-matrix-calculation.h5')
        self.file = None
        self.filters = tb.Filters(complevel=5, complib='blosc')
        self.open()

    def open(self):
        self.file = tb.open_file(self.location, 'w')

    def write_to_coord_x_y(self, i_group, j_node, data):
        abs_group = '/gmat_{}'.format(str(i_group))
        matrix_data = self.file.create_carray(abs_group, 'sub_mat_{}'.format(str(j_node)),
                                              atom=tb.Float32Atom(), shape=data.shape, filters=self.filters)
        matrix_data[:] = data

    def create_group(self, group_name):
        self.file.create_group(self.file.root, group_name)

    def close(self):
        self.file.close()
        size = os.path.getsize(self.location)
        logger.info('Size of temporary Doc2Doc matrix storage {} bytes ~ {} GB'.format(size, size * (9.31 * 10 ** -10)))

    def delete(self):
        if os.path.exists(BigDataStorageHDF5.TEMP_STORAGE) and os.path.exists(BigDataStorageHDF5.MATRIX_STORAGE):
            try:
                temp_files = os.listdir(BigDataStorageHDF5.MATRIX_STORAGE)
                for temp_file in temp_files:
                    temp_file_path = os.path.join(BigDataStorageHDF5.MATRIX_STORAGE, temp_file)
                    try:
                        os.remove(temp_file_path)
                    except OSError as e:
                        logger.error('Failed to delete temporary Doc2Doc matrix storage file {}'.format(temp_file_path))
                        logger.error(e.args[0])
            except OSError as e:
                logger.warning('WARNING - Cleaning temporary Doc2Doc matrix storage process issues. '
                               'Please contact administrator for technical support')
                logger.error(e.args[0])
            finally:
                logger.info('Cleaned temporary Doc2Doc matrix storage process')
        else:
            os.makedirs(BigDataStorageHDF5.MATRIX_STORAGE)
            self.delete()


class BigDataReport:
    def __init__(self):
        self.cluster_docids_map = {}
        self.status = 'ERROR'
        self.chunk_size = 0


class BigDataClusterring:
    def __init__(self, cluster_threshold, node_ids, storage='hdf5'):
        logger.info('Activate Big Data matrix calculation')
        logger.info('Num_nodes={}, Storage Mode={}, Cluster_threshold={}'.
                    format(len(node_ids), storage, cluster_threshold))
        self.cluster_similar_threshold = cluster_threshold
        self.node_ids = node_ids
        self.bigdata_report = BigDataReport()
        self.storage = storage
        self.storage_instance = None
        self.table_nodes = []
        self.status = None
        self.init_storage()

    def init_storage(self):
        if self.storage == 'hdf5':
            self.storage_instance = BigDataStorageHDF5()
            self.storage_instance.init_columns()

    def add(self, chunk_idx, uuids, hashed_stacktraces):
        assert uuids is not None
        assert hashed_stacktraces is not None
        assert len(uuids) == len(hashed_stacktraces), "Mismatched shape between UUID and Data"
        start = datetime.now()
        np_matrix = np.array([np.isin(self.node_ids, hash_stacktrace).astype(np.int32)
                              for hash_stacktrace in hashed_stacktraces])
        logger.info('--- --- Looked up one-hot-matrix within {}'.format(datetime.now() - start))
        # TODO: Add option to convert crs_matrix format (scipy)
        # ohv_matrix = csr_matrix(np_matrix)
        start = datetime.now()
        tb_node = self.storage_instance.write_into_file(chunk_idx, uuids, np_matrix)
        logger.info('--- --- Wrote one-hot-matrix into temp storage {}'.format(datetime.now() - start))
        self.table_nodes.append(tb_node)

    def wipe_out(self):
        self.storage_instance.close()
        self.storage_instance.delete()
        logger.info('Wiped out temporary data')

    def execute(self):
        start = datetime.now()
        # Write Doc-Doc similarity matrix into H5
        matrix_calculation = BigDataMatrixCalculation()
        logger.info('Saving temporary Doc2Doc similarity matrix storage at {}'.format(matrix_calculation.location))
        logger.info('STEP 2/3: CALCULATE COSINE SIMILARITY')
        total_nodes = len(self.table_nodes)
        for i in range(len(self.table_nodes)):
            start_loop = datetime.now()
            matrix_calculation.create_group('gmat_{}'.format(i))
            doc_term_f = self.storage_instance.file
            tb_node_i = doc_term_f.get_node(self.table_nodes[i][1], classname='Array')
            matrix_chunk_1 = np.array(tb_node_i)
            for j in range(len(self.table_nodes)):
                tb_node_j = doc_term_f.get_node(self.table_nodes[j][1], classname='Array')
                matrix_chunk_2 = np.array(tb_node_j)
                dot_sub_mat_ij = MatrixCalculation.doc_doc_similarity(matrix_chunk_1, matrix_chunk_2.T)
                matrix_calculation.write_to_coord_x_y(i, j, dot_sub_mat_ij)
            logger.info('--- Calculated cosine similiarity of group matrix gmat_{}/{} - {}'.
                        format(i, total_nodes - 1, datetime.now() - start_loop))
        logger.info('Saved temporary Doc2Doc similarity matrix storage within {}'.format(datetime.now() - start))

        start1 = datetime.now()
        logger.info('Clustering big data Doc2Doc similarity matrix')
        logger.info('STEP 3/3: CLUSTER MATRIX')
        # Cluster matrix similarity - join row by row by iterating on y-coordinate
        clusterid_docids_map = {}
        cluster_id = 0
        grouped_indices = []
        inc_index_i = 0
        for i in range(len(self.table_nodes)):
            logger.info('--- Iterating chunk {}/{} row matrix'.format(i + 1, total_nodes))
            # Hstack on chunk matrix
            start_stack = datetime.now()
            pivot_i_submat = np.array(matrix_calculation.file.get_node('/gmat_{}'.format(i),
                                                                       'sub_mat_0',
                                                                       classname='Array'))
            abs_docid_i = set(list(range(inc_index_i, pivot_i_submat.shape[0] + inc_index_i)))
            leftover_abs_i_indices = list(set(abs_docid_i) - (set(abs_docid_i) & set(grouped_indices)))
            leftover_rel_i_indices = list(np.array(leftover_abs_i_indices) - inc_index_i)
            row_matrix = np.array([])
            for j in range(len(self.table_nodes)):
                sub_mat_j = np.array(matrix_calculation.file.get_node('/gmat_{}'.format(i),
                                                                      'sub_mat_{}'.format(j),
                                                                      classname='Array'))
                row_matrix = np.hstack((row_matrix, sub_mat_j[leftover_rel_i_indices])) if row_matrix.size \
                    else sub_mat_j[leftover_rel_i_indices]
            logger.info('--- --- Stacked horizontal row matrix {} '.format(datetime.now() - start_stack))

            # Cluster on hstack matrix
            start_cluster = datetime.now()
            leftover_abs_j_indices = list(set(list(range(row_matrix.shape[1]))) - set(grouped_indices))
            rel_docids = list(range(row_matrix.shape[0]))
            abs_docids = np.array(rel_docids) + inc_index_i
            abs_intersection = list(set(abs_docids) & set(leftover_abs_j_indices))
            rel_itersection = (np.array(abs_intersection) - inc_index_i).tolist()
            while len(rel_itersection) > 0:
                rel_pivot = rel_itersection[0]
                abs_pivot = rel_pivot + inc_index_i
                if abs_pivot + 1 == row_matrix.shape[1]:
                    break
                abs_sim_indicies = np.where(row_matrix[rel_pivot][abs_pivot + 1:] >= self.cluster_similar_threshold)[0]
                abs_sim_indicies = list(set(abs_sim_indicies) & set(leftover_abs_j_indices))
                abs_sim_indicies.append(abs_pivot)
                grouped_indices.extend(abs_sim_indicies)

                clusterid_docids_map[cluster_id] = clusterid_docids_map.get(cluster_id, []) + abs_sim_indicies
                cluster_id += 1

                leftover_abs_j_indices = list(set(list(range(row_matrix.shape[1]))) - set(grouped_indices))
                rel_docids = list(range(row_matrix.shape[0]))
                abs_docids = np.array(rel_docids) + inc_index_i
                abs_intersection = list(set(abs_docids) & set(leftover_abs_j_indices))
                rel_itersection = (np.array(abs_intersection) - inc_index_i).tolist()

                total_est_clusterd_id = sum([len(_) for _ in clusterid_docids_map.values()])
                total_real_clustered_id = len(grouped_indices)
                total_leftover_id = len(leftover_abs_j_indices)
                total_doc = row_matrix.shape[1]
                assert total_est_clusterd_id == total_real_clustered_id, \
                    'Estimate {} - Real {} - Leftover {} - Total {}'. \
                        format(total_est_clusterd_id, total_real_clustered_id, total_leftover_id, total_doc)
                # FIXME: check total
                # assert total_leftover_id + total_real_clustered_id == total_doc, \
                #     'Estimate {} - Real {} - Leftover {} - Total {}'.\
                #     format(total_est_clusterd_id, total_real_clustered_id, total_leftover_id, total_doc)
            logger.info('--- --- Clustered chunk {} row matrix {} '.format(i + 1, datetime.now() - start_cluster))
            inc_index_i += pivot_i_submat.shape[0]

        start_reindex = datetime.now()
        for k, v in clusterid_docids_map.items():
            clusterid_docids_map[k] = sorted(v)
        logger.info('Reindexed clustering docids {}'.format(datetime.now() - start_reindex))
        # Prepare report
        self.bigdata_report.cluster_docids_map = clusterid_docids_map
        self.bigdata_report.status = 'OK'
        logger.info('Finished clustering big data Doc2Doc similarity matrix within {}'.format(datetime.now() - start1))
        matrix_calculation.close()
        matrix_calculation.delete()
