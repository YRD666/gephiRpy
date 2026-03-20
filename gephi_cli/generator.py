"""Graph generators - create sample/random graphs."""

import random as _random
import math

from .core import start_jvm, init_workspace, get_graph_model


def _init_gen(workspace):
    """Common init: start JVM, create workspace, return (workspace, graph_model, graph)."""
    start_jvm()
    if workspace is None:
        workspace = init_workspace()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    return workspace, gm, graph


def _make_nodes(gm, graph, n):
    """Create n nodes labeled 0..n-1, return list."""
    nodes = []
    for i in range(n):
        node = gm.factory().newNode(str(i))
        node.setLabel(str(i))
        graph.addNode(node)
        nodes.append(node)
    return nodes


def _add_edge(gm, graph, src, tgt, weight=1.0, directed=True):
    """Add one edge (skip if already exists)."""
    edge = gm.factory().newEdge(src, tgt, 0, weight, directed)
    graph.addEdge(edge)


# ─── Random (Erdos-Renyi) ────────────────────────────────────

def generate_random(node_count=100, wiring_prob=0.05, workspace=None):
    """Generate a random graph (Erdos-Renyi G(n,p) model).

    Args:
        node_count: Number of nodes
        wiring_prob: Probability of edge between any two nodes (0.0-1.0)
        workspace: Gephi workspace
    """
    if node_count < 1:
        raise ValueError("node_count must be >= 1")
    if not 0.0 <= wiring_prob <= 1.0:
        raise ValueError("wiring_prob must be in [0.0, 1.0]")
    start_jvm()
    from org.gephi.io.generator.plugin import RandomGraph
    from org.gephi.io.importer.api import ImportController
    from org.gephi.io.importer.impl import ImportContainerImpl
    from org.gephi.io.processor.plugin import DefaultProcessor
    from org.openide.util import Lookup

    if workspace is None:
        workspace = init_workspace()

    gen = RandomGraph()
    gen.setNumberOfNodes(int(node_count))
    gen.setWiringProbability(float(wiring_prob))

    container = ImportContainerImpl()
    gen.generate(container.getLoader())

    ic = Lookup.getDefault().lookup(ImportController)
    ic.process(container, DefaultProcessor(), workspace)

    return workspace


# ─── Scale-Free (Barabasi-Albert) ─────────────────────────────

def generate_scale_free(node_count=100, m=2, seed=None, workspace=None):
    """Generate a scale-free graph using Barabasi-Albert preferential attachment.

    Args:
        node_count: Total number of nodes
        m: Number of edges each new node attaches (default 2)
        seed: Random seed for reproducibility
        workspace: Gephi workspace
    """
    if node_count < 2:
        raise ValueError("node_count must be >= 2")
    workspace, gm, graph = _init_gen(workspace)
    rng = _random.Random(seed)

    if m < 1:
        raise ValueError("m must be >= 1")
    if node_count <= m:
        raise ValueError(f"node_count ({node_count}) must be > m ({m})")

    nodes = _make_nodes(gm, graph, node_count)

    # Start with a fully connected initial cluster of m+1 nodes
    for i in range(m + 1):
        for j in range(i + 1, m + 1):
            _add_edge(gm, graph, nodes[i], nodes[j], directed=False)

    # Degree list for preferential attachment (repeated entries)
    degree_list = []
    for i in range(m + 1):
        degree_list.extend([i] * m)  # each initial node has degree m

    # Add remaining nodes
    for i in range(m + 1, node_count):
        chosen = set()
        max_attempts = m * 100
        attempts = 0
        while len(chosen) < m and attempts < max_attempts:
            pick = degree_list[rng.randint(0, len(degree_list) - 1)]
            if pick != i:
                chosen.add(pick)
            attempts += 1
        for t in chosen:
            _add_edge(gm, graph, nodes[i], nodes[t], directed=False)
            degree_list.append(i)
            degree_list.append(t)

    return workspace


# ─── Small-World (Watts-Strogatz) ─────────────────────────────

def generate_small_world(node_count=100, k=4, beta=0.3, seed=None, workspace=None):
    """Generate a small-world graph using Watts-Strogatz model.

    Args:
        node_count: Number of nodes
        k: Each node connects to k nearest neighbors (must be even)
        beta: Rewiring probability (0.0 = ring lattice, 1.0 = random)
        seed: Random seed for reproducibility
        workspace: Gephi workspace
    """
    if node_count < 3:
        raise ValueError("node_count must be >= 3 for small-world")
    if not 0.0 <= beta <= 1.0:
        raise ValueError("beta must be in [0.0, 1.0]")
    workspace, gm, graph = _init_gen(workspace)
    rng = _random.Random(seed)

    if k < 2 or k % 2 != 0:
        raise ValueError("k must be an even number >= 2")
    if k >= node_count:
        raise ValueError(f"k ({k}) must be < node_count ({node_count})")

    nodes = _make_nodes(gm, graph, node_count)

    # Build ring lattice
    edges = set()
    for i in range(node_count):
        for j in range(1, k // 2 + 1):
            target = (i + j) % node_count
            edges.add((min(i, target), max(i, target)))

    # Rewire edges
    new_edges = set()
    for (u, v) in edges:
        if rng.random() < beta:
            # Rewire u's end
            existing_pairs = edges | new_edges
            candidates = [x for x in range(node_count)
                          if x != u and (min(u, x), max(u, x)) not in existing_pairs]
            if candidates:
                w = rng.choice(candidates)
                new_edges.add((min(u, w), max(u, w)))
                continue
        new_edges.add((u, v))

    # Create edges in graph
    for u, v in new_edges:
        _add_edge(gm, graph, nodes[u], nodes[v], directed=False)

    return workspace


# ─── Complete Graph ───────────────────────────────────────────

def generate_complete(node_count=10, directed=False, workspace=None):
    """Generate a complete graph (every node connected to every other).

    Args:
        node_count: Number of nodes
        directed: If True, create directed edges in both directions
        workspace: Gephi workspace
    """
    if node_count < 1:
        raise ValueError("node_count must be >= 1")
    workspace, gm, graph = _init_gen(workspace)
    nodes = _make_nodes(gm, graph, node_count)

    for i in range(node_count):
        j_start = 0 if directed else i + 1
        for j in range(j_start, node_count):
            if i != j:
                _add_edge(gm, graph, nodes[i], nodes[j], directed=directed)

    return workspace


# ─── Star Graph ──────────────────────────────────────────────

def generate_star(node_count=10, workspace=None):
    """Generate a star graph (one center node connected to all others).

    Args:
        node_count: Total nodes (1 center + n-1 leaves)
        workspace: Gephi workspace
    """
    if node_count < 2:
        raise ValueError("node_count must be >= 2 for a star graph")
    workspace, gm, graph = _init_gen(workspace)
    nodes = _make_nodes(gm, graph, node_count)

    for i in range(1, node_count):
        _add_edge(gm, graph, nodes[0], nodes[i], directed=False)

    return workspace


# ─── Ring Graph ──────────────────────────────────────────────

def generate_ring(node_count=10, workspace=None):
    """Generate a ring graph (cycle: each node connected to next, last to first).

    Args:
        node_count: Number of nodes (>= 3)
        workspace: Gephi workspace
    """
    if node_count < 3:
        raise ValueError("node_count must be >= 3 for a ring graph")
    workspace, gm, graph = _init_gen(workspace)
    nodes = _make_nodes(gm, graph, node_count)

    for i in range(node_count):
        _add_edge(gm, graph, nodes[i], nodes[(i + 1) % node_count], directed=False)

    return workspace


# ─── Grid / Lattice ──────────────────────────────────────────

def generate_grid(rows=10, cols=10, workspace=None):
    """Generate a 2D grid/lattice graph.

    Args:
        rows: Number of rows (>= 1)
        cols: Number of columns (>= 1)
        workspace: Gephi workspace
    """
    if rows < 1 or cols < 1:
        raise ValueError("rows and cols must be >= 1")
    workspace, gm, graph = _init_gen(workspace)
    node_count = rows * cols
    nodes = _make_nodes(gm, graph, node_count)

    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            # Right neighbor
            if c + 1 < cols:
                _add_edge(gm, graph, nodes[idx], nodes[idx + 1], directed=False)
            # Bottom neighbor
            if r + 1 < rows:
                _add_edge(gm, graph, nodes[idx], nodes[idx + cols], directed=False)

    return workspace


# ─── Tree ────────────────────────────────────────────────────

def generate_tree(depth=4, branching=2, workspace=None):
    """Generate a balanced tree.

    Args:
        depth: Tree depth (root is depth 0, >= 0)
        branching: Number of children per node (default 2 = binary tree, >= 1)
        workspace: Gephi workspace
    """
    if depth < 0:
        raise ValueError("depth must be >= 0")
    if branching < 1:
        raise ValueError("branching must be >= 1")

    # Calculate total nodes
    if branching == 1:
        total = depth + 1
    else:
        total = (branching ** (depth + 1) - 1) // (branching - 1)
    if total > 1_000_000:
        raise ValueError(f"Tree would have {total} nodes - too large (max 1,000,000)")

    workspace, gm, graph = _init_gen(workspace)

    nodes = _make_nodes(gm, graph, total)

    # Connect parent to children
    for i in range(total):
        for b in range(branching):
            child = i * branching + b + 1
            if child < total:
                _add_edge(gm, graph, nodes[i], nodes[child], directed=False)

    return workspace


# ─── Dynamic Graph (built-in) ────────────────────────────────

def generate_dynamic(workspace=None, **_kwargs):
    """Generate a dynamic graph with time-varying properties (built-in gephi generator).

    Args:
        workspace: Gephi workspace
    """
    start_jvm()
    from org.gephi.io.generator.plugin import DynamicGraph
    from org.gephi.io.importer.api import ImportController
    from org.gephi.io.importer.impl import ImportContainerImpl
    from org.gephi.io.processor.plugin import DefaultProcessor
    from org.openide.util import Lookup

    if workspace is None:
        workspace = init_workspace()

    gen = DynamicGraph()
    container = ImportContainerImpl()
    gen.generate(container.getLoader())

    ic = Lookup.getDefault().lookup(ImportController)
    ic.process(container, DefaultProcessor(), workspace)

    return workspace


# ─── Empty Graph ─────────────────────────────────────────────

def generate_empty(node_count=10, workspace=None):
    """Generate a graph with nodes but no edges.

    Args:
        node_count: Number of nodes (>= 0)
        workspace: Gephi workspace
    """
    if node_count < 0:
        raise ValueError("node_count must be >= 0")
    workspace, gm, graph = _init_gen(workspace)
    _make_nodes(gm, graph, node_count)
    return workspace


# ─── Path Graph ──────────────────────────────────────────────

def generate_path(node_count=10, workspace=None):
    """Generate a path graph (linear chain of nodes).

    Args:
        node_count: Number of nodes (>= 1)
        workspace: Gephi workspace
    """
    if node_count < 1:
        raise ValueError("node_count must be >= 1")
    workspace, gm, graph = _init_gen(workspace)
    nodes = _make_nodes(gm, graph, node_count)

    for i in range(node_count - 1):
        _add_edge(gm, graph, nodes[i], nodes[i + 1], directed=False)

    return workspace


GENERATORS = {
    "random": "Erdos-Renyi random graph (nodes + wiring probability)",
    "scale_free": "Barabasi-Albert preferential attachment (nodes + m edges per new node)",
    "small_world": "Watts-Strogatz small-world (nodes + k neighbors + beta rewiring)",
    "complete": "Complete graph (all pairs connected)",
    "star": "Star graph (one center, all others as leaves)",
    "ring": "Ring/cycle graph",
    "grid": "2D grid/lattice (rows x cols)",
    "tree": "Balanced tree (depth + branching factor)",
    "path": "Path graph (linear chain)",
    "empty": "Empty graph (nodes only, no edges)",
    "dynamic": "Dynamic graph with time-varying properties",
}

_DISPATCH = {
    "random": generate_random,
    "scale_free": generate_scale_free,
    "small_world": generate_small_world,
    "complete": generate_complete,
    "star": generate_star,
    "ring": generate_ring,
    "grid": generate_grid,
    "tree": generate_tree,
    "path": generate_path,
    "empty": generate_empty,
    "dynamic": generate_dynamic,
}


def generate(graph_type, **kwargs):
    """Generate a graph of the specified type.

    Args:
        graph_type: One of the GENERATORS keys
        **kwargs: Parameters specific to the graph type

    Returns:
        workspace
    """
    if graph_type not in _DISPATCH:
        raise ValueError(f"Unknown graph type: {graph_type}. Available: {list(GENERATORS.keys())}")
    return _DISPATCH[graph_type](**kwargs)
