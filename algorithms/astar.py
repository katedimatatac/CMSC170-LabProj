import heapq
import math
from typing import Dict, List, Set, Tuple
from dataloading import GridMap, Scenario

SQRT2_MINUS_1 = math.sqrt(2) - 1.0  # Precompute constant once


def Astar(grid: GridMap, scenario: Scenario) -> Tuple[List[Tuple[int, int]], float, Set[Tuple[int, int]]]:
    start = scenario.start
    goal = scenario.goal
    goal_x, goal_y = goal

    dx = abs(start[0] - goal_x)
    dy = abs(start[1] - goal_y)
    start_h = (dx if dx > dy else dy) + SQRT2_MINUS_1 * (dy if dx > dy else dx)

    # Tuple: (f_cost, h_cost, g_cost, x, y) -> tie-breaks cleanly on lower h_cost
    pq = [(start_h, start_h, 0.0, start[0], start[1])]

    g_costs: Dict[Tuple[int, int], float] = {start: 0.0}
    old_set: Dict[Tuple[int, int], Tuple[int, int]] = {}
    closed_set: Set[Tuple[int, int]] = set()

    while pq:
        f_cost, h_cost, curr_g, cx, cy = heapq.heappop(pq)
        currpos = (cx, cy)

        if currpos == goal:
            break

        if currpos in closed_set:
            continue
        closed_set.add(currpos)

        for nx, ny, step_cost in grid.neighbors(cx, cy):
            nbpos = (nx, ny)
            if nbpos in closed_set:
                continue

            new_g = curr_g + step_cost
            if new_g < g_costs.get(nbpos, float('inf')):
                g_costs[nbpos] = new_g
                old_set[nbpos] = currpos

                # Inline octile distance (avoids Python function-call overhead)
                dx = abs(nx - goal_x)
                dy = abs(ny - goal_y)
                h = (dx if dx > dy else dy) + SQRT2_MINUS_1 * (dy if dx > dy else dx)

                heapq.heappush(pq, (new_g + h, h, new_g, nx, ny))

    if goal not in g_costs:
        return [], float('inf'), closed_set

    path = []
    curr = goal
    while curr != start:
        path.append(curr)
        curr = old_set[curr]
    path.append(start)
    path.reverse()

    return path, g_costs[goal], closed_set