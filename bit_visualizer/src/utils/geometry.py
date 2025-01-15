import math


def calculate_positions(n, levels, scale=1):
    """Calculate node positions based on levels"""
    if scale is None:
        scale = 1

    positions = {}
    max_level = max(levels.keys())
    left_margin = 100 * scale
    top_margin = 80 * scale
    x_spacing = 50 * scale

    for level in sorted(levels.keys(), reverse=True):
        y = top_margin + (max_level - level) * 50 * scale
        for node in levels[level]:
            x = left_margin + node * x_spacing
            positions[node] = (x, y)

    return positions


def calculate_root_position(positions, scale=1):
    """Calculate position for root node"""
    if scale is None:
        scale = 1

    if not positions:
        return (0, 0)
    min_y = min(y for x, y in positions.values())
    max_x = max(x for x, y in positions.values())
    return (max_x + 70 * scale, min_y - 10 * scale)


def calculate_arrow_intersection(x1, y1, x2, y2, r, scale=1):
    """Calculate intersection point of arrow with node circle"""
    if scale is None:
        scale = 1

    x1, x2, y1, y2, r = x1 * scale, x2 * scale, y1 * scale, y2 * scale, r * scale

    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist == 0:
        return x2, y2

    dx = dx / dist * r
    dy = dy / dist * r

    ix = x2 - dx
    iy = y2 - dy

    return ix, iy


def calculate_visual_properties(scale=1):
    """Calculate visual properties based on scale"""
    if scale is None:
        scale = 1

    base_arrow_line_width = 3
    arrow_head_length = 12
    base_to_tip_distance = 12
    half_width_at_base = 4
    base_node_line_width = 3
    base_rect_line_width = 2

    # Arrow properties
    arrow_line_width = max(base_arrow_line_width, round(base_arrow_line_width * scale))
    d1 = max(arrow_head_length, int(arrow_head_length * scale))
    d2 = max(base_to_tip_distance, int(base_to_tip_distance * scale))
    d3 = max(half_width_at_base, int(half_width_at_base * scale))
    arrow_shape = (d1, d2, d3)

    # Node and rectangle properties
    node_line_width = max(base_node_line_width, round(base_node_line_width * scale))
    rect_line_width = max(base_rect_line_width, round(base_rect_line_width * scale))

    return {
        'arrow_line_width': arrow_line_width,
        'arrow_shape': arrow_shape,
        'node_line_width': node_line_width,
        'rect_line_width': rect_line_width
    }