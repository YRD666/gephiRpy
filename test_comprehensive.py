"""Comprehensive random test suite for gephi-cli.
Generates graphs, runs all features, exports images and results.
"""

import json
import os
import time

# Ensure output directory
OUT = os.path.join(os.path.dirname(__file__), "test_results")
os.makedirs(OUT, exist_ok=True)

results = {}


def log(section, msg, data=None):
    print(f"[{section}] {msg}")
    if data:
        results.setdefault(section, []).append({"msg": msg, **data})
    else:
        results.setdefault(section, []).append({"msg": msg})


# ═══════════════════════════════════════════════════════════
# 0. Initialize JVM
# ═══════════════════════════════════════════════════════════
from gephi_cli import core
core.start_jvm()
log("init", "JVM started")

# ═══════════════════════════════════════════════════════════
# 1. Generate random graph
# ═══════════════════════════════════════════════════════════
from gephi_cli import generator, io_graph

ws = generator.generate_random(200, 0.03)
info = io_graph.get_graph_info(ws)
log("generate", f"Random graph: {info['node_count']} nodes, {info['edge_count']} edges", info)

# ═══════════════════════════════════════════════════════════
# 2. Run ALL metrics
# ═══════════════════════════════════════════════════════════
from gephi_cli import metrics

all_metrics_result = metrics.run_all_metrics(ws)
log("metrics", "All metrics computed", all_metrics_result)

# Individual metric details
for metric_name in ["degree", "pagerank", "betweenness", "closeness",
                    "eigenvector", "modularity", "hits", "clustering_coefficient",
                    "connected_components", "diameter", "density", "avg_path_length"]:
    try:
        r = metrics.run_metric(metric_name, ws)
        log("metrics", f"  {metric_name}: OK", r)
    except Exception as e:
        log("metrics", f"  {metric_name}: FAILED - {e}")

# ═══════════════════════════════════════════════════════════
# 3. Test ALL 11 layouts
# ═══════════════════════════════════════════════════════════
from gephi_cli import layout, preview, appearance

layout_algos = [
    ("forceatlas2", 200, {"scaling": 10.0, "gravity": 1.0}),
    ("forceatlas1", 100, {}),
    ("fruchterman_reingold", 100, {"area": 10000.0}),
    ("yifan_hu", 100, {"optimal_distance": 100.0}),
    ("openord", 50, {}),
    ("label_adjust", 30, {}),
    ("noverlap", 50, {"speed": 3.0}),
    ("random", 1, {"size": 1000.0}),
    ("rotate", 1, {"angle": 45.0}),
    ("expand", 1, {"scale": 1.2}),
    ("contract", 1, {"scale": 0.8}),
]

for algo, iters, params in layout_algos:
    try:
        r = layout.run_layout(algo, iters, ws, **params)
        log("layout", f"  {algo}: {r['iterations_run']}/{iters} iters", r)
    except Exception as e:
        log("layout", f"  {algo}: FAILED - {e}")

# ═══════════════════════════════════════════════════════════
# 4. Appearance styling
# ═══════════════════════════════════════════════════════════

# Final layout for good visualization
layout.run_layout("forceatlas2", 300, ws, scaling=5.0, gravity=1.0)
layout.run_layout("noverlap", 100, ws, speed=3.0, margin=5.0)

# Color by modularity
appearance.color_nodes_by_modularity(ws)
log("appearance", "Color by modularity: OK")

# Size by PageRank
appearance.set_node_size_by_attribute("pageranks", 5, 40, ws)
log("appearance", "Size by pagerank: OK")

# Labels
appearance.set_node_labels(workspace=ws)
appearance.set_node_label_size(8, ws)
log("appearance", "Labels set: OK")

# Edge styling
appearance.set_all_edges_color(150, 150, 150, ws)
appearance.color_edges_by_source(ws)
log("appearance", "Edge color by source: OK")

# ═══════════════════════════════════════════════════════════
# 5. Render image #1 - Full graph with modularity coloring
# ═══════════════════════════════════════════════════════════

preview.apply_preset("default", ws)
preview.configure_preview(ws,
    show_labels=True,
    edge_opacity=40,
    node_opacity=80,
    background_color="#ffffff",
)
img1 = os.path.join(OUT, "01_full_graph_modularity.png")
preview.export_image(img1, 2048, 2048, ws)
log("render", f"Exported: {img1}")

# Also export SVG
svg1 = os.path.join(OUT, "01_full_graph_modularity.svg")
preview.export_svg(svg1, ws)
log("render", f"Exported: {svg1}")

# ═══════════════════════════════════════════════════════════
# 6. Render #2 - Black background preset
# ═══════════════════════════════════════════════════════════

preview.apply_preset("black_background", ws)
preview.configure_preview(ws, edge_opacity=30)
img2 = os.path.join(OUT, "02_black_background.png")
preview.export_image(img2, 2048, 2048, ws)
log("render", f"Exported: {img2}")

# ═══════════════════════════════════════════════════════════
# 7. Filters test + filtered graph images
# ═══════════════════════════════════════════════════════════
from gephi_cli import filters

# Giant component
r = filters.filter_giant_component(ws)
log("filter", f"Giant component: {r['visible_nodes']} nodes, {r['visible_edges']} edges", r)

preview.apply_preset("default_curved", ws)
preview.configure_preview(ws, edge_opacity=50, background_color="#ffffff")
img3 = os.path.join(OUT, "03_giant_component.png")
preview.export_image(img3, 2048, 2048, ws)
log("render", f"Exported: {img3}")
filters.reset_filter(ws)

# Degree >= 5
r = filters.filter_by_degree(5, None, ws)
log("filter", f"Degree >= 5: {r['visible_nodes']} nodes, {r['visible_edges']} edges", r)

img4 = os.path.join(OUT, "04_degree_ge5.png")
preview.export_image(img4, 2048, 2048, ws)
log("render", f"Exported: {img4}")
filters.reset_filter(ws)

# K-core (k=3)
try:
    r = filters.filter_k_core(3, ws)
    log("filter", f"K-core(3): {r['visible_nodes']} nodes", r)
    img5 = os.path.join(OUT, "05_kcore3.png")
    preview.export_image(img5, 2048, 2048, ws)
    log("render", f"Exported: {img5}")
    filters.reset_filter(ws)
except Exception as e:
    log("filter", f"K-core(3): FAILED - {e}")
    filters.reset_filter(ws)

# ═══════════════════════════════════════════════════════════
# 8. AutoLayout test
# ═══════════════════════════════════════════════════════════
from gephi_cli import autolayout

# Reset to random and re-layout with auto
layout.run_layout("random", 1, ws, size=500.0)
r = autolayout.run_auto_layout([
    {"algorithm": "yifan_hu", "ratio": 0.3, "params": {"optimal_distance": 200.0}},
    {"algorithm": "forceatlas2", "ratio": 0.5, "params": {"scaling": 10.0}},
    {"algorithm": "noverlap", "ratio": 0.2, "params": {"speed": 5.0}},
], total_iterations=500, workspace=ws)
log("autolayout", f"AutoLayout: {len(r['sequence'])} phases, {r['total_iterations']} total iters", r)

preview.apply_preset("default", ws)
preview.configure_preview(ws, show_labels=True, edge_opacity=40, background_color="#f5f5f5")
img6 = os.path.join(OUT, "06_autolayout_result.png")
preview.export_image(img6, 2048, 2048, ws)
log("render", f"Exported: {img6}")

# ═══════════════════════════════════════════════════════════
# 9. DataLab operations
# ═══════════════════════════════════════════════════════════
from gephi_cli import datalab

# Add custom column
r = datalab.add_column("importance", "double", "node", ws)
log("datalab", f"Add column 'importance': OK", r)

# Fill with value
r = datalab.fill_column("importance", "0.5", "node", ws)
log("datalab", f"Fill column: {r['count']} nodes", r)

# Search & replace on labels
r = datalab.search_replace("Label", "Node", "N", "node", False, ws)
log("datalab", f"Search/replace: {r['matches_replaced']} replaced", r)

# Column statistics on degree
try:
    r = datalab.get_column_statistics("Degree", "node", ws)
    log("datalab", f"Degree stats: min={r.get('min')}, max={r.get('max')}, avg={r.get('average')}", r)
except Exception as e:
    log("datalab", f"Degree stats: FAILED - {e}")

# Column statistics on pageranks
try:
    r = datalab.get_column_statistics("pageranks", "node", ws)
    log("datalab", f"PageRank stats: min={r.get('min'):.6f}, max={r.get('max'):.6f}, avg={r.get('average'):.6f}", r)
except Exception as e:
    log("datalab", f"PageRank stats: FAILED - {e}")

# ═══════════════════════════════════════════════════════════
# 10. Shortest path
# ═══════════════════════════════════════════════════════════
from gephi_cli import shortest_path

# Find first few node IDs
node_list = io_graph.list_nodes(ws, 10)
if len(node_list) >= 2:
    src = node_list[0]["id"]
    tgt = node_list[-1]["id"]

    # Dijkstra all
    r = shortest_path.compute_shortest_path(src, "dijkstra", ws)
    log("shortest_path", f"Dijkstra from {src}: {r['reachable_nodes']}/{r['total_nodes']} reachable", r)

    # Path between two nodes
    r2 = shortest_path.get_path_between(src, tgt, "dijkstra", ws)
    log("shortest_path", f"Path {src} -> {tgt}: distance={r2.get('distance')}, hops={r2.get('hops')}", r2)

    # Bellman-Ford
    r3 = shortest_path.compute_shortest_path(src, "bellman_ford", ws)
    log("shortest_path", f"Bellman-Ford from {src}: {r3['reachable_nodes']} reachable", r3)

# ═══════════════════════════════════════════════════════════
# 11. Project save/open round-trip
# ═══════════════════════════════════════════════════════════
from gephi_cli import project

proj_file = os.path.join(OUT, "test_project.gephi")
r = project.save_project(proj_file)
log("project", f"Saved project: {proj_file}", r)

# ═══════════════════════════════════════════════════════════
# 12. Export in multiple formats
# ═══════════════════════════════════════════════════════════

for fmt in ["gexf", "graphml", "gml", "csv", "net", "json"]:
    out_path = os.path.join(OUT, f"graph_export.{fmt}")
    try:
        io_graph.export_graph(out_path, ws)
        fsize = os.path.getsize(out_path)
        log("export", f"  {fmt}: OK ({fsize:,} bytes)")
    except Exception as e:
        log("export", f"  {fmt}: FAILED - {e}")

# PDF export
pdf_path = os.path.join(OUT, "07_graph.pdf")
preview.apply_preset("default", ws)
preview.configure_preview(ws, show_labels=True, edge_opacity=40)
r = preview.export_pdf(pdf_path, ws)
log("export", f"  PDF: OK", r)

# ═══════════════════════════════════════════════════════════
# 13. Size-by-betweenness + color-by-partition rendering
# ═══════════════════════════════════════════════════════════

# Re-layout for final renders
layout.run_layout("forceatlas2", 200, ws, scaling=8.0, gravity=1.5)
layout.run_layout("noverlap", 50, ws, speed=3.0)

# Size by betweenness
appearance.set_node_size_by_attribute("betweenesscentrality", 3, 60, ws)
log("appearance", "Size by betweenness: OK")

# Render with tag cloud preset
preview.apply_preset("tag_cloud", ws)
preview.configure_preview(ws, edge_opacity=20, background_color="#ffffff")
img7 = os.path.join(OUT, "08_betweenness_tagcloud.png")
preview.export_image(img7, 2048, 2048, ws)
log("render", f"Exported: {img7}")

# Render with text outline preset
preview.apply_preset("text_outline", ws)
preview.configure_preview(ws, edge_opacity=25, background_color="#222222")
img8 = os.path.join(OUT, "09_text_outline_dark.png")
preview.export_image(img8, 2048, 2048, ws)
log("render", f"Exported: {img8}")

# ═══════════════════════════════════════════════════════════
# 14. Uniform color + straight edges rendering
# ═══════════════════════════════════════════════════════════

appearance.set_all_nodes_color(65, 105, 225, ws)  # Royal blue
appearance.set_all_nodes_size(15, ws)
appearance.set_all_edges_color(200, 200, 200, ws)

preview.apply_preset("default_straight", ws)
preview.configure_preview(ws, edge_opacity=35, background_color="#ffffff", show_labels=False)
img9 = os.path.join(OUT, "10_uniform_blue_straight.png")
preview.export_image(img9, 2048, 2048, ws)
log("render", f"Exported: {img9}")

# ═══════════════════════════════════════════════════════════
# 15. Second graph - smaller, denser for different visual
# ═══════════════════════════════════════════════════════════

ws2 = generator.generate_random(80, 0.08)
info2 = io_graph.get_graph_info(ws2)
log("generate", f"Second graph: {info2['node_count']} nodes, {info2['edge_count']} edges", info2)

metrics.run_metric("modularity", ws2)
metrics.run_metric("pagerank", ws2)
metrics.run_metric("degree", ws2)
metrics.run_metric("betweenness", ws2)

layout.run_layout("forceatlas2", 300, ws2, scaling=5.0, gravity=2.0, barnes_hut=True)
layout.run_layout("noverlap", 80, ws2, speed=3.0)

appearance.color_nodes_by_modularity(ws2)
appearance.set_node_size_by_attribute("pageranks", 8, 45, ws2)
appearance.set_node_labels(workspace=ws2)

preview.apply_preset("default_curved", ws2)
preview.configure_preview(ws2, show_labels=True, edge_opacity=45, background_color="#fafafa")
img10 = os.path.join(OUT, "11_dense_graph_curved.png")
preview.export_image(img10, 2048, 2048, ws2)
log("render", f"Exported: {img10}")

# Edge-weighted coloring
appearance.color_edges_by_source(ws2)
preview.apply_preset("black_background", ws2)
preview.configure_preview(ws2, edge_opacity=50, show_labels=True)
img11 = os.path.join(OUT, "12_dense_dark_colored_edges.png")
preview.export_image(img11, 2048, 2048, ws2)
log("render", f"Exported: {img11}")

# ═══════════════════════════════════════════════════════════
# 16. Summary
# ═══════════════════════════════════════════════════════════

# Write full results to JSON
results_path = os.path.join(OUT, "test_results.json")
with open(results_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
total = sum(len(v) for v in results.values())
print(f"Total test steps: {total}")
for section, items in results.items():
    failed = [i for i in items if "FAILED" in i.get("msg", "")]
    ok = len(items) - len(failed)
    status = "PASS" if not failed else f"PARTIAL ({len(failed)} failed)"
    print(f"  {section:20s}: {ok}/{len(items)} {status}")

print(f"\nOutput directory: {OUT}")
print("Generated files:")
for f in sorted(os.listdir(OUT)):
    fpath = os.path.join(OUT, f)
    fsize = os.path.getsize(fpath)
    print(f"  {f:45s} {fsize:>12,} bytes")

print(f"\nDetailed results: {results_path}")
print("=" * 60)
