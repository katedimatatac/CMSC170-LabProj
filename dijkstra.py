import heapq
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Set
from dataloading import GridMap, Scenario, load_instance

def Dijkstra(grid: GridMap, scenario: Scenario) -> Tuple[List[Tuple[int, int]], float, Set[Tuple[int, int]]]:
    start = scenario.start
    goal = scenario.goal

    if not grid.is_passable(*start):
        raise ValueError(f"Start position {start} is not passable (it's a wall or out of bounds)!")
    if not grid.is_passable(*goal):
        raise ValueError(f"Goal position {goal} is not passable (it's a wall or out of bounds)!")

    pq = [(0.0, start[0], start[1])] #priority queue stores (cummulative_cost, x, y)
    
    g_costs: Dict[Tuple[int, int], float] = {start: 0.0}
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    closed_set: Set[Tuple[int, int]] = set()

    while pq:
        current_cost, cx, cy = heapq.heappop(pq)
        current_pos = (cx, cy)
        if current_pos == goal:
            break
        if current_pos in closed_set:
            continue
        closed_set.add(current_pos)

        for nx, ny, step_cost in grid.neighbors(cx, cy): # explore valid neighbors from gridmap
            neighbor_pos = (nx, ny)

            if neighbor_pos in closed_set:
                continue

            new_cost = current_cost + step_cost

            if new_cost < g_costs.get(neighbor_pos, float('inf')):
                g_costs[neighbor_pos] = new_cost
                came_from[neighbor_pos] = current_pos
                heapq.heappush(pq, (new_cost, nx, ny))

    if goal not in g_costs:
        return [], float('inf'), closed_set

    path = []
    curr = goal
    while curr != start:
        path.append(curr)
        curr = came_from[curr]
    path.append(start)
    path.reverse()

    return path, g_costs[goal], closed_set


def visualize_search(grid: GridMap, path: List[Tuple[int, int]], closed_set: Set[Tuple[int, int]], start: Tuple[int, int], goal: Tuple[int, int]):
    arr = np.frombuffer(grid.cells, dtype=np.uint8).reshape((grid.height, grid.width))
    
    img = np.zeros((grid.height, grid.width, 3), dtype=np.float32)
    img[arr == 0] = [0.15, 0.15, 0.15]  
    img[arr == 1] = [0.92, 0.92, 0.92]  
    
    for (x, y) in closed_set:
        if 0 <= x < grid.width and 0 <= y < grid.height:
            img[y, x] = [0.40, 0.60, 0.70]
            
    for (x, y) in path:
        if 0 <= x < grid.width and 0 <= y < grid.height:
            img[y, x] = [0.90, 0.15, 0.15]

    plt.figure(figsize=(9, 9))
    plt.imshow(img, origin='upper')
    
    plt.scatter(start[0], start[1], color='limegreen', s=60, label='Start', zorder=5)
    plt.scatter(goal[0], goal[1], color='orange', s=60, label='Goal', zorder=5)
    
    plt.title(f"{grid.name} | Dijkstra | Explored: {len(closed_set)} states", fontsize=12)
    plt.legend(loc='upper right')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        map_path = sys.argv[1]
        scen_path = sys.argv[2]
        
        print("Loading instance...")
        grid, scenarios = load_instance(map_path, scen_path)
        
        if scenarios:
            test_scen = scenarios[0]
            
            print(f"Running Dijkstra on {grid.name}...")
            print(f"Start: {test_scen.start} | Goal: {test_scen.goal}")
            
            path, cost, closed_set = Dijkstra(grid, test_scen)
            
            print(f"--- Results ---")
            print(f"Path Length: {len(path)}")
            print(f"Total Path Cost: {cost:.4f}")
            print(f"Nodes Explored: {len(closed_set)}")
            
            visualize_search(grid, path, closed_set, test_scen.start, test_scen.goal)
    else:
        print("Usage: python dijkstra.py <path_to_map> <path_to_scen>")