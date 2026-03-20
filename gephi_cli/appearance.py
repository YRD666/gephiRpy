"""Visual appearance: node/edge color, size, labels - complete Gephi styling."""

from .core import start_jvm, get_graph_model


def _parse_hex_color(hex_str):
    """Parse a hex color string to (r, g, b) tuple."""
    hex_color = str(hex_str).lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color[0]*2 + hex_color[1]*2 + hex_color[2]*2
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: '{hex_str}'. Expected format: '#RRGGBB' or '#RGB'")
    return int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)


# ─── Node Color ───────────────────────────────────────────────

def set_node_color_by_attribute(column_name, workspace=None):
    """Color nodes by a ranking attribute (gradient)."""
    start_jvm()
    from org.gephi.appearance.api import AppearanceController
    from org.gephi.appearance.plugin import RankingElementColorTransformer
    from org.openide.util import Lookup

    ac = Lookup.getDefault().lookup(AppearanceController)
    model = ac.getModel()
    gm = get_graph_model(workspace)

    node_table = gm.getNodeTable()
    col = node_table.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    func = model.getNodeFunction(col, RankingElementColorTransformer)
    if func is None:
        raise ValueError(f"Cannot create color ranking for column '{column_name}'. "
                         "Ensure it is a numeric column with varying values.")
    ac.transform(func)

    return {"action": "color_by_attribute", "column": column_name}


def set_all_nodes_color(r, g, b, workspace=None):
    """Set uniform color for all nodes."""
    start_jvm()
    import java.awt

    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    color = java.awt.Color(int(r), int(g), int(b))

    for node in graph.getNodes():
        node.setColor(color)

    return {"action": "uniform_color", "color": [r, g, b]}


def color_nodes_by_partition(column_name, workspace=None,
                             color_min=30, color_max=220, seed=None):
    """Color nodes by partition (categorical) attribute with distinct colors.

    Args:
        column_name: Categorical attribute column
        workspace: Gephi workspace
        color_min: Minimum RGB channel value (default 30, avoids too dark)
        color_max: Maximum RGB channel value (default 220, avoids too bright)
        seed: Random seed for color generation. None = deterministic per partition value.
              Set to an integer for a fixed global seed.
    """
    start_jvm()
    import java.awt
    import random

    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    node_table = gm.getNodeTable()
    col = node_table.getColumn(column_name)

    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    lo, hi = int(color_min), int(color_max)
    colors = {}
    for node in graph.getNodes():
        val = node.getAttribute(col)
        key = str(val) if val is not None else "__null__"
        if key not in colors:
            if seed is not None:
                random.seed(seed + len(colors))
            else:
                random.seed(hash(key) % 2**31)
            colors[key] = java.awt.Color(
                random.randint(lo, hi),
                random.randint(lo, hi),
                random.randint(lo, hi),
            )
        node.setColor(colors[key])

    return {"action": "color_by_partition", "column": column_name, "partitions": len(colors)}


def color_nodes_by_modularity(workspace=None):
    """Color nodes by modularity class (run modularity metric first)."""
    return color_nodes_by_partition("modularity_class", workspace)


def set_node_color_hex(node_id, hex_color, workspace=None):
    """Set color of a specific node by hex color."""
    start_jvm()
    import java.awt

    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    node = graph.getNode(str(node_id))
    if node is None:
        try:
            node = graph.getNode(int(node_id))
        except (ValueError, TypeError):
            pass
    if node is None:
        raise ValueError(f"Node '{node_id}' not found")

    r, g, b = _parse_hex_color(hex_color)
    node.setColor(java.awt.Color(r, g, b))
    return {"action": "set_node_color", "node": str(node_id), "color": hex_color}


# ─── Node Size ────────────────────────────────────────────────

def set_node_size_by_attribute(column_name, min_size=10, max_size=50, workspace=None):
    """Size nodes by a numeric ranking attribute."""
    start_jvm()
    from org.gephi.appearance.api import AppearanceController
    from org.gephi.appearance.plugin import RankingNodeSizeTransformer
    from org.openide.util import Lookup

    ac = Lookup.getDefault().lookup(AppearanceController)
    model = ac.getModel()
    gm = get_graph_model(workspace)

    node_table = gm.getNodeTable()
    col = node_table.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    func = model.getNodeFunction(col, RankingNodeSizeTransformer)
    if func is None:
        raise ValueError(f"Cannot create size ranking for column '{column_name}'. "
                         "Ensure it is a numeric column with varying values.")
    transformer = func.getTransformer()
    transformer.setMinSize(float(min_size))
    transformer.setMaxSize(float(max_size))
    ac.transform(func)

    return {"action": "size_by_attribute", "column": column_name, "range": [min_size, max_size]}


def set_all_nodes_size(size, workspace=None):
    """Set uniform size for all nodes."""
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    for node in graph.getNodes():
        node.setSize(float(size))

    return {"action": "uniform_size", "size": size}


# ─── Node Labels ──────────────────────────────────────────────

def set_node_labels(column_name=None, workspace=None):
    """Set node labels from an attribute column."""
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    if column_name:
        node_table = gm.getNodeTable()
        col = node_table.getColumn(column_name)
        if col is None:
            raise ValueError(f"Column '{column_name}' not found")
        for node in graph.getNodes():
            val = node.getAttribute(col)
            if val is not None:
                node.setLabel(str(val))
    return {"action": "set_labels", "column": column_name or "default"}


def set_node_label_color(r, g, b, workspace=None):
    """Set uniform label color for all nodes via preview property."""
    start_jvm()
    from org.gephi.preview.api import PreviewController, PreviewProperty
    from org.openide.util import Lookup
    import java.awt

    pc = Lookup.getDefault().lookup(PreviewController)
    model = pc.getModel()
    props = model.getProperties()
    color = java.awt.Color(int(r), int(g), int(b))

    # Try DependentColor first, fallback to direct color
    try:
        from org.gephi.preview.types import DependentColor
        props.putValue(PreviewProperty.NODE_LABEL_COLOR, DependentColor(color))
    except Exception:
        props.putValue(PreviewProperty.NODE_LABEL_COLOR, color)
    pc.refreshPreview()

    return {"action": "label_color", "color": [r, g, b]}


def set_node_label_size(size, workspace=None, font_name="Arial", font_style="plain"):
    """Set uniform label font for all nodes via preview property.

    Args:
        size: Font size in points
        workspace: Gephi workspace
        font_name: Font family name (default "Arial")
        font_style: "plain", "bold", "italic", or "bold_italic"
    """
    start_jvm()
    from org.gephi.preview.api import PreviewController, PreviewProperty
    from org.openide.util import Lookup
    import java.awt

    style_map = {
        "plain": java.awt.Font.PLAIN,
        "bold": java.awt.Font.BOLD,
        "italic": java.awt.Font.ITALIC,
        "bold_italic": java.awt.Font.BOLD | java.awt.Font.ITALIC,
    }
    java_style = style_map.get(font_style.lower(), java.awt.Font.PLAIN)

    pc = Lookup.getDefault().lookup(PreviewController)
    model = pc.getModel()
    props = model.getProperties()
    font = java.awt.Font(str(font_name), java_style, max(1, int(size)))
    props.putValue(PreviewProperty.NODE_LABEL_FONT, font)
    pc.refreshPreview()

    return {"action": "label_size", "size": size, "font": font_name, "style": font_style}


# ─── Edge Color ───────────────────────────────────────────────

def set_all_edges_color(r, g, b, workspace=None):
    """Set uniform color for all edges."""
    start_jvm()
    import java.awt

    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    color = java.awt.Color(int(r), int(g), int(b))

    for edge in graph.getEdges():
        edge.setColor(color)

    return {"action": "edge_uniform_color", "color": [r, g, b]}


def set_edge_color_by_attribute(column_name, workspace=None):
    """Color edges by a ranking attribute."""
    start_jvm()
    from org.gephi.appearance.api import AppearanceController
    from org.gephi.appearance.plugin import RankingElementColorTransformer
    from org.openide.util import Lookup

    ac = Lookup.getDefault().lookup(AppearanceController)
    model = ac.getModel()
    gm = get_graph_model(workspace)

    edge_table = gm.getEdgeTable()
    col = edge_table.getColumn(column_name)
    if col is None:
        raise ValueError(f"Edge column '{column_name}' not found")

    func = model.getEdgeFunction(col, RankingElementColorTransformer)
    if func is None:
        raise ValueError(f"Cannot create color ranking for edge column '{column_name}'. "
                         "Ensure it is a numeric column with varying values.")
    ac.transform(func)

    return {"action": "edge_color_by_attribute", "column": column_name}


def color_edges_by_source(workspace=None):
    """Color each edge with its source node's color."""
    start_jvm()

    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    for edge in graph.getEdges():
        source = edge.getSource()
        edge.setColor(source.getColor())

    return {"action": "edge_color_by_source"}


def color_edges_by_target(workspace=None):
    """Color each edge with its target node's color."""
    start_jvm()

    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    for edge in graph.getEdges():
        target = edge.getTarget()
        edge.setColor(target.getColor())

    return {"action": "edge_color_by_target"}


# ─── Edge Weight / Thickness ─────────────────────────────────

def set_edge_weight_by_attribute(column_name, workspace=None):
    """Set edge weight from an attribute column."""
    start_jvm()

    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    edge_table = gm.getEdgeTable()
    col = edge_table.getColumn(column_name)

    if col is None:
        raise ValueError(f"Edge column '{column_name}' not found")

    for edge in graph.getEdges():
        val = edge.getAttribute(col)
        if val is not None:
            edge.setWeight(float(val))

    return {"action": "edge_weight_by_attribute", "column": column_name}


def set_all_edges_weight(weight, workspace=None):
    """Set uniform weight for all edges."""
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    for edge in graph.getEdges():
        edge.setWeight(float(weight))

    return {"action": "edge_uniform_weight", "weight": weight}


# ─── Edge Labels ──────────────────────────────────────────────

def set_edge_labels(column_name=None, workspace=None):
    """Set edge labels from an attribute column."""
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    if column_name:
        edge_table = gm.getEdgeTable()
        col = edge_table.getColumn(column_name)
        if col is None:
            raise ValueError(f"Edge column '{column_name}' not found")
        for edge in graph.getEdges():
            val = edge.getAttribute(col)
            if val is not None:
                edge.setLabel(str(val))
    else:
        # Use weight as label
        for edge in graph.getEdges():
            edge.setLabel(str(edge.getWeight()))

    return {"action": "set_edge_labels", "column": column_name or "weight"}


# ─── Node Position ───────────────────────────────────────────

def set_node_position(node_id, x, y, workspace=None):
    """Set the position of a specific node."""
    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    node = graph.getNode(str(node_id))
    if node is None:
        try:
            node = graph.getNode(int(node_id))
        except (ValueError, TypeError):
            pass
    if node is None:
        raise ValueError(f"Node '{node_id}' not found")

    node.setX(float(x))
    node.setY(float(y))
    return {"action": "set_position", "node": str(node_id), "x": x, "y": y}


def set_node_fixed(node_id, fixed=True, workspace=None):
    """Set a node's fixed state (prevents layout from moving it)."""
    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    node = graph.getNode(str(node_id))
    if node is None:
        try:
            node = graph.getNode(int(node_id))
        except (ValueError, TypeError):
            pass
    if node is None:
        raise ValueError(f"Node '{node_id}' not found")

    node.setFixed(bool(fixed))
    return {"action": "set_fixed", "node": str(node_id), "fixed": fixed}
