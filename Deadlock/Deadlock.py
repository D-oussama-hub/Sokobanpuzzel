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

    # --- 2) Deadlock de ligne -----------------------------------------
 
    for (i1, j1) in corners:
        for (i2, j2) in corners:

            # ligne horizontale
            if i1 == i2 and j1 < j2:
                entre = [(i1, j) for j in range(j1 + 1, j2)]
                if entre and all(not wall(i, j) and not target(i, j)
                                 for (i, j) in entre):
                    mur_haut = all(wall(i - 1, j) for (i, j) in entre)
                    mur_bas = all(wall(i + 1, j) for (i, j) in entre)
                    if mur_haut or mur_bas:
                        dead.update(entre)

            # ligne verticale
            if j1 == j2 and i1 < i2:
                entre = [(i, j1) for i in range(i1 + 1, i2)]
                if entre and all(not wall(i, j) and not target(i, j)
                                 for (i, j) in entre):
                    mur_gauche = all(wall(i, j - 1) for (i, j) in entre)
                    mur_droite = all(wall(i, j + 1) for (i, j) in entre)
                    if mur_gauche or mur_droite:
                        dead.update(entre)

    return dead


def has_deadlock(state, dead_positions):
    """True si une caisse (hors cible) est sur une case morte."""
    for (i, j) in state.boxes_left():
        if (i, j) in dead_positions:
            return True
    return False


def show_dead_positions(grid, dead_positions):
    """Affiche la grille avec 'x' sur les cases mortes (pour le rapport)."""
    for i in range(len(grid)):
        ligne = ""
        for j in range(len(grid[i])):
            if (i, j) in dead_positions:
                ligne += 'x'
            else:
                ligne += grid[i][j] if grid[i][j] not in ('R', 'B') else ' '
        print(ligne)