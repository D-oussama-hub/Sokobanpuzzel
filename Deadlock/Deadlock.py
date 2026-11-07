def compute_dead_positions(grid):
    """Retourne l'ensemble des cases (i, j) où une caisse serait perdue."""

    def wall(i, j):
        # hors grille ou ligne plus courte : on considère que c'est un mur
        if i < 0 or i >= len(grid) or j < 0 or j >= len(grid[i]):
            return True
        return grid[i][j] == 'O'

    def target(i, j):
        return grid[i][j] in ('S', '.', '*')

    # --- 1) Deadlock de coin ------------------------------------------

    corners = []
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if wall(i, j) or target(i, j):
                continue
            mur_vertical = wall(i - 1, j) or wall(i + 1, j)
            mur_horizontal = wall(i, j - 1) or wall(i, j + 1)
            if mur_vertical and mur_horizontal:
                corners.append((i, j))

    dead = set(corners)

    # 2) Deadlock de ligne 

    for (i1, j1) in corners:
        for (i2, j2) in corners:

            # LIGNE HORIZONTALE 
            if i1 == i2 and j1 < j2:

                # 1) Construire la liste des cases entre les deux coins
                entre = []
                for j in range(j1 + 1, j2):
                    entre.append((i1, j))

                if len(entre) > 0:

                    # 3) Vérifier qu'il n'y a ni mur ni cible entre les coins
                    segment_libre = True
                    for (i, j) in entre:
                        if wall(i, j) or target(i, j):
                            segment_libre = False

                    # 4) Vérifier si un mur longe le segment en haut ou en bas
                    mur_haut = True
                    mur_bas = True
                    for (i, j) in entre:
                        if not wall(i - 1, j):      
                            mur_haut = False
                        if not wall(i + 1, j):      
                            mur_bas = False

                    if segment_libre and (mur_haut or mur_bas):
                        for case in entre:
                            dead.add(case)

            # LIGNE VERTICALE 
            if j1 == j2 and i1 < i2:

                # 1) Construire la liste des cases entre les deux coins
                entre = []
                for i in range(i1 + 1, i2):
                    entre.append((i, j1))

                if len(entre) > 0:

                    # 3) Vérifier qu'il n'y a ni mur ni cible entre les coins
                    segment_libre = True
                    for (i, j) in entre:
                        if wall(i, j) or target(i, j):
                            segment_libre = False

                    # 4) Vérifier si un mur longe le segment à gauche ou à droite
                    mur_gauche = True
                    mur_droite = True
                    for (i, j) in entre:
                        if not wall(i, j - 1):      
                            mur_gauche = False
                        if not wall(i, j + 1):     
                            mur_droite = False

                    # 5) Si tout est bon, toutes ces cases sont mortes
                    if segment_libre and (mur_gauche or mur_droite):
                        for case in entre:
                            dead.add(case)

    return dead


def has_deadlock(state, dead_positions):
    """True si une caisse (hors cible) est sur une case morte."""
    for (i, j) in state.boxes_left():
        if (i, j) in dead_positions: # verifie si la caisse est sur une case morte
            return True
    return False