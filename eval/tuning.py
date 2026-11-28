import math
import time
from typing import Callable

HeuristicFn = Callable[[int, int, int, int], float]


def octile_dist(x: int, y: int, gx: int, gy: int) -> float:
    dx, dy = abs(x - gx), abs(y - gy)
    return max(dx, dy) + (math.sqrt(2.0) - 1.0) * min(dx, dy)


def euclidean_dist(x: int, y: int, gx: int, gy: int) -> float:
    return math.hypot(x - gx, y - gy)


def manhattan_dist(x: int, y: int, gx: int, gy: int) -> float:
    return float(abs(x - gx) + abs(y - gy))


HEURISTICS = {
    "octile": octile_dist,
    "euclidean": euclidean_dist,
    "manhattan": manhattan_dist,
}


def get_heuristic(name: str = "octile") -> HeuristicFn:
    if name not in HEURISTICS:
        raise ValueError(f"Unknown heuristic {name!r}; choose from {list(HEURISTICS)}")
    return HEURISTICS[name]


def make_tie_key(mode: str, g: float, h: float, order: int):
    if mode == "high_g":
        return -g
    if mode == "low_h":
        return h
    return order            # fifo as the default tie-breaking strategy


def resolve_step_cost(step_cost: float, uniform_cost: bool = False) -> float:
    return 1.0 if uniform_cost else step_cost


def evaluate_method(algo_name, config_label, algo_fn, grid, scale, sampled_scenarios, **kwargs):
    n = len(sampled_scenarios)
    if n == 0:
        return {
            "algorithm": algo_name,
            "config": config_label,
            "scale": scale,
            "avg_suboptimality": float("inf"),
            "avg_time_ms": 0.0,
            "avg_expanded": 0.0,
        }

    subopt_ratios = []
    runtimes_ms = []
    states_expanded = []

    for _, scen in sampled_scenarios:
        t0 = time.perf_counter()
        _, cost, expanded = algo_fn(grid, scen, **kwargs)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        runtimes_ms.append(elapsed_ms)
        states_expanded.append(len(expanded) if hasattr(expanded, "__len__") else expanded)
        if scen.optimal_length > 0 and cost is not None and cost < float("inf"):
            subopt_ratios.append(cost / scen.optimal_length)

    avg_subopt = (
        round(sum(subopt_ratios) / len(subopt_ratios), 4)
        if subopt_ratios
        else float("inf")
    )

    return {
        "algorithm": algo_name,
        "config": config_label,
        "scale": scale,
        "avg_suboptimality": avg_subopt,
        "avg_time_ms": round(sum(runtimes_ms) / n, 3),
        "avg_expanded": round(sum(states_expanded) / n, 1),
    }


def print_markdown_table(rows):
    if not rows:
        print("No results to display.")
        return

    headers = [
        "Algorithm",
        "Config",
        "Scale",
        "Avg Suboptimality",
        "Avg Time (ms)",
        "Avg States Expanded",
    ]
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        print(
            f"| {r['algorithm']} | {r['config']} | {r['scale']} | "
            f"{r['avg_suboptimality']:.4f} | {r['avg_time_ms']:.3f} | {r['avg_expanded']:.1f} |"
        )


if __name__ == "__main__":
    # Test heuristics
    assert octile_dist(0, 0, 3, 4) > 0
    assert abs(euclidean_dist(0, 0, 3, 4) - 5.0) < 1e-9
    assert manhattan_dist(0, 0, 3, 4) == 7.0
    assert callable(get_heuristic("octile"))

    # Test tie-breakers
    assert make_tie_key("high_g", 10.0, 4.0, 0) == -10.0
    assert make_tie_key("low_h", 10.0, 4.0, 0) == 4.0
    assert make_tie_key("fifo", 10.0, 4.0, 7) == 7

    # Test step-cost resolution
    assert resolve_step_cost(1.414, uniform_cost=False) == 1.414
    assert resolve_step_cost(1.414, uniform_cost=True) == 1.0

    # Test empty scenario guard
    empty_res = evaluate_method("A*", "default", lambda g, s: ([], 0.0, 0), None, 1, [])
    assert empty_res["avg_time_ms"] == 0.0
    assert empty_res["avg_expanded"] == 0.0

    # Test table formatting with sample rows
    sample_rows = [
        {
            "algorithm": "A*",
            "config": "octile+fifo",
            "scale": 1,
            "avg_suboptimality": 1.0,
            "avg_time_ms": 12.345,
            "avg_expanded": 450.0,
        }
    ]
    print_markdown_table(sample_rows)

    print("All tuning.py tests passed.")