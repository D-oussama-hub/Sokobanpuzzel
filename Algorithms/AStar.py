import heapq
import itertools
from Sokoban.node import Node
from Deadlock.Deadlock import has_deadlock


def AStar(s, successorsFn, isGoal, h, dead=None):
    stats = {"expanded": 0, "generated": 0, "max_nodes": 1, "pruned": 0}

    if dead is not None and has_deadlock(s, dead):
        return None, stats                       # niveau déjà bloqué

    init_node = Node(s, None, None)
    init_node.setF(h)                            # f = 0 + h(s)

    Open = []                                    # file de priorité sur f
    open_dict = {init_node.state: init_node}
    closed_dict = {}
    counter = itertools.count()                  # départage les f égaux
    heapq.heappush(Open, (init_node.f, next(counter), init_node))

    while len(Open) > 0:
        f, _, current = heapq.heappop(Open)      # plus petit f

        # nœud périmé (remplacé par un meilleur) : on l'ignore
        if open_dict.get(current.state) is not current:
            continue
        del open_dict[current.state]

        if isGoal(current.state):                # test du but à la sortie de Open
            return current, stats

        closed_dict[current.state] = current
        stats["expanded"] += 1

        for action, successor in successorsFn(current.state):
            if dead is not None and has_deadlock(successor, dead):
                continue          # on ne développe pas un état perdu
            child = Node(successor, current, action)
            child.setF(h)                        # f = g + h
            stats["generated"] += 1

            if child.state not in open_dict and child.state not in closed_dict:
                open_dict[child.state] = child
                heapq.heappush(Open, (child.f, next(counter), child))

            elif child.state in open_dict and open_dict[child.state].f > child.f:
                open_dict[child.state] = child
                heapq.heappush(Open, (child.f, next(counter), child))

            elif child.state in closed_dict and closed_dict[child.state].f > child.f:
                del closed_dict[child.state]
                open_dict[child.state] = child
                heapq.heappush(Open, (child.f, next(counter), child))

        stats["max_nodes"] = max(stats["max_nodes"],
                                 len(open_dict) + len(closed_dict))

    return None, stats