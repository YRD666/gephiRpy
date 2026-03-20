"""
gephi-cli Python 完整使用教程
===============================

本教程演示 gephi-cli 的所有功能模块：
  1. 图生成 (11种)
  2. 图导入 (文件、边列表、邻接矩阵、字符串、URL、NetworkX、pandas)
  3. 图导出 (文件、NetworkX、pandas)
  4. 图信息与验证
  5. 布局算法 (11种 + 归一化 + 自动布局)
  6. 图指标 (15种)
  7. 过滤器 (17种)
  8. 外观样式 (节点颜色/大小/标签、边样式)
  9. 预览与图片导出 (PNG/PDF/SVG + 预设)
  10. 数据实验室 (节点/边CRUD、列操作、搜索替换)
  11. 最短路径
  12. 项目与工作区管理
  13. YAML 流水线

运行前请确保：
  pip install -e ".[all]"
  python download_toolkit.py
"""

import os

OUTPUT_DIR = "tutorial_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# 1. 图生成 - 11 种生成器
# ============================================================================
print("=" * 60)
print("1. 图生成 (Graph Generation)")
print("=" * 60)

from gephi_cli import generator, io_graph

# 1.1 随机图 (Erdos-Renyi)
ws = generator.generate("random", node_count=100, wiring_prob=0.05)
info = io_graph.get_graph_info(ws)
print(f"随机图: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.2 无标度网络 (Barabasi-Albert)
ws = generator.generate("scale_free", node_count=200, m=3)
info = io_graph.get_graph_info(ws)
print(f"无标度网络: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.3 小世界网络 (Watts-Strogatz)
ws = generator.generate("small_world", node_count=100, k=6, beta=0.3)
info = io_graph.get_graph_info(ws)
print(f"小世界网络: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.4 完全图
ws = generator.generate("complete", node_count=15)
info = io_graph.get_graph_info(ws)
print(f"完全图: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.5 星形图
ws = generator.generate("star", node_count=20)
info = io_graph.get_graph_info(ws)
print(f"星形图: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.6 环形图
ws = generator.generate("ring", node_count=20)
info = io_graph.get_graph_info(ws)
print(f"环形图: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.7 网格图
ws = generator.generate("grid", rows=8, cols=8)
info = io_graph.get_graph_info(ws)
print(f"网格图: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.8 树形图
ws = generator.generate("tree", depth=4, branching=3)
info = io_graph.get_graph_info(ws)
print(f"树形图: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.9 路径图
ws = generator.generate("path", node_count=15)
info = io_graph.get_graph_info(ws)
print(f"路径图: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.10 空图
ws = generator.generate("empty", node_count=10)
info = io_graph.get_graph_info(ws)
print(f"空图: {info['node_count']} 节点, {info['edge_count']} 边")

# 1.11 动态图 (带时间戳)
ws = generator.generate("dynamic")
info = io_graph.get_graph_info(ws)
print(f"动态图: {info['node_count']} 节点, {info['edge_count']} 边")

# 可以传入 seed 参数确保可复现
ws = generator.generate("scale_free", node_count=50, m=2, seed=42)
print("指定随机种子: seed=42")


# ============================================================================
# 2. 图导入 - 7 种导入方式
# ============================================================================
print("\n" + "=" * 60)
print("2. 图导入 (Graph Import)")
print("=" * 60)

# 2.1 从边列表导入
# 支持 tuple、list、dict 三种格式混合使用
ws = io_graph.import_from_edge_list([
    ("Alice", "Bob", 2.0),           # tuple: (source, target, weight)
    ("Bob", "Charlie"),              # tuple: (source, target), 默认 weight=1
    ["Charlie", "David", 1.5],       # list 也行
    {"source": "David", "target": "Alice", "weight": 3.0},  # dict 格式
])
info = io_graph.get_graph_info(ws)
print(f"边列表导入: {info['node_count']} 节点, {info['edge_count']} 边")

# 2.2 从邻接矩阵导入
matrix = [
    [0, 1, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 1, 0],
]
ws = io_graph.import_from_adjacency_matrix(
    matrix,
    node_labels=["北京", "上海", "广州", "深圳"],
    directed=False
)
info = io_graph.get_graph_info(ws)
print(f"邻接矩阵导入: {info['node_count']} 节点, {info['edge_count']} 边")

# 2.3 从 GEXF 字符串导入
gexf_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
  <graph defaultedgetype="undirected">
    <nodes>
      <node id="0" label="Alpha"/>
      <node id="1" label="Beta"/>
      <node id="2" label="Gamma"/>
    </nodes>
    <edges>
      <edge id="0" source="0" target="1" weight="1.0"/>
      <edge id="1" source="1" target="2" weight="2.0"/>
      <edge id="2" source="2" target="0" weight="0.5"/>
    </edges>
  </graph>
</gexf>'''
ws = io_graph.import_from_string(gexf_xml, format="gexf")
info = io_graph.get_graph_info(ws)
print(f"字符串导入: {info['node_count']} 节点, {info['edge_count']} 边")

# 2.4 从 pandas DataFrame 导入
try:
    import pandas as pd

    edges_df = pd.DataFrame({
        "source": ["A", "B", "C", "D", "E"],
        "target": ["B", "C", "D", "E", "A"],
        "weight": [1.0, 2.0, 1.5, 3.0, 0.5],
        "type":   ["friend", "colleague", "friend", "colleague", "friend"],
    })
    ws = io_graph.import_from_pandas(
        edges_df,
        source_col="source",
        target_col="target",
        weight_col="weight"
    )
    info = io_graph.get_graph_info(ws)
    print(f"pandas 导入: {info['node_count']} 节点, {info['edge_count']} 边")
except ImportError:
    print("pandas 未安装，跳过")

# 2.5 从 NetworkX 导入
try:
    import networkx as nx

    G = nx.karate_club_graph()
    ws = io_graph.import_from_networkx(G)
    info = io_graph.get_graph_info(ws)
    print(f"NetworkX 导入 (空手道俱乐部): {info['node_count']} 节点, {info['edge_count']} 边")
except ImportError:
    print("NetworkX 未安装，跳过")

# 2.6 从文件导入 (先导出再导入)
ws_gen = generator.generate("scale_free", node_count=50, m=2)
io_graph.export_graph(f"{OUTPUT_DIR}/sample.gexf", ws_gen)
ws = io_graph.import_graph(f"{OUTPUT_DIR}/sample.gexf")
info = io_graph.get_graph_info(ws)
print(f"文件导入 (GEXF): {info['node_count']} 节点, {info['edge_count']} 边")

# 2.7 查看支持的格式
formats_in = io_graph.list_import_formats()
formats_out = io_graph.list_export_formats()
print(f"支持导入格式: {len(formats_in)} 种")
print(f"支持导出格式: {len(formats_out)} 种")


# ============================================================================
# 3. 图导出 - 文件 + 数据结构
# ============================================================================
print("\n" + "=" * 60)
print("3. 图导出 (Graph Export)")
print("=" * 60)

ws = generator.generate("scale_free", node_count=30, m=2)

# 3.1 导出为多种文件格式
for fmt in ["gexf", "graphml", "csv", "gml"]:
    path = f"{OUTPUT_DIR}/export_demo.{fmt}"
    io_graph.export_graph(path, ws)
    size = os.path.getsize(path)
    print(f"导出 {fmt.upper()}: {size} 字节")

# 3.2 导出到 NetworkX
try:
    G = io_graph.export_to_networkx(ws)
    print(f"导出 NetworkX: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
except ImportError:
    print("NetworkX 未安装，跳过")

# 3.3 导出到 pandas DataFrame
try:
    edges_df, nodes_df = io_graph.export_to_pandas(ws)
    print(f"导出 pandas: edges={len(edges_df)}, nodes={len(nodes_df)}")
    print(f"  边表列: {list(edges_df.columns)}")
    print(f"  节点表列: {list(nodes_df.columns)}")
except ImportError:
    print("pandas 未安装，跳过")


# ============================================================================
# 4. 图信息与验证
# ============================================================================
print("\n" + "=" * 60)
print("4. 图信息与验证 (Graph Info & Validation)")
print("=" * 60)

ws = generator.generate("scale_free", node_count=100, m=2)

# 4.1 基本信息
info = io_graph.get_graph_info(ws)
print("图信息:")
for k, v in info.items():
    print(f"  {k}: {v}")

# 4.2 验证报告
report = io_graph.validate_graph(ws)
print("\n验证报告:")
for k, v in report.items():
    print(f"  {k}: {v}")

# 4.3 查看节点列表
nodes = io_graph.list_nodes(ws, limit=5)
print(f"\n前 5 个节点:")
for n in nodes:
    print(f"  {n}")

# 4.4 查看边列表
edges = io_graph.list_edges(ws, limit=5)
print(f"\n前 5 条边:")
for e in edges:
    print(f"  {e}")


# ============================================================================
# 5. 布局算法 - 11种 + 归一化 + 自动布局
# ============================================================================
print("\n" + "=" * 60)
print("5. 布局算法 (Layout Algorithms)")
print("=" * 60)

from gephi_cli import layout

ws = generator.generate("scale_free", node_count=100, m=2)

# 5.1 列出所有布局
layouts = layout.list_layouts()
print(f"可用布局算法: {len(layouts)} 种")
for name, desc in layouts.items():
    print(f"  {name}: {desc}")

# 5.2 ForceAtlas2 - 迭代模式
r = layout.run_layout("forceatlas2", iterations=100, workspace=ws)
print(f"\nForceAtlas2 (迭代): {r['iterations_run']} 次迭代")

# 5.3 ForceAtlas2 - 持续时间模式
r = layout.run_layout("forceatlas2", workspace=ws, duration=3)
print(f"ForceAtlas2 (3秒): {r['iterations_run']} 次迭代, {r['duration_seconds']:.1f}s")

# 5.4 其他力导向布局
r = layout.run_layout("fruchterman_reingold", iterations=50, workspace=ws)
print(f"Fruchterman-Reingold: {r['iterations_run']} 次迭代")

r = layout.run_layout("yifan_hu", iterations=50, workspace=ws)
print(f"Yifan Hu: {r['iterations_run']} 次迭代")

r = layout.run_layout("forceatlas1", iterations=50, workspace=ws)
print(f"ForceAtlas1: {r['iterations_run']} 次迭代")

r = layout.run_layout("openord", iterations=10, workspace=ws)
print(f"OpenOrd: {r['iterations_run']} 次迭代")

# 5.5 调整类布局
r = layout.run_layout("label_adjust", iterations=10, workspace=ws)
print(f"Label Adjust: {r['iterations_run']} 次迭代")

r = layout.run_layout("noverlap", iterations=10, workspace=ws)
print(f"Noverlap: {r['iterations_run']} 次迭代")

# 5.6 变换类布局
r = layout.run_layout("random", iterations=1, workspace=ws)
print(f"Random: 随机放置")

r = layout.run_layout("rotate", iterations=1, workspace=ws, angle=45.0)
print(f"Rotate: 旋转 45 度")

r = layout.run_layout("expand", iterations=1, workspace=ws)
print(f"Expand: 扩展")

r = layout.run_layout("contract", iterations=1, workspace=ws)
print(f"Contract: 收缩")

# 5.7 归一化坐标
r = layout.normalize_layout(ws, scale=1000)
print(f"归一化: 缩放因子={r['scale_factor']:.2f}, 原始范围={r['original_range']:.1f}")

# 5.8 自动布局 (多步骤序列)
from gephi_cli import autolayout

ws = generator.generate("scale_free", node_count=80, m=2)
sequence = [
    {"algorithm": "forceatlas2", "ratio": 0.7},   # 70% 时间用 FA2
    {"algorithm": "noverlap", "ratio": 0.3},       # 30% 时间去重叠
]
r = autolayout.run_auto_layout(sequence, total_duration=3, workspace=ws)
print(f"\n自动布局 (2步序列):")
for step in r["sequence"]:
    print(f"  {step['algorithm']}: {step['iterations_run']} 次迭代")


# ============================================================================
# 6. 图指标 - 15种
# ============================================================================
print("\n" + "=" * 60)
print("6. 图指标 (Graph Metrics)")
print("=" * 60)

from gephi_cli import metrics

ws = generator.generate("scale_free", node_count=100, m=2)

# 6.1 列出所有指标
ml = metrics.list_metrics()
print(f"可用指标: {len(ml)} 种")
for name, desc in ml.items():
    print(f"  {name}: {desc}")

# 6.2 逐个运行重要指标
print("\n--- 度 (Degree) ---")
r = metrics.run_metric("degree", ws)
print(f"  平均度: {r['average_degree']}")

print("\n--- 加权度 (Weighted Degree) ---")
r = metrics.run_metric("weighted_degree", ws)
print(f"  平均加权度: {r['average_weighted_degree']}")

print("\n--- PageRank ---")
r = metrics.run_metric("pagerank", ws)
print(f"  结果: {r['metric']} 计算完成")

print("\n--- 介数中心性 (Betweenness) ---")
r = metrics.run_metric("betweenness", ws)
print(f"  直径: {r['diameter']}, 半径: {r['radius']}")
print(f"  平均路径长度: {r['avg_path_length']}")

print("\n--- 接近中心性 (Closeness) ---")
r = metrics.run_metric("closeness", ws)
print(f"  直径: {r['diameter']}")

print("\n--- 特征向量中心性 (Eigenvector) ---")
r = metrics.run_metric("eigenvector", ws)
print(f"  迭代次数: {r['iterations']}")

print("\n--- 模块度 (Modularity) ---")
r = metrics.run_metric("modularity", ws)
print(f"  模块度: {r['modularity_score']}")

print("\n--- 模块度 (Modularity) 自定义分辨率 ---")
r = metrics.run_metric("modularity", ws, resolution=2.0)
print(f"  模块度 (resolution=2.0): {r['modularity_score']}")

print("\n--- HITS ---")
r = metrics.run_metric("hits", ws)
print(f"  HITS 计算完成")

print("\n--- 聚类系数 (Clustering Coefficient) ---")
r = metrics.run_metric("clustering_coefficient", ws)
print(f"  平均聚类系数: {r['avg_clustering_coefficient']}")

print("\n--- 连通分量 (Connected Components) ---")
r = metrics.run_metric("connected_components", ws)
print(f"  分量数: {r['component_count']}")

print("\n--- 直径 (Diameter) ---")
r = metrics.run_metric("diameter", ws)
print(f"  直径: {r['diameter']}, 半径: {r['radius']}")

print("\n--- 密度 (Density) ---")
r = metrics.run_metric("density", ws)
print(f"  密度: {r['density']}")

print("\n--- 离心率 (Eccentricity) ---")
r = metrics.run_metric("eccentricity", ws)
print(f"  直径: {r['diameter']}")

print("\n--- 平均路径长度 ---")
r = metrics.run_metric("avg_path_length", ws)
print(f"  平均路径长度: {r['avg_path_length']}")

# 6.3 一次运行所有指标
all_results = metrics.run_all_metrics(ws)
print(f"\n一次运行全部: {len(all_results)} 个指标")
for name, result in all_results.items():
    keys = list(result.keys())[:2]
    print(f"  {name}: {keys}...")


# ============================================================================
# 7. 过滤器 - 17种
# ============================================================================
print("\n" + "=" * 60)
print("7. 过滤器 (Filters)")
print("=" * 60)

from gephi_cli import filters

ws = generator.generate("scale_free", node_count=100, m=2)
metrics.run_metric("degree", ws)
metrics.run_metric("modularity", ws)

# 7.1 列出所有过滤器
fl = filters.list_filters()
print(f"可用过滤器: {len(fl)} 种")

# 7.2 度过滤
r = filters.filter_by_degree(min_val=3, workspace=ws)
print(f"\n度过滤 (degree >= 3): {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.3 度范围过滤
r = filters.filter_by_degree(min_val=2, max_val=10, workspace=ws)
print(f"度范围 (2-10): {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.4 入度过滤 (有向图)
r = filters.filter_by_in_degree(min_val=1, workspace=ws)
print(f"入度 >= 1: {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.5 出度过滤
r = filters.filter_by_out_degree(min_val=1, workspace=ws)
print(f"出度 >= 1: {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.6 巨分量
r = filters.filter_giant_component(ws)
print(f"巨分量: {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.7 K-核
r = filters.filter_k_core(2, ws)
print(f"2-核: {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.8 自我网络
r = filters.filter_ego("0", depth=1, workspace=ws)
print(f"自我网络 (节点0, 深度1): {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.9 自环过滤
r = filters.filter_has_self_loop(ws)
print(f"有自环的节点: {r['visible_nodes']} 节点")
filters.reset_filter(ws)

# 7.10 边权重过滤
r = filters.filter_edge_weight(min_val=0.5, workspace=ws)
print(f"边权重 >= 0.5: {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.11 属性过滤 (使用 modularity_class)
r = filters.filter_by_attribute("modularity_class", "0", ws)
print(f"模块 0: {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.12 属性范围过滤
r = filters.filter_by_attribute_range("Degree", min_val=2, max_val=8, workspace=ws)
print(f"Degree 2-8: {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.13 非空属性
r = filters.filter_by_attribute_non_null("Label", ws)
print(f"Label 非空: {r['visible_nodes']} 节点可见")
filters.reset_filter(ws)

# 7.14 重置所有过滤
r = filters.reset_filter(ws)
print(f"重置后: {r['visible_nodes']} 节点可见")


# ============================================================================
# 8. 外观样式 (Appearance & Styling)
# ============================================================================
print("\n" + "=" * 60)
print("8. 外观样式 (Appearance)")
print("=" * 60)

from gephi_cli import appearance

ws = generator.generate("scale_free", node_count=80, m=2)
layout.run_layout("forceatlas2", iterations=100, workspace=ws)
layout.normalize_layout(ws)
metrics.run_metric("modularity", ws)
metrics.run_metric("pagerank", ws)
metrics.run_metric("degree", ws)

# 8.1 按模块度着色
r = appearance.color_nodes_by_modularity(ws)
print(f"模块度着色: {r['partitions']} 个分区")

# 8.2 按分区着色 (指定列)
r = appearance.color_nodes_by_partition("modularity_class", ws, seed=42)
print(f"按分区着色: {r['partitions']} 个分区")

# 8.3 统一节点颜色
appearance.set_all_nodes_color(70, 130, 180, ws)  # Steel Blue
print("统一颜色: RGB(70, 130, 180)")

# 8.4 单个节点颜色
appearance.set_node_color_hex("0", "#FF4500", ws)  # OrangeRed
print("节点0颜色: #FF4500")

# 8.5 按属性调整大小
r = appearance.set_node_size_by_attribute("pageranks", 5, 40, ws)
print(f"按 PageRank 调大小: 范围 [{r['range'][0]}, {r['range'][1]}]")

# 8.6 统一大小
appearance.set_all_nodes_size(15, ws)
print("统一大小: 15")

# 8.7 设置标签
r = appearance.set_node_labels("Label", ws)
print(f"标签: {r['column']}")

# 8.8 标签颜色
appearance.set_node_label_color(30, 30, 30, ws)
print("标签颜色: RGB(30, 30, 30)")

# 8.9 标签大小
appearance.set_node_label_size(12, ws, font_name="Arial", font_style="bold")
print("标签大小: 12, Arial Bold")

# 8.10 边颜色
appearance.set_all_edges_color(180, 180, 180, ws)
print("边颜色: RGB(180, 180, 180)")

# 8.11 边颜色按源/目标节点
appearance.color_edges_by_source(ws)
print("边颜色: 按源节点")

appearance.color_edges_by_target(ws)
print("边颜色: 按目标节点")

# 8.12 边权重
appearance.set_all_edges_weight(2.0, ws)
print("边权重: 2.0")

# 8.13 边标签
appearance.set_edge_labels("Weight", ws)
print("边标签: Weight")

# 8.14 节点位置
appearance.set_node_position("0", 0.0, 0.0, ws)
print("节点0位置: (0, 0)")

# 8.15 固定节点
appearance.set_node_fixed("0", True, ws)
print("节点0: 已固定")


# ============================================================================
# 9. 预览与图片导出 (Preview & Export)
# ============================================================================
print("\n" + "=" * 60)
print("9. 预览与图片导出 (Preview)")
print("=" * 60)

from gephi_cli import preview

# 重新设置漂亮的样式
ws = generator.generate("scale_free", node_count=100, m=2)
layout.run_layout("forceatlas2", workspace=ws, duration=3)
layout.normalize_layout(ws)
metrics.run_metric("modularity", ws)
metrics.run_metric("pagerank", ws)
appearance.color_nodes_by_modularity(ws)
appearance.set_node_size_by_attribute("pageranks", 5, 40, ws)
appearance.set_node_labels(workspace=ws)

# 9.1 预设
presets = ["default", "black_background", "text_outline"]
for preset_name in presets:
    preview.apply_preset(preset_name, ws)
    print(f"预设 '{preset_name}': 已应用")

# 9.2 自定义预览设置
r = preview.configure_preview(ws,
    show_labels=True,
    edge_opacity=40,
    node_opacity=100,
    node_border_width=1.0,
    edge_thickness=0.5,
    background_color="#FFFFFF",
)
print(f"自定义预览: {r['applied']}")

# 9.3 列出所有预览属性
props = preview.list_preview_properties()
print(f"\n可用预览属性: {len(props)} 个")
for name, desc in list(props.items())[:5]:
    print(f"  {name}: {desc}")
print("  ...")

# 9.4 导出 PNG
preview.apply_preset("default", ws)
preview.configure_preview(ws, show_labels=True, edge_opacity=30)
preview.export_image(f"{OUTPUT_DIR}/demo_default.png", 2048, 2048, ws)
print(f"\nPNG: {os.path.getsize(f'{OUTPUT_DIR}/demo_default.png')} 字节")
from IPython.display import Image, display
display(Image(filename=f"{OUTPUT_DIR}/demo_default.png", width=600))

# 9.5 导出 PNG (黑底)
preview.apply_preset("black_background", ws)
preview.configure_preview(ws, show_labels=True, edge_opacity=50)
preview.export_image(f"{OUTPUT_DIR}/demo_black.png", 2048, 2048, ws)
print(f"PNG (黑底): {os.path.getsize(f'{OUTPUT_DIR}/demo_black.png')} 字节")
display(Image(filename=f"{OUTPUT_DIR}/demo_black.png", width=600))

# 9.6 导出 PDF
preview.apply_preset("default", ws)
preview.export_pdf(f"{OUTPUT_DIR}/demo.pdf", ws)
print(f"PDF: {os.path.getsize(f'{OUTPUT_DIR}/demo.pdf')} 字节")

# 9.7 导出 SVG
preview.export_svg(f"{OUTPUT_DIR}/demo.svg", ws)
print(f"SVG: {os.path.getsize(f'{OUTPUT_DIR}/demo.svg')} 字节")


# ============================================================================
# 10. 数据实验室 (DataLab)
# ============================================================================
print("\n" + "=" * 60)
print("10. 数据实验室 (DataLab)")
print("=" * 60)

from gephi_cli import datalab

ws = generator.generate("path", node_count=5)
print(f"初始图: 5 节点, 4 边")

# 10.1 创建节点
r = datalab.create_node("新节点", workspace=ws)
print(f"创建节点: id={r['id']}, label={r['label']}")

# 10.2 创建边
r = datalab.create_edge("0", "4", weight=2.5, workspace=ws)
print(f"创建边: {r['source']} -> {r['target']}, weight={r['weight']}")

# 10.3 添加列
r = datalab.add_column("category", "string", "node", ws)
print(f"添加列: {r['name']} ({r['type']})")

r = datalab.add_column("score", "double", "node", ws)
print(f"添加列: {r['name']} ({r['type']})")

# 10.4 填充列
r = datalab.fill_column("category", "default", "node", ws)
print(f"填充列: {r['column']} = '{r['value']}', 影响 {r['count']} 个节点")

r = datalab.fill_column("score", "0.5", "node", ws)
print(f"填充列: {r['column']} = {r['value']}")

# 10.5 设置单个属性
r = datalab.set_attribute("0", "category", "important", "node", ws)
print(f"设置属性: 节点{r['id']}.{r['column']} = {r['value']}")

r = datalab.set_attribute("0", "score", "0.95", "node", ws)
print(f"设置属性: 节点{r['id']}.{r['column']} = {r['value']}")

# 10.6 列统计 (仅数值列)
r = datalab.get_column_statistics("score", "node", ws)
print(f"列统计: avg={r['average']}, min={r['min']}, max={r['max']}")

# 10.7 搜索替换
r = datalab.search_replace("category", "default", "normal", "node", False, ws)
print(f"搜索替换: '{r['search']}' -> '{r['replace']}', {r['matches_replaced']} 处替换")

# 10.8 复制列
r = datalab.duplicate_column("category", "category_backup", "node", ws)
print(f"复制列: {r['source']} -> {r['new']}")

# 10.9 清空列
r = datalab.clear_column("category_backup", "node", ws)
print(f"清空列: {r['column']}")

# 10.10 删除列
r = datalab.delete_column("category_backup", "node", ws)
print(f"删除列: {r['name']}")

# 10.11 删除边
r = datalab.delete_edge("0", "4", ws)
print(f"删除边: {r['source']} -> {r['target']}")

# 10.12 删除节点
r = datalab.delete_node("5", ws)
print(f"删除节点: id={r['id']}")

info = io_graph.get_graph_info(ws)
print(f"最终: {info['node_count']} 节点, {info['edge_count']} 边")


# ============================================================================
# 11. 最短路径 (Shortest Path)
# ============================================================================
print("\n" + "=" * 60)
print("11. 最短路径 (Shortest Path)")
print("=" * 60)

from gephi_cli import shortest_path

ws = generator.generate("grid", rows=5, cols=5)

# 11.1 两点之间最短路径
r = shortest_path.get_path_between("0", "24", workspace=ws)
print(f"路径 0 -> 24:")
print(f"  距离: {r['distance']}")
print(f"  路径: {' -> '.join(r['path'])}")
print(f"  路径长度: {r['path_length']} 个节点")

# 11.2 从源点到所有点的最短路径
r = shortest_path.compute_shortest_path("0", algorithm="dijkstra", workspace=ws)
print(f"\n从节点 0 出发 (Dijkstra):")
print(f"  算法: {r['algorithm']}")
print(f"  源节点: {r['source']}")
print(f"  最大距离: {r['max_distance']}")
# 显示部分距离
distances = {k: v for k, v in r.items() if k.startswith("distance_")}
for k, v in list(distances.items())[:5]:
    print(f"  {k}: {v}")


# ============================================================================
# 12. 项目与工作区管理 (Project Management)
# ============================================================================
print("\n" + "=" * 60)
print("12. 项目与工作区管理 (Project)")
print("=" * 60)

from gephi_cli import project

# 12.1 查看工作区
r = project.list_workspaces()
print(f"当前工作区数: {len(r['workspaces'])}")

# 12.2 新建工作区
ws1 = project.new_workspace()
print(f"新建工作区: {ws1}")

# 12.3 重命名
project.rename_workspace("分析工作区", ws1)
print("重命名: 分析工作区")

# 12.4 再新建一个
ws2 = project.new_workspace()
project.rename_workspace("可视化工作区", ws2)

# 12.5 查看所有工作区
r = project.list_workspaces()
print(f"工作区列表 ({len(r['workspaces'])} 个):")
for w in r["workspaces"]:
    flag = " <-- 当前" if w["is_current"] else ""
    print(f"  {w['name']}{flag}")

# 12.6 切换工作区
project.switch_workspace(0)
print("切换到工作区 0")

# 12.7 保存项目
project.save_project(f"{OUTPUT_DIR}/demo_project.gephi")
print(f"保存项目: {OUTPUT_DIR}/demo_project.gephi")

# 12.8 删除多余工作区
project.switch_workspace(0)
project.delete_workspace(ws2)
project.delete_workspace(ws1)
r = project.list_workspaces()
print(f"清理后工作区数: {len(r['workspaces'])}")


# ============================================================================
# 13. YAML 流水线 (Pipeline)
# ============================================================================
print("\n" + "=" * 60)
print("13. YAML 流水线 (Pipeline)")
print("=" * 60)

import yaml

# 13.1 定义流水线
pipeline_config = {
    "steps": [
        # 第1步: 生成无标度网络
        {"action": "generate", "type": "scale_free", "nodes": 150, "m": 3},
        # 第2步: 运行布局
        {"action": "layout", "algorithm": "forceatlas2", "duration": 3},
        # 第3步: 归一化坐标
        {"action": "normalize"},
        # 第4步: 计算模块度
        {"action": "metric", "name": "modularity"},
        # 第5步: 计算 PageRank
        {"action": "metric", "name": "pagerank"},
        # 第6步: 按模块度着色
        {"action": "appearance", "type": "color_by_modularity"},
        # 第7步: 按 PageRank 调节点大小
        {"action": "appearance", "type": "size_by_attribute",
         "column": "pageranks", "min_size": 5, "max_size": 40},
        # 第8步: 应用预设
        {"action": "preview", "preset": "default",
         "show_labels": True, "edge_opacity": 30},
        # 第9步: 导出 PNG
        {"action": "export", "file": f"{OUTPUT_DIR}/pipeline_result.png",
         "width": 2048, "height": 2048},
        # 第10步: 导出 GEXF
        {"action": "export", "file": f"{OUTPUT_DIR}/pipeline_result.gexf"},
    ]
}

# 保存 YAML
yaml_path = f"{OUTPUT_DIR}/demo_pipeline.yaml"
with open(yaml_path, "w", encoding="utf-8") as f:
    yaml.dump(pipeline_config, f, allow_unicode=True, default_flow_style=False)
print(f"YAML 已保存: {yaml_path}")

# 13.2 执行流水线
from gephi_cli import pipeline
results = pipeline.run_pipeline(yaml_path)
print(f"执行完成: {len(results)} 个步骤")
for i, r in enumerate(results):
    action = r.get("action", r.get("algorithm", "?"))
    print(f"  步骤 {i+1}: {action}")

print(f"\n输出文件:")
print(f"  PNG: {os.path.getsize(f'{OUTPUT_DIR}/pipeline_result.png')} 字节")
print(f"  GEXF: {os.path.getsize(f'{OUTPUT_DIR}/pipeline_result.gexf')} 字节")
from IPython.display import Image, display
display(Image(filename=f"{OUTPUT_DIR}/pipeline_result.png", width=600))


# ============================================================================
# 完成
# ============================================================================
print("\n" + "=" * 60)
print("教程完成! 所有功能演示成功。")
print(f"输出目录: {os.path.abspath(OUTPUT_DIR)}")
print("=" * 60)
