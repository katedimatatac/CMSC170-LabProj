import heapq
from typing import Dict, List, Set, Tuple
from dataloading import GridMap, Scenario
from tuning import get_heuristic, make_tie_key


def Astar(
    grid: GridMap,
    scenario: Scenario,
    heuristic: str = "octile",
    tie_breaker: str = "low_h",
) -> Tuple[List[Tuple[int, int]], float, Set[Tuple[int, int]]]:
    """A* search.

    heuristic   : "octile" | "euclidean" | "manhattan"
    tie_breaker : "fifo" | "high_g" | "low_h"  (how equal-f nodes are ordered)
    Defaults (octile + low_h) match the original behaviour.
    """
    h_fn = get_heuristic(heuristic)
    start = scenario.start
    goal = scenario.goal
    goal_x, goal_y = goal

    order = 0
    start_h = h_fn(start[0], start[1], goal_x, goal_y)
    # Heap item: (f, tie_key, order, g, x, y). `order` is unique, so ties never
    # fall through to comparing g/x/y.
    pq = [(round(start_h, 9), make_tie_key(tie_breaker, 0.0, start_h, order), order, 0.0, start[0], start[1])]

    g_costs: Dict[Tuple[int, int], float] = {start: 0.0}
    old_set: Dict[Tuple[int, int], Tuple[int, int]] = {}
    closed_set: Set[Tuple[int, int]] = set()

    while pq:
        _, _, _, curr_g, cx, cy = heapq.heappop(pq)
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

                h = h_fn(nx, ny, goal_x, goal_y)
                order += 1
                # round(f, 9): mathematically equal f values (e.g. sums of sqrt(2))
                # can differ by ~1e-15 in floating point, which would hide ties.
                f = round(new_g + h, 9)
                heapq.heappush(pq, (f, make_tie_key(tie_breaker, new_g, h, order), order, new_g, nx, ny))

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
