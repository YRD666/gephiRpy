"""Data Laboratory: node/edge CRUD, attribute management, search & replace."""

from .core import start_jvm, get_graph_model


# ─── Node/Edge CRUD ──────────────────────────────────────────

def create_node(label=None, attributes=None, workspace=None):
    """Create a new node in the graph.

    Args:
        label: Node label
        attributes: dict of attribute_name: value
    """
    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    node = gm.factory().newNode()
    if label:
        node.setLabel(str(label))

    if attributes:
        node_table = gm.getNodeTable()
        for key, val in attributes.items():
            col = node_table.getColumn(key)
            if col is not None:
                node.setAttribute(col, val)

    graph.addNode(node)
    return {
        "action": "create_node",
        "id": str(node.getId()),
        "label": label,
    }


def create_edge(source_id, target_id, weight=1.0, directed=True, workspace=None):
    """Create a new edge between two nodes."""
    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    source = _find_node(graph, source_id)
    target = _find_node(graph, target_id)

    edge = gm.factory().newEdge(source, target, 0, float(weight), bool(directed))
    graph.addEdge(edge)

    return {
        "action": "create_edge",
        "source": str(source_id),
        "target": str(target_id),
        "weight": weight,
    }


def delete_node(node_id, workspace=None):
    """Delete a node and its connected edges."""
    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    node = _find_node(graph, node_id)
    graph.removeNode(node)
    return {"action": "delete_node", "id": str(node_id)}


def delete_edge(source_id, target_id, workspace=None):
    """Delete an edge between two nodes."""
    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    source = _find_node(graph, source_id)
    target = _find_node(graph, target_id)
    edge = graph.getEdge(source, target)
    if edge is None:
        raise ValueError(f"Edge from '{source_id}' to '{target_id}' not found")
    graph.removeEdge(edge)
    return {"action": "delete_edge", "source": str(source_id), "target": str(target_id)}


def duplicate_node(node_id, workspace=None):
    """Duplicate a node with all its attributes."""
    start_jvm()
    from org.gephi.datalab.api import GraphElementsController
    from org.openide.util import Lookup

    gec = Lookup.getDefault().lookup(GraphElementsController)
    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    node = _find_node(graph, node_id)

    new_nodes = gec.duplicateNodes([node])
    new_id = str(new_nodes[0].getId()) if new_nodes else None
    return {"action": "duplicate_node", "original": str(node_id), "new_id": new_id}


def merge_nodes(node_ids, keep_id=None, workspace=None):
    """Merge multiple nodes into one.

    Args:
        node_ids: List of node IDs to merge
        keep_id: ID of the node to keep (first if None)
    """
    start_jvm()
    from org.gephi.datalab.api import GraphElementsController
    from org.openide.util import Lookup

    gec = Lookup.getDefault().lookup(GraphElementsController)
    gm = get_graph_model(workspace)
    graph = gm.getGraph()

    nodes = [_find_node(graph, nid) for nid in node_ids]
    selected = nodes[0]
    if keep_id is not None:
        selected = _find_node(graph, keep_id)

    # Get columns for merge strategy
    node_table = gm.getNodeTable()
    columns = [col for col in node_table.toArray()]

    gec.mergeNodes(graph, nodes, selected, columns, None, True)
    return {
        "action": "merge_nodes",
        "merged": [str(nid) for nid in node_ids],
        "kept": str(selected.getId()),
    }


# ─── Attribute Column Management ─────────────────────────────

def add_column(column_name, column_type="string", table="node", workspace=None):
    """Add a new attribute column.

    Args:
        column_name: Column name
        column_type: "string", "integer", "float", "double", "boolean", "long"
        table: "node" or "edge"
    """
    start_jvm()
    import jpype

    gm = get_graph_model(workspace)
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    type_map = {
        "string": jpype.JClass("java.lang.String"),
        "integer": jpype.JClass("java.lang.Integer"),
        "float": jpype.JClass("java.lang.Float"),
        "double": jpype.JClass("java.lang.Double"),
        "boolean": jpype.JClass("java.lang.Boolean"),
        "long": jpype.JClass("java.lang.Long"),
    }

    java_type = type_map.get(column_type.lower())
    if java_type is None:
        raise ValueError(f"Unknown type: {column_type}. Available: {list(type_map.keys())}")

    tbl.addColumn(column_name, java_type)
    return {"action": "add_column", "name": column_name, "type": column_type, "table": table}


def delete_column(column_name, table="node", workspace=None):
    """Delete an attribute column."""
    start_jvm()
    gm = get_graph_model(workspace)
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    col = tbl.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found in {table} table")

    tbl.removeColumn(col)
    return {"action": "delete_column", "name": column_name, "table": table}


def fill_column(column_name, value, table="node", workspace=None):
    """Fill an entire column with a single value."""
    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    col = tbl.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found in {table} table")

    elements = graph.getNodes() if table == "node" else graph.getEdges()
    count = 0
    for elem in elements:
        elem.setAttribute(col, _cast_value(value, col))
        count += 1

    return {"action": "fill_column", "column": column_name, "value": value, "count": count}


def set_attribute(element_id, column_name, value, table="node", workspace=None):
    """Set a single attribute value on a node or edge."""
    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    col = tbl.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    if table == "node":
        elem = _find_node(graph, element_id)
    else:
        raise ValueError("For edges, use source_id:target_id format")

    elem.setAttribute(col, _cast_value(value, col))
    return {"action": "set_attribute", "id": str(element_id), "column": column_name, "value": value}


def clear_column(column_name, table="node", workspace=None):
    """Clear all values in a column (set to null)."""
    start_jvm()
    from org.gephi.datalab.api import AttributeColumnsController
    from org.openide.util import Lookup

    acc = Lookup.getDefault().lookup(AttributeColumnsController)
    gm = get_graph_model(workspace)
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    col = tbl.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    acc.clearColumnData(tbl, col)
    return {"action": "clear_column", "column": column_name, "table": table}


def duplicate_column(column_name, new_name, table="node", workspace=None):
    """Duplicate a column with a new name."""
    start_jvm()
    from org.gephi.datalab.api import AttributeColumnsController
    from org.openide.util import Lookup

    acc = Lookup.getDefault().lookup(AttributeColumnsController)
    gm = get_graph_model(workspace)
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    col = tbl.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    acc.duplicateColumn(tbl, col, new_name, col.getTypeClass())
    return {"action": "duplicate_column", "source": column_name, "new": new_name}


def negate_boolean_column(column_name, table="node", workspace=None):
    """Negate all values in a boolean column."""
    start_jvm()
    from org.gephi.datalab.api import AttributeColumnsController
    from org.openide.util import Lookup

    acc = Lookup.getDefault().lookup(AttributeColumnsController)
    gm = get_graph_model(workspace)
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    col = tbl.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    acc.negateBooleanColumn(tbl, col)
    return {"action": "negate_boolean", "column": column_name}


def get_column_statistics(column_name, table="node", workspace=None):
    """Get statistics for a numeric column (min, max, avg, median, etc.)."""
    start_jvm()
    from org.gephi.datalab.api import AttributeColumnsController
    from org.openide.util import Lookup

    acc = Lookup.getDefault().lookup(AttributeColumnsController)
    gm = get_graph_model(workspace)
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    col = tbl.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    stats = acc.getNumberOrNumberListColumnStatistics(tbl, col)
    if stats is None:
        return {"column": column_name, "error": "Not a numeric column"}

    # Returns BigDecimal[8]: [avg, median, q1, q3, iqr, sum, min, max]
    return {
        "column": column_name,
        "average": float(stats[0].doubleValue()),
        "median": float(stats[1].doubleValue()),
        "q1": float(stats[2].doubleValue()),
        "q3": float(stats[3].doubleValue()),
        "iqr": float(stats[4].doubleValue()),
        "sum": float(stats[5].doubleValue()),
        "min": float(stats[6].doubleValue()),
        "max": float(stats[7].doubleValue()),
    }


# ─── Search & Replace ────────────────────────────────────────

def search_replace(column_name, search_value, replace_value, table="node",
                   regex=False, workspace=None):
    """Search and replace values in an attribute column.

    Simple implementation that iterates over all elements.
    """
    start_jvm()
    import re as re_module

    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    tbl = gm.getNodeTable() if table == "node" else gm.getEdgeTable()

    col = tbl.getColumn(column_name)
    if col is None:
        raise ValueError(f"Column '{column_name}' not found")

    elements = graph.getNodes() if table == "node" else graph.getEdges()
    count = 0
    for elem in elements:
        val = elem.getAttribute(col)
        if val is None:
            continue
        val_str = str(val)
        if regex:
            new_val = re_module.sub(search_value, replace_value, val_str)
        else:
            new_val = val_str.replace(str(search_value), str(replace_value))
        if new_val != val_str:
            elem.setAttribute(col, _cast_value(new_val, col))
            count += 1

    return {
        "action": "search_replace",
        "column": column_name,
        "search": search_value,
        "replace": replace_value,
        "matches_replaced": count,
    }


# ─── Helpers ──────────────────────────────────────────────────

def _find_node(graph, node_id):
    """Find a node by ID (string or int)."""
    node = graph.getNode(str(node_id))
    if node is None:
        try:
            node = graph.getNode(int(node_id))
        except (ValueError, TypeError):
            pass
    if node is None:
        raise ValueError(f"Node '{node_id}' not found")
    return node


def _cast_value(value, column):
    """Cast a Python value to match the column type."""
    start_jvm()
    import jpype

    type_name = str(column.getTypeClass().getName())
    if type_name == "java.lang.String":
        return str(value)
    elif type_name == "java.lang.Integer":
        return jpype.JInt(int(value))
    elif type_name == "java.lang.Float":
        return jpype.JFloat(float(value))
    elif type_name == "java.lang.Double":
        return jpype.JDouble(float(value))
    elif type_name == "java.lang.Boolean":
        if isinstance(value, bool):
            return jpype.JBoolean(value)
        return jpype.JBoolean(str(value).lower() in ("true", "1", "yes"))
    elif type_name == "java.lang.Long":
        return jpype.JLong(int(value))
    # Fallback: try string conversion
    return str(value)
