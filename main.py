import os
import sys
import random as r
from visuals import visualize_search
from dataloading import load_instance
from algorithms.astar import Astar
from algorithms.dijkstra import Dijkstra


def main():
    global scenario_sample 
    global scenario_num
    global path, cost, states_expanded 

    map_file = "maze-map/maze512-32-0.map"                      # default test case file
    scenario_file = "maze-scen/maze512-32-0.map.scen"

    grid, scenarios = load_instance(map_file, scenario_file)

    scenario_num = r.randint(0,len(scenarios)-1)            # select random scenario
    scenario_sample = scenarios[scenario_num]
    scenario_sample = max(scenarios, key=lambda s: s.optimal_length)
    path, cost, states_expanded = Astar(grid, scenario_sample)

    print_run_metrics(grid, scenarios, states_expanded)

    visualize_search(                   # call visuals.py to generate solved maze figure
        grid=grid,
        scenario=scenario_sample,
        explored_coords=states_expanded,
        path=path,
        output_dir="images",                # generated images will be saved in "images" directory 
        filename="maze512-1-0_astar.png"
    )



def print_run_metrics(grid, scenarios, states_expanded=None):
    # find the maximum optimal path length across all scenarios in the file
    max_problem_length = max(s.optimal_length for s in scenarios) if scenarios else 0
    total_map_states = grid.num_passable()

    print("--- Dataset and Search Metrics ---\n")
    print(f"Map: {grid.name}")
    print(f"Scenario Num: {scenario_num+1}")
    print(f"Start State: {scenario_sample.start}")
    print(f"Goal State: {scenario_sample.goal}\n")
    print(f"Optimal Cost: {cost:.2f}")
    print(f"Algorithm Cost: {scenario_sample.optimal_length:.2f}\n")
    print(f"Max Problem Length (Optimal): {max_problem_length:.2f}")
    print(f"Total Valid States in Map: {total_map_states}")
    print(f"States Expanded by Search: {len(states_expanded) if states_expanded else 0}")
    
    # if states_expanded is not None:
    #     print(f"States Expanded by Search: {states_expanded}")                    # comment out to view ALL expanded state tuples


if __name__ == "__main__":
    main()