import heapq
import math
from typing import Dict, List, Tuple, Set
from data.dataloading import GridMap, Scenario
from eval.tuning import get_heuristic, make_tie_key


def Greedy(
    grid: GridMap,
    scenario: Scenario,
    heuristic: str = "octile",
    tie_breaker: str = "fifo",
) -> Tuple[List[Tuple[int, int]], float, Set[Tuple[int, int]]]:
    """Greedy best-first search (priority = h only).

    heuristic   : "octile" | "euclidean" | "manhattan"
    tie_breaker : "fifo" | "high_g" | "low_h"  (how equal-h nodes are ordered).
    Note: in Greedy, "low_h" is a no-op (ties already have equal h), so it
    behaves like insertion order; the meaningful options are "fifo" and "high_g".
    """
    h_fn = get_heuristic(heuristic)

    start = scenario.start
    goal = scenario.goal

    if not grid.is_passable(*start):
        raise ValueError(f"Start position {start} is not passable!")

    if not grid.is_passable(*goal):
        raise ValueError(f"Goal position {goal} is not passable!")

    order = 0
    start_h = h_fn(start[0], start[1], goal[0], goal[1])
    # Heap item: (h, tie_key, order, g, x, y)
    pq = [(round(start_h, 9), make_tie_key(tie_breaker, 0.0, start_h, order), order, 0.0, start[0], start[1])]

    # parent of each discovered position
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    # g along the (first-discovered) parent chain; only used for the high_g tie-break
    g_costs: Dict[Tuple[int, int], float] = {start: 0.0}

    closed_set: Set[Tuple[int, int]] = set()

    while pq:
        _, _, _, curr_g, cx, cy = heapq.heappop(pq)
        current_pos = (cx, cy)

        if current_pos in closed_set:
            continue

        closed_set.add(current_pos)

        if current_pos == goal:
            break

        for nx, ny, step_cost in grid.neighbors(cx, cy):
            neighbor_pos = (nx, ny)

            if neighbor_pos in closed_set:
                continue

            h = h_fn(nx, ny, goal[0], goal[1])

            if neighbor_pos not in came_from:
                came_from[neighbor_pos] = current_pos
                g_costs[neighbor_pos] = curr_g + step_cost

            new_g = g_costs[neighbor_pos]
            order += 1
            heapq.heappush(pq, (round(h, 9), make_tie_key(tie_breaker, new_g, h, order), order, new_g, nx, ny))

    if goal not in closed_set:
        return [], float('inf'), closed_set

    path = []
    curr = goal
    while curr != start:
        path.append(curr)
        curr = came_from[curr]

    path.append(start)
    path.reverse()

    total_cost = 0.0
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        if x1 != x2 and y1 != y2:
            total_cost += math.sqrt(2)
        else:
            total_cost += 1.0

    return path, total_cost, closed_set
