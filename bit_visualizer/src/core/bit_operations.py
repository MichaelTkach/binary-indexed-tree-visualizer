def calculate_bit_array(initial_array):
    """Calculate BIT array values from initial array"""
    bit_array = [0] * (len(initial_array) + 1)

    # Initialize BIT array
    for i in range(len(initial_array)):
        bit_array[i + 1] = initial_array[i]

    # Calculate parent values
    for i in range(1, len(bit_array)):
        parent = i + (i & -i)
        if parent < len(bit_array):
            bit_array[parent] += bit_array[i]

    return bit_array


def calculate_levels(n):
    """Calculate levels for each node based on RSB"""
    levels = {}
    for i in range(1, n + 1):
        RSB = i & -i
        level = RSB.bit_length()
        if level not in levels:
            levels[level] = []
        levels[level].append(i)
    return levels


def find_parentless_nodes(n):
    """Find nodes that don't have parents in the tree"""
    parentless = set(range(1, n + 1))
    for i in range(1, n + 1):
        parent = i + (i & -i)
        if parent <= n:
            parentless.discard(i)
    return parentless