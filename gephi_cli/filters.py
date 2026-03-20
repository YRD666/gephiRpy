"""All graph filtering operations from Gephi Toolkit."""

from .core import start_jvm, get_graph_model, get_project_controller


FILTERS = {
    # Graph topology filters
    "degree": "Filter nodes by degree range",
    "in_degree": "Filter nodes by in-degree range",
    "out_degree": "Filter nodes by out-degree range",
    "mutual_degree": "Filter nodes by mutual degree range",
    "giant_component": "Keep only the largest connected component",
    "k_core": "K-core decomposition (nodes with at least k connections)",
    "ego": "Ego network (neighbors within depth from a node)",
    "has_self_loop": "Filter nodes that have self-loops",
    # Edge filters
    "edge_weight": "Filter edges by weight range",
    "mutual_edge": "Keep only mutual/reciprocal edges",
    "self_loop": "Remove self-loop edges",
    # Attribute filters
    "attribute_equal": "Filter by exact attribute value match",
    "attribute_range": "Filter by numeric attribute range",
    "attribute_non_null": "Filter nodes/edges with non-null attribute",
    # Path filter
    "shortest_path": "Keep nodes on shortest path between two nodes",
}


def _get_filter_controller():
    start_jvm()
    from org.gephi.filters.api import FilterController
    from org.openide.util import Lookup
    return Lookup.getDefault().lookup(FilterController)


def _get_workspace(workspace=None):
    """Get the workspace object for filter builder.getFilter()."""
    if workspace is not None:
        return workspace
    pc = get_project_controller()
    ws = pc.getCurrentWorkspace()
    if ws is None:
        raise ValueError("No active workspace. Import a graph or call init_workspace() first.")
    return ws


def _apply_filter(fc, gm, filt):
    """Apply a filter and return visible counts."""
    query = fc.createQuery(filt)
    view = fc.filter(query)
    gm.setVisibleView(view)
    visible = gm.getGraphVisible()
    return {
        "visible_nodes": visible.getNodeCount(),
        "visible_edges": visible.getEdgeCount(),
    }


def filter_by_degree(min_val=None, max_val=None, workspace=None):
    """Filter nodes by degree range."""
    start_jvm()
    from org.gephi.filters.api import Range
    from org.gephi.filters.plugin.graph import DegreeRangeBuilder
    import java.lang

    lo_val = int(min_val) if min_val is not None else 0
    hi_val = int(max_val) if max_val is not None else 2147483647
    if min_val is not None and max_val is not None and lo_val > hi_val:
        raise ValueError(f"min ({lo_val}) cannot be greater than max ({hi_val})")

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = DegreeRangeBuilder()
    filt = builder.getFilter(_get_workspace(workspace))
    filt.setRange(Range(java.lang.Integer(lo_val), java.lang.Integer(hi_val)))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "degree", "range": [lo_val, hi_val]})
    return result


def filter_by_in_degree(min_val=None, max_val=None, workspace=None):
    """Filter nodes by in-degree range."""
    start_jvm()
    from org.gephi.filters.api import Range
    from org.gephi.filters.plugin.graph import InDegreeRangeBuilder
    import java.lang

    lo_val = int(min_val) if min_val is not None else 0
    hi_val = int(max_val) if max_val is not None else 2147483647
    if min_val is not None and max_val is not None and lo_val > hi_val:
        raise ValueError(f"min ({lo_val}) cannot be greater than max ({hi_val})")

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = InDegreeRangeBuilder()
    filt = builder.getFilter(_get_workspace(workspace))
    filt.setRange(Range(java.lang.Integer(lo_val), java.lang.Integer(hi_val)))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "in_degree", "range": [lo_val, hi_val]})
    return result


def filter_by_out_degree(min_val=None, max_val=None, workspace=None):
    """Filter nodes by out-degree range."""
    start_jvm()
    from org.gephi.filters.api import Range
    from org.gephi.filters.plugin.graph import OutDegreeRangeBuilder
    import java.lang

    lo_val = int(min_val) if min_val is not None else 0
    hi_val = int(max_val) if max_val is not None else 2147483647
    if min_val is not None and max_val is not None and lo_val > hi_val:
        raise ValueError(f"min ({lo_val}) cannot be greater than max ({hi_val})")

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = OutDegreeRangeBuilder()
    filt = builder.getFilter(_get_workspace(workspace))
    filt.setRange(Range(java.lang.Integer(lo_val), java.lang.Integer(hi_val)))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "out_degree", "range": [lo_val, hi_val]})
    return result


def filter_by_mutual_degree(min_val=None, max_val=None, workspace=None):
    """Filter nodes by mutual degree range."""
    start_jvm()
    from org.gephi.filters.api import Range
    from org.gephi.filters.plugin.graph import MutualDegreeRangeBuilder
    import java.lang

    lo_val = int(min_val) if min_val is not None else 0
    hi_val = int(max_val) if max_val is not None else 2147483647
    if min_val is not None and max_val is not None and lo_val > hi_val:
        raise ValueError(f"min ({lo_val}) cannot be greater than max ({hi_val})")

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = MutualDegreeRangeBuilder()
    filt = builder.getFilter(_get_workspace(workspace))
    filt.setRange(Range(java.lang.Integer(lo_val), java.lang.Integer(hi_val)))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "mutual_degree", "range": [lo_val, hi_val]})
    return result


def filter_giant_component(workspace=None):
    """Keep only the giant (largest) connected component."""
    start_jvm()
    from org.gephi.filters.plugin.graph import GiantComponentBuilder

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = GiantComponentBuilder()
    filt = builder.getFilter(_get_workspace(workspace))

    result = _apply_filter(fc, gm, filt)
    result["filter"] = "giant_component"
    return result


def filter_k_core(k, workspace=None):
    """K-core decomposition filter."""
    start_jvm()
    from org.gephi.filters.plugin.graph import KCoreBuilder
    import java.lang

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = KCoreBuilder()
    filt = builder.getFilter(_get_workspace(workspace))
    filt.setK(java.lang.Integer(int(k)))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "k_core", "k": k})
    return result


def filter_ego(node_id, depth=1, workspace=None):
    """Ego network filter - keep neighbors within depth."""
    start_jvm()
    from org.gephi.filters.plugin.graph import EgoBuilder
    import java.lang

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = EgoBuilder()
    filt = builder.getFilter(_get_workspace(workspace))
    filt.setPattern(str(node_id))
    filt.setDepth(java.lang.Integer(int(depth)))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "ego", "node_id": node_id, "depth": depth})
    return result


def filter_has_self_loop(workspace=None):
    """Filter nodes that have self-loops."""
    start_jvm()
    from org.gephi.filters.plugin.graph import HasSelfLoopBuilder

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = HasSelfLoopBuilder()
    filt = builder.getFilter(_get_workspace(workspace))

    result = _apply_filter(fc, gm, filt)
    result["filter"] = "has_self_loop"
    return result


def filter_edge_weight(min_val=None, max_val=None, workspace=None):
    """Filter edges by weight range."""
    start_jvm()
    from org.gephi.filters.api import Range
    from org.gephi.filters.plugin.edge import EdgeWeightBuilder
    import java.lang

    lo_val = float(min_val) if min_val is not None else 0.0
    hi_val = float(max_val) if max_val is not None else 1e15
    if min_val is not None and max_val is not None and lo_val > hi_val:
        raise ValueError(f"min ({lo_val}) cannot be greater than max ({hi_val})")

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = EdgeWeightBuilder()
    filt = builder.getFilter(_get_workspace(workspace))
    filt.setRange(Range(java.lang.Double(lo_val), java.lang.Double(hi_val)))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "edge_weight", "range": [lo_val, hi_val]})
    return result


def filter_mutual_edge(workspace=None):
    """Keep only mutual/reciprocal edges."""
    start_jvm()
    from org.gephi.filters.plugin.edge import MutualEdgeBuilder

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = MutualEdgeBuilder()
    filt = builder.getFilter(_get_workspace(workspace))

    result = _apply_filter(fc, gm, filt)
    result["filter"] = "mutual_edge"
    return result


def filter_self_loop(workspace=None):
    """Remove self-loop edges."""
    start_jvm()
    from org.gephi.filters.plugin.edge import SelfLoopFilterBuilder

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = SelfLoopFilterBuilder()
    filt = builder.getFilter(_get_workspace(workspace))

    result = _apply_filter(fc, gm, filt)
    result["filter"] = "self_loop"
    return result


def filter_by_attribute(column_name, value, workspace=None):
    """Filter nodes by attribute equal value."""
    start_jvm()
    from org.gephi.filters.plugin.attribute import AttributeEqualBuilder

    ws = _get_workspace(workspace)
    fc = _get_filter_controller()
    gm = get_graph_model(ws)

    node_table = gm.getNodeTable()
    col = node_table.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found. Available: "
                         f"{[str(c.getTitle()) for c in node_table.toArray()]}")

    category_builder = AttributeEqualBuilder()
    sub_builders = category_builder.getBuilders(ws)
    if len(sub_builders) == 0:
        raise ValueError(f"No attribute filter builders available for column '{column_name}'")

    # Use the first sub-builder to create a filter
    filt = sub_builders[0].getFilter(ws)
    filt.setColumn(col)

    # Auto-convert value type based on filter type
    import java.lang
    filter_class = type(filt).__name__
    if "Number" in filter_class:
        try:
            filt.setMatch(java.lang.Integer(int(value)))
        except (ValueError, TypeError):
            filt.setMatch(java.lang.Double(float(value)))
    else:
        filt.setMatch(str(value))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "attribute_equal", "column": column_name, "value": value})
    return result


def filter_by_attribute_range(column_name, min_val=None, max_val=None, workspace=None):
    """Filter by numeric attribute range."""
    start_jvm()
    from org.gephi.filters.api import Range
    from org.gephi.filters.plugin.attribute import AttributeRangeBuilder

    ws = _get_workspace(workspace)
    fc = _get_filter_controller()
    gm = get_graph_model(ws)

    node_table = gm.getNodeTable()
    col = node_table.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    import java.lang
    lo_val = float(min_val) if min_val is not None else -1e15
    hi_val = float(max_val) if max_val is not None else 1e15
    if min_val is not None and max_val is not None and lo_val > hi_val:
        raise ValueError(f"min ({lo_val}) cannot be greater than max ({hi_val})")

    category_builder = AttributeRangeBuilder()
    sub_builders = category_builder.getBuilders(ws)
    if len(sub_builders) == 0:
        raise ValueError(f"No range filter builders available for column '{column_name}'")

    filt = sub_builders[0].getFilter(ws)
    filt.setColumn(col)

    # Match Java type of column for Range bounds
    col_type = str(col.getTypeClass().getSimpleName()).lower()
    if col_type in ("integer", "int"):
        filt.setRange(Range(java.lang.Integer(int(lo_val)), java.lang.Integer(int(hi_val))))
    elif col_type in ("long",):
        filt.setRange(Range(java.lang.Long(int(lo_val)), java.lang.Long(int(hi_val))))
    elif col_type in ("float",):
        filt.setRange(Range(java.lang.Float(float(lo_val)), java.lang.Float(float(hi_val))))
    else:
        filt.setRange(Range(java.lang.Double(lo_val), java.lang.Double(hi_val)))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "attribute_range", "column": column_name, "range": [lo_val, hi_val]})
    return result


def filter_by_attribute_non_null(column_name, workspace=None):
    """Filter nodes with non-null attribute value."""
    start_jvm()
    from org.gephi.filters.plugin.attribute import AttributeNonNullBuilder

    ws = _get_workspace(workspace)
    fc = _get_filter_controller()
    gm = get_graph_model(ws)

    node_table = gm.getNodeTable()
    col = node_table.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    category_builder = AttributeNonNullBuilder()
    sub_builders = category_builder.getBuilders(ws)
    if len(sub_builders) == 0:
        raise ValueError(f"No non-null filter builders available for column '{column_name}'")

    filt = sub_builders[0].getFilter(ws)
    filt.setColumn(col)

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "attribute_non_null", "column": column_name})
    return result


def filter_shortest_path(source_id, target_id, workspace=None):
    """Keep only nodes on the shortest path between two nodes."""
    start_jvm()
    from org.gephi.filters.plugin.graph import ShortestPathBuilder

    fc = _get_filter_controller()
    gm = get_graph_model(workspace)
    builder = ShortestPathBuilder()
    filt = builder.getFilter(_get_workspace(workspace))
    filt.setSource(str(source_id))
    filt.setTarget(str(target_id))

    result = _apply_filter(fc, gm, filt)
    result.update({"filter": "shortest_path", "source": source_id, "target": target_id})
    return result


def reset_filter(workspace=None):
    """Reset all filters and show the full graph."""
    start_jvm()
    gm = get_graph_model(workspace)
    gm.setVisibleView(None)
    graph = gm.getGraph()
    return {
        "filter": "reset",
        "visible_nodes": graph.getNodeCount(),
        "visible_edges": graph.getEdgeCount(),
    }


def list_filters():
    """Return available filters with descriptions."""
    return FILTERS.copy()
