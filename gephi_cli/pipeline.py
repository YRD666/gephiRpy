"""Pipeline: run multi-step workflows from YAML config."""

import yaml
from . import io_graph, layout, metrics, filters, appearance, preview
from . import generator, shortest_path, datalab, autolayout, project, dynamic


def run_pipeline(config_path):
    """Run a YAML-defined pipeline. See examples/pipeline_full.yaml for reference."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    steps = config.get("steps", [])
    results = []
    workspace = None

    for i, step in enumerate(steps):
        action = step.get("action")
        result = {"step": i + 1, "action": action}

        try:
            if action == "generate":
                gen_type = step.get("type", "random")
                gen_kwargs = {k: v for k, v in step.items()
                              if k not in ("action", "type")}
                # Remap common param names
                if "nodes" in gen_kwargs and "node_count" not in gen_kwargs:
                    gen_kwargs["node_count"] = gen_kwargs.pop("nodes")
                workspace = generator.generate(gen_type, **gen_kwargs)
                result["status"] = "ok"
                result.update(io_graph.get_graph_info(workspace))

            elif action == "import":
                workspace = io_graph.import_graph(
                    step["file"], workspace, step.get("processor", "default"))
                result.update(io_graph.get_graph_info(workspace))

            elif action == "export":
                file_path = step["file"]
                ext = file_path.lower().rsplit(".", 1)[-1]
                if ext == "png":
                    result.update(preview.export_image(
                        file_path, step.get("width", 1024), step.get("height", 1024), workspace))
                elif ext == "pdf":
                    result.update(preview.export_pdf(file_path, workspace))
                elif ext == "svg":
                    result.update(preview.export_svg(file_path, workspace))
                else:
                    io_graph.export_graph(file_path, workspace)
                    result["path"] = file_path

            elif action == "layout":
                params = step.get("params", {})
                duration = step.get("duration")
                auto_tune = step.get("auto_tune", True)
                result.update(layout.run_layout(
                    step["algorithm"], step.get("iterations", 100), workspace,
                    duration=duration, auto_tune=auto_tune, **params))

            elif action == "autolayout":
                sequence = step.get("sequence", [])
                duration = step.get("duration")
                if duration:
                    result.update(autolayout.run_auto_layout(
                        sequence, total_duration=duration, workspace=workspace))
                else:
                    result.update(autolayout.run_auto_layout(
                        sequence, step.get("iterations", 1000), workspace=workspace))

            elif action == "metric":
                params = step.get("params", {})
                if step.get("name") == "all":
                    result.update(metrics.run_all_metrics(workspace))
                else:
                    result.update(metrics.run_metric(step["name"], workspace, **params))

            elif action == "dynamic_metric":
                result.update(dynamic.run_dynamic_metric(
                    step["name"], step.get("window", 1.0), step.get("tick", 1.0), workspace))

            elif action == "filter":
                result.update(_run_filter_step(step, workspace))

            elif action == "appearance":
                result.update(_run_appearance_step(step, workspace))

            elif action == "preview":
                opts = {k: v for k, v in step.items() if k != "action"}
                if "preset" in opts:
                    preview.apply_preset(opts.pop("preset"), workspace)
                if opts:
                    result.update(preview.configure_preview(workspace, **opts))

            elif action == "shortest_path":
                if "target" in step:
                    result.update(shortest_path.get_path_between(
                        step["source"], step["target"],
                        step.get("algorithm", "dijkstra"), workspace))
                else:
                    result.update(shortest_path.compute_shortest_path(
                        step["source"], step.get("algorithm", "dijkstra"), workspace))

            elif action == "datalab":
                result.update(_run_datalab_step(step, workspace))

            elif action == "import_url":
                workspace = io_graph.import_from_url(
                    step["url"], workspace,
                    processor=step.get("processor", "default"),
                    format=step.get("format"),
                    timeout=step.get("timeout", 30),
                    headers=step.get("headers"))
                result.update(io_graph.get_graph_info(workspace))

            elif action == "import_string":
                workspace = io_graph.import_from_string(
                    step["content"], step.get("format", "gexf"),
                    workspace, step.get("processor", "default"))
                result.update(io_graph.get_graph_info(workspace))

            elif action == "import_edge_list":
                workspace = io_graph.import_from_edge_list(
                    step["edges"], step.get("directed", True), workspace)
                result.update(io_graph.get_graph_info(workspace))

            elif action == "validate":
                result.update(io_graph.validate_graph(workspace))

            elif action == "project_save":
                result.update(project.save_project(step["file"]))

            else:
                result["error"] = f"Unknown action: {action}"

        except Exception as e:
            result["error"] = str(e)

        results.append(result)

    return results


def _run_filter_step(step, workspace):
    ft = step.get("type")
    dispatch = {
        "degree": lambda: filters.filter_by_degree(step.get("min"), step.get("max"), workspace),
        "in_degree": lambda: filters.filter_by_in_degree(step.get("min"), step.get("max"), workspace),
        "out_degree": lambda: filters.filter_by_out_degree(step.get("min"), step.get("max"), workspace),
        "mutual_degree": lambda: filters.filter_by_mutual_degree(step.get("min"), step.get("max"), workspace),
        "giant_component": lambda: filters.filter_giant_component(workspace),
        "k_core": lambda: filters.filter_k_core(step["k"], workspace),
        "ego": lambda: filters.filter_ego(step["node_id"], step.get("depth", 1), workspace),
        "has_self_loop": lambda: filters.filter_has_self_loop(workspace),
        "edge_weight": lambda: filters.filter_edge_weight(step.get("min"), step.get("max"), workspace),
        "mutual_edge": lambda: filters.filter_mutual_edge(workspace),
        "self_loop": lambda: filters.filter_self_loop(workspace),
        "attribute_equal": lambda: filters.filter_by_attribute(step["column"], step["value"], workspace),
        "attribute_range": lambda: filters.filter_by_attribute_range(step["column"], step.get("min"), step.get("max"), workspace),
        "attribute_non_null": lambda: filters.filter_by_attribute_non_null(step["column"], workspace),
        "shortest_path": lambda: filters.filter_shortest_path(step["source"], step["target"], workspace),
        "reset": lambda: filters.reset_filter(workspace),
    }
    if ft in dispatch:
        return dispatch[ft]()
    return {"error": f"Unknown filter type: {ft}"}


def _run_appearance_step(step, workspace):
    at = step.get("type")
    dispatch = {
        "color_by_modularity": lambda: appearance.color_nodes_by_modularity(workspace),
        "color_by_partition": lambda: appearance.color_nodes_by_partition(
            step["column"], workspace,
            color_min=step.get("color_min", 30), color_max=step.get("color_max", 220),
            seed=step.get("seed")),
        "color_by_attribute": lambda: appearance.set_node_color_by_attribute(step["column"], workspace),
        "size_by_attribute": lambda: appearance.set_node_size_by_attribute(
            step["column"], step.get("min_size", 10), step.get("max_size", 50), workspace),
        "uniform_color": lambda: appearance.set_all_nodes_color(step["r"], step["g"], step["b"], workspace),
        "uniform_size": lambda: appearance.set_all_nodes_size(step["size"], workspace),
        "labels": lambda: appearance.set_node_labels(step.get("column"), workspace),
        "label_color": lambda: appearance.set_node_label_color(step["r"], step["g"], step["b"], workspace),
        "label_size": lambda: appearance.set_node_label_size(
            step["size"], workspace,
            font_name=step.get("font_name", "Arial"),
            font_style=step.get("font_style", "plain")),
        "edge_color": lambda: appearance.set_all_edges_color(step["r"], step["g"], step["b"], workspace),
        "edge_color_by_attribute": lambda: appearance.set_edge_color_by_attribute(step["column"], workspace),
        "edge_color_by_source": lambda: appearance.color_edges_by_source(workspace),
        "edge_color_by_target": lambda: appearance.color_edges_by_target(workspace),
        "edge_weight": lambda: appearance.set_all_edges_weight(step["weight"], workspace),
        "edge_weight_by_attribute": lambda: appearance.set_edge_weight_by_attribute(step["column"], workspace),
        "edge_labels": lambda: appearance.set_edge_labels(step.get("column"), workspace),
    }
    if at in dispatch:
        return dispatch[at]()
    return {"error": f"Unknown appearance type: {at}"}


def _run_datalab_step(step, workspace):
    op = step.get("operation")
    dispatch = {
        "create_node": lambda: datalab.create_node(step.get("label"), step.get("attributes"), workspace),
        "create_edge": lambda: datalab.create_edge(step["source"], step["target"], step.get("weight", 1.0), workspace=workspace),
        "delete_node": lambda: datalab.delete_node(step["node_id"], workspace),
        "delete_edge": lambda: datalab.delete_edge(step["source"], step["target"], workspace),
        "add_column": lambda: datalab.add_column(step["column"], step.get("column_type", "string"), step.get("table", "node"), workspace),
        "delete_column": lambda: datalab.delete_column(step["column"], step.get("table", "node"), workspace),
        "fill_column": lambda: datalab.fill_column(step["column"], step["value"], step.get("table", "node"), workspace),
        "clear_column": lambda: datalab.clear_column(step["column"], step.get("table", "node"), workspace),
        "search_replace": lambda: datalab.search_replace(step["column"], step["search"], step["replace"], step.get("table", "node"), step.get("regex", False), workspace),
    }
    if op in dispatch:
        return dispatch[op]()
    return {"error": f"Unknown datalab operation: {op}"}
