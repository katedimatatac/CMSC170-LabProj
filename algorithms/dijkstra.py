import heapq
from typing import Dict, List, Tuple, Set
from dataloading import GridMap, Scenario

def Dijkstra(grid: GridMap, scenario: Scenario) -> Tuple[List[Tuple[int, int]], float, Set[Tuple[int, int]]]:
    start = scenario.start
    goal = scenario.goal

    if not grid.is_passable(*start):
        raise ValueError(f"Start position {start} is not passable (it's a wall or out of bounds)!")
    if not grid.is_passable(*goal):
        raise ValueError(f"Goal position {goal} is not passable (it's a wall or out of bounds)!")

    pq = [(0.0, start[0], start[1])] # priority queue stores (cumulative_cost, x, y)
    
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

        for nx, ny, step_cost in grid.neighbors(cx, cy):
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