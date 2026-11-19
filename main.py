import os
import sys
import time
from visuals import visualize_search
from dataloading import load_instance
from sampling import sample_scenarios_systematic
from algorithms.astar import Astar
from algorithms.dijkstra import Dijkstra
from algorithms.bfs import BFS
from algorithms.greedy import Greedy

ALGORITHMS = {
    "astar": Astar,
    "dijkstra": Dijkstra,
    "bfs": BFS,
    "greedy": Greedy
}

def main():
    corr_widths = {1,2,4,8,16,32}
    for w in corr_widths:
        filespec = f"{w}-0"  # modify this to specify the map and scenario file
        map_file = f"maze-map/maze512-{filespec}.map"
        scenario_file = f"maze-scen/maze512-{filespec}.map.scen"

        if len(sys.argv) == 3:
            map_file = sys.argv[1]
            scenario_file = sys.argv[2]

        print(f"Loading instance from {map_file} and {scenario_file}...")
        grid, scenarios = load_instance(map_file, scenario_file)

        if not scenarios:
            print("Error: No valid scenarios found for this map instance!")
            return

        # Sample a random scenario from each bucket
        test_cases = sample_scenarios_systematic(scenarios, target_count=100, seed=67)
        print(f"Sampled {len(test_cases)} scenarios across buckets.\n")

        os.makedirs("images", exist_ok=True)

        # Register algorithms to evaluate (uncomment GBFS and BFS once imported)
        algorithms = {
            "Dijkstra": Dijkstra,
            "Astar": Astar,
            
            # "GBFS": GBFS,
            # "BFS": BFS,
        }

        for algo_name, search_fn in algorithms.items():
            print(f"=== Running {algo_name} ===")
            total_ratio = 0.0
            total_time = 0.0

            for scen_num, scen in test_cases:
                s_time = time.perf_counter()
                path, cost, states_expanded = search_fn(grid, scen)
                e_time = time.perf_counter()

                final_time = e_time - s_time
                suboptimality = cost / scen.optimal_length

                total_ratio += suboptimality
                total_time += final_time

                # print(
                #     f"Scenario #{scen_num:4d} (Bucket {scen.bucket:3d}) | "
                #     f"Ratio: {suboptimality:.5f} | Time: {final_time * 1000:.3f} ms | "
                #     f"Expanded: {len(states_expanded) if states_expanded else 0}"
                # )

                # Optional: print full metrics and save visualization for the last scenario
                if (scen_num, scen) == test_cases[-1]:
                    print_run_metrics(grid, scenarios, scen_num, scen, cost, states_expanded, final_time)
                    output_filename = f"{grid.name}_scen{scen_num}_{algo_name.lower()}.png"
                    visualize_search(
                        grid=grid,
                        scenario=scen,
                        explored_coords=states_expanded,
                        path=path,
                        output_dir="images",
                        filename=output_filename,
                    )

            avg_ratio = total_ratio / len(test_cases)
            avg_time_ms = (total_time / len(test_cases)) * 1000
            print(f"\n[{algo_name} Summary] Avg Suboptimality: {avg_ratio:.5f} | Avg Time: {avg_time_ms:.3f} ms\n")


def print_run_metrics(grid, scenarios, scenario_num, scenario_sample, cost, states_expanded=None, runtime=0.0):
    max_problem_length = max(s.optimal_length for s in scenarios) if scenarios else 0
    total_map_states = grid.num_passable()

    print("\n--- Dataset and Search Metrics ---")
    print(f"Map Name: {grid.name}")
    print(f"Scenario Index: {scenario_num} (Bucket {scenario_sample.bucket})")
    print(f"Start State: {scenario_sample.start}")
    print(f"Goal State: {scenario_sample.goal}\n")
    print(f"Algorithm Cost: {cost:.2f}")
    print(f"Optimal Cost (from .scen): {scenario_sample.optimal_length:.2f}\n")
    print(f"Max Problem Length (Optimal): {max_problem_length:.2f}")
    print(f"Suboptimality Ratio: {(cost / scenario_sample.optimal_length):.5f}:1.0")
    print(f"Total Valid States in Map: {total_map_states}")
    print(f"States Expanded by Search: {len(states_expanded) if states_expanded else 0}")
    print(f"Run Time: {runtime:.6f} s\n")


if __name__ == "__main__":
    main()