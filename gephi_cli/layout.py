"""All 11 layout algorithms from Gephi Toolkit."""

from .core import start_jvm, get_graph_model

# Type markers for Java boxed types
# "D" = java.lang.Double, "F" = java.lang.Float, "I" = java.lang.Integer
# "L" = java.lang.Long, "B" = java.lang.Boolean

LAYOUTS = {
    "forceatlas2": {
        "desc": "Force-directed layout, best for most networks (supports multi-threading & Barnes-Hut)",
        "builder": "org.gephi.layout.plugin.forceAtlas2.ForceAtlas2Builder",
        "params": {
            "scaling": ("setScalingRatio", "D", "Scaling ratio (default ~2.0)"),
            "gravity": ("setGravity", "D", "Gravity strength (default ~1.0)"),
            "jitter_tolerance": ("setJitterTolerance", "D", "Jitter tolerance (default ~1.0)"),
            "barnes_hut": ("setBarnesHutOptimize", "B", "Enable Barnes-Hut optimization"),
            "barnes_hut_theta": ("setBarnesHutTheta", "D", "Barnes-Hut theta (default ~1.2)"),
            "linlog": ("setLinLogMode", "B", "LinLog mode for tighter clusters"),
            "strong_gravity": ("setStrongGravityMode", "B", "Strong gravity mode"),
            "outbound_attraction": ("setOutboundAttractionDistribution", "B", "Outbound attraction distribution"),
            "edge_weight_influence": ("setEdgeWeightInfluence", "D", "Edge weight influence (default ~1.0)"),
            "adjust_sizes": ("setAdjustSizes", "B", "Prevent node overlap"),
            "threads": ("setThreadsCount", "I", "Number of threads"),
        },
    },
    "forceatlas1": {
        "desc": "Original ForceAtlas (v1), predecessor of ForceAtlas2",
        "builder": "org.gephi.layout.plugin.forceAtlas.ForceAtlas",
        "params": {
            "inertia": ("setInertia", "D", "Inertia (default ~0.1)"),
            "repulsion_strength": ("setRepulsionStrength", "D", "Repulsion strength"),
            "attraction_strength": ("setAttractionStrength", "D", "Attraction strength"),
            "max_displacement": ("setMaxDisplacement", "D", "Max displacement"),
            "freeze_balance": ("setFreezeBalance", "B", "Auto freeze balance"),
            "freeze_strength": ("setFreezeStrength", "D", "Freeze strength"),
            "freeze_inertia": ("setFreezeInertia", "D", "Freeze inertia"),
            "gravity": ("setGravity", "D", "Gravity strength"),
            "outbound_attraction": ("setOutboundAttractionDistribution", "B", "Outbound attraction distribution"),
            "adjust_sizes": ("setAdjustSizes", "B", "Prevent node overlap"),
            "speed": ("setSpeed", "D", "Speed"),
            "cooling": ("setCooling", "D", "Cooling"),
        },
    },
    "fruchterman_reingold": {
        "desc": "Classic Fruchterman-Reingold force-directed layout",
        "builder": "org.gephi.layout.plugin.fruchterman.FruchtermanReingoldBuilder",
        "params": {
            "area": ("setArea", "F", "Layout area (default ~10000)"),
            "gravity": ("setGravity", "D", "Gravity strength (default ~10)"),
            "speed": ("setSpeed", "D", "Speed (default ~1)"),
        },
    },
    "yifan_hu": {
        "desc": "Multi-level force-directed, good for large graphs",
        "builder": "org.gephi.layout.plugin.force.yifanHu.YifanHuProportional",
        "params": {
            "optimal_distance": ("setOptimalDistance", "F", "Optimal distance (default ~100)"),
            "step_ratio": ("setStepRatio", "F", "Step ratio (default ~0.95)"),
            "initial_step": ("setInitialStep", "F", "Initial step size"),
            "convergence_threshold": ("setConvergenceThreshold", "F", "Convergence threshold"),
            "adaptive_cooling": ("setAdaptiveCooling", "B", "Adaptive cooling"),
            "barnes_hut_theta": ("setBarnesHutTheta", "F", "Barnes-Hut theta"),
            "quadtree_max_level": ("setQuadTreeMaxLevel", "I", "Quadtree max level"),
            "relative_strength": ("setRelativeStrength", "F", "Relative strength"),
            "step": ("setStep", "F", "Current step size"),
        },
    },
    "openord": {
        "desc": "Large-scale graph layout (millions of nodes), multi-threaded",
        "builder": "org.gephi.layout.plugin.openord.OpenOrdLayoutBuilder",
        "params": {
            "edge_cut": ("setEdgeCut", "F", "Edge cut (0-1, default ~0.8)"),
            "num_iterations": ("setNumIterations", "I", "Number of iterations"),
            "num_threads": ("setNumThreads", "I", "Number of threads"),
            "rand_seed": ("setRandSeed", "L", "Random seed"),
            "real_time": ("setRealTime", "F", "Real time"),
            "liquid_stage": ("setLiquidStage", "I", "Liquid stage percentage"),
            "expansion_stage": ("setExpansionStage", "I", "Expansion stage percentage"),
            "cooldown_stage": ("setCooldownStage", "I", "Cooldown stage percentage"),
            "crunch_stage": ("setCrunchStage", "I", "Crunch stage percentage"),
            "simmer_stage": ("setSimmerStage", "I", "Simmer stage percentage"),
        },
    },
    "label_adjust": {
        "desc": "Adjust node positions to prevent label overlap",
        "builder": "org.gephi.layout.plugin.labelAdjust.LabelAdjustBuilder",
        "params": {
            "speed": ("setSpeed", "D", "Adjustment speed"),
            "adjust_by_size": ("setAdjustBySize", "B", "Adjust by node size"),
        },
    },
    "noverlap": {
        "desc": "Push overlapping nodes apart (anti-overlap)",
        "builder": "org.gephi.layout.plugin.noverlap.NoverlapLayoutBuilder",
        "params": {
            "speed": ("setSpeed", "D", "Speed"),
            "ratio": ("setRatio", "D", "Ratio"),
            "margin": ("setMargin", "D", "Margin between nodes"),
        },
    },
    "random": {
        "desc": "Randomly place nodes in a given area",
        "builder": "org.gephi.layout.plugin.random.Random",
        "params": {
            "size": ("setSize", "D", "Area size (default ~1000)"),
        },
    },
    "rotate": {
        "desc": "Rotate entire graph by an angle",
        "builder": "org.gephi.layout.plugin.rotate.Rotate",
        "params": {
            "angle": ("setAngle", "D", "Rotation angle in degrees"),
        },
    },
    "expand": {
        "desc": "Expand (scale up) graph layout",
        "builder": "org.gephi.layout.plugin.scale.Expand",
        "params": {
            "scale": ("setScale", "D", "Scale factor"),
        },
    },
    "contract": {
        "desc": "Contract (scale down) graph layout",
        "builder": "org.gephi.layout.plugin.scale.Contract",
        "params": {
            "scale": ("setScale", "D", "Scale factor"),
        },
    },
}


def run_layout(algorithm, iterations=100, workspace=None, duration=None,
               auto_tune=True, **params):
    """Run a layout algorithm.

    Two modes:
      - iterations mode (default): run exactly N iterations
      - duration mode: run for N seconds (use duration=10.0 for 10 seconds)

    When duration is set, iterations is ignored. The layout runs continuously
    until the time limit is reached, which produces much better results for
    force-directed layouts on large graphs.

    Args:
        algorithm: One of the keys in LAYOUTS
        iterations: Number of iterations to run (ignored if duration is set)
        workspace: Gephi workspace (uses current if None)
        duration: Run time in seconds (e.g. 10.0). Overrides iterations.
        auto_tune: Auto-tune FA2 params in duration mode (default True).
                   Set to False for full manual control.
        **params: Algorithm-specific parameters (see LAYOUTS dict)

    Returns:
        dict with algorithm name and iteration/time info
    """
    start_jvm()
    import jpype
    import java.lang
    import time

    algo = algorithm.lower()
    if algo not in LAYOUTS:
        raise ValueError(f"Unknown algorithm: {algorithm}. Available: {list(LAYOUTS.keys())}")

    layout_info = LAYOUTS[algo]
    gm = get_graph_model(workspace)

    # Build layout via its builder class
    builder_cls = jpype.JClass(layout_info["builder"])
    builder = builder_cls()
    layout = builder.buildLayout()
    layout.setGraphModel(gm)
    layout.resetPropertiesValues()

    # Java boxed type converters
    _converters = {
        "D": lambda v: java.lang.Double(float(v)),
        "F": lambda v: java.lang.Float(float(v)),
        "I": lambda v: java.lang.Integer(int(v)),
        "L": lambda v: java.lang.Long(int(v)),
        "B": lambda v: java.lang.Boolean(bool(v)),
    }

    # For duration mode on ForceAtlas2: auto-tune parameters to prevent collapse
    if auto_tune and duration is not None and algo == "forceatlas2":
        node_count = gm.getGraph().getNodeCount()
        if "scaling" not in params:
            auto_scaling = max(2.0, node_count / 10.0)
            setter_name, type_code, _ = layout_info["params"]["scaling"]
            getattr(layout, setter_name)(_converters[type_code](auto_scaling))
        if "gravity" not in params:
            setter_name, type_code, _ = layout_info["params"]["gravity"]
            getattr(layout, setter_name)(_converters[type_code](0.5))
        if "adjust_sizes" not in params:
            setter_name, type_code, _ = layout_info["params"]["adjust_sizes"]
            getattr(layout, setter_name)(_converters[type_code](True))
        if "barnes_hut" not in params and node_count > 100:
            setter_name, type_code, _ = layout_info["params"]["barnes_hut"]
            getattr(layout, setter_name)(_converters[type_code](True))

    # Apply user parameters (override auto-tuned values)
    for param_name, value in params.items():
        if param_name in layout_info["params"]:
            setter_name, type_code, _ = layout_info["params"][param_name]
            setter = getattr(layout, setter_name)
            setter(_converters[type_code](value))

    # Validate parameters
    if duration is not None and duration <= 0:
        raise ValueError("duration must be > 0")
    if duration is None and iterations < 1:
        raise ValueError("iterations must be >= 1")

    # Run layout
    layout.initAlgo()
    actual_iterations = 0

    if duration is not None:
        # Time-based mode: run until time limit
        start_time = time.time()
        deadline = start_time + float(duration)
        while time.time() < deadline:
            if layout.canAlgo():
                layout.goAlgo()
                actual_iterations += 1
            else:
                break
        elapsed = time.time() - start_time
        layout.endAlgo()
        return {
            "algorithm": algorithm,
            "mode": "duration",
            "duration_seconds": round(elapsed, 2),
            "iterations_run": actual_iterations,
        }
    else:
        # Iteration-based mode
        for _ in range(iterations):
            if layout.canAlgo():
                layout.goAlgo()
                actual_iterations += 1
            else:
                break
        layout.endAlgo()
        return {
            "algorithm": algorithm,
            "mode": "iterations",
            "iterations_requested": iterations,
            "iterations_run": actual_iterations,
        }


def normalize_layout(workspace=None, scale=1000.0, percentile=0.05, margin_ratio=0.6):
    """Normalize node positions: center at origin and scale to fill canvas.

    Uses percentile bounds to ignore outlier nodes, preventing
    a few distant nodes from making the main graph tiny.

    Args:
        workspace: Gephi workspace
        scale: Target coordinate range (default 1000)
        percentile: Lower/upper percentile for outlier detection (default 0.05 = 5th/95th)
                    Set to 0.0 to use full range (no outlier removal)
        margin_ratio: Outlier clamp ratio beyond main area (default 0.6 = 60%)
                      Set to 0.0 to disable clamping, or >1.0 for looser clamp
    """
    if scale <= 0:
        raise ValueError("scale must be > 0")
    if not 0.0 <= percentile < 0.5:
        raise ValueError("percentile must be in [0.0, 0.5)")
    if margin_ratio < 0:
        raise ValueError("margin_ratio must be >= 0")

    start_jvm()
    gm = get_graph_model(workspace)
    graph = gm.getGraph()
    nodes = list(graph.getNodes())

    if not nodes:
        return {"action": "normalize", "nodes": 0}

    xs = [float(n.x()) for n in nodes]
    ys = [float(n.y()) for n in nodes]

    # Use percentile bounds to ignore outliers
    xs_sorted = sorted(xs)
    ys_sorted = sorted(ys)
    n = len(nodes)
    lo_idx = max(0, int(n * percentile))
    hi_idx = min(n - 1, int(n * (1.0 - percentile)))
    # Guard against lo_idx crossing hi_idx for very small graphs
    if lo_idx >= hi_idx:
        lo_idx = 0
        hi_idx = n - 1

    x_lo, x_hi = xs_sorted[lo_idx], xs_sorted[hi_idx]
    y_lo, y_hi = ys_sorted[lo_idx], ys_sorted[hi_idx]

    # Center on the percentile midpoint
    cx = (x_lo + x_hi) / 2.0
    cy = (y_lo + y_hi) / 2.0
    x_range = x_hi - x_lo
    y_range = y_hi - y_lo
    max_range = max(x_range, y_range, 1.0)

    # Scale to target range, centered at origin; optionally clamp outliers
    factor = scale / max_range
    clamp = margin_ratio > 0
    margin = scale * margin_ratio if clamp else float('inf')
    for node in nodes:
        nx = (float(node.x()) - cx) * factor
        ny = (float(node.y()) - cy) * factor
        if clamp:
            nx = max(-margin, min(margin, nx))
            ny = max(-margin, min(margin, ny))
        node.setX(float(nx))
        node.setY(float(ny))

    return {
        "action": "normalize",
        "nodes": len(nodes),
        "scale_factor": round(factor, 4),
        "original_range": round(max_range, 2),
    }


def list_layouts():
    """Return all available layouts with descriptions and parameters."""
    result = {}
    for name, info in LAYOUTS.items():
        result[name] = {
            "description": info["desc"],
            "parameters": {
                k: desc for k, (_, _, desc) in info["params"].items()
            },
        }
    return result
