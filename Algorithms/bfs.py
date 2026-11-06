from collections import deque
from Sokoban.node import Node


def BFS(s, successorsFn, isGoal):

    # Statistiques de l'algorithme
    stats = {
        "expanded": 0,
        "generated": 0,
        "max_nodes": 1,
        "pruned": 0
    }

    # Création du nœud initial
    init_node = Node(s, None, None)

    # Vérifier si l'état initial est déjà une solution
    if isGoal(init_node.state):
        return init_node, stats

    # File FIFO
    Open = deque([init_node])

    # Ensemble des états déjà découverts
    visited = {s}

    while Open:

        # Extraire le premier nœud
        current = Open.popleft()

        stats["expanded"] += 1

        # Générer les successeurs
        for action, successor in successorsFn(current.state):

            stats["generated"] += 1

            # Vérifier si l'état a déjà été visité
            if successor not in visited:

                visited.add(successor)

                # Créer le nouveau nœud
                child = Node(successor, current, action)

                # Vérifier si on a trouvé la solution
                if isGoal(successor):
                    stats["max_nodes"] = max(
                        stats["max_nodes"],
                        len(visited)
                    )
                    return child, stats

                # Ajouter le nœud à la file
                Open.append(child)

        # Mettre à jour le nombre maximal de nœuds
        stats["max_nodes"] = max(
            stats["max_nodes"],
            len(visited)
        )

    # Aucune solution trouvée
    return None, stats
