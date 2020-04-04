import re
import collections
from datetime import datetime
from algorithms.core.nlp.algorithms import TopicModelling
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DeepAnalysis:
    PATTERN = r'[A-Z]+[a-z]+'
    MAX_NUMBER_NODES = 1000
    LOWER_BOUND_NODES = 500
    COMMON_TOKENS = {'com', 'kms', 'katalon', 'main', 'core', 'webui', 'builtin', 'common', 'keyword'}

    def __init__(self):
        self.all_tokens = []
        self.valid_tokens = set()

    def execute(self, graph_manager):
        # Analayze total tokens
        start = datetime.now()
        for node_id, node in graph_manager.node_manager.pool.items():
            self.add_tokens(node.name)
        # Get statictis of graph
        token_counter_map = collections.Counter(self.all_tokens)
        token_counter_map = self.remove_under_criteria_token(token_counter_map)
        self.valid_tokens = set(list(token_counter_map.keys()))
        # Assign additional attributes to graph
        for node_id, node in graph_manager.node_manager.pool.items():
            graph_manager.node_manager.pool[node_id].static_attribute = {'token': self.tokenize(node.name)}
        logger.info('Add "tokenization" attribute {}'.format(datetime.now() - start))
        # Topic Modelling issue #21
        logger.info('Analyze Topic Modelling')
        sentences = [[_ for node in nodes for _ in node.static_attribute['token']]
                     for uuid, nodes in graph_manager.stacktrace_manager.uuid_nodes_map.items()]
        topic_model = TopicModelling()
        topic_model.apply_lda(sentences)

    @staticmethod
    def remove_under_criteria_token(token_counter_map):
        # Remove common tokens
        for common_token in DeepAnalysis.COMMON_TOKENS:
            if common_token in token_counter_map.keys():
                del token_counter_map[common_token]
        # Reduce number of token under 1000 for better visualization
        logger.info('Number of tokens {}'.format(len(token_counter_map.keys())))
        if len(token_counter_map.keys()) > DeepAnalysis.MAX_NUMBER_NODES:
            desc_ordered_tokens = sorted(token_counter_map.items(), key=lambda x: x[1], reverse=False)
            num_leftover = len(token_counter_map.keys()) - DeepAnalysis.MAX_NUMBER_NODES
            pivot_cutting = num_leftover
            # If post-token has frequency equal current tokens'frequency then remove as well
            while desc_ordered_tokens[pivot_cutting][1] == desc_ordered_tokens[pivot_cutting + 1][1]:
                if pivot_cutting > DeepAnalysis.LOWER_BOUND_NODES:
                    # Until it reach a certain threshold
                    break
                pivot_cutting += 1
            num_leftover = pivot_cutting
            removed_keys = desc_ordered_tokens[:num_leftover]
            for removed_key in removed_keys:
                del token_counter_map[removed_key]
        return token_counter_map

    def add_tokens(self, node_name):
        for _ in re.split(r'\.', node_name):
            if re.search(DeepAnalysis.PATTERN, _):
                tokens = re.findall(DeepAnalysis.PATTERN, node_name)
                self.all_tokens.extend(tokens)
            else:
                self.all_tokens.append(_)

    def tokenize(self, node_name):
        local_tokens = []
        for _ in re.split(r'\.', node_name):
            if re.search(DeepAnalysis.PATTERN, _):
                tokens = re.findall(DeepAnalysis.PATTERN, node_name)
                words = set(tokens) & self.valid_tokens
                for word in words:
                    if not re.search(r'\d', _):
                        local_tokens.append(word)
            else:
                if _ in self.valid_tokens:
                    if not re.search(r'\d', _):
                        local_tokens.append(_)
        return local_tokens
