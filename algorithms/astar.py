"""
    A* Algorithm for Maze Pathfinding

    from Group ABCD W-3L by Karl Margueritte V. Dimatatac

    PL Used: Python

"""
# import packages
import math

# class representing a node in the A* search tree
class Node:
    def __init__(self, matrix, g=0, h=0, parent=None, move=None):
        self.matrix = matrix
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent
        self.move = move


# heuristic function     = Octile Distance for 8-Way Navigation  h(n) = max(dx, dy) + (sqrt(2) - 1) * min(dx, dy)
def octile_dist(self, cardinal_cost=1.0):
    dx = abs(node[0] - goal[0])
    dy = abs(node[1] - goal[1])
    diagonal_cost = cardinal_cost * math.sqrt(2)
    return cardinal_cost * max(dx, dy) + (diagonal_cost - cardinal_cost) * min(dx, dy)


def Astar(self):        # the main search algorithm used
    initial_h = self.octiledist(self.matrix)
    initialNode = Node(self.matrix, g=0, h=initial_h, parent=None)
    openList = [initialNode]
    closedList = []
    actions = ['N', 'S', 'W', 'E', 'NW', 'NE', 'SW', 'SE']

    while len(openList)>0:
        # bestNode = openList.removeMinF();
        bestNode = min(openList, key=lambda node: node.f)
        openList.remove(bestNode)
        closedList.append(bestNode)

        # if(GoalTest(bestNode)) return bestNode;
        if bestNode.matrix == self.goal:
            path = []
            curr = bestNode
            while curr:
                path.append(curr)
                curr = curr.parent
            path.reverse()

            print(f"\n--- A* Search Path Found ({len(path) - 1} moves) ---")
            for step, node in enumerate(path):
                print(f"Step {step} | g(n)={node.g}, h(n)={node.h}, f(n)={node.f}:")

            self.matrix = [row[:] for row in bestNode.matrix]
            return bestNode

        # for a in Actions(bestNode)
        for a in actions:
            res_matrix = self.test_move(bestNode.matrix, a)
            if res_matrix is not None:
                g = bestNode.g + 1
                h = self.manhattan(res_matrix)
                x = Node(res_matrix, g=g, h=h, parent=bestNode, move=a)

                in_open = any(node.matrix == x.matrix for node in openList)
                in_closed = any(node.matrix == x.matrix for node in closedList)

                if (not in_open and not in_closed):
                    openList.append(x)
                elif in_open:
                    duplicate = next(node for node in openList if node.matrix == x.matrix)
                    if x.f < duplicate.f:
                        openList.remove(duplicate)
                        openList.append(x)

    print("No solution found.")
    return None