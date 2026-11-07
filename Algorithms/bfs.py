from collections import deque
from Sokoban.node import Node


def BFS(s, successorsFn, isGoal):
    stats = {"expanded": 0, "generated": 0, "max_nodes": 1, "pruned": 0}

    init_node = Node(s, None, None)
    
    # File FIFO et ensemble des visités
    Open = deque([init_node])
    visited = {s}

    while Open:
        # Extraire le premier nœud
        current = Open.popleft()

        # TEST DE BUT ICI 
        if isGoal(current.state):
            stats["max_nodes"] = max(stats["max_nodes"], len(visited))
            return current, stats

        stats["expanded"] += 1

        # Générer les successeurs
        for action, successor in successorsFn(current.state):
            stats["generated"] += 1

            if successor not in visited:
                visited.add(successor)
                child = Node(successor, current, action)
                Open.append(child)

        stats["max_nodes"] = max(stats["max_nodes"], len(visited))

    return None, stats