"""
    A* Algorithm for Maze Pathfinding

    from Group ABCD W-3L by Karl Margueritte V. Dimatatac

"""
# import packages
import math
import heapq

# class representing a node in the A* search tree
class Node:
    def __init__(self, x, y, g=0, h=0, parent=None):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent

    # Required for heapq to compare nodes
    def __lt__(self, other):
        return self.f < other.f


# heuristic function     = Octile Distance for 8-Way Navigation  h(n) = max(dx, dy) + (sqrt(2) - 1) * min(dx, dy)
def octile_dist(x, y, goal_x, goal_y):
    dx = abs(x - goal_x)
    dy = abs(y - goal_y)
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


# Astar coordiante-based algorithm: uses python heapq
def Astar(grid, scenario):
    start_x, start_y = scenario.start
    goal_x, goal_y = scenario.goal
    
    initial_h = octile_dist(start_x, start_y, goal_x, goal_y)
    start_node = Node(start_x, start_y, g=0, h=initial_h)
    
    openList = []
    heapq.heappush(openList, start_node)
    g_values = {(start_x, start_y): 0}
    
    # counter for the number of states expanded
    expanded_states = 0

    while len(openList) > 0:
        currNode = heapq.heappop(openList)
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
            return path, currNode.g, list(g_values.keys())

        for nx, ny, step_cost in grid.neighbors(currNode.x, currNode.y):
            new_g = currNode.g + step_cost
            if new_g < g_values.get((nx, ny), float('inf')):
                g_values[(nx, ny)] = new_g
                h = octile_dist(nx, ny, goal_x, goal_y)
                nextNode = Node(nx, ny, g=new_g, h=h, parent=currNode)
                heapq.heappush(openList, nextNode)

    return None, 0, list(g_values.keys())