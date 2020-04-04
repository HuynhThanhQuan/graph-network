import numpy as np


class Layout:

    @staticmethod
    def get_volcano_layout(digraph, position):
        def relocate_z_position(node_layer_map, pos):
            top_z = 1
            new_pos = {}
            num_layers = max(list(zip(*node_layer_map))[1])
            for node, pos in pos.items():
                x_loc, y_loc = pos[0], pos[1]
                layer = node_layer_map[node]
                z_loc = top_z - layer / num_layers
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_xy_location(node_layer_map, pos):
            new_pos = {}
            num_layers = max(list(zip(*node_layer_map))[1])
            for node, pos in pos.items():
                z_loc = pos[2]
                layer = node_layer_map[node]
                radius = layer / num_layers
                x_loc = np.random.uniform(-radius, radius)
                y_loc = [-1, 1][np.random.randint(2)] * np.sqrt(radius ** 2 - x_loc ** 2)
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_node_position(node_layer_map, pos):
            new_pos = relocate_z_position(node_layer_map, pos)
            new_pos = relocate_xy_location(node_layer_map, new_pos)
            return new_pos
        return relocate_node_position(digraph.nodes.data('level'), position)

    @staticmethod
    def get_cylinder_layout(digraph, position):
        def relocate_z_position(node_layer_map, pos):
            top_z = 1
            new_pos = {}
            num_layers = max(list(zip(*node_layer_map))[1])
            for node, pos in pos.items():
                x_loc, y_loc = pos[0], pos[1]
                layer = node_layer_map[node]
                z_loc = top_z - layer / num_layers
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_xy_location(pos):
            new_pos = {}
            for node, pos in pos.items():
                z_loc = pos[2]
                radius = 1
                x_loc = np.random.uniform(-radius, radius)
                y_loc = [-1, 1][np.random.randint(2)] * np.sqrt(radius ** 2 - x_loc ** 2)
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_node_position(node_layer_map, pos):
            new_pos = relocate_z_position(node_layer_map, pos)
            new_pos = relocate_xy_location(new_pos)
            return new_pos
        return relocate_node_position(digraph.nodes.data('level'), position)

    @staticmethod
    def get_tree_layout(digraph, position):
        def relocate_z_position(node_layer_map, pos):
            top_z = 1
            new_pos = {}
            num_layers = max(list(zip(*node_layer_map))[1])
            for node, pos in pos.items():
                x_loc, y_loc = pos[0], pos[1]
                layer = node_layer_map[node]
                z_loc = top_z - layer / num_layers
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_node_position(node_layer_map, pos):
            new_pos = relocate_z_position(node_layer_map, pos)
            return new_pos
        return relocate_node_position(digraph.nodes.data('level'), position)

    @staticmethod
    def get_tree_centralized_layout(digraph, position):
        def relocate_z_position(node_layer_map, pos):
            top_z = 1
            new_pos = {}
            num_layers = max(list(zip(*node_layer_map))[1])
            for node, pos in pos.items():
                x_loc, y_loc = pos[0], pos[1]
                layer = node_layer_map[node]
                z_loc = top_z - layer / num_layers
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_xy_location(pos, margin=0.1):
            new_pos = {}
            for node, pos in pos.items():
                weight = digraph.nodes[node]['frequency']
                z_loc = pos[2]
                radius = 1/weight + margin
                x_loc = np.random.uniform(-radius, radius)
                y_loc = np.random.uniform(-radius, radius)
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_node_position(node_layer_map, pos):
            new_pos = relocate_z_position(node_layer_map, pos)
            new_pos = relocate_xy_location(new_pos)
            return new_pos
        return relocate_node_position(digraph.nodes.data('level'), position)

    @staticmethod
    def get_word2vector_layout(digraph, position):
        def relocate_z_position(node_layer_map, pos):
            top_z = 1
            new_pos = {}
            num_layers = max(list(zip(*node_layer_map))[1])
            for node, pos in pos.items():
                x_loc, y_loc = pos[0], pos[1]
                layer = node_layer_map[node]
                z_loc = top_z - layer / num_layers
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_xy_location(node_layer_map, pos):
            new_pos = {}
            num_layers = max(list(zip(*node_layer_map))[1])
            for node, pos in pos.items():
                z_loc = pos[2]
                layer = node_layer_map[node]
                radius = layer / num_layers
                x_loc = np.random.uniform(-radius, radius)
                y_loc = [-1, 1][np.random.randint(2)] * np.sqrt(radius ** 2 - x_loc ** 2)
                new_pos[node] = (x_loc, y_loc, z_loc)
            return new_pos

        def relocate_node_position(node_layer_map, pos):
            new_pos = relocate_z_position(node_layer_map, pos)
            new_pos = relocate_xy_location(node_layer_map, new_pos)
            return new_pos
        return relocate_node_position(digraph.nodes.data('level'), position)
