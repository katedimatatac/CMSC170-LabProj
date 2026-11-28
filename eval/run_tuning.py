"""Tie-breaker / heuristic tuning sweep.

Usage:
    python run_tuning.py                      # default: scales 1 2 4 8 16 32, 20 scenarios each
    python run_tuning.py --scenarios 100      # bigger sample
    python run_tuning.py --scales 1 8         # only some corridor widths
"""
import argparse

from data.dataloading import load_instance
from data.sampling import sample_scenarios_systematic
from algorithms.astar import Astar
from algorithms.greedy import Greedy
from tuning import evaluate_method, print_markdown_table

TIE_BREAKERS = ["fifo", "high_g", "low_h"]
HEURISTICS = ["octile", "euclidean", "manhattan"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scales", type=int, nargs="+", default=[1, 2, 4, 8, 16, 32])
    ap.add_argument("--scenarios", type=int, default=20)
    ap.add_argument("--map-index", type=int, default=0, help="the N in maze512-<scale>-N.map")
    ap.add_argument("--seed", type=int, default=67)
    args = ap.parse_args()

    rows = []
    for scale in args.scales:
        spec = f"{scale}-{args.map_index}"
        grid, scens = load_instance(f"maze-map/maze512-{spec}.map", f"maze-scen/maze512-{spec}.map.scen")
        sample = sample_scenarios_systematic(scens, target_count=args.scenarios, seed=args.seed)
        print(f"scale {scale}: {len(sample)} scenarios", flush=True)

        # 1) tie-breakers with a fixed heuristic (octile)
        for tb in TIE_BREAKERS:
            rows.append(evaluate_method("A*", f"octile+{tb}", Astar, grid, scale, sample,
                                        heuristic="octile", tie_breaker=tb))
        for tb in TIE_BREAKERS:
            rows.append(evaluate_method("Greedy", f"octile+{tb}", Greedy, grid, scale, sample,
                                        heuristic="octile", tie_breaker=tb))

        # 2) heuristics with a fixed tie-breaker (octile is already covered above)
        for h in HEURISTICS[1:]:
            rows.append(evaluate_method("A*", f"{h}+low_h", Astar, grid, scale, sample,
                                        heuristic=h, tie_breaker="low_h"))
            rows.append(evaluate_method("Greedy", f"{h}+fifo", Greedy, grid, scale, sample,
                                        heuristic=h, tie_breaker="fifo"))

    print()
    print_markdown_table(rows)


if __name__ == "__main__":
    main()