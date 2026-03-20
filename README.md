# gephiRpy

Python and R interface to Gephi graph analysis toolkit. Provides **CLI**, **Python API**, and **R API** for graph import/export, layout, metrics, filtering, styling, and visualization.

## Tutorials

- **Python 教程 (Jupyter Notebook)**: [tutorial_python.html](tutorials/tutorial_python.html) | [tutorial_python.ipynb](tutorials/tutorial_python.ipynb)
- **R 教程 (RMarkdown)**: [tutorial_R.html](tutorials/tutorial_R.html) | [tutorial_R.Rmd](tutorials/tutorial_R.Rmd)

## Requirements

- Python >= 3.10
- Java >= 11 (JDK or JRE)

## Installation

### Python

```bash
# From GitHub
pip install git+https://github.com/YRD666/gephiRpy.git

# From local clone
git clone https://github.com/YRD666/gephiRpy.git
cd gephiRpy
pip install -e .

# With optional dependencies
pip install -e ".[all]"       # NetworkX + pandas + numpy
pip install -e ".[networkx]"  # NetworkX only
pip install -e ".[pandas]"    # pandas only
```

### R

```r
# Install from GitHub (requires devtools)
install.packages("devtools")
devtools::install_github("YRD666/gephiRpy", subdir = "gephir")

# Or from local clone
devtools::install_local("gephir")
```

**Note:** The R package (`gephir`) requires the Python package (`gephi-cli`) to be installed first.

### Download gephi-toolkit JAR

```bash
python download_toolkit.py
```

Or manually download from [gephi-toolkit releases](https://github.com/gephi/gephi-toolkit/releases) and place in `lib/`.

## Python API Usage

### Basic workflow

```python
from gephi_cli import io_graph, layout, metrics, preview

# Import
ws = io_graph.import_graph("network.gexf")

# Layout
layout.run_layout("forceatlas2", workspace=ws, duration=10)
layout.normalize_layout(ws)

# Metrics
r = metrics.run_metric("modularity", ws)
print(f"Modularity: {r['modularity_score']}")

# Export
io_graph.export_graph("output.gexf", ws)
preview.export_image("output.png", 2048, 2048, ws)
```

### Generate graphs

```python
from gephi_cli import generator

# 11 types available
ws = generator.generate("random", node_count=100, wiring_prob=0.05)
ws = generator.generate("scale_free", node_count=500, m=3)
ws = generator.generate("small_world", node_count=200, k=6, beta=0.3)
ws = generator.generate("complete", node_count=20)
ws = generator.generate("star", node_count=50)
ws = generator.generate("ring", node_count=30)
ws = generator.generate("grid", rows=10, cols=10)
ws = generator.generate("tree", depth=5, branching=3)
ws = generator.generate("path", node_count=20)
ws = generator.generate("empty", node_count=10)
```

### Import from Python data structures

```python
from gephi_cli import io_graph

# From edge list
ws = io_graph.import_from_edge_list([
    ("Alice", "Bob", 2.0),
    ("Bob", "Charlie"),
    {"source": "Charlie", "target": "Alice", "weight": 1.5},
])

# From URL
ws = io_graph.import_from_url("https://example.com/network.gexf")

# From string
ws = io_graph.import_from_string(gexf_xml_string, format="gexf")

# From adjacency matrix
ws = io_graph.import_from_adjacency_matrix(
    [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
    node_labels=["A", "B", "C"]
)
```

### NetworkX interop

```python
import networkx as nx
from gephi_cli import io_graph

# NetworkX -> Gephi
G = nx.karate_club_graph()
ws = io_graph.import_from_networkx(G)

# Gephi -> NetworkX
G2 = io_graph.export_to_networkx(ws)
```

### pandas interop

```python
import pandas as pd
from gephi_cli import io_graph

# DataFrame -> Gephi
df = pd.DataFrame({"source": ["A","B","C"], "target": ["B","C","A"], "weight": [1,2,3]})
ws = io_graph.import_from_pandas(df)

# Gephi -> DataFrame
edges_df, nodes_df = io_graph.export_to_pandas(ws)
```

### Metrics

```python
from gephi_cli import metrics

# Single metric
r = metrics.run_metric("pagerank", ws)
r = metrics.run_metric("modularity", ws, resolution=1.5)
r = metrics.run_metric("betweenness", ws)

# All metrics at once
results = metrics.run_all_metrics(ws)
```

### Filters

```python
from gephi_cli import filters

filters.filter_by_degree(min_val=3, workspace=ws)
filters.filter_giant_component(ws)
filters.filter_k_core(5, ws)
filters.filter_by_attribute("category", "tech", ws)
filters.reset_filter(ws)
```

### Appearance / Styling

```python
from gephi_cli import appearance

appearance.color_nodes_by_modularity(ws)
appearance.set_node_size_by_attribute("pageranks", 10, 50, ws)
appearance.set_node_labels("Label", ws)
appearance.set_all_edges_color(180, 180, 180, ws)
```

### Preview & Export

```python
from gephi_cli import preview

preview.apply_preset("black_background", ws)
preview.configure_preview(ws, show_labels=True, edge_opacity=30)
preview.export_image("graph.png", 4096, 4096, ws)
preview.export_pdf("graph.pdf", ws)
preview.export_svg("graph.svg", ws)
```

### Graph validation

```python
from gephi_cli import io_graph

report = io_graph.validate_graph(ws)
# {'node_count': 100, 'edge_count': 245, 'density': 0.049,
#  'isolated_nodes': 3, 'self_loops': 0, 'degree_min': 0, ...}
```

### YAML Pipeline

```python
from gephi_cli import pipeline

results = pipeline.run_pipeline("workflow.yaml")
```

```yaml
# workflow.yaml
steps:
  - action: generate
    type: scale_free
    nodes: 500
    m: 3
  - action: layout
    algorithm: forceatlas2
    duration: 10
  - action: metric
    name: modularity
  - action: appearance
    type: color_by_modularity
  - action: export
    file: output.png
    width: 2048
    height: 2048
```

## R Usage

### Setup

```r
# Install gephir package (see Installation section above)
library(gephir)
gephi_init()  # or: gephi_init(python = "/path/to/python")
```

### Basic workflow

```r
# Import
ws <- gephi_import("network.gexf")

# Layout + Normalize
gephi_layout(ws, "forceatlas2", duration = 10)
gephi_normalize(ws)

# Metrics
r <- gephi_metric(ws, "modularity")
cat("Modularity:", r$modularity_score, "\n")

# Style
gephi_color_modularity(ws)
gephi_size_by(ws, "pageranks", min_size = 10, max_size = 50)

# Export
gephi_export_image(ws, "output.png", width = 2048, height = 2048)
```

### From R data structures

```r
# From data.frame
edges <- data.frame(source = c("A","B","C"), target = c("B","C","A"), weight = c(1,2,3))
ws <- gephi_import_df(edges)

# From adjacency matrix
mat <- matrix(c(0,1,0, 1,0,1, 0,1,0), nrow = 3)
ws <- gephi_import_matrix(mat, labels = c("X", "Y", "Z"))

# From igraph
library(igraph)
g <- sample_gnp(100, 0.05)
ws <- gephi_import_igraph(g)

# Export back to igraph
g2 <- gephi_to_igraph(ws)

# Export to data.frames
dfs <- gephi_to_df(ws)
head(dfs$edges)
head(dfs$nodes)
```

### Generate graphs

```r
ws <- gephi_generate("scale_free", node_count = 500, m = 3)
ws <- gephi_generate("small_world", node_count = 200, k = 6, beta = 0.3)
ws <- gephi_generate("grid", rows = 10, cols = 10)
```

### One-line quick visualization

```r
# From file
gephi_quick("network.gexf", "output.png")

# From data.frame
gephi_quick(edges_df, "output.png", duration = 10, width = 4096, height = 4096)

# From igraph
gephi_quick(g, "output.pdf", algorithm = "yifan_hu", preset = "black_background")
```

## CLI Usage

```bash
gephi-cli import network.gexf
gephi-cli layout network.gexf forceatlas2 -d 10 -o laid_out.gexf
gephi-cli metric network.gexf modularity -o enriched.gexf
gephi-cli render network.gexf output.png -w 2048 -h 2048
gephi-cli generate scale_free output.gexf -n 500 --m 3
gephi-cli validate network.gexf
gephi-cli list layouts
gephi-cli pipeline workflow.yaml
```

## Features

- **14 CLI commands** - import, export, convert, info, layout, autolayout, metric, dynamic-metric, filter, style, render, shortest-path, generate, validate, pipeline, datalab, project, list
- **11 layout algorithms** - ForceAtlas2, ForceAtlas1, Fruchterman-Reingold, Yifan Hu, OpenOrd, Label Adjust, Noverlap, Random, Rotate, Expand, Contract
- **15+ metrics** - Degree, PageRank, Betweenness, Modularity, Eigenvector, HITS, Clustering Coefficient, etc.
- **17 filters** - Degree range, Giant component, K-core, Ego, Attribute filters, etc.
- **11 graph generators** - Random, Scale-free, Small-world, Complete, Star, Ring, Grid, Tree, Path, Empty, Dynamic
- **10+ file formats** - GEXF, GraphML, GML, CSV, Pajek, DOT, GDF, JSON, etc.
- **Python data interop** - NetworkX, pandas, numpy, edge lists, adjacency matrices, URL import
- **R language support** - igraph interop, data.frame, matrix, one-line `gephi_quick()`
- **Graph validation** - Structural quality reports
- **YAML pipelines** - Multi-step automated workflows
