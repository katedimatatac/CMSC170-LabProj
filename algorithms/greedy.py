import heapq
import math
from typing import Dict, List, Tuple, Set
from dataloading import GridMap, Scenario


def octile_dist(x, y, goal_x, goal_y):
    dx = abs(x - goal_x)
    dy = abs(y - goal_y)

    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


def Greedy(grid: GridMap, scenario: Scenario) -> Tuple[List[Tuple[int, int]], float, Set[Tuple[int, int]]]:

    start = scenario.start
    goal = scenario.goal

    if not grid.is_passable(*start):
        raise ValueError(f"Start position {start} is not passable!")

    if not grid.is_passable(*goal):
        raise ValueError(f"Goal position {goal} is not passable!")

    # priority queue: (heuristic, x, y)
    pq = []

    start_h = octile_dist(start[0], start[1], goal[0], goal[1])
    heapq.heappush(pq, (start_h, start[0], start[1]))

    # stores the parent of each discovered position
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

    # stores positions that have already been explored
    closed_set: Set[Tuple[int, int]] = set()

    while pq:

        # get the position with the lowest heuristic
        current_h, cx, cy = heapq.heappop(pq)
        current_pos = (cx, cy)

        # skip positions that were already explored
        if current_pos in closed_set:
            continue

        closed_set.add(current_pos)



        # check if the goal has been reached
        if current_pos == goal:
            break



        # examine neighboring positions
        for nx, ny, step_cost in grid.neighbors(cx, cy):

            neighbor_pos = (nx, ny)

            if neighbor_pos in closed_set:
                continue

            # calculate the neighbor's heuristic
            h = octile_dist(nx, ny, goal[0], goal[1])

            # record the parent for path reconstruction
            if neighbor_pos not in came_from:
                came_from[neighbor_pos] = current_pos

            # add neighbor to priority queue
            heapq.heappush(pq, (h, nx, ny))

    # check if the goal was reached
    if goal not in closed_set:
        return [], float('inf'), closed_set

    # reconstruct the path
    path = []
    curr = goal

    while curr != start:
        path.append(curr)
        curr = came_from[curr]

    path.append(start)
    path.reverse()

    # calculate the actual path cost
    total_cost = 0.0

    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]

        if x1 != x2 and y1 != y2:
            total_cost += math.sqrt(2)
        else:
            total_cost += 1.0

    return path, total_cost, closed_set
