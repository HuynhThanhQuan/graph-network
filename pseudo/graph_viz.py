import networkx as nx
import plotly.graph_objects as go
import numpy as np
import operator
from sklearn import decomposition
import collections
from datetime import datetime
from graph.visualize.graph_layout import Layout
from algorithms.core.nlp.algorithms import Word2VectorManagement
import logging
import time
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphViz:
    COLOR_SCALE = ['reds', 'RdPu', 'YlOrBr', 'Greens', 'Oranges', 'Blues', 'Purples']
    COLOR = ['red', 'pink', 'yellow', 'green', 'orange', 'blue', 'purple']

    DIRECTION_BOTTOM_UP = 'bottom-up'
    DIRECTION_TOP_DOWN = 'top-down'

    EDGE_SCALED_WIDTH_FACTOR = 0.1
    EDGE_MIN_WIDTH = 0.05
    EDGE_MAX_WIDTH = 1
    EDGE_INCREMENTAL_VALUE = 1

    NODE_MIN_SIZE = 5
    NODE_MAX_SIZE = 10
    NODE_INCREMENTAL_VALUE = 1

    VOLCANO_LAYOUT_3D = 'volcano-3d'
    CYLINDER_LAYOUT_3D = 'cylinder-3d'
    TREE_LAYOUT_3D = 'tree-3d'
    TREE_CENTRALIZED_LAYOUT_3D = 'tree-centralized-3d'
    WORD2VECTOR_LAYOUT_3D = 'word2vector-3d'

    def __init__(self, perf_saver=None, flow_direction=DIRECTION_BOTTOM_UP):
        self.perf_saver = perf_saver
        self.flow_direction = flow_direction

    @staticmethod
    def rescale_node_size(node_sizes):
        node_sizes = np.array(node_sizes)
        min_value, max_value = min(node_sizes), max(node_sizes)
        _range = max_value - min_value
        return node_sizes / _range * GraphViz.NODE_MAX_SIZE + GraphViz.NODE_MIN_SIZE

    @staticmethod
    def rescale_edge_with(edge_widths):
        edge_widths = np.array(edge_widths)
        min_value, max_value = min(edge_widths), max(edge_widths)
        _range = max_value - min_value
        return edge_widths / _range * GraphViz.EDGE_MAX_WIDTH + GraphViz.EDGE_MIN_WIDTH

    @staticmethod
    def get_text_node_info(digraph, node):
        return 'ID:{} - Freq:{} - Cons:{}'.format(node, digraph.nodes()[node]['frequency'], digraph.degree[node])

    @staticmethod
    def init_node_traces_3d(digraph, position, colorscale='YlOrRd'):
        node_x = []
        node_y = []
        node_z = []
        node_size = []
        node_color = []
        for node in digraph.nodes():
            x, y, z = position[node]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            node_size.append(digraph.nodes[node].get('frequency', 0))
            node_color.append(digraph.degree[node])
        node_trace = go.Scatter3d(x=node_x, y=node_y, z=node_z, name='All Nodes', mode='markers', hoverinfo='text',
                                  marker=dict(showscale=True, colorscale=colorscale, reversescale=True,
                                              size=GraphViz.rescale_node_size(node_size),
                                              color=node_color, colorbar=dict(thickness=15,
                                                                              title='Node Connections',
                                                                              xanchor='left', titleside='right'),
                                              line_width=2))

        # Find adjacencies nodes
        node_adjacencies = []
        node_text = []
        for i, adjacencies in enumerate(digraph.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            node_text.append(GraphViz.get_text_node_info(digraph, adjacencies[0]))
        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text
        return node_trace

    @staticmethod
    def init_node_traces_3d_with_condition(condition, digraph, position, colorscale='YlOrRd'):
        node_x = []
        node_y = []
        node_z = []
        node_size = []
        node_color = []
        for node in digraph.nodes():
            if (digraph.nodes[node]['frequency'] < condition['frequency'].get('lt', 10 ** 6)) and (
                    digraph.nodes[node]['frequency'] > condition['frequency'].get('gt', 0)):
                x, y, z = position[node]
                node_x.append(x)
                node_y.append(y)
                node_z.append(z)
                node_size.append(digraph.nodes[node]['frequency'])
                node_color.append(digraph.degree[node])
        node_trace = go.Scatter3d(x=node_x, y=node_y, z=node_z, name='All Nodes', mode='markers', hoverinfo='text',
                                  marker=dict(showscale=True, colorscale=colorscale, reversescale=True,
                                              size=GraphViz.rescale_node_size(node_size),
                                              color=node_color, colorbar=dict(thickness=15,
                                                                              title='Node Connections',
                                                                              xanchor='left', titleside='right'),
                                              line_width=2))

        # Find adjacencies nodes
        node_adjacencies = []
        node_text = []
        for i, adjacencies in enumerate(digraph.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            node_text.append(GraphViz.get_text_node_info(digraph, adjacencies[0]))
        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text
        return node_trace

    @staticmethod
    def init_node_traces_2d(digraph, position, colorscale='YlOrRd'):
        node_x = []
        node_y = []
        node_size = []
        node_color = []
        for node in digraph.nodes():
            x, y = position[node]
            node_x.append(x)
            node_y.append(y)
            node_size.append(digraph.nodes[node]['frequency'])
            node_color.append(digraph.degree[node])
        node_trace = go.Scatter(x=node_x, y=node_y, name='All Nodes', mode='markers', hoverinfo='text',
                                marker=dict(showscale=True, colorscale=colorscale, reversescale=True,
                                            size=GraphViz.rescale_node_size(node_size),
                                            color=node_color, colorbar=dict(thickness=15,
                                                                            title='Node Connections',
                                                                            xanchor='center', titleside='right'),
                                            line_width=2))

        # Find adjacencies nodes
        node_adjacencies = []
        node_text = []
        for node, adjacencies in enumerate(digraph.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            node_text.append(GraphViz.get_text_node_info(digraph, adjacencies[0]))
        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text
        return node_trace

    def _init_digraph_(self, paths):
        start = datetime.now()
        digraph = nx.DiGraph()
        # Init Nodes and Edges
        for path in paths:
            digraph.add_nodes_from(path, iter_level=dict(), level=0)
            for idx, node in enumerate(path):
                digraph.nodes[node]['frequency'] = digraph.nodes[node].get('frequency', 0) + \
                                                   GraphViz.NODE_INCREMENTAL_VALUE
                digraph.nodes[node]['iter_level'][idx + 1] = digraph.nodes[node]['iter_level'].get(idx, 0) + 1
                digraph.nodes[node]['level'] = \
                    max(digraph.nodes[node]['iter_level'].items(), key=operator.itemgetter(1))[0]

            # Add edges based-on FLOW DIRECTION
            if self.flow_direction == GraphViz.DIRECTION_BOTTOM_UP:
                digraph.add_edges_from([(path[i], path[i - 1]) for i in range(len(path) - 1, 0, -1)])
                for i in range(len(path) - 1, 0, -1):
                    digraph.edges[path[i], path[i - 1]]['weight'] = \
                        digraph.edges[path[i], path[i - 1]].get('weight', 0) + GraphViz.NODE_INCREMENTAL_VALUE
            elif self.flow_direction == GraphViz.DIRECTION_TOP_DOWN:
                digraph.add_edges_from([(path[i], path[i + 1]) for i in range(len(path) - 1)])
                for i in range(len(path) - 1):
                    digraph.edges[path[i], path[i + 1]]['weight'] = \
                        digraph.edges[path[i], path[i - 1]].get('weight', 0) + GraphViz.NODE_INCREMENTAL_VALUE
        logger.info('Initiated Graph nodes and edges objects {}'.format(datetime.now() - start))
        return digraph

    @staticmethod
    def init_edge_traces_3d(digraph, position):
        go_edges = []
        for edge in digraph.edges():
            x0, y0, z0 = position[edge[0]]
            x1, y1, z1 = position[edge[1]]
            go_edge = go.Scatter3d(x=[x0, x1], y=[y0, y1], z=[z0, z1],
                                   line=dict(width=min(digraph.edges[edge[0], edge[1]]['weight'] *
                                                       GraphViz.EDGE_SCALED_WIDTH_FACTOR,
                                                       GraphViz.EDGE_MAX_WIDTH),
                                             color='#888'),
                                   showlegend=False,
                                   text='Connections\t{}'.format(digraph.edges[edge[0], edge[1]]['weight']),
                                   mode='lines')
            go_edges.append(go_edge)
        return go_edges

    @staticmethod
    def init_edge_traces_3d_with_condition(condition, digraph, position):
        go_edges = []
        for edge in digraph.edges():
            x0, y0, z0 = position[edge[0]]
            x1, y1, z1 = position[edge[1]]
            if (digraph.nodes[edge[0]]['frequency'] < condition['frequency'].get('lt', 10 ** 6)) and (
                    digraph.nodes[edge[0]]['frequency'] > condition['frequency'].get('gt', 0)) and (
                    digraph.nodes[edge[1]]['frequency'] < condition['frequency'].get('lt', 10 ** 6)) and (
                    digraph.nodes[edge[1]]['frequency'] > condition['frequency'].get('gt', 0)):
                go_edge = go.Scatter3d(x=[x0, x1], y=[y0, y1], z=[z0, z1],
                                       line=dict(width=min(digraph.edges[edge[0], edge[1]]['weight'] *
                                                           GraphViz.EDGE_SCALED_WIDTH_FACTOR,
                                                           GraphViz.EDGE_MAX_WIDTH),
                                                 color='#888'),
                                       showlegend=False,
                                       text='Connections\t{}'.format(digraph.edges[edge[0], edge[1]]['weight']),
                                       mode='lines')
                go_edges.append(go_edge)
        return go_edges

    @staticmethod
    def init_edge_traces_2d(digraph, position):
        go_edges = []
        for edge in digraph.edges():
            x0, y0 = position[edge[0]]
            x1, y1 = position[edge[1]]
            go_edge = go.Scatter(x=[x0, x1], y=[y0, y1],
                                 line=dict(width=min(digraph.edges[edge[0], edge[1]]['weight'] *
                                                     GraphViz.EDGE_SCALED_WIDTH_FACTOR,
                                                     GraphViz.EDGE_MAX_WIDTH), color='#888'),
                                 showlegend=False,
                                 text='Connections\t{}'.format(digraph.edges[edge[0], edge[1]]['weight']),
                                 mode='lines')
            go_edges.append(go_edge)
        return go_edges

    @staticmethod
    def layout_figure(node_traces, go_edges=None):
        fig = go.Figure(data=[node_traces],
                        layout=go.Layout(
                            title='<br>Network graph',
                            titlefont_size=12,
                            showlegend=True,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=[dict(
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        if go_edges is not None:
            for go_edge in go_edges:
                fig.add_trace(go_edge)
        fig.show()
        return fig

    @staticmethod
    def update_position_layout(layout, digraph, position):
        if layout == GraphViz.VOLCANO_LAYOUT_3D:
            return Layout.get_volcano_layout(digraph, position)
        elif layout == GraphViz.CYLINDER_LAYOUT_3D:
            return Layout.get_cylinder_layout(digraph, position)
        elif layout == GraphViz.TREE_LAYOUT_3D:
            return Layout.get_tree_layout(digraph, position)
        elif layout == GraphViz.TREE_CENTRALIZED_LAYOUT_3D:
            return Layout.get_tree_centralized_layout(digraph, position)
        elif layout == GraphViz.WORD2VECTOR_LAYOUT_3D:
            return Layout.get_word2vector_layout(digraph, position)
        return position

    def plot_3d_network(self, paths, position=None, layout=None):
        logger.info('Rendering 3D Graph Network')

        # Init Graph Objects
        digraph = self._init_digraph_(paths)

        # Positioning
        start = datetime.now()
        position = nx.random_layout(digraph, dim=3) if position is None else position
        position = GraphViz.update_position_layout(layout, digraph, position) if layout is not None else position

        # Check Performance issue while rendering in JS
        digraph, position = self.perf_saver.filter(digraph, position)
        edge_property = self.perf_saver.edge_property

        node_traces = GraphViz.init_node_traces_3d(digraph, position)
        go_edges = None
        if edge_property is not None and edge_property.get('plot') is True:
            go_edges = GraphViz.init_edge_traces_3d(digraph, position)

        # Layout
        figure = GraphViz.layout_figure(node_traces, go_edges)
        logger.info('Plotted 3D Graph Network {}'.format(datetime.now() - start))
        return {'digraph': digraph,
                'position': position,
                'figure': figure}

    def plot_2d_network(self, paths, position=None, **kwargs):
        logger.info('Rendering 2D Graph Network')
        edge_property = kwargs.get('edge_property')

        # Init Graph Objects
        digraph = self._init_digraph_(paths)

        # Positioning
        start = datetime.now()
        position = nx.random_layout(digraph, dim=2) if position is None else position
        node_traces = GraphViz.init_node_traces_2d(digraph, position)
        go_edges = None
        if edge_property is not None and edge_property.get('plot') is True:
            go_edges = GraphViz.init_edge_traces_2d(digraph, position)

        # Layout
        figure = GraphViz.layout_figure(node_traces, go_edges)
        logger.info('Plotted 2D Graph Network {}'.format(datetime.now() - start))
        return {'digraph': digraph,
                'position': position,
                'figure': figure}

    def plot_risk_graph_3d(self, user_properties, user_linkage, set_default_graph=True):
        """
        Construct graph visualization for Risk detection

        Args:
            user_properties (dict): a dictionary describes user'property with format <CSN_id, attribute_dict> 
            user_linkage (list): a list of tuple of 2 CSN users, first CSN indicating the source and second CSN indicating the destination of transaction

        Returns:

        """
        start = datetime.now()
        
        # Input node and edges
        graph = nx.Graph(author='quanht6', project='risk', description='TODO')
        graph.add_nodes_from(user_properties.items())
        graph.add_edges_from(user_linkage)

        # Layout graph position
        position = nx.random_layout(graph, dim=3)
        node_traces = GraphViz.init_node_traces_3d(graph, position)
        go_edges = GraphViz.init_edge_traces_3d(graph, position)
        figure = GraphViz.layout_figure(node_traces, go_edges)

        if set_default_graph is True:
            self.default_graph = graph
        return graph


    def get_random_position_2d(self, paths):
        digraph = self._init_digraph_(paths)
        position = nx.random_layout(digraph, dim=2)
        return digraph, position

    def get_random_position_3d(self, paths):
        digraph = self._init_digraph_(paths)
        position = nx.random_layout(digraph, dim=3)
        return digraph, position

    def get_layout_position_3d(self, paths, layout=VOLCANO_LAYOUT_3D):
        digraph = self._init_digraph_(paths)
        position = nx.random_layout(digraph, dim=3)
        position = GraphViz.update_position_layout(layout, digraph, position)
        return digraph, position

    def get_word2vector_position_2d(self, paths):
        digraph = self._init_digraph_(paths)
        word2vec_manager = Word2VectorManagement(paths)
        w2v = word2vec_manager.get_model()
        position = collections.OrderedDict({node: w2v.word_embedding.wv.__getitem__(node) for node in digraph.nodes})
        pca = decomposition.PCA(n_components=2)
        transformed_pos = pca.fit_transform(np.array(list(position.values())))
        position = dict(zip(position.keys(), transformed_pos))
        return digraph, position

    def get_word2vector_position_3d(self, paths):
        digraph = self._init_digraph_(paths)
        start = datetime.now()
        word2vec_manager = Word2VectorManagement(paths)
        w2v = word2vec_manager.get_model()
        position = collections.OrderedDict({node: w2v.wv.__getitem__(node) for node in digraph.nodes})
        start_1 = datetime.now()
        pca = decomposition.PCA(n_components=3)
        transformed_pos = pca.fit_transform(np.array(list(position.values())))
        position = dict(zip(position.keys(), transformed_pos))
        logger.info('Reducing dimensionality of Word2Vector {}'.format(datetime.now() - start_1))
        logger.info('Positioning nodes process {}'.format(datetime.now() - start))
        return digraph, position

    def highlight_path_2d(self, sel_path, paths, position):
        digraph = self._init_digraph_(paths)
        position = nx.random_layout(digraph, dim=2) if position is None else position
        # Construct Node traces and Edge traces of all graph
        node_traces = GraphViz.init_node_traces_2d(digraph, position, colorscale='Greys')
        edge_x = []
        edge_y = []
        for edge in digraph.edges():
            x0, y0 = position[edge[0]]
            x1, y1 = position[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_traces = go.Scatter(x=edge_x, y=edge_y, name='All Edges',
                                 line=dict(width=0.5, color='#888', ),
                                 mode='lines')
        # Construct Node traces and Edge traces for selected path
        sel_node_x = []
        sel_node_y = []
        sel_node_size = []
        sel_node_color = []
        sel_node_text = []
        for sel_node in sel_path:
            sel_node_x.append(position[sel_node][0])
            sel_node_y.append(position[sel_node][1])
            sel_node_size.append(min([digraph.nodes[sel_node]['frequency'], GraphViz.NODE_MAX_SIZE]))
            sel_node_color.append(digraph.degree[sel_node])
            sel_node_text.append(GraphViz.get_text_node_info(digraph, sel_node))
        sel_node_trace = go.Scatter(x=sel_node_x, y=sel_node_y, name='Sel Nodes',
                                    mode='markers', hoverinfo='text', text=sel_node_text,
                                    marker=dict(showscale=True, colorscale='greens',
                                                reversescale=True, color=sel_node_color, size=sel_node_size,
                                                colorbar=dict(thickness=15, title='Node Connections',
                                                              xanchor='left', titleside='right'), line_width=2))
        sel_edge_x = []
        sel_edge_y = []
        for i in range(len(sel_path) - 1):
            x0, y0 = position[sel_path[i]]
            x1, y1 = position[sel_path[i + 1]]
            sel_edge_x.append(x0)
            sel_edge_x.append(x1)
            sel_edge_x.append(None)
            sel_edge_y.append(y0)
            sel_edge_y.append(y1)
            sel_edge_y.append(None)

        sel_edge_trace = go.Scatter(x=sel_edge_x, y=sel_edge_y, name='Sel Edges',
                                    line=dict(width=3, color='#888'), mode='lines')

        # Layout all traces
        figure = go.Figure(data=[node_traces, edge_traces, sel_node_trace, sel_edge_trace],
                           layout=go.Layout(
                               title='<br>Network graph',
                               titlefont_size=12,
                               showlegend=True,
                               legend=go.layout.Legend(
                                   x=0,
                                   y=1,
                                   traceorder="normal",
                                   font=dict(
                                       family="sans-serif",
                                       size=12,
                                       color="black"
                                   ),
                                   bgcolor="LightSteelBlue",
                                   bordercolor="Black",
                                   borderwidth=2),
                               hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               annotations=[dict(
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002)],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        figure.show()
        return {'digraph': digraph,
                'position': position,
                'figure': figure}

    def highlight_path_3d(self, sel_path, paths, position):
        digraph = self._init_digraph_(paths)
        position = nx.random_layout(digraph, dim=3) if position is None else position
        # Construct Node traces and Edge traces of all graph
        node_traces = GraphViz.init_node_traces_3d(digraph, position, colorscale='Greys')
        edge_x = []
        edge_y = []
        edge_z = []
        for edge in digraph.edges():
            x0, y0, z0 = position[edge[0]]
            x1, y1, z1 = position[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_z.append(z0)
            edge_z.append(z1)

        edge_traces = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, name='All Edges', connectgaps=True,
                                   line=dict(width=0.5, color='#888'),
                                   mode='lines')
        # Construct Node traces and Edge traces for selected path
        sel_node_x = []
        sel_node_y = []
        sel_node_z = []
        sel_node_size = []
        sel_node_color = []
        sel_node_text = []
        for sel_node in sel_path:
            sel_node_x.append(position[sel_node][0])
            sel_node_y.append(position[sel_node][1])
            sel_node_z.append(position[sel_node][2])
            sel_node_size.append(digraph.nodes[sel_node]['frequency'])
            sel_node_color.append(digraph.degree[sel_node])
            sel_node_text.append(GraphViz.get_text_node_info(digraph, sel_node))
        sel_node_trace = go.Scatter3d(x=sel_node_x, y=sel_node_y, z=sel_node_z, name='Sel Nodes',
                                      mode='markers', hoverinfo='text', text=sel_node_text,
                                      marker=dict(showscale=True, colorscale='greens',
                                                  reversescale=True, color=sel_node_color,
                                                  size=GraphViz.rescale_node_size(sel_node_size),
                                                  colorbar=dict(thickness=15, title='Node Connections',
                                                                xanchor='left', titleside='right'), line_width=2))
        sel_edge_x = []
        sel_edge_y = []
        sel_edge_z = []
        for i in range(len(sel_path) - 1):
            x0, y0, z0 = position[sel_path[i]]
            x1, y1, z1 = position[sel_path[i + 1]]
            sel_edge_x.append(x0)
            sel_edge_x.append(x1)
            sel_edge_y.append(y0)
            sel_edge_y.append(y1)
            sel_edge_z.append(z0)
            sel_edge_z.append(z1)

        sel_edge_trace = go.Scatter3d(x=sel_edge_x, y=sel_edge_y, z=sel_edge_z, name='Sel Edges',
                                      line=dict(width=5, color='yellow'), mode='lines')

        # Layout all traces
        figure = go.Figure(data=[node_traces, edge_traces, sel_node_trace, sel_edge_trace],
                           layout=go.Layout(
                               title='<br>Network graph',
                               titlefont_size=12,
                               showlegend=True,
                               legend=go.layout.Legend(
                                   x=0,
                                   y=1,
                                   traceorder="normal",
                                   font=dict(
                                       family="sans-serif",
                                       size=12,
                                       color="black"
                                   ),
                                   bgcolor="LightSteelBlue",
                                   bordercolor="Black",
                                   borderwidth=2),
                               hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               annotations=[dict(
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002)],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        figure.show()
        return {'digraph': digraph,
                'position': position,
                'figure': figure}

    def highlight_multi_path_2d(self, sel_paths, paths, position):
        assert len(sel_paths) <= 7, "Too many path to display, this can cause hanging JS"
        digraph = self._init_digraph_(paths)
        position = nx.random_layout(digraph, dim=2) if position is None else position
        # Construct Node traces and Edge traces of all graph
        node_traces = GraphViz.init_node_traces_2d(digraph, position, colorscale='Greys')
        edge_x = []
        edge_y = []
        for edge in digraph.edges():
            x0, y0 = position[edge[0]]
            x1, y1 = position[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_y.append(y0)
            edge_y.append(y1)

        edge_traces = go.Scatter(x=edge_x, y=edge_y, name='All Edges', connectgaps=True,
                                 line=dict(width=0.5, color='#888'),
                                 mode='lines')

        # Construct Node traces and Edge traces for selected paths
        sel_node_traces = []
        sel_edge_traces = []
        for idx, sel_path in enumerate(sel_paths):
            sel_node_x = []
            sel_node_y = []
            sel_node_size = []
            sel_node_color = []
            sel_node_text = []
            for sel_node in sel_path:
                sel_node_x.append(position[sel_node][0])
                sel_node_y.append(position[sel_node][1])
                sel_node_size.append(digraph.nodes[sel_node]['frequency'])
                sel_node_color.append(digraph.degree[sel_node])
                sel_node_text.append(GraphViz.get_text_node_info(digraph, sel_node))
            sel_node_trace = go.Scatter(x=sel_node_x, y=sel_node_y, name='Sel Nodes {}'.format(idx),
                                        mode='markers', hoverinfo='text', text=sel_node_text,
                                        marker=dict(showscale=True, colorscale=GraphViz.COLOR_SCALE[idx],
                                                    reversescale=True, color=sel_node_color,
                                                    colorbar=dict(thickness=15, title='Node Connections',
                                                                  xanchor='left', titleside='right'), line_width=2))
            sel_edge_x = []
            sel_edge_y = []
            for i in range(len(sel_path) - 1):
                x0, y0 = position[sel_path[i]]
                x1, y1 = position[sel_path[i + 1]]
                sel_edge_x.append(x0)
                sel_edge_x.append(x1)
                sel_edge_y.append(y0)
                sel_edge_y.append(y1)
            sel_edge_trace = go.Scatter(x=sel_edge_x, y=sel_edge_y, name='Sel Edges {}'.format(idx),
                                        line=dict(width=5, color=GraphViz.COLOR[idx]), mode='lines')

            sel_node_traces.append(sel_node_trace)
            sel_edge_traces.append(sel_edge_trace)

        # Layout all traces
        figure = go.Figure(data=[node_traces, edge_traces],
                           layout=go.Layout(
                               title='<br>Network graph',
                               titlefont_size=12,
                               showlegend=True,
                               legend=go.layout.Legend(
                                   x=0,
                                   y=1,
                                   traceorder="normal",
                                   font=dict(
                                       family="sans-serif",
                                       size=12,
                                       color="black"
                                   ),
                                   bgcolor="LightSteelBlue",
                                   bordercolor="Black",
                                   borderwidth=2),
                               hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               annotations=[dict(
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002)],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        for node_trace, edge_trace in zip(sel_node_traces, sel_edge_traces):
            figure.add_trace(node_trace)
            figure.add_trace(edge_trace)

        figure.show()
        return {'digraph': digraph,
                'position': position,
                'figure': figure}

    def highlight_multi_path_3d(self, sel_paths, paths, position):
        assert len(sel_paths) <= 7, "Too many path to display, this can cause hanging JS"
        digraph = self._init_digraph_(paths)
        position = nx.random_layout(digraph, dim=3) if position is None else position
        # Construct Node traces and Edge traces of all graph
        node_traces = GraphViz.init_node_traces_3d(digraph, position, colorscale='Greys')
        edge_x = []
        edge_y = []
        edge_z = []
        for edge in digraph.edges():
            x0, y0, z0 = position[edge[0]]
            x1, y1, z1 = position[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_z.append(z0)
            edge_z.append(z1)

        edge_traces = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, name='All Edges', connectgaps=True,
                                   line=dict(width=0.5, color='#888'),
                                   mode='lines')

        # Construct Node traces and Edge traces for selected paths
        sel_node_traces = []
        sel_edge_traces = []
        for idx, sel_path in enumerate(sel_paths):
            sel_node_x = []
            sel_node_y = []
            sel_node_z = []
            sel_node_size = []
            sel_node_color = []
            sel_node_text = []
            for sel_node in sel_path:
                sel_node_x.append(position[sel_node][0])
                sel_node_y.append(position[sel_node][1])
                sel_node_z.append(position[sel_node][2])
                sel_node_size.append(digraph.nodes[sel_node]['frequency'])
                sel_node_color.append(digraph.degree[sel_node])
                sel_node_text.append(GraphViz.get_text_node_info(digraph, sel_node))
            sel_node_trace = go.Scatter3d(x=sel_node_x, y=sel_node_y, z=sel_node_z, name='Sel Nodes {}'.format(idx),
                                          mode='markers', hoverinfo='text', text=sel_node_text,
                                          marker=dict(showscale=True, colorscale=GraphViz.COLOR_SCALE[idx],
                                                      reversescale=True, color=sel_node_color,
                                                      colorbar=dict(thickness=15, title='Node Connections',
                                                                    xanchor='left', titleside='right'), line_width=2))
            sel_edge_x = []
            sel_edge_y = []
            sel_edge_z = []
            for i in range(len(sel_path) - 1):
                x0, y0, z0 = position[sel_path[i]]
                x1, y1, z1 = position[sel_path[i + 1]]
                sel_edge_x.append(x0)
                sel_edge_x.append(x1)
                sel_edge_y.append(y0)
                sel_edge_y.append(y1)
                sel_edge_z.append(z0)
                sel_edge_z.append(z1)
            sel_edge_trace = go.Scatter3d(x=sel_edge_x, y=sel_edge_y, z=sel_edge_z, name='Sel Edges {}'.format(idx),
                                          line=dict(width=5, color=GraphViz.COLOR[idx]), mode='lines')

            sel_node_traces.append(sel_node_trace)
            sel_edge_traces.append(sel_edge_trace)

        # Layout all traces
        figure = go.Figure(data=[node_traces, edge_traces],
                           layout=go.Layout(
                               title='<br>Network graph',
                               titlefont_size=12,
                               showlegend=True,
                               legend=go.layout.Legend(
                                   x=0,
                                   y=1,
                                   traceorder="normal",
                                   font=dict(
                                       family="sans-serif",
                                       size=12,
                                       color="black"
                                   ),
                                   bgcolor="LightSteelBlue",
                                   bordercolor="Black",
                                   borderwidth=2),
                               hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               annotations=[dict(
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002)],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        for node_trace, edge_trace in zip(sel_node_traces, sel_edge_traces):
            figure.add_trace(node_trace)
            figure.add_trace(edge_trace)

        figure.show()
        return {'digraph': digraph,
                'position': position,
                'figure': figure}

    def highlight_cluster_3d(self, paths, position):
        condition = {'frequency': {'lt': 1000, 'gt': 3}}
        digraph = self._init_digraph_(paths)
        position = nx.random_layout(digraph, dim=3) if position is None else position
        # Construct Node traces and Edge traces of all graph
        node_traces = GraphViz.init_node_traces_3d_with_condition(condition, digraph, position, colorscale='Greys')
        edge_traces = GraphViz.init_edge_traces_3d_with_condition(condition, digraph, position)
        # Layout all traces
        figure = go.Figure(data=[node_traces],
                           layout=go.Layout(
                               title='<br>Network graph',
                               titlefont_size=12,
                               showlegend=True,
                               legend=go.layout.Legend(
                                   x=0,
                                   y=1,
                                   traceorder="normal",
                                   font=dict(
                                       family="sans-serif",
                                       size=12,
                                       color="black"
                                   ),
                                   bgcolor="LightSteelBlue",
                                   bordercolor="Black",
                                   borderwidth=2),
                               hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               annotations=[dict(
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002)],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        for edge_trace in edge_traces:
            figure.add_trace(edge_trace)
        figure.show()
        return {'digraph': digraph,
                'position': position,
                'figure': figure}
