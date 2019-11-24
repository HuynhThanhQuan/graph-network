import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PerformanceSaver:
    MAX_NUMBER_NODES_RESPECT_TO_SHORT_TIME_RENDERING = 300
    MAX_NUMBER_NODES_RESPECT_TO_MEDIUM_TIME_RENDERING = 500
    MAX_NUMBER_NODES_RESPECT_TO_LONG_TIME_RENDERING = 1000
    MIN_NUMBER_NODES_RESPECT_TO_LOST_INFORMATION = 100

    STANDARD_MAX_NODES = None

    def __init__(self, graph_manager, response_time='short'):
        assert graph_manager is not None, 'Graph must must not be None'
        self.graph_manager = graph_manager
        self.response_time = response_time
        self.edge_property = {}
        self.remove_node_names = []
        self.validate()

    def validate(self):
        # Reduce number of token under 1000 for better visualization
        token_counter_map = {node.name: node.weight for hash_id, node in self.graph_manager.node_manager.pool.items()}
        num_total_tokens = len(token_counter_map.keys())
        logger.info('Number of tokens {}'.format(num_total_tokens))
        if self.response_time == 'short':
            PerformanceSaver.STANDARD_MAX_NODES = PerformanceSaver.MAX_NUMBER_NODES_RESPECT_TO_SHORT_TIME_RENDERING
            self.load_short_time_response_property()
        elif self.response_time == 'medium':
            PerformanceSaver.STANDARD_MAX_NODES = PerformanceSaver.MAX_NUMBER_NODES_RESPECT_TO_MEDIUM_TIME_RENDERING
            self.load_medium_time_response_property()
        elif self.response_time == 'long':
            PerformanceSaver.STANDARD_MAX_NODES = PerformanceSaver.MAX_NUMBER_NODES_RESPECT_TO_LONG_TIME_RENDERING
            self.load_long_time_response_property()

        if num_total_tokens > PerformanceSaver.STANDARD_MAX_NODES:
            desc_ordered_tokens = sorted(token_counter_map.items(), key=lambda x: x[1], reverse=False)
            num_leftover = num_total_tokens - PerformanceSaver.STANDARD_MAX_NODES
            pivot_cutting = num_leftover
            # If post-token has frequency equal current tokens'frequency then remove as well
            while desc_ordered_tokens[pivot_cutting][1] == desc_ordered_tokens[pivot_cutting + 1][1]:
                if pivot_cutting > PerformanceSaver.MIN_NUMBER_NODES_RESPECT_TO_LOST_INFORMATION:
                    # Until it reach a certain threshold
                    break
                pivot_cutting += 1
            num_leftover = pivot_cutting
            self.remove_node_names = desc_ordered_tokens[:num_leftover]

    def load_short_time_response_property(self):
        self.edge_property['plot'] = False

    def load_medium_time_response_property(self):
        self.edge_property['plot'] = False

    def load_long_time_response_property(self):
        self.edge_property['plot'] = True

    def filter(self, graph, position):
        graph.remove_nodes_from([_[0] for _ in self.remove_node_names])
        for node_name in self.remove_node_names:
            del position[node_name[0]]
        assert len(graph.nodes()) == len(position.keys()), \
            "Mismatched between Graph length {} and Position length {}".format(len(graph.nodes()), len(position.keys()))
        return graph, position
