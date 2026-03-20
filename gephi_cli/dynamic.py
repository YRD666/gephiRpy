"""Dynamic graph statistics over time."""

from .core import start_jvm, get_graph_model


DYNAMIC_METRICS = {
    "dynamic_degree": "Degree distribution over time",
    "dynamic_clustering": "Clustering coefficient over time",
    "dynamic_edges": "Number of edges over time",
    "dynamic_nodes": "Number of nodes over time",
}


def run_dynamic_metric(metric_name, window=1.0, tick=1.0, workspace=None):
    """Run a dynamic statistic over time intervals.

    Requires a dynamic/temporal graph (GEXF with time intervals or timestamps).
    Static graphs will raise an error.

    Args:
        metric_name: One of dynamic_degree, dynamic_clustering, dynamic_edges, dynamic_nodes
        window: Time window size
        tick: Time tick (step size)
        workspace: Gephi workspace

    Returns:
        dict with metric results
    """
    start_jvm()
    gm = get_graph_model(workspace)

    # Check if graph has time bounds
    try:
        bounds = gm.getTimeBounds()
        if bounds is None:
            raise ValueError(
                "Graph has no time bounds. Dynamic metrics require a temporal graph "
                "(e.g., GEXF with <dynamics>/<slices> or timestamp attributes)."
            )
    except Exception as e:
        if "NullPointerException" in str(type(e).__name__) or "bounds" in str(e):
            raise ValueError(
                "Graph has no time bounds. Dynamic metrics require a temporal graph "
                "(e.g., GEXF with <dynamics>/<slices> or timestamp attributes)."
            ) from e
        raise

    algo = metric_name.lower()

    if algo == "dynamic_degree":
        return _run_dynamic_degree(gm, window, tick)
    elif algo == "dynamic_clustering":
        return _run_dynamic_clustering(gm, window, tick)
    elif algo == "dynamic_edges":
        return _run_dynamic_edges(gm, window, tick)
    elif algo == "dynamic_nodes":
        return _run_dynamic_nodes(gm, window, tick)
    else:
        raise ValueError(f"Unknown dynamic metric: {metric_name}. "
                         f"Available: {list(DYNAMIC_METRICS.keys())}")


def _get_report(stat):
    """Safely get report from a dynamic statistic."""
    report = stat.getReport()
    return str(report) if report else "computed"


def _run_dynamic_degree(gm, window, tick):
    from org.gephi.statistics.plugin.dynamic import DynamicDegree
    stat = DynamicDegree()
    stat.setWindow(float(window))
    stat.setTick(float(tick))
    stat.execute(gm)
    return {
        "metric": "dynamic_degree",
        "window": window,
        "tick": tick,
        "report": _get_report(stat),
    }


def _run_dynamic_clustering(gm, window, tick):
    from org.gephi.statistics.plugin.dynamic import DynamicClusteringCoefficient
    stat = DynamicClusteringCoefficient()
    stat.setWindow(float(window))
    stat.setTick(float(tick))
    stat.execute(gm)
    return {
        "metric": "dynamic_clustering",
        "window": window,
        "tick": tick,
        "report": _get_report(stat),
    }


def _run_dynamic_edges(gm, window, tick):
    from org.gephi.statistics.plugin.dynamic import DynamicNbEdges
    stat = DynamicNbEdges()
    stat.setWindow(float(window))
    stat.setTick(float(tick))
    stat.execute(gm)
    return {
        "metric": "dynamic_edges",
        "window": window,
        "tick": tick,
        "report": _get_report(stat),
    }


def _run_dynamic_nodes(gm, window, tick):
    from org.gephi.statistics.plugin.dynamic import DynamicNbNodes
    stat = DynamicNbNodes()
    stat.setWindow(float(window))
    stat.setTick(float(tick))
    stat.execute(gm)
    return {
        "metric": "dynamic_nodes",
        "window": window,
        "tick": tick,
        "report": _get_report(stat),
    }
