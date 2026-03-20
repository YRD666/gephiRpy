"""Preview configuration and export to image/PDF/SVG with all Gephi properties."""

import os
from .core import start_jvm


def _parse_hex_color(hex_str):
    """Parse a hex color string to (r, g, b) tuple."""
    hex_color = str(hex_str).lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color[0]*2 + hex_color[1]*2 + hex_color[2]*2
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: '{hex_str}'. Expected format: '#RRGGBB' or '#RGB'")
    return int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)


# All configurable preview properties
PREVIEW_PROPERTIES = {
    # Node properties
    "show_labels": ("SHOW_NODE_LABELS", bool, "Show node labels"),
    "node_opacity": ("NODE_OPACITY", float, "Node opacity (0-100)"),
    "node_border_width": ("NODE_BORDER_WIDTH", float, "Node border width"),
    "node_border_color": ("NODE_BORDER_COLOR", "color", "Node border color hex"),
    "node_per_node_opacity": ("NODE_PER_NODE_OPACITY", bool, "Per-node opacity from attribute"),
    # Node label properties
    "label_font_size": ("NODE_LABEL_FONT", "font", "Node label font size (int or 'size:fontname:style')"),
    "label_color": ("NODE_LABEL_COLOR", "dependent_color", "Node label color"),
    "label_max_char": ("NODE_LABEL_MAX_CHAR", int, "Max characters in node label"),
    "label_shorten": ("NODE_LABEL_SHORTEN", bool, "Shorten long labels"),
    "label_proportional_size": ("NODE_LABEL_PROPORTIONAL_SIZE", bool, "Proportional label size"),
    "label_outline_size": ("NODE_LABEL_OUTLINE_SIZE", float, "Label outline size"),
    "label_outline_opacity": ("NODE_LABEL_OUTLINE_OPACITY", float, "Label outline opacity"),
    "label_outline_color": ("NODE_LABEL_OUTLINE_COLOR", "dependent_color", "Label outline color"),
    "label_box": ("NODE_LABEL_SHOW_BOX", bool, "Show label box background"),
    "label_box_opacity": ("NODE_LABEL_BOX_OPACITY", float, "Label box opacity"),
    # Edge properties
    "show_edges": ("SHOW_EDGES", bool, "Show edges"),
    "edge_opacity": ("EDGE_OPACITY", float, "Edge opacity (0-100)"),
    "edge_thickness": ("EDGE_THICKNESS", float, "Edge thickness"),
    "edge_curved": ("EDGE_CURVED", bool, "Use curved edges"),
    "edge_radius": ("EDGE_RADIUS", float, "Edge radius for curved edges"),
    "edge_rescale_weight": ("EDGE_RESCALE_WEIGHT", bool, "Rescale edge weight"),
    "edge_rescale_weight_min": ("EDGE_RESCALE_WEIGHT_MIN", float, "Min rescaled weight"),
    "edge_rescale_weight_max": ("EDGE_RESCALE_WEIGHT_MAX", float, "Max rescaled weight"),
    # Edge label properties
    "show_edge_labels": ("SHOW_EDGE_LABELS", bool, "Show edge labels"),
    "edge_label_max_char": ("EDGE_LABEL_MAX_CHAR", int, "Max chars in edge label"),
    # Arrow properties
    "arrow_size": ("ARROW_SIZE", float, "Arrow size for directed edges"),
    # Global
    "background_color": ("BACKGROUND_COLOR", "color", "Background color hex"),
    "margin": ("MARGIN", float, "Preview margin"),
    "visibility_ratio": ("VISIBILITY_RATIO", float, "Visibility ratio"),
}


def configure_preview(workspace=None, **options):
    """Configure preview settings with all available properties.

    Args:
        workspace: Gephi workspace
        **options: Key-value pairs from PREVIEW_PROPERTIES keys
    """
    start_jvm()
    from org.gephi.preview.api import PreviewController, PreviewProperty
    from org.openide.util import Lookup
    import java.awt

    pc = Lookup.getDefault().lookup(PreviewController)
    model = pc.getModel()
    props = model.getProperties()

    unknown_keys = [k for k in options if k not in PREVIEW_PROPERTIES]
    if unknown_keys:
        raise ValueError(f"Unknown preview properties: {unknown_keys}. "
                         f"Available: {list(PREVIEW_PROPERTIES.keys())}")

    applied = {}
    for key, value in options.items():

        prop_name, prop_type, _ = PREVIEW_PROPERTIES[key]
        prop_const = getattr(PreviewProperty, prop_name)

        if prop_type == bool:
            props.putValue(prop_const, bool(value))
        elif prop_type == float:
            props.putValue(prop_const, float(value))
        elif prop_type == int:
            props.putValue(prop_const, int(value))
        elif prop_type == "color":
            r, g, b = _parse_hex_color(value)
            props.putValue(prop_const, java.awt.Color(r, g, b))
        elif prop_type == "font":
            # Accept int (size only) or "size:fontname:style"
            if isinstance(value, (int, float)):
                font = java.awt.Font("Arial", java.awt.Font.PLAIN, max(1, int(value)))
            elif isinstance(value, str) and ":" in value:
                parts = value.split(":")
                try:
                    f_size = max(1, int(parts[0]))
                except ValueError:
                    raise ValueError(f"Invalid font format: '{value}'. Expected 'size:fontname:style'")
                f_name = parts[1] if len(parts) > 1 and parts[1] else "Arial"
                f_style_str = parts[2].lower() if len(parts) > 2 else "plain"
                style_map = {
                    "plain": java.awt.Font.PLAIN,
                    "bold": java.awt.Font.BOLD,
                    "italic": java.awt.Font.ITALIC,
                    "bold_italic": java.awt.Font.BOLD | java.awt.Font.ITALIC,
                }
                f_style = style_map.get(f_style_str, java.awt.Font.PLAIN)
                font = java.awt.Font(f_name, f_style, f_size)
            else:
                font = java.awt.Font("Arial", java.awt.Font.PLAIN, max(1, int(value)))
            props.putValue(prop_const, font)
        elif prop_type == "dependent_color":
            r, g, b = _parse_hex_color(value)
            props.putValue(prop_const, java.awt.Color(r, g, b))

        applied[key] = value

    pc.refreshPreview()
    return {"action": "configure_preview", "applied": applied}


def export_image(output_path, width=1024, height=1024, workspace=None):
    """Export graph to PNG image."""
    start_jvm()
    from org.gephi.io.exporter.api import ExportController
    from org.openide.util import Lookup
    import java.io

    ec = Lookup.getDefault().lookup(ExportController)
    exporter = ec.getExporter("png")
    exporter.setWidth(int(width))
    exporter.setHeight(int(height))

    f = java.io.File(os.path.abspath(output_path))
    fos = java.io.FileOutputStream(f)
    try:
        ec.exportStream(fos, exporter)
    finally:
        fos.close()

    return {"action": "export_png", "path": output_path, "size": f"{width}x{height}"}


def export_pdf(output_path, workspace=None):
    """Export graph to PDF."""
    start_jvm()
    from org.gephi.io.exporter.api import ExportController
    from org.openide.util import Lookup
    import java.io

    ec = Lookup.getDefault().lookup(ExportController)
    exporter = ec.getExporter("pdf")

    f = java.io.File(os.path.abspath(output_path))
    fos = java.io.FileOutputStream(f)
    try:
        ec.exportStream(fos, exporter)
    finally:
        fos.close()

    return {"action": "export_pdf", "path": output_path}


def export_svg(output_path, workspace=None):
    """Export graph to SVG."""
    start_jvm()
    from org.gephi.io.exporter.api import ExportController
    from org.openide.util import Lookup
    import java.io

    ec = Lookup.getDefault().lookup(ExportController)
    exporter = ec.getExporter("svg")

    # SVG is a CharacterExporter, needs Writer not OutputStream
    f = java.io.File(os.path.abspath(output_path))
    writer = java.io.FileWriter(f)
    try:
        ec.exportWriter(writer, exporter)
    finally:
        writer.close()

    return {"action": "export_svg", "path": output_path}


def apply_preset(preset_name, workspace=None):
    """Apply a built-in preview preset.

    Available presets:
        default, default_curved, default_straight,
        black_background, tag_cloud, text_outline, edges_custom_color
    """
    start_jvm()
    from org.gephi.preview.api import PreviewController
    from org.openide.util import Lookup

    preset_map = {
        "default": "org.gephi.preview.presets.DefaultPreset",
        "default_curved": "org.gephi.preview.presets.DefaultCurved",
        "default_straight": "org.gephi.preview.presets.DefaultStraight",
        "black_background": "org.gephi.preview.presets.BlackBackground",
        "tag_cloud": "org.gephi.preview.presets.TagCloud",
        "text_outline": "org.gephi.preview.presets.TextOutline",
        "edges_custom_color": "org.gephi.preview.presets.EdgesCustomColor",
    }

    if preset_name not in preset_map:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(preset_map.keys())}")

    import jpype
    preset_cls = jpype.JClass(preset_map[preset_name])
    preset = preset_cls()

    pc = Lookup.getDefault().lookup(PreviewController)
    model = pc.getModel()
    props = model.getProperties()

    # getProperties() returns Map<String, Object>
    preset_props = preset.getProperties()
    for entry in preset_props.entrySet():
        props.putValue(str(entry.getKey()), entry.getValue())

    pc.refreshPreview()
    return {"action": "apply_preset", "preset": preset_name}


PREVIEW_PRESETS = {
    "default": "Default preview settings",
    "default_curved": "Default with curved edges",
    "default_straight": "Default with straight edges",
    "black_background": "Dark theme with black background",
    "tag_cloud": "Emphasize labels (tag cloud style)",
    "text_outline": "Labels with text outline",
    "edges_custom_color": "Edges with custom uniform color",
}


def list_preview_properties():
    """Return all configurable preview properties."""
    return {k: desc for k, (_, _, desc) in PREVIEW_PROPERTIES.items()}
