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

    filespec = "1-0"            # modify this to specify the map and scenario file
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

    #       # select random scenario
    scenario_sample = scenarios[3391] #scenarios[r.randint(0, len(scenarios) - 1)]
    scenario_num = scenarios.index(scenario_sample)
    
    
    # run algorithm (Change method as needed)
    path, cost, states_expanded = Astar(grid, scenario_sample)
    output_filename = f"{grid.name}_astar.png"


    # path, cost, states_expanded = Dijkstra(grid, scenario_sample)
    # output_filename = f"{grid.name}_dijkstra.png"

    print_run_metrics(grid, scenarios, states_expanded)

    
    

    visualize_search(                   # call visuals.py to generate solved maze figure
        grid=grid,
        scenario=scenario_sample,
        explored_coords=states_expanded,
        path=path,
        output_dir="images",                # generated images will be saved in "images" directory 
        filename=output_filename
    )

def print_run_metrics(grid, scenarios, states_expanded=None):
    max_problem_length = max(s.optimal_length for s in scenarios) if scenarios else 0
    total_map_states = grid.num_passable()

    print("\n--- Dataset and Search Metrics ---\n")
    print(f"Map Name: {grid.name}")                    
    print(f"Scenario Index: {scenario_num}")
    print(f"Start State: {scenario_sample.start}")        
    print(f"Goal State: {scenario_sample.goal}\n")         
    print(f"Algorithm Cost: {cost:.2f}")
    print(f"Optimal Cost (from .scen): {scenario_sample.optimal_length:.2f}\n")
    print(f"Max Problem Length (Optimal): {max_problem_length:.2f}")
    print(f"Total Valid States in Map: {total_map_states}")
    print(f"States Expanded by Search: {len(states_expanded) if states_expanded else 0}")

if __name__ == "__main__":
    main()