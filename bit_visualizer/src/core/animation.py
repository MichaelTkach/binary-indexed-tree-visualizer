from ..utils.geometry import calculate_positions, calculate_root_position
from .bit_operations import find_parentless_nodes

def prepare_animation_steps(initial_array, bit_array, levels, is_loaded_from_file=False):
    """Prepare sequence of animation steps with grouped animations"""
    animation_steps = []
    n = len(initial_array)

    # Calculate node positions and levels
    # If loading from file, use scale=1; otherwise scale=None for default behavior
    positions = calculate_positions(n, levels)

    # Group nodes with their immediate connections
    for i in range(1, n + 1):
        children = []
        children_values = []

        # Find all existing children for this node
        for j in range(1, i):
            if j + (j & -j) == i:
                children.append({
                    'index': j,
                    'position': positions[j],
                    'value': bit_array[j]
                })
                children_values.append({
                    'from': j,
                    'value': bit_array[j]
                })

        if children:  # If node has children
            animation_steps.append({
                'type': 'parent_with_children',
                'parent': {
                    'index': i,
                    'value': initial_array[i - 1],
                    'position': positions[i]
                },
                'children': children,
                'value_transfers': children_values,
                'final_value': bit_array[i]
            })
        else:  # Leaf node
            animation_steps.append({
                'type': 'leaf_node',
                'node': {
                    'index': i,
                    'value': initial_array[i - 1],
                    'position': positions[i]
                }
            })

    # Add root node with all connections as single step
    root_pos = calculate_root_position(positions)
    parentless = find_parentless_nodes(n)
    if parentless:
        animation_steps.append({
            'type': 'root_with_connections',
            'position': root_pos,
            'connections': [{
                'node': node,
                'position': positions[node]
            } for node in parentless]
        })

    return animation_steps