def compute_dead_positions(grid):
    """Retourne l'ensemble des cases (i, j) où une caisse serait perdue."""
    rows = len(grid)
    cols = len(grid[0])

    def wall(i, j):
        return grid[i][j] == 'O'

    def target(i, j):
        return grid[i][j] in ('S', '.', '*')

    # --- 1) Corner deadlock : case non cible, entourée de 2 murs en coin ---
    corners = []
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if wall(i, j) or target(i, j):
                continue
            mur_vertical = wall(i - 1, j) or wall(i + 1, j)
            mur_horizontal = wall(i, j - 1) or wall(i, j + 1)
            if mur_vertical and mur_horizontal:
                corners.append((i, j))

    dead = set(corners)

    # --- 2) Line deadlock : deux coins reliés par une ligne droite le long
    #        d'un mur continu, sans cible sur la ligne ---
    for (i1, j1) in corners:
        for (i2, j2) in corners:

            # ligne horizontale (même ligne, j1 < j2)
            if i1 == i2 and j1 < j2:
                cells = [(i1, j) for j in range(j1, j2 + 1)]
                if all(not wall(i, j) and not target(i, j) for (i, j) in cells):
                    mur_haut = all(wall(i - 1, j) for (i, j) in cells)
                    mur_bas = all(wall(i + 1, j) for (i, j) in cells)
                    if mur_haut or mur_bas:
                        dead.update(cells)

            # ligne verticale (même colonne, i1 < i2)
            if j1 == j2 and i1 < i2:
                cells = [(i, j1) for i in range(i1, i2 + 1)]
                if all(not wall(i, j) and not target(i, j) for (i, j) in cells):
                    mur_gauche = all(wall(i, j - 1) for (i, j) in cells)
                    mur_droite = all(wall(i, j + 1) for (i, j) in cells)
                    if mur_gauche or mur_droite:
                        dead.update(cells)

    return dead


def has_deadlock(state, dead_positions):
    """True si une caisse (hors cible) est sur une position morte."""
    for (i, j) in dead_positions:
        if state.grid[i][j] == 'B':
            return True
    return False


def show_dead_positions(grid, dead_positions):
    """Affiche la grille avec 'x' sur les positions mortes (pour le rapport)."""
    for i in range(len(grid)):
        ligne = ""
        for j in range(len(grid[i])):
            if (i, j) in dead_positions:
                ligne += 'x'
            else:
                ligne += grid[i][j] if grid[i][j] not in ('R', 'B') else ' '
        print(ligne)