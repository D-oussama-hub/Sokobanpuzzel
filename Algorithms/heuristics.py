import itertools


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def h1(state):
    #Nombre de caisses pas encore sur une cible
    return len(state.boxes_left())


def h2(state):
    #2 * nb_left_blocks + somme des distances de Manhattan
    #(chaque caisse -> cible libre la plus proche).
    boxes = state.boxes_left()
    targets = state.free_targets()
    if not boxes:
        return 0
    total = sum(min(manhattan(b, s) for s in targets) for b in boxes)
    return 2 * len(boxes) + total


def h3(state):

    boxes = state.boxes_left()
    targets = state.free_targets()
    if not boxes:
        return 0

    best = None
    for perm in itertools.permutations(targets, len(boxes)):
        cost = sum(manhattan(b, t) for b, t in zip(boxes, perm))
        if best is None or cost < best:
            best = cost

    d_player = min(manhattan(state.player, b) for b in boxes) - 1
    return best + max(0, d_player)