
ACTIONS = [('UP', -1, 0), ('DOWN', 1, 0), ('LEFT', 0, -1), ('RIGHT', 0, 1)]


def move(state, dr, dc):
    #Applique un mouvement (dr, dc). Renvoie le nouvel état ou None
    r, c = state.player
    nr, nc = r + dr, c + dc
    target = state.grid[nr][nc]

    # 1) mur 
    if target == 'O':
        return None

    new_grid = [row[:] for row in state.grid]          # copie de la grille

    # 2) caisse : on essaie de la pousser
    if target == 'B' or target == '*':
        br, bc = nr + dr, nc + dc
        beyond = state.grid[br][bc]
        if beyond == ' ':
            new_grid[br][bc] = 'B'
        elif beyond == 'S':
            new_grid[br][bc] = '*'
        else:                                          # mur ou autre caisse
            return None
        new_grid[nr][nc] = 'R' if target == 'B' else '.'

      # 3) case libre 
    else:
        new_grid[nr][nc] = 'R' if target == ' ' else '.'

      # ancienne case du joueur
    new_grid[r][c] = ' ' if state.grid[r][c] == 'R' else 'S'

    return type(state)(new_grid)


def successor_function(state):
    #Liste de paires (action, état successeur)
    successors = []
    for action, dr, dc in ACTIONS:
        new_state = move(state, dr, dc)
        if new_state is not None:
            successors.append((action, new_state))
    return successors