class BigDataEnvVar:
    CHUNKSIZE = 5000
    TEMP_FOLDER = '.temp'
    DOC_TERM_FOLDER = 'doc_term'
    MAT_CAL_FOLDER = 'mat_cal'
    STANDARD_FORMAT = 'pickle'
    COMPLEVEL = 5
    COMPLIB = 'blosc'

    def __init__(self, kwargs):
        BigDataEnvVar.CHUNKSIZE = int(kwargs.get('chunksize', 5000))
        BigDataEnvVar.TEMP_FOLDER = kwargs.get('temp_folder', '.temp')
        BigDataEnvVar.DOC_TERM_FOLDER = kwargs.get('doc_term_folder', 'doc_term')
        BigDataEnvVar.MAT_CAL_FOLDER = kwargs.get('matrix_cal_folder', 'matrix_cal')
        BigDataEnvVar.STANDARD_FORMAT = kwargs.get('standard_format', 'pickle')
        BigDataEnvVar.COMPLEVEL = int(kwargs.get('complevel', 5))
        BigDataEnvVar.COMPLIB = kwargs.get('complib', 'blosc')
