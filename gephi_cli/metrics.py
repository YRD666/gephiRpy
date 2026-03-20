"""All graph metrics and statistics from Gephi Toolkit."""

from .core import start_jvm, get_graph_model


METRICS = {
    "degree": "Degree distribution (in/out/total degree)",
    "weighted_degree": "Weighted degree distribution",
    "pagerank": "PageRank centrality",
    "betweenness": "Betweenness centrality (via graph distance)",
    "closeness": "Closeness centrality (via graph distance)",
    "eccentricity": "Eccentricity (via graph distance)",
    "eigenvector": "Eigenvector centrality",
    "modularity": "Modularity (Louvain community detection)",
    "statistical_inference": "Statistical inference clustering (SBM)",
    "connected_components": "Connected components (weakly/strongly)",
    "diameter": "Graph diameter, radius & average path length",
    "density": "Graph density",
    "hits": "HITS (Hub & Authority scores)",
    "clustering_coefficient": "Clustering coefficient (local & average)",
    "avg_path_length": "Average path length",
}


def run_metric(metric_name, workspace=None, **params):
    """Run a graph metric/statistic.

    Args:
        metric_name: One of the keys in METRICS
        workspace: Gephi workspace
        **params: Metric-specific parameters

    Returns:
        dict with metric results
    """
    start_jvm()
    gm = get_graph_model(workspace)
    algo = metric_name.lower()

    dispatch = {
        "degree": _run_degree,
        "weighted_degree": _run_weighted_degree,
        "pagerank": _run_pagerank,
        "betweenness": _run_graph_distance,
        "closeness": _run_graph_distance,
        "eccentricity": _run_graph_distance,
        "eigenvector": _run_eigenvector,
        "modularity": _run_modularity,
        "statistical_inference": _run_statistical_inference,
        "connected_components": _run_connected_components,
        "diameter": _run_graph_distance,
        "density": _run_density,
        "avg_path_length": _run_graph_distance,
        "hits": _run_hits,
        "clustering_coefficient": _run_clustering,
    }

    if algo not in dispatch:
        raise ValueError(f"Unknown metric: {metric_name}. Available: {list(METRICS.keys())}")

    result = dispatch[algo](gm, **params)
    result["metric"] = algo
    return result


def _run_degree(gm, **params):
    from org.gephi.statistics.plugin import Degree
    stat = Degree()
    stat.execute(gm)
    return {
        "average_degree": float(stat.getAverageDegree()),
        "note": "Degree values stored as node attributes: 'Degree', 'In-Degree', 'Out-Degree'",
    }


def _run_weighted_degree(gm, **params):
    from org.gephi.statistics.plugin import WeightedDegree
    stat = WeightedDegree()
    stat.execute(gm)
    return {
        "average_weighted_degree": float(stat.getAverageDegree()),
        "note": "Weighted degree stored as node attribute 'Weighted Degree'",
    }


def _run_pagerank(gm, **params):
    from org.gephi.statistics.plugin import PageRank
    stat = PageRank()
    stat.setDirected(gm.isDirected())
    if "epsilon" in params:
        stat.setEpsilon(float(params["epsilon"]))
    if "probability" in params:
        stat.setProbability(float(params["probability"]))
    stat.execute(gm)
    return {
        "note": "PageRank values stored as node attribute 'pageranks'",
    }


def _run_graph_distance(gm, **params):
    from org.gephi.statistics.plugin import GraphDistance
    stat = GraphDistance()
    stat.setDirected(gm.isDirected())
    if "normalize" in params:
        stat.setNormalized(bool(params["normalize"]))
    stat.execute(gm)
    return {
        "diameter": float(stat.getDiameter()),
        "radius": float(stat.getRadius()),
        "avg_path_length": float(stat.getPathLength()),
        "note": "Betweenness, Closeness, Eccentricity stored as node attributes",
    }


def _run_eigenvector(gm, **params):
    from org.gephi.statistics.plugin import EigenvectorCentrality
    stat = EigenvectorCentrality()
    stat.setDirected(gm.isDirected())
    if "num_runs" in params:
        stat.setNumRuns(int(params["num_runs"]))
    stat.execute(gm)
    return {
        "iterations": int(stat.getNumRuns()),
        "note": "Eigenvector centrality stored as node attribute 'eigencentrality'",
    }


def _run_modularity(gm, **params):
    from org.gephi.statistics.plugin import Modularity
    stat = Modularity()
    resolution = params.get("resolution", 1.0)
    stat.setResolution(float(resolution))
    if "use_weight" in params:
        stat.setUseWeight(bool(params["use_weight"]))
    if "random" in params:
        stat.setRandom(bool(params["random"]))
    stat.execute(gm)
    return {
        "modularity_score": float(stat.getModularity()),
        "note": "Community IDs stored as node attribute 'modularity_class'",
    }


def _run_statistical_inference(gm, **params):
    from org.gephi.statistics.plugin import StatisticalInferenceClustering
    stat = StatisticalInferenceClustering()
    stat.execute(gm)
    return {
        "description_length": float(stat.getDescriptionLength()),
        "note": "Cluster IDs stored as node attribute",
    }


def _run_connected_components(gm, **params):
    from org.gephi.statistics.plugin import ConnectedComponents
    stat = ConnectedComponents()
    stat.setDirected(gm.isDirected())
    stat.execute(gm)
    return {
        "component_count": int(stat.getConnectedComponentsCount()),
        "note": "Component IDs stored as node attribute 'componentnumber'",
    }


def _run_density(gm, **params):
    from org.gephi.statistics.plugin import GraphDensity
    stat = GraphDensity()
    stat.setDirected(gm.isDirected())
    stat.execute(gm)
    return {
        "density": float(stat.getDensity()),
    }


def _run_hits(gm, **params):
    from org.gephi.statistics.plugin import Hits
    stat = Hits()
    stat.setUndirected(not gm.isDirected())
    if "epsilon" in params:
        stat.setEpsilon(float(params["epsilon"]))
    stat.execute(gm)
    return {
        "note": "Hub and Authority scores stored as node attributes 'authority' and 'hub'",
    }


def _run_clustering(gm, **params):
    from org.gephi.statistics.plugin import ClusteringCoefficient
    stat = ClusteringCoefficient()
    stat.setDirected(gm.isDirected())
    stat.execute(gm)
    return {
        "avg_clustering_coefficient": float(stat.getAverageClusteringCoefficient()),
        "note": "Local clustering coefficients stored as node attribute 'clustering'",
    }


def run_all_metrics(workspace=None):
    """Run all metrics and return combined results."""
    results = {}
    for metric in METRICS:
        try:
            results[metric] = run_metric(metric, workspace)
        except Exception as e:
            results[metric] = {"metric": metric, "error": str(e)}
    return results


def list_metrics():
    """Return available metrics with descriptions."""
    return METRICS.copy()
