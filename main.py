
import time
from math import comb
from pathlib import Path

from game_UI.interface import show_solution
from Sokoban.state import SokobanPuzzle

from Algorithms.bfs import BFS
from Algorithms.AStar import AStar
from Algorithms.heuristics import h1, h2, h3

from Deadlock.Deadlock import (
    compute_dead_positions,
    show_dead_positions
)


# ==================================================
# PARAMETRES
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

LEVEL_FILES = [
    "levels/level1.txt",
    "levels/level2.txt",
    "levels/level3.txt",
    "levels/level4.txt",
    "levels/level5.txt"
]

SHOW_GUI = False
SHOW_DEAD_POSITIONS = True


# ==================================================
# 1. CHARGEMENT DU NIVEAU
# ==================================================

def load_level(path):
    """Lire un fichier niveau et retourner la grille."""

    with open(path, encoding="utf-8") as f:

        lines = [
            line.rstrip("\r\n")
            for line in f
            if line.strip() != ""
        ]

    if not lines:
        raise ValueError(f"Niveau vide : {path}")

    width = max(len(line) for line in lines)

    # Compléter les lignes avec des murs
    lines = [
        line.ljust(width, 'O')
        for line in lines
    ]

    return [list(line) for line in lines]


# ==================================================
# 2. VALIDATION DU NIVEAU
# ==================================================

def validate_level(grid):
    """Vérifier la cohérence du niveau."""

    player_count = sum(
        row.count('R') + row.count('.')
        for row in grid
    )

    box_count = sum(
        row.count('B') + row.count('*')
        for row in grid
    )

    target_count = sum(
        row.count('S') + row.count('.') + row.count('*')
        for row in grid
    )

    if player_count != 1:
        raise ValueError(
            f"Le niveau doit contenir un seul joueur. "
            f"Trouvé : {player_count}"
        )

    if box_count != target_count:
        raise ValueError(
            f"Nombre de caisses ({box_count}) différent "
            f"du nombre de cibles ({target_count})"
        )


# ==================================================
# 3. FACTEUR DE BRANCHEMENT EFFECTIF
# ==================================================

def effective_branching_factor(generated, depth):
    """
    Calculer le facteur de branchement effectif b*.

    N + 1 = 1 + b + b² + ... + b^d

    generated = nombre de successeurs générés
    depth = profondeur de la solution
    """

    if depth == 0 or generated == 0:
        return 0.0

    target = generated + 1

    lo = 0.0
    hi = 2.0

    # Recherche d'une borne supérieure
    while sum(hi ** k for k in range(depth + 1)) < target:
        hi *= 2

    # Dichotomie
    for _ in range(60):

        b = (lo + hi) / 2

        total = sum(
            b ** k
            for k in range(depth + 1)
        )

        if total < target:
            lo = b
        else:
            hi = b

    return round((lo + hi) / 2, 2)


# ==================================================
# 4. MAJORANT DE L'ESPACE D'ETATS
# ==================================================

def state_space_bound(grid):
    """
    Calcul du majorant :

    C(F,k) * (F-k)

    F = nombre de cases non murs
    k = nombre de caisses
    """

    free = sum(
        row.count(c)
        for row in grid
        for c in (' ', 'S', 'B', 'R', '.', '*')
    )

    boxes = sum(
        row.count('B') + row.count('*')
        for row in grid
    )

    return comb(free, boxes) * (free - boxes)


# ==================================================
# 5. EXECUTION ET MESURE DU TEMPS
# ==================================================


def run(name, algo):

    t0 = time.perf_counter()

    result = algo()

    elapsed = time.perf_counter() - t0

    print("\nDEBUG :", name)
    print("Résultat retourné :", result)
    print("Type du résultat :", type(result))

    goal, stats = result

    print("Type de goal :", type(goal))
    print("Type de stats :", type(stats))

    if not isinstance(stats, dict):
        raise TypeError(
            f"{name} retourne stats de type {type(stats).__name__} "
            f"au lieu d'un dictionnaire."
        )

    return name, goal, stats, elapsed



# ==================================================
# 6. AFFICHAGE DES RESULTATS
# ==================================================

def display_results(name, goal, stats, elapsed):

    if goal is None:

        print(f"{name:<17} Pas de solution")
        return

    generated = stats.get("generated", 0)

    b_star = effective_branching_factor(
        generated,
        goal.g
    )

    print(
        "%-17s %5d %9d %9d %9d %8d %6.2fs %6.2f"
        % (
            name,
            goal.g,
            stats.get("expanded", 0),
            generated,
            stats.get("max_nodes", 0),
            stats.get("pruned", 0),
            elapsed,
            b_star
        )
    )


# ==================================================
# 7. PROGRAMME PRINCIPAL
# ==================================================

if __name__ == "__main__":

    for level_file in LEVEL_FILES:

        path = BASE_DIR / level_file

        # Vérifier l'existence du fichier
        if not path.is_file():

            print(f"\nNiveau introuvable : {level_file}")
            continue

        # Charger le niveau
        grid = load_level(path)

        # Vérifier le niveau
        validate_level(grid)

        # Créer l'état initial
        start = SokobanPuzzle(grid)

        # Calculer les positions mortes
        dead = compute_dead_positions(grid)

        # Fonctions du problème
        succ = lambda state: state.successorFunction()

        isGoal = lambda state: state.isGoal()

        # ------------------------------------------------
        # AFFICHAGE DU NIVEAU
        # ------------------------------------------------

        print("\n" + "=" * 85)

        print("NIVEAU :", level_file)

        for row in grid:
            print("   " + "".join(row))

        print(
            "\nMajorant du nombre d'états : C(F,k)*(F-k) =",
            state_space_bound(grid)
        )

        # ------------------------------------------------
        # AFFICHAGE DES DEADLOCKS
        # ------------------------------------------------

        if SHOW_DEAD_POSITIONS:

            print(
                "\nPositions mortes (x) :",
                len(dead)
            )

            show_dead_positions(grid, dead)

        # ------------------------------------------------
        # LISTE DES ALGORITHMES
        # ------------------------------------------------

        algos = [

            (
                "BFS",
                lambda: BFS(
                    SokobanPuzzle(grid),
                    succ,
                    isGoal
                )
            ),

            (
                "A* (h1)",
                lambda: AStar(
                    SokobanPuzzle(grid),
                    succ,
                    isGoal,
                    h1
                )
            ),

            (
                "A* (h2)",
                lambda: AStar(
                    SokobanPuzzle(grid),
                    succ,
                    isGoal,
                    h2
                )
            ),

            (
                "A* (h3)",
                lambda: AStar(
                    SokobanPuzzle(grid),
                    succ,
                    isGoal,
                    h3
                )
            ),

            (
                "A* (h3)+deadlock",
                lambda: AStar(
                    SokobanPuzzle(grid),
                    succ,
                    isGoal,
                    h3,
                    dead
                )
            )

        ]

        # ------------------------------------------------
        # TABLEAU DES RESULTATS
        # ------------------------------------------------

        print(
            "\n%-17s %5s %9s %9s %9s %8s %7s %6s"
            % (
                "Algorithme",
                "Cout",
                "Developpes",
                "Generes",
                "Memoire",
                "Coupes",
                "Temps",
                "b*"
            )
        )

        last_ok = None

        # ------------------------------------------------
        # EXECUTION DES ALGORITHMES
        # ------------------------------------------------

        for name, algo in algos:

            name, goal, stats, elapsed = run(
                name,
                algo
            )

            display_results(
                name,
                goal,
                stats,
                elapsed
            )

            if goal is not None:

                last_ok = (name, goal, stats)

        # ------------------------------------------------
        # AFFICHAGE DE LA SOLUTION
        # ------------------------------------------------

        if last_ok:

            print(
                "\nSolution (%s) : %s"
                % (
                    last_ok[0],
                    last_ok[1].getSolution()
                )
            )

            print(
                "Nombre de mouvements :",
                last_ok[1].g
            )

            # ------------------------------------------------
            # INTERFACE PYGAME
            # ------------------------------------------------
            SHOW_GUI = True
            if SHOW_GUI:

                from game_UI.interface import show_solution

                show_solution(
                    last_ok[1].getPath(),
                    last_ok[1].g,
                    last_ok[2],
                    last_ok[0]
                )

        else:

            print("\nAucun algorithme n'a trouvé de solution.")

        print("\n" + "=" * 85)
