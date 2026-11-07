import argparse
import time

from game_UI.interface import run, load_level, solve, H_NAMES, NB_LEVELS
from Sokoban.state import SokobanPuzzle


def benchmark(levels):
    """Compare BFS et A* (h1, h2, h3, avec deadlock) sur chaque niveau."""
    print(f"{'Niveau':<7}{'Algo':<10}{'Long.':>6}{'Temps(s)':>10}"
          f"{'Dével.':>9}{'Générés':>10}{'MaxNœuds':>10}")
    print("-" * 62)

    for n in levels:
        configs = [("BFS", None)] + [("A*", h) for h in H_NAMES]
        for algo, h in configs:
            puzzle = SokobanPuzzle(load_level(n))
            actions, stats, elapsed = solve(puzzle, algo, h or "h1",
                                            use_dead=True)
            label = "BFS" if algo == "BFS" else f"A*-{h}"
            length = len(actions) if actions is not None else "-"
            print(f"{n:<7}{label:<10}{length!s:>6}{elapsed:>10.3f}"
                  f"{stats['expanded']:>9}{stats['generated']:>10}"
                  f"{stats['max_nodes']:>10}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Sokoban - BFS / A*")
    parser.add_argument("--level", type=int, default=1,
                        choices=range(1, NB_LEVELS + 1),
                        help="niveau à lancer dans l'interface")
    parser.add_argument("--bench", action="store_true",
                        help="comparer BFS et A* (h1,h2,h3) en console")
    args = parser.parse_args()

    if args.bench:
        benchmark(range(1, NB_LEVELS + 1))
    else:
        run(args.level)


if __name__ == "__main__":
    main()