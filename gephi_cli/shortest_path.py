"""Shortest path algorithms: Dijkstra and Bellman-Ford."""

from .core import start_jvm, get_graph_model


ALGORITHMS = {
    "dijkstra": "Dijkstra shortest path (non-negative weights)",
    "bellman_ford": "Bellman-Ford shortest path (supports negative weights)",
}


def compute_shortest_path(source_id, algorithm="dijkstra", workspace=None):
    """Compute shortest paths from a source node to all other nodes.

    Args:
        source_id: Source node ID
        algorithm: "dijkstra" or "bellman_ford"
        workspace: Gephi workspace

    Returns:
        dict with distances and path info
    """
    start_jvm()
    import jpype

    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    # Find source node
    source_node = graph.getNode(str(source_id))
    if source_node is None:
        # Try numeric ID
        try:
            source_node = graph.getNode(int(source_id))
        except (ValueError, TypeError):
            pass
    if source_node is None:
        raise ValueError(f"Node '{source_id}' not found in graph")

    if algorithm == "dijkstra":
        from org.gephi.algorithms.shortestpath import DijkstraShortestPathAlgorithm
        algo = DijkstraShortestPathAlgorithm(graph, source_node)
    elif algorithm == "bellman_ford":
        from org.gephi.algorithms.shortestpath import BellmanFordShortestPathAlgorithm
        algo = BellmanFordShortestPathAlgorithm(graph, source_node)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. Use 'dijkstra' or 'bellman_ford'")

    algo.compute()

    # Collect distances
    distances = {}
    max_distance = algo.getMaxDistance()
    dist_map = algo.getDistances()

    for node in graph.getNodes():
        node_id = str(node.getId())
        if node_id == str(source_id):
            distances[node_id] = 0.0
        else:
            d = dist_map.get(node)
            if d is not None:
                distances[node_id] = float(d)

    return {
        "algorithm": algorithm,
        "source": str(source_id),
        "max_distance": float(max_distance),
        "reachable_nodes": len(distances),
        "total_nodes": graph.getNodeCount(),
        "distances": distances,
    }


def get_path_between(source_id, target_id, algorithm="dijkstra", workspace=None):
    """Get shortest path between two specific nodes.

    Returns:
        dict with path nodes and total distance
    """
    start_jvm()

    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    source_node = graph.getNode(str(source_id))
    if source_node is None:
        try:
            source_node = graph.getNode(int(source_id))
        except (ValueError, TypeError):
            pass
    if source_node is None:
        raise ValueError(f"Source node '{source_id}' not found")

    target_node = graph.getNode(str(target_id))
    if target_node is None:
        try:
            target_node = graph.getNode(int(target_id))
        except (ValueError, TypeError):
            pass
    if target_node is None:
        raise ValueError(f"Target node '{target_id}' not found")

    if algorithm == "dijkstra":
        from org.gephi.algorithms.shortestpath import DijkstraShortestPathAlgorithm
        algo = DijkstraShortestPathAlgorithm(graph, source_node)
    elif algorithm == "bellman_ford":
        from org.gephi.algorithms.shortestpath import BellmanFordShortestPathAlgorithm
        algo = BellmanFordShortestPathAlgorithm(graph, source_node)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. Use 'dijkstra' or 'bellman_ford'")

    algo.compute()

    # Reconstruct path with safety limit
    path = []
    current = target_node
    max_path_len = graph.getNodeCount()
    while current is not None and len(path) <= max_path_len:
        path.append(str(current.getId()))
        edge = algo.getPredecessorIncoming(current)
        if edge is None:
            break
        predecessor = edge.getSource()
        if predecessor == current:
            predecessor = edge.getTarget()
        if str(predecessor.getId()) in path:
            break
        current = predecessor

    path.reverse()

    dist_map = algo.getDistances()
    distance = dist_map.get(target_node)

    return {
        "source": str(source_id),
        "target": str(target_id),
        "distance": float(distance) if distance is not None else None,
        "path": path,
        "path_length": len(path),
    }
