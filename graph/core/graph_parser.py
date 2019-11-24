from graph import util
from graph.core import graph_evaluation
import re
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphParser:
    def __init__(self, detect_ka=False):
        self.detect_ka = detect_ka

    @staticmethod
    def recognize_ka_preprocess(error_logs):
        detection = re.search(r'[a-zA-Z]', error_logs[0])
        return True if detection is None else False

    def parse(self, error_logs):
        if self.detect_ka is True and GraphParser.recognize_ka_preprocess(error_logs) is True:
            methods_list = [stacktrace.split(',') for stacktrace in error_logs]
        else:
            methods_list = util.parse_with_regex(error_logs)
        return methods_list

    def validate(self, error_logs):
        if self.detect_ka is True and GraphParser.recognize_ka_preprocess(error_logs) is True:
            exclude_idx = []
            valid_indices = range(len(error_logs))
            list_stacktrace = [stacktrace.split(',') for stacktrace in error_logs]
        else:
            list_stacktrace, valid_indices, exclude_idx = \
                graph_evaluation.Evaluation.validate(util.parse_with_regex(error_logs))
            if len(exclude_idx) > 0:
                logger.info('Auto excluded {} error logs because they are not valid {}...'.format(len(exclude_idx),
                                                                                                  exclude_idx[:5]))
            if len(list_stacktrace) == 0:
                logger.error('Invalid error logs after preprocessing')
                raise Exception('Invalid error logs after preprocessing')
        return list_stacktrace, valid_indices, exclude_idx
