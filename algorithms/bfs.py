"""
    BFS Algorithm for Maze Pathfinding

    from Group ABCD W-3L by Allen Gabriel R. Casuga
"""
# import packages
from collections import deque

class Node:
    def __init__(self, x, y, g=0, parent=None):
        self.x = x
        self.y = y
        self.g = g
        self.parent = parent


# BFS finds the path with the fewest moves, not necessarily the lowest cost
def BFS(grid, scenario):
    start_x, start_y = scenario.start
    goal_x, goal_y = scenario.goal

    start_node = Node(start_x, start_y, g=0)

    openList = deque()
    openList.append(start_node)
    visited = {(start_x, start_y)}

    # counter for the number of states expanded
    expanded_states = 0

    while len(openList) > 0:
        currNode = openList.popleft()
        expanded_states += 1  # inc when a state is evaluated

        # goal check
        if (currNode.x, currNode.y) == (goal_x, goal_y):
            path = []
            curr = currNode
            while curr:
                path.append((curr.x, curr.y))
                curr = curr.parent
            path.reverse()
            # return path, total cost, and the explored coordinates
            return path, currNode.g, list(visited)

        for nx, ny, step_cost in grid.neighbors(currNode.x, currNode.y):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                nextNode = Node(nx, ny, g=currNode.g + step_cost, parent=currNode)
                openList.append(nextNode)

    return None, 0, list(visited)