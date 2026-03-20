"""CLI entry point - complete Gephi control from command line."""

import json
import click
from rich.console import Console
from rich.table import Table

console = Console()


def _print_json(data):
    console.print_json(json.dumps(data, ensure_ascii=False, default=str))


# ─── Main Group ───────────────────────────────────────────────

@click.group()
@click.version_option(version="2.0.0")
def main():
    """Gephi CLI - Full Gephi control via Python command line.

    \b
    Features:
      14 commands  |  11 layouts  |  15+ metrics  |  17 filters
      10+ formats  |  7 presets   |  Data lab      |  Shortest path
      AutoLayout   |  Projects    |  Dynamic stats |  YAML pipelines
      11 generators|  URL import  |  Validation    |  NetworkX/pandas
    """
    pass


# ─── Import ───────────────────────────────────────────────────

@main.command("import")
@click.argument("file")
@click.option("--processor", "-p", type=click.Choice(["default", "append", "merge"]),
              default="default", help="Import mode: default/append/merge")
def import_cmd(file, processor):
    """Import a graph file.

    \b
    Formats: GEXF, GraphML, GML, CSV, Pajek, DOT, GDF, DL, VNA, JSON
    Processors:
      default - Replace existing graph
      append  - Add to existing graph
      merge   - Merge nodes with same ID
    """
    from . import io_graph
    console.print(f"[bold]Importing[/bold] {file} (processor={processor})...")
    ws = io_graph.import_graph(file, processor=processor)
    info = io_graph.get_graph_info(ws)
    _print_json(info)
    console.print("[green]Import complete.[/green]")


# ─── Export ───────────────────────────────────────────────────

@main.command("export")
@click.argument("input_file")
@click.argument("output_file")
def export_cmd(input_file, output_file):
    """Export/convert graph between formats.

    Formats: GEXF, GraphML, GML, CSV, Pajek, GDF, DL, VNA, JSON, XLSX, PNG, PDF, SVG
    """
    from . import io_graph, preview
    ws = io_graph.import_graph(input_file)

    ext = output_file.lower().rsplit(".", 1)[-1]
    if ext == "png":
        r = preview.export_image(output_file, workspace=ws)
    elif ext == "pdf":
        r = preview.export_pdf(output_file, ws)
    elif ext == "svg":
        r = preview.export_svg(output_file, ws)
    else:
        io_graph.export_graph(output_file, ws)
        r = {"path": output_file}

    _print_json(r)
    console.print(f"[green]Exported to {output_file}[/green]")


# ─── Convert ─────────────────────────────────────────────────

@main.command("convert")
@click.argument("input_file")
@click.argument("output_file")
def convert_cmd(input_file, output_file):
    """Convert graph between any two formats."""
    from . import io_graph
    r = io_graph.convert_graph(input_file, output_file)
    _print_json(r)


# ─── Info ─────────────────────────────────────────────────────

@main.command("info")
@click.argument("file")
@click.option("--nodes", "-n", is_flag=True, help="List nodes with attributes")
@click.option("--edges", "-e", is_flag=True, help="List edges")
@click.option("--limit", "-l", default=50, help="Max items to list")
def info_cmd(file, nodes, edges, limit):
    """Show graph information, nodes, and edges."""
    from . import io_graph
    ws = io_graph.import_graph(file)
    info = io_graph.get_graph_info(ws)
    _print_json(info)

    if nodes:
        console.print("\n[bold]Nodes:[/bold]")
        node_list = io_graph.list_nodes(ws, limit)
        if node_list:
            cols = list(node_list[0].keys())
            table = Table(*cols)
            for n in node_list:
                table.add_row(*[str(n.get(c, "")) for c in cols])
            console.print(table)

    if edges:
        console.print("\n[bold]Edges:[/bold]")
        edge_list = io_graph.list_edges(ws, limit)
        table = Table("Source", "Target", "Weight", "Type")
        for e in edge_list:
            table.add_row(e["source"], e["target"], str(e["weight"]), e["type"])
        console.print(table)


# ─── Layout ───────────────────────────────────────────────────

ALL_LAYOUTS = [
    "forceatlas2", "forceatlas1", "fruchterman_reingold", "yifan_hu",
    "openord", "label_adjust", "noverlap", "random", "rotate",
    "expand", "contract",
]


@main.command("layout")
@click.argument("file")
@click.argument("algorithm", type=click.Choice(ALL_LAYOUTS))
@click.option("--iterations", "-i", default=100, help="Number of iterations")
@click.option("--duration", "-d", type=float, help="Run time in seconds (overrides --iterations)")
@click.option("--output", "-o", help="Output file")
@click.option("--scaling", type=float, help="FA2: scaling ratio")
@click.option("--gravity", type=float, help="Gravity strength")
@click.option("--jitter-tolerance", type=float, help="FA2: jitter tolerance")
@click.option("--barnes-hut", is_flag=True, help="FA2: Barnes-Hut optimization")
@click.option("--barnes-hut-theta", type=float, help="FA2/YH: Barnes-Hut theta")
@click.option("--linlog", is_flag=True, help="FA2: LinLog mode")
@click.option("--strong-gravity", is_flag=True, help="FA2: strong gravity")
@click.option("--outbound-attraction", is_flag=True, help="Outbound attraction distribution")
@click.option("--edge-weight-influence", type=float, help="FA2: edge weight influence")
@click.option("--adjust-sizes", is_flag=True, help="Prevent node overlap")
@click.option("--threads", type=int, help="FA2/OpenOrd: threads")
@click.option("--area", type=float, help="FR: layout area")
@click.option("--speed", type=float, help="FR/LA/Noverlap: speed")
@click.option("--optimal-distance", type=float, help="YH: optimal distance")
@click.option("--step-ratio", type=float, help="YH: step ratio")
@click.option("--edge-cut", type=float, help="OpenOrd: edge cut (0-1)")
@click.option("--num-iterations", type=int, help="OpenOrd: iterations")
@click.option("--margin", type=float, help="Noverlap: margin")
@click.option("--ratio", type=float, help="Noverlap: ratio")
@click.option("--angle", type=float, help="Rotate: degrees")
@click.option("--scale", type=float, help="Expand/Contract: scale factor")
@click.option("--size", type=float, help="Random: area size")
@click.option("--no-auto-tune", is_flag=True, help="Disable FA2 auto-tuning in duration mode")
def layout_cmd(file, algorithm, iterations, duration, output, no_auto_tune, **params):
    """Run a layout algorithm (11 available).

    \b
    Force-directed: forceatlas2, forceatlas1, fruchterman_reingold, yifan_hu
    Large-scale:    openord
    Adjustment:     label_adjust, noverlap
    Transform:      random, rotate, expand, contract

    Use --duration/-d for time-based mode (recommended for force-directed):
      gephi-cli layout graph.gexf forceatlas2 -d 10    # run 10 seconds
    """
    from . import io_graph, layout as layout_mod
    ws = io_graph.import_graph(file)

    clean_params = {k.replace("-", "_"): v for k, v in params.items()
                    if v is not None and v is not False}

    auto_tune = not no_auto_tune
    if duration:
        console.print(f"[bold]Running {algorithm}[/bold] for {duration} seconds...")
        r = layout_mod.run_layout(algorithm, workspace=ws, duration=duration,
                                  auto_tune=auto_tune, **clean_params)
        layout_mod.normalize_layout(ws)
    else:
        console.print(f"[bold]Running {algorithm}[/bold] for {iterations} iterations...")
        r = layout_mod.run_layout(algorithm, iterations, ws,
                                  auto_tune=auto_tune, **clean_params)
    _print_json(r)

    if output:
        io_graph.export_graph(output, ws)
        console.print(f"[green]Saved to {output}[/green]")


# ─── AutoLayout ───────────────────────────────────────────────

@main.command("autolayout")
@click.argument("file")
@click.argument("config_file")
@click.option("--iterations", "-i", default=1000, help="Total iterations to distribute")
@click.option("--duration", "-d", type=float, help="Total time in seconds (overrides --iterations)")
@click.option("--output", "-o", help="Output file")
def autolayout_cmd(file, config_file, iterations, duration, output):
    """Run chained layouts from YAML config.

    \b
    YAML format:
      - algorithm: yifan_hu
        ratio: 0.3
        params:
          optimal_distance: 100
      - algorithm: forceatlas2
        ratio: 0.6
        params:
          scaling: 2.0
      - algorithm: noverlap
        ratio: 0.1

    Use --duration/-d for time-based mode (recommended):
      gephi-cli autolayout graph.gexf layout.yaml -d 30   # run 30 seconds total
    """
    import yaml
    from . import io_graph, autolayout as auto_mod

    ws = io_graph.import_graph(file)
    with open(config_file, "r", encoding="utf-8") as f:
        sequence = yaml.safe_load(f)

    if duration:
        console.print(f"[bold]Running AutoLayout[/bold] ({duration}s, {len(sequence)} phases)...")
        r = auto_mod.run_auto_layout(sequence, total_duration=duration, workspace=ws)
    else:
        console.print(f"[bold]Running AutoLayout[/bold] ({iterations} iterations, {len(sequence)} phases)...")
        r = auto_mod.run_auto_layout(sequence, iterations, workspace=ws)
    _print_json(r)

    if output:
        io_graph.export_graph(output, ws)
        console.print(f"[green]Saved to {output}[/green]")


# ─── Metrics ──────────────────────────────────────────────────

ALL_METRICS = [
    "degree", "weighted_degree", "pagerank", "betweenness", "closeness",
    "eccentricity", "eigenvector", "modularity", "statistical_inference",
    "connected_components", "diameter", "density", "hits",
    "clustering_coefficient", "avg_path_length", "all",
]


@main.command("metric")
@click.argument("file")
@click.argument("name", type=click.Choice(ALL_METRICS))
@click.option("--output", "-o", help="Save enriched graph")
@click.option("--resolution", type=float, help="Modularity: resolution")
@click.option("--use-weight", is_flag=True, help="Modularity: use weights")
@click.option("--normalize", is_flag=True, help="Distance: normalize")
@click.option("--epsilon", type=float, help="PageRank/HITS: epsilon")
@click.option("--probability", type=float, help="PageRank: damping")
@click.option("--num-runs", type=int, help="Eigenvector: iterations")
def metric_cmd(file, name, output, **params):
    """Calculate graph metrics (15 available).

    \b
    Centrality: degree, weighted_degree, pagerank, betweenness,
                closeness, eccentricity, eigenvector, hits
    Community:  modularity, statistical_inference
    Structure:  connected_components, diameter, density,
                clustering_coefficient, avg_path_length
    """
    from . import io_graph, metrics as metrics_mod
    ws = io_graph.import_graph(file)
    clean_params = {k: v for k, v in params.items() if v is not None and v is not False}

    console.print(f"[bold]Computing {name}...[/bold]")
    if name == "all":
        r = metrics_mod.run_all_metrics(ws)
    else:
        r = metrics_mod.run_metric(name, ws, **clean_params)
    _print_json(r)

    if output:
        io_graph.export_graph(output, ws)
        console.print(f"[green]Saved to {output}[/green]")


# ─── Dynamic Metrics ─────────────────────────────────────────

@main.command("dynamic-metric")
@click.argument("file")
@click.argument("name", type=click.Choice([
    "dynamic_degree", "dynamic_clustering", "dynamic_edges", "dynamic_nodes",
]))
@click.option("--window", "-w", default=1.0, help="Time window size")
@click.option("--tick", "-t", default=1.0, help="Time tick (step size)")
@click.option("--output", "-o", help="Save enriched graph")
def dynamic_metric_cmd(file, name, window, tick, output):
    """Calculate dynamic metrics over time.

    \b
    dynamic_degree      - Degree over time
    dynamic_clustering  - Clustering coefficient over time
    dynamic_edges       - Edge count over time
    dynamic_nodes       - Node count over time
    """
    from . import io_graph, dynamic as dyn_mod
    ws = io_graph.import_graph(file)

    console.print(f"[bold]Computing {name}[/bold] (window={window}, tick={tick})...")
    r = dyn_mod.run_dynamic_metric(name, window, tick, ws)
    _print_json(r)

    if output:
        io_graph.export_graph(output, ws)
        console.print(f"[green]Saved to {output}[/green]")


# ─── Filter ───────────────────────────────────────────────────

ALL_FILTERS = [
    "degree", "in_degree", "out_degree", "mutual_degree",
    "giant_component", "k_core", "ego", "has_self_loop",
    "edge_weight", "mutual_edge", "self_loop",
    "attribute_equal", "attribute_range", "attribute_non_null",
    "shortest_path", "reset",
]


@main.command("filter")
@click.argument("file")
@click.argument("filter_type", type=click.Choice(ALL_FILTERS))
@click.option("--min", "min_val", type=float, help="Min value")
@click.option("--max", "max_val", type=float, help="Max value")
@click.option("--k", type=int, help="K value (k-core)")
@click.option("--node-id", help="Node ID (ego/shortest_path)")
@click.option("--target-id", help="Target node ID (shortest_path)")
@click.option("--depth", type=int, default=1, help="Depth (ego)")
@click.option("--column", help="Attribute column")
@click.option("--value", help="Attribute value")
@click.option("--output", "-o", required=True, help="Output file")
def filter_cmd(file, filter_type, min_val, max_val, k, node_id, target_id,
               depth, column, value, output):
    """Filter nodes/edges (17 filters available).

    \b
    Topology:   degree, in_degree, out_degree, mutual_degree
                giant_component, k_core, ego, has_self_loop
    Edge:       edge_weight, mutual_edge, self_loop
    Attribute:  attribute_equal, attribute_range, attribute_non_null
    Path:       shortest_path (--node-id SRC --target-id DST)
    Reset:      reset
    """
    from . import io_graph, filters as filters_mod
    ws = io_graph.import_graph(file)

    console.print(f"[bold]Applying filter: {filter_type}...[/bold]")

    dispatch = {
        "degree": lambda: filters_mod.filter_by_degree(min_val, max_val, ws),
        "in_degree": lambda: filters_mod.filter_by_in_degree(min_val, max_val, ws),
        "out_degree": lambda: filters_mod.filter_by_out_degree(min_val, max_val, ws),
        "mutual_degree": lambda: filters_mod.filter_by_mutual_degree(min_val, max_val, ws),
        "giant_component": lambda: filters_mod.filter_giant_component(ws),
        "k_core": lambda: filters_mod.filter_k_core(k, ws),
        "ego": lambda: filters_mod.filter_ego(node_id, depth, ws),
        "has_self_loop": lambda: filters_mod.filter_has_self_loop(ws),
        "edge_weight": lambda: filters_mod.filter_edge_weight(min_val, max_val, ws),
        "mutual_edge": lambda: filters_mod.filter_mutual_edge(ws),
        "self_loop": lambda: filters_mod.filter_self_loop(ws),
        "attribute_equal": lambda: filters_mod.filter_by_attribute(column, value, ws),
        "attribute_range": lambda: filters_mod.filter_by_attribute_range(column, min_val, max_val, ws),
        "attribute_non_null": lambda: filters_mod.filter_by_attribute_non_null(column, ws),
        "shortest_path": lambda: filters_mod.filter_shortest_path(node_id, target_id, ws),
        "reset": lambda: filters_mod.reset_filter(ws),
    }

    r = dispatch[filter_type]()
    _print_json(r)
    io_graph.export_graph(output, ws)
    console.print(f"[green]Filtered graph saved to {output}[/green]")


# ─── Style (Appearance) ──────────────────────────────────────

@main.command("style")
@click.argument("file")
# Node color
@click.option("--color-by", help="Color nodes by ranking attribute")
@click.option("--partition-color", help="Color nodes by partition (categorical) attribute")
@click.option("--color", nargs=3, type=int, help="Uniform RGB (e.g. 255 0 0)")
@click.option("--modularity-color", is_flag=True, help="Color by modularity class")
# Node size
@click.option("--size-by", help="Size nodes by attribute")
@click.option("--min-size", type=float, default=10, help="Min node size")
@click.option("--max-size", type=float, default=50, help="Max node size")
@click.option("--size", type=float, help="Uniform node size")
# Node labels
@click.option("--labels", help="Set labels from column")
@click.option("--label-color", nargs=3, type=int, help="Label RGB color")
@click.option("--label-size", type=float, help="Label size")
@click.option("--label-font", default="Arial", help="Label font name (default Arial)")
@click.option("--label-font-style", type=click.Choice(["plain", "bold", "italic", "bold_italic"]),
              default="plain", help="Label font style")
# Edge style
@click.option("--edge-color", nargs=3, type=int, help="Uniform edge RGB")
@click.option("--edge-color-by", help="Color edges by attribute")
@click.option("--edge-color-source", is_flag=True, help="Color edges by source node")
@click.option("--edge-color-target", is_flag=True, help="Color edges by target node")
@click.option("--edge-weight", type=float, help="Uniform edge weight")
@click.option("--edge-weight-by", help="Set edge weight from attribute")
@click.option("--edge-labels", help="Set edge labels from column")
# Output
@click.option("--output", "-o", required=True, help="Output file")
def style_cmd(file, color_by, partition_color, color, modularity_color,
              size_by, min_size, max_size, size, labels, label_color, label_size,
              label_font, label_font_style,
              edge_color, edge_color_by, edge_color_source, edge_color_target,
              edge_weight, edge_weight_by, edge_labels, output):
    """Style node and edge appearance.

    \b
    Node color:  --color-by COL, --partition-color COL, --color R G B, --modularity-color
    Node size:   --size-by COL, --size N
    Node labels: --labels COL, --label-color R G B, --label-size N
    Edge style:  --edge-color R G B, --edge-color-by COL, --edge-color-source/target
                 --edge-weight N, --edge-weight-by COL, --edge-labels COL
    """
    from . import io_graph, appearance as app
    ws = io_graph.import_graph(file)
    results = []

    # Node color
    if color_by:
        results.append(app.set_node_color_by_attribute(color_by, ws))
    if partition_color:
        results.append(app.color_nodes_by_partition(partition_color, ws))
    if color:
        results.append(app.set_all_nodes_color(*color, ws))
    if modularity_color:
        results.append(app.color_nodes_by_modularity(ws))

    # Node size
    if size_by:
        results.append(app.set_node_size_by_attribute(size_by, min_size, max_size, ws))
    if size:
        results.append(app.set_all_nodes_size(size, ws))

    # Node labels
    if labels:
        results.append(app.set_node_labels(labels, ws))
    if label_color:
        results.append(app.set_node_label_color(*label_color, ws))
    if label_size:
        results.append(app.set_node_label_size(label_size, ws,
                                               font_name=label_font, font_style=label_font_style))

    # Edge style
    if edge_color:
        results.append(app.set_all_edges_color(*edge_color, ws))
    if edge_color_by:
        results.append(app.set_edge_color_by_attribute(edge_color_by, ws))
    if edge_color_source:
        results.append(app.color_edges_by_source(ws))
    if edge_color_target:
        results.append(app.color_edges_by_target(ws))
    if edge_weight is not None:
        results.append(app.set_all_edges_weight(edge_weight, ws))
    if edge_weight_by:
        results.append(app.set_edge_weight_by_attribute(edge_weight_by, ws))
    if edge_labels:
        results.append(app.set_edge_labels(edge_labels, ws))

    _print_json(results)
    io_graph.export_graph(output, ws)
    console.print(f"[green]Styled graph saved to {output}[/green]")


# ─── Render ───────────────────────────────────────────────────

@main.command("render")
@click.argument("file")
@click.argument("output")
@click.option("--width", "-w", default=1024, help="Image width (PNG)")
@click.option("--height", "-h", default=1024, help="Image height (PNG)")
@click.option("--preset", type=click.Choice([
    "default", "default_curved", "default_straight",
    "black_background", "tag_cloud", "text_outline", "edges_custom_color",
]), help="Apply a preview preset")
@click.option("--show-labels/--no-labels", default=True)
@click.option("--node-opacity", type=float)
@click.option("--node-border-width", type=float)
@click.option("--label-font-size", help="Font size (int) or 'size:fontname:style'")
@click.option("--label-proportional-size", is_flag=True)
@click.option("--label-outline-size", type=float)
@click.option("--label-max-char", type=int)
@click.option("--show-edges/--no-edges", default=True)
@click.option("--edge-opacity", type=float, default=50)
@click.option("--edge-thickness", type=float)
@click.option("--edge-curved/--edge-straight", default=False)
@click.option("--edge-rescale-weight", is_flag=True)
@click.option("--show-edge-labels", is_flag=True)
@click.option("--arrow-size", type=float)
@click.option("--background", default="#ffffff", help="Background color hex")
@click.option("--margin", type=float)
def render_cmd(file, output, width, height, preset, **opts):
    """Render graph to image (PNG, PDF, SVG).

    Supports 7 presets and 30+ preview properties.
    """
    from . import io_graph, preview as preview_mod
    ws = io_graph.import_graph(file)

    # Apply preset if specified
    if preset:
        preview_mod.apply_preset(preset, ws)

    # Map CLI opts to preview properties
    opt_mapping = {
        "show_labels": "show_labels", "node_opacity": "node_opacity",
        "node_border_width": "node_border_width", "label_font_size": "label_font_size",
        "label_proportional_size": "label_proportional_size",
        "label_outline_size": "label_outline_size", "label_max_char": "label_max_char",
        "show_edges": "show_edges", "edge_opacity": "edge_opacity",
        "edge_thickness": "edge_thickness", "edge_curved": "edge_curved",
        "edge_rescale_weight": "edge_rescale_weight",
        "show_edge_labels": "show_edge_labels", "arrow_size": "arrow_size",
        "background": "background_color", "margin": "margin",
    }
    preview_opts = {}
    for cli_name, prop_name in opt_mapping.items():
        val = opts.get(cli_name)
        if val is not None and val is not False:
            preview_opts[prop_name] = val

    if preview_opts:
        preview_mod.configure_preview(ws, **preview_opts)

    ext = output.lower().rsplit(".", 1)[-1]
    if ext == "png":
        r = preview_mod.export_image(output, width, height, ws)
    elif ext == "pdf":
        r = preview_mod.export_pdf(output, ws)
    elif ext == "svg":
        r = preview_mod.export_svg(output, ws)
    else:
        console.print(f"[red]Unsupported format: {ext}. Use png, pdf, or svg.[/red]")
        return

    _print_json(r)
    console.print(f"[green]Rendered to {output}[/green]")


# ─── Shortest Path ───────────────────────────────────────────

@main.command("shortest-path")
@click.argument("file")
@click.argument("source")
@click.option("--target", "-t", help="Target node ID (omit for all nodes)")
@click.option("--algorithm", "-a", type=click.Choice(["dijkstra", "bellman_ford"]),
              default="dijkstra", help="Algorithm")
def shortest_path_cmd(file, source, target, algorithm):
    """Compute shortest paths from a source node.

    \b
    Examples:
      gephi-cli shortest-path graph.gexf 0              # All distances from node 0
      gephi-cli shortest-path graph.gexf 0 -t 42        # Path from 0 to 42
      gephi-cli shortest-path graph.gexf 0 -a bellman_ford
    """
    from . import io_graph, shortest_path as sp_mod
    ws = io_graph.import_graph(file)

    if target:
        console.print(f"[bold]Shortest path[/bold] {source} -> {target} ({algorithm})...")
        r = sp_mod.get_path_between(source, target, algorithm, ws)
    else:
        console.print(f"[bold]Shortest paths[/bold] from {source} ({algorithm})...")
        r = sp_mod.compute_shortest_path(source, algorithm, ws)

    _print_json(r)


# ─── Data Lab ────────────────────────────────────────────────

@main.group("datalab")
def datalab_group():
    """Data laboratory: node/edge CRUD, attribute management, search & replace."""
    pass


@datalab_group.command("create-node")
@click.argument("file")
@click.option("--label", "-l", help="Node label")
@click.option("--output", "-o", required=True, help="Output file")
def datalab_create_node(file, label, output):
    """Create a new node."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.create_node(label, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("create-edge")
@click.argument("file")
@click.argument("source")
@click.argument("target")
@click.option("--weight", "-w", type=float, default=1.0)
@click.option("--output", "-o", required=True, help="Output file")
def datalab_create_edge(file, source, target, weight, output):
    """Create a new edge."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.create_edge(source, target, weight, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("delete-node")
@click.argument("file")
@click.argument("node_id")
@click.option("--output", "-o", required=True)
def datalab_delete_node(file, node_id, output):
    """Delete a node and its edges."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.delete_node(node_id, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("delete-edge")
@click.argument("file")
@click.argument("source")
@click.argument("target")
@click.option("--output", "-o", required=True)
def datalab_delete_edge(file, source, target, output):
    """Delete an edge."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.delete_edge(source, target, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("merge-nodes")
@click.argument("file")
@click.argument("node_ids", nargs=-1, required=True)
@click.option("--keep", help="Node ID to keep")
@click.option("--output", "-o", required=True)
def datalab_merge_nodes(file, node_ids, keep, output):
    """Merge multiple nodes into one."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.merge_nodes(list(node_ids), keep, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("add-column")
@click.argument("file")
@click.argument("column_name")
@click.option("--type", "column_type", default="string",
              type=click.Choice(["string", "integer", "float", "double", "boolean", "long"]))
@click.option("--table", default="node", type=click.Choice(["node", "edge"]))
@click.option("--output", "-o", required=True)
def datalab_add_column(file, column_name, column_type, table, output):
    """Add a new attribute column."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.add_column(column_name, column_type, table, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("delete-column")
@click.argument("file")
@click.argument("column_name")
@click.option("--table", default="node", type=click.Choice(["node", "edge"]))
@click.option("--output", "-o", required=True)
def datalab_delete_column(file, column_name, table, output):
    """Delete an attribute column."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.delete_column(column_name, table, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("fill-column")
@click.argument("file")
@click.argument("column_name")
@click.argument("value")
@click.option("--table", default="node", type=click.Choice(["node", "edge"]))
@click.option("--output", "-o", required=True)
def datalab_fill_column(file, column_name, value, table, output):
    """Fill entire column with a value."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.fill_column(column_name, value, table, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("clear-column")
@click.argument("file")
@click.argument("column_name")
@click.option("--table", default="node", type=click.Choice(["node", "edge"]))
@click.option("--output", "-o", required=True)
def datalab_clear_column(file, column_name, table, output):
    """Clear all values in a column."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.clear_column(column_name, table, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("duplicate-column")
@click.argument("file")
@click.argument("column_name")
@click.argument("new_name")
@click.option("--table", default="node", type=click.Choice(["node", "edge"]))
@click.option("--output", "-o", required=True)
def datalab_duplicate_column(file, column_name, new_name, table, output):
    """Duplicate a column with a new name."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.duplicate_column(column_name, new_name, table, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("column-stats")
@click.argument("file")
@click.argument("column_name")
@click.option("--table", default="node", type=click.Choice(["node", "edge"]))
def datalab_column_stats(file, column_name, table):
    """Get statistics for a numeric column."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.get_column_statistics(column_name, table, workspace=ws)
    _print_json(r)


@datalab_group.command("search-replace")
@click.argument("file")
@click.argument("column_name")
@click.argument("search")
@click.argument("replace")
@click.option("--table", default="node", type=click.Choice(["node", "edge"]))
@click.option("--regex", is_flag=True, help="Use regex matching")
@click.option("--output", "-o", required=True)
def datalab_search_replace(file, column_name, search, replace, table, regex, output):
    """Search and replace in an attribute column."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.search_replace(column_name, search, replace, table, regex, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


@datalab_group.command("set-attribute")
@click.argument("file")
@click.argument("node_id")
@click.argument("column_name")
@click.argument("value")
@click.option("--output", "-o", required=True)
def datalab_set_attribute(file, node_id, column_name, value, output):
    """Set attribute value on a specific node."""
    from . import io_graph, datalab
    ws = io_graph.import_graph(file)
    r = datalab.set_attribute(node_id, column_name, value, workspace=ws)
    _print_json(r)
    io_graph.export_graph(output, ws)


# ─── Project Management ──────────────────────────────────────

@main.group("project")
def project_group():
    """Project and workspace management."""
    pass


@project_group.command("save")
@click.argument("input_file")
@click.argument("project_file")
def project_save(input_file, project_file):
    """Save graph as a .gephi project file."""
    from . import io_graph, project as proj_mod
    io_graph.import_graph(input_file)
    r = proj_mod.save_project(project_file)
    _print_json(r)


@project_group.command("open")
@click.argument("project_file")
def project_open(project_file):
    """Open a .gephi project file."""
    from . import project as proj_mod
    r = proj_mod.open_project(project_file)
    _print_json(r)


@project_group.command("workspaces")
@click.argument("project_file")
def project_workspaces(project_file):
    """List workspaces in a project."""
    from . import project as proj_mod
    proj_mod.open_project(project_file)
    r = proj_mod.list_workspaces()
    _print_json(r)


# ─── Generate ─────────────────────────────────────────────────

@main.command("generate")
@click.argument("graph_type", type=click.Choice([
    "random", "scale_free", "small_world", "complete", "star",
    "ring", "grid", "tree", "path", "empty", "dynamic",
]))
@click.argument("output")
@click.option("--nodes", "-n", default=100, help="Number of nodes")
@click.option("--wiring-prob", "-p", default=0.05, help="Random: wiring probability (0.0-1.0)")
@click.option("--m", default=2, help="Scale-free: edges per new node")
@click.option("--k", default=4, help="Small-world: nearest neighbors (even)")
@click.option("--beta", default=0.3, help="Small-world: rewiring probability")
@click.option("--rows", default=10, help="Grid: number of rows")
@click.option("--cols", default=10, help="Grid: number of columns")
@click.option("--depth", default=4, help="Tree: depth")
@click.option("--branching", default=2, help="Tree: children per node")
@click.option("--directed", is_flag=True, help="Complete: create directed edges")
@click.option("--seed", type=int, help="Random seed for reproducibility")
def generate_cmd(graph_type, output, nodes, wiring_prob, m, k, beta,
                 rows, cols, depth, branching, directed, seed):
    """Generate a graph (11 types available).

    \b
    Types:
      random       - Erdos-Renyi G(n,p)
      scale_free   - Barabasi-Albert preferential attachment
      small_world  - Watts-Strogatz
      complete     - Fully connected
      star         - Center + leaves
      ring         - Cycle
      grid         - 2D lattice (rows x cols)
      tree         - Balanced tree (depth x branching)
      path         - Linear chain
      empty        - Nodes only (no edges)
      dynamic      - Time-varying graph
    """
    from . import generator as gen_mod, io_graph

    kwargs = {}
    if graph_type == "random":
        kwargs = {"node_count": nodes, "wiring_prob": wiring_prob}
    elif graph_type == "scale_free":
        kwargs = {"node_count": nodes, "m": m, "seed": seed}
    elif graph_type == "small_world":
        kwargs = {"node_count": nodes, "k": k, "beta": beta, "seed": seed}
    elif graph_type == "complete":
        kwargs = {"node_count": nodes, "directed": directed}
    elif graph_type in ("star", "ring", "path", "empty"):
        kwargs = {"node_count": nodes}
    elif graph_type == "grid":
        kwargs = {"rows": rows, "cols": cols}
    elif graph_type == "tree":
        kwargs = {"depth": depth, "branching": branching}
    elif graph_type == "dynamic":
        kwargs = {"node_count": nodes}

    console.print(f"[bold]Generating {graph_type} graph[/bold]...")
    ws = gen_mod.generate(graph_type, **kwargs)
    io_graph.export_graph(output, ws)
    info = io_graph.get_graph_info(ws)
    _print_json(info)
    console.print(f"[green]Graph saved to {output}[/green]")


# ─── Import URL ──────────────────────────────────────────────

@main.command("import-url")
@click.argument("url")
@click.argument("output")
@click.option("--processor", "-p", type=click.Choice(["default", "append", "merge"]),
              default="default", help="Import mode")
@click.option("--format", "fmt", help="Force format (e.g. gexf, graphml). Auto-detect if omitted")
@click.option("--timeout", default=30, help="Download timeout in seconds")
def import_url_cmd(url, output, processor, fmt, timeout):
    """Import a graph from a URL (HTTP/HTTPS).

    \b
    Downloads the file and imports it. Format auto-detected from URL extension.
    Use --format to override (e.g. --format gexf).
    """
    from . import io_graph
    console.print(f"[bold]Importing from URL[/bold]...")
    ws = io_graph.import_from_url(url, processor=processor, format=fmt, timeout=timeout)
    info = io_graph.get_graph_info(ws)
    _print_json(info)
    io_graph.export_graph(output, ws)
    console.print(f"[green]Imported and saved to {output}[/green]")


# ─── Validate ────────────────────────────────────────────────

@main.command("validate")
@click.argument("file")
def validate_cmd(file):
    """Validate graph structure and report quality issues.

    \b
    Checks: density, isolated nodes, self-loops, degree distribution,
            attribute completeness
    """
    from . import io_graph
    ws = io_graph.import_graph(file)
    r = io_graph.validate_graph(ws)
    _print_json(r)
    if r.get("issues") and r["issues"] != ["No issues found"]:
        console.print(f"[yellow]Found {len(r['issues'])} issue(s)[/yellow]")
    else:
        console.print("[green]No issues found.[/green]")


# ─── Pipeline ─────────────────────────────────────────────────

@main.command("pipeline")
@click.argument("config_file")
def pipeline_cmd(config_file):
    """Run a multi-step pipeline from YAML.

    \b
    Actions: generate, import, export, layout, metric,
             filter, appearance, preview, shortest_path,
             datalab, autolayout, project_save
    """
    from . import pipeline as pipe_mod
    console.print(f"[bold]Running pipeline:[/bold] {config_file}")
    results = pipe_mod.run_pipeline(config_file)
    for r in results:
        _print_json(r)
    console.print("[green]Pipeline complete.[/green]")


# ─── List ─────────────────────────────────────────────────────

@main.command("list")
@click.argument("category", type=click.Choice([
    "layouts", "metrics", "filters", "generators", "formats",
    "preview_properties", "preview_presets", "dynamic_metrics",
]))
def list_cmd(category):
    """List available algorithms, metrics, filters, etc.

    \b
    Categories: layouts, metrics, filters, generators, formats,
                preview_properties, preview_presets, dynamic_metrics
    """
    from . import layout as layout_mod, metrics as metrics_mod
    from . import filters as filters_mod, generator as gen_mod
    from . import io_graph, preview as preview_mod, dynamic as dyn_mod

    if category == "layouts":
        layout_info = layout_mod.list_layouts()
        for name, info in layout_info.items():
            console.print(f"\n[bold cyan]{name}[/bold cyan] - {info['description']}")
            if info["parameters"]:
                param_table = Table("Parameter", "Description", show_header=True)
                for pname, pdesc in info["parameters"].items():
                    param_table.add_row(pname, pdesc)
                console.print(param_table)

    elif category == "metrics":
        table = Table("Name", "Description")
        for name, desc in metrics_mod.METRICS.items():
            table.add_row(name, desc)
        console.print(table)

    elif category == "dynamic_metrics":
        table = Table("Name", "Description")
        for name, desc in dyn_mod.DYNAMIC_METRICS.items():
            table.add_row(name, desc)
        console.print(table)

    elif category == "filters":
        table = Table("Name", "Description")
        for name, desc in filters_mod.FILTERS.items():
            table.add_row(name, desc)
        console.print(table)

    elif category == "generators":
        table = Table("Name", "Description")
        for name, desc in gen_mod.GENERATORS.items():
            table.add_row(name, desc)
        console.print(table)

    elif category == "formats":
        console.print("\n[bold]Import Formats:[/bold]")
        table = Table("Extension", "Format")
        for ext, desc in io_graph.IMPORT_FORMATS.items():
            table.add_row(ext, desc)
        console.print(table)
        console.print("\n[bold]Export Formats:[/bold]")
        table = Table("Extension", "Format")
        for ext, desc in io_graph.EXPORT_FORMATS.items():
            table.add_row(ext, desc)
        console.print(table)
        console.print("\n[bold]Import Processors:[/bold]")
        table = Table("Mode", "Description")
        for name, desc in io_graph.IMPORT_PROCESSORS.items():
            table.add_row(name, desc)
        console.print(table)

    elif category == "preview_properties":
        table = Table("Property", "Type", "Description")
        for name, (_, ptype, desc) in preview_mod.PREVIEW_PROPERTIES.items():
            type_str = ptype.__name__ if isinstance(ptype, type) else str(ptype)
            table.add_row(name, type_str, desc)
        console.print(table)

    elif category == "preview_presets":
        table = Table("Preset", "Description")
        for name, desc in preview_mod.PREVIEW_PRESETS.items():
            table.add_row(name, desc)
        console.print(table)


if __name__ == "__main__":
    main()
