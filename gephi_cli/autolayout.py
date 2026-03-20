"""AutoLayout: chain multiple layout algorithms sequentially with time/iteration allocation."""

from .core import start_jvm, get_graph_model
from .layout import run_layout


def run_auto_layout(layout_sequence, total_iterations=1000, total_duration=None,
                    workspace=None, min_duration=0.5, min_iterations=1,
                    auto_tune=True):
    """Run multiple layout algorithms sequentially.

    Two modes:
      - iterations mode (default): distribute total_iterations by ratio
      - duration mode: distribute total_duration (seconds) by ratio

    Args:
        layout_sequence: List of dicts, each with:
            - algorithm: layout algorithm name
            - ratio: time/iteration ratio (0.0-1.0), should sum to 1.0
            - params: optional dict of algorithm parameters
        total_iterations: Total iterations to distribute (ignored if total_duration set)
        total_duration: Total time in seconds to distribute (e.g. 30.0)
        workspace: Gephi workspace
        min_duration: Minimum seconds per layout step (default 0.5)
        min_iterations: Minimum iterations per layout step (default 1)
        auto_tune: Pass through to run_layout's auto_tune (default True)

    Example (time-based, recommended):
        run_auto_layout([
            {"algorithm": "yifan_hu", "ratio": 0.3, "params": {"optimal_distance": 100}},
            {"algorithm": "forceatlas2", "ratio": 0.6, "params": {"scaling": 2.0}},
            {"algorithm": "noverlap", "ratio": 0.1},
        ], total_duration=30)
    """
    start_jvm()

    if not layout_sequence:
        raise ValueError("layout_sequence must not be empty")

    # Validate ratio sum
    total_ratio = sum(float(entry.get("ratio", 1.0 / len(layout_sequence)))
                      for entry in layout_sequence)
    if abs(total_ratio - 1.0) > 0.05:
        import warnings
        warnings.warn(f"Layout ratios sum to {total_ratio:.3f}, expected ~1.0. "
                      f"Time/iteration allocation may be uneven.")

    results = []
    for entry in layout_sequence:
        algo_name = entry["algorithm"].lower()
        ratio = float(entry.get("ratio", 1.0 / len(layout_sequence)))
        params = entry.get("params", {})

        if total_duration is not None:
            secs = max(min_duration, total_duration * ratio)
            result = run_layout(algo_name, workspace=workspace, duration=secs,
                                auto_tune=auto_tune, **params)
        else:
            iters = max(min_iterations, int(total_iterations * ratio))
            result = run_layout(algo_name, iterations=iters, workspace=workspace,
                                auto_tune=auto_tune, **params)

        result["ratio"] = ratio
        results.append(result)

    summary = {
        "action": "auto_layout",
        "sequence": results,
    }
    if total_duration is not None:
        summary["total_duration"] = total_duration
    else:
        summary["total_iterations"] = total_iterations
    return summary
