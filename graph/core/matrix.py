import numpy as np


class MatrixCalculation:

    @staticmethod
    def doc_doc_similarity(matrix_a, matrix_b):
        """
        Shape of 2 matrices must be a[m,n] * b[n,m]
        Basic dot product, for other inner product consider to use broadcasting
        :param matrix_a: Vector a
        :param matrix_b: Vector b
        :return: Cosine simliarity
        """
        assert matrix_a.shape[1] == matrix_b.shape[0], "Mismatched shape between matrix A and matrix B"
        numerator = np.dot(matrix_a, matrix_b)
        assert numerator.shape == (matrix_a.shape[0], matrix_b.shape[1]), numerator.shape
        denominator = np.sqrt(np.sum(matrix_a ** 2, axis=1))[:, np.newaxis] * np.sqrt(
            np.sum(matrix_b.T ** 2, axis=1))[:, np.newaxis].T
        assert (denominator > 0).all(), "Denominator is zero {}".format(denominator)
        similarity_matrix = np.multiply(numerator, 1 / denominator)
        return similarity_matrix

    @staticmethod
    def xnor_score(matrix_a, matrix_b, weights=1):
        """
        Shape of 2 matrices must be a[m,n] * b[n,m]
        :param weights: Broadcasting weight into inner product
        :param matrix_a:
        :param matrix_b:
        :return:
        """
        assert matrix_a.shape[1] == matrix_b.shape[0], "Mismatched shape between matrix A and matrix B"
        weights = np.array([1] * matrix_a.shape[1]) if weights == 1 else weights
        return np.sum((matrix_a[..., np.newaxis] == matrix_b.T) * weights[..., np.newaxis], axis=1)/np.sum(weights)
