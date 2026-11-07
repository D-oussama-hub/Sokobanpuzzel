import os
import time
import queue
import threading
import traceback
import pygame

from Sokoban.state import SokobanPuzzle
from Sokoban.moves import move, ACTIONS
from Algorithms.bfs import BFS
from Algorithms.AStar import AStar
from Algorithms.heuristics import h1, h2, h3
from Deadlock.Deadlock import compute_dead_positions

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVELS_DIR = os.path.join(ROOT, "Levels")
NB_LEVELS = 5

HEURISTICS = {"h1": h1, "h2": h2, "h3": h3}
H_NAMES = list(HEURISTICS.keys())
H_DESC = {
    "h1": "h1 : nombre de caisses pas sur une cible",
    "h2": "h2 : 2*nb caisses + distances de Manhattan",
    "h3": "h3 : affectation optimale + distance joueur",
}
ACTION_DELTA = {name: (dr, dc) for name, dr, dc in ACTIONS}

# Touches de niveau : QWERTY et AZERTY
LEVEL_KEYS = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
              "&": 1, "é": 2, '"': 3, "'": 4, "(": 5}

CELL_MAX = 60
HUD_H = 190
MENU_W, MENU_H = 800, 560
PLAY_MIN_W = 820
STEP_MS = 120                      # vitesse de l'animation

C_BG = (30, 30, 36)
C_WALL = (70, 70, 80)
C_FLOOR = (225, 220, 205)
C_TARGET = (200, 60, 60)
C_BOX = (160, 105, 50)
C_BOX_OK = (70, 160, 80)
C_PLAYER = (50, 100, 210)
C_TEXT = (240, 240, 240)
C_TEXT_DIS = (110, 110, 118)
C_BTN = (60, 63, 80)
C_BTN_HOVER = (85, 90, 115)
C_BTN_ON = (50, 100, 210)
C_BTN_DIS = (45, 45, 52)
C_GO = (40, 140, 70)
C_OK = (120, 220, 140)


# ----------------------------------------------------------------------
# Chargement d'un niveau
# ----------------------------------------------------------------------
def load_level(n):
    """Lit Levels/level<n>.txt et renvoie une grille fermée (liste de listes).

    - les lignes courtes sont complétées avec des murs 'O'
      (au lieu d'espaces, sinon le joueur pourrait "sortir" du plateau) ;
    - un cadre de murs est ajouté autour de la grille, ce qui
      garantit que move() ne sort jamais des limites.
    """
    path = os.path.join(LEVELS_DIR, f"level{n}.txt")
    with open(path, encoding="utf-8") as f:
        lines = [l.rstrip("\r\n") for l in f.readlines()]
    while lines and lines[-1].strip() == "":
        lines.pop()
    width = max(len(l) for l in lines)

    grid = [list(l.ljust(width, 'O')) for l in lines]
    border = ['O'] * (width + 2)
    return [border[:]] + [['O'] + row + ['O'] for row in grid] + [border[:]]

def check_level(grid):
    """Renvoie un message d'erreur si le niveau est invalide, sinon None."""
    p = SokobanPuzzle(grid)
    nb, nt = len(p.boxes_left()), len(p.free_targets())
    if p.player is None:
        return "Niveau invalide : aucun joueur (R) dans la grille."
    if nb == 0:
        return "Niveau invalide : aucune caisse (B) dans la grille."
    if nt < nb:
        return (f"Niveau invalide : {nb} caisses mais seulement "
                f"{nt} cible(s) libre(s) (S).")
    return None


# ----------------------------------------------------------------------
# Résolution
# ----------------------------------------------------------------------
def solve(puzzle, algo, h_name, use_dead):
    """Lance BFS ou A*. Renvoie (liste d'actions | None, stats, temps)."""
    dead = compute_dead_positions(puzzle.grid) if use_dead else None
    succ = lambda s: s.successorFunction()
    goal = lambda s: s.isGoal()

    t0 = time.perf_counter()
    if algo == "BFS":
        node, stats = BFS(puzzle, succ, goal)
    else:
        node, stats = AStar(puzzle, succ, goal, HEURISTICS[h_name], dead)
    elapsed = time.perf_counter() - t0

    actions = node.getSolution() if node is not None else None
    return actions, stats, elapsed


# ----------------------------------------------------------------------
# Interface Pygame
# ----------------------------------------------------------------------
class Game:
    def __init__(self, level=1):
        pygame.init()
        pygame.display.set_caption("Sokoban - BFS / A*")
        self.font = pygame.font.SysFont("consolas", 16)
        self.big = pygame.font.SysFont("consolas", 20, bold=True)
        self.title = pygame.font.SysFont("consolas", 28, bold=True)
        self.clock = pygame.time.Clock()

        # choix de l'utilisateur
        self.algo = "A*"
        self.h_idx = 2
        self.use_dead = True
        self.level = level
        self.preview = load_level(level)
        self.warning = check_level(self.preview)

        # état de la résolution
        self.job = 0
        self.results = queue.Queue()
        self.phase = "menu"          # menu | solving | animating | done
        self.mode = "menu"           # menu | play
        self.buttons = []
        self.plan = []
        self.solution = None
        self.result = None
        self.message = ""
        self.label = ""
        self.last_step = 0
        self.t_start = 0
        self.screen = pygame.display.set_mode((MENU_W, MENU_H))

    # -- choix du menu ---------------------------------------------------
    def set_level(self, n):
        self.level = n
        self.preview = load_level(n)
        self.warning = check_level(self.preview)

    def set_algo(self, a):
        self.algo = a

    def set_h(self, k):
        self.h_idx = k

    def toggle_dead(self):
        self.use_dead = not self.use_dead

    # -- navigation ------------------------------------------------------
    def go_menu(self):
        self.job += 1                # ignore toute résolution en cours
        self.mode = "menu"
        self.phase = "menu"
        self.screen = pygame.display.set_mode((MENU_W, MENU_H))

    def start_play(self):
        grid = load_level(self.level)
        rows, cols = len(grid), len(grid[0])
        self.cell = max(30, min(CELL_MAX, 460 // rows, 760 // cols))
        w = max(cols * self.cell, PLAY_MIN_W)
        h = rows * self.cell + HUD_H
        self.ox = (w - cols * self.cell) // 2
        self.screen = pygame.display.set_mode((w, h))

        self.mode = "play"
        self.phase = "solving"
        self.puzzle = SokobanPuzzle(grid)
        self.initial = self.puzzle
        self.moves_done = 0
        self.plan = []
        self.solution = None
        self.result = None
        self.t_start = time.time()

        h_name = H_NAMES[self.h_idx]
        if self.algo == "BFS":
            self.label = "BFS"
        else:
            dl = "deadlock ON" if self.use_dead else "deadlock OFF"
            self.label = f"A* ({h_name}, {dl})"
        self.message = "Résolution en cours..."

        self.job += 1
        job, puzzle = self.job, self.puzzle
        algo, use_dead = self.algo, self.use_dead

        def work():
            try:
                actions, stats, elapsed = solve(puzzle, algo, h_name, use_dead)
                self.results.put(dict(job=job, actions=actions, stats=stats,
                                      elapsed=elapsed, error=None))
            except Exception as e:
                traceback.print_exc()
                self.results.put(dict(job=job, actions=None, stats=None,
                                      elapsed=0, error=repr(e)))

        threading.Thread(target=work, daemon=True).start()

    def replay(self):
        if self.solution is None or self.phase == "solving":
            return
        self.puzzle = self.initial
        self.moves_done = 0
        self.plan = list(self.solution)
        self.phase = "animating"
        self.message = "Rejeu de la solution..."
        self.last_step = pygame.time.get_ticks()

    # -- résultats et animation -----------------------------------------
    def check_results(self):
        while not self.results.empty():
            r = self.results.get_nowait()
            if r["job"] != self.job:         # résultat périmé
                continue
            self.result = r
            if r["error"]:
                self.phase = "done"
                self.message = f"Erreur : {r['error'][:90]}"
            elif r["actions"] is None:
                self.phase = "done"
                self.message = "Aucune solution trouvée."
            else:
                self.solution = r["actions"]
                self.plan = list(self.solution)
                self.phase = "animating"
                self.message = "L'algorithme joue la solution..."
                self.last_step = pygame.time.get_ticks()

    def animate(self):
        if self.phase != "animating":
            return
        now = pygame.time.get_ticks()
        if now - self.last_step < STEP_MS:
            return
        self.last_step = now
        if self.plan:
            dr, dc = ACTION_DELTA[self.plan.pop(0)]
            new = move(self.puzzle, dr, dc)
            if new is not None:
                self.puzzle = new
                self.moves_done += 1
        if not self.plan:
            self.phase = "done"
            self.message = "Problème résolu !"

    # -- outils de dessin ------------------------------------------------
    def text(self, txt, x, y, font=None, color=C_TEXT):
        surf = (font or self.font).render(txt, True, color)
        self.screen.blit(surf, (x, y))

    def btn(self, label, x, y, w, h, cb, active=False, enabled=True,
            color=None):
        rect = pygame.Rect(x, y, w, h)
        mouse = pygame.mouse.get_pos()
        if not enabled:
            bg, fg = C_BTN_DIS, C_TEXT_DIS
        elif active:
            bg, fg = C_BTN_ON, C_TEXT
        elif color is not None:
            bg, fg = color, C_TEXT
        elif rect.collidepoint(mouse):
            bg, fg = C_BTN_HOVER, C_TEXT
        else:
            bg, fg = C_BTN, C_TEXT
        pygame.draw.rect(self.screen, bg, rect, border_radius=8)
        surf = self.font.render(label, True, fg)
        self.screen.blit(surf, (x + (w - surf.get_width()) // 2,
                                y + (h - surf.get_height()) // 2))
        if enabled:
            self.buttons.append((rect, cb))

    def draw_cell(self, ch, x, y, cell):
        rect = pygame.Rect(x, y, cell, cell)
        if ch == 'O':
            pygame.draw.rect(self.screen, C_WALL, rect)
            pygame.draw.rect(self.screen, C_BG, rect, 1)
            return

        pygame.draw.rect(self.screen, C_FLOOR, rect)
        pygame.draw.rect(self.screen, (200, 195, 180), rect, 1)
        cx, cy = x + cell // 2, y + cell // 2

        if ch in ('S', '.', '*'):
            pygame.draw.circle(self.screen, C_TARGET, (cx, cy), cell // 6)

        if ch in ('B', '*'):
            color = C_BOX_OK if ch == '*' else C_BOX
            box = rect.inflate(-cell // 4, -cell // 4)
            pygame.draw.rect(self.screen, color, box,
                             border_radius=max(3, cell // 10))
            pygame.draw.rect(self.screen, (60, 40, 20), box,
                             max(2, cell // 20),
                             border_radius=max(3, cell // 10))

        if ch in ('R', '.'):
            pygame.draw.circle(self.screen, C_PLAYER, (cx, cy), cell // 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy),
                               cell // 3, 2)

    def draw_grid(self, grid, ox, oy, cell):
        for i, row in enumerate(grid):
            for j, ch in enumerate(row):
                self.draw_cell(ch, ox + j * cell, oy + i * cell, cell)

    # -- écran menu ------------------------------------------------------
    def draw_menu(self):
        astar = self.algo == "A*"
        dis = None if astar else C_TEXT_DIS

        self.text("Sokoban - Résolution automatique", 20, 15, self.title)

        self.text("1. Algorithme", 20, 70, self.big)
        self.btn("BFS", 20, 100, 120, 40, lambda: self.set_algo("BFS"),
                 self.algo == "BFS")
        self.btn("A*", 150, 100, 120, 40, lambda: self.set_algo("A*"),
                 astar)

        self.text("2. Heuristique (A* seulement)", 20, 160, self.big,
                  dis or C_TEXT)
        for k, name in enumerate(H_NAMES):
            self.btn(name, 20 + k * 110, 190, 100, 36,
                     lambda k=k: self.set_h(k),
                     astar and self.h_idx == k, enabled=astar)
        desc = (H_DESC[H_NAMES[self.h_idx]] if astar
                else "BFS n'utilise pas d'heuristique")
        self.text(desc, 20, 235, self.font, dis or C_TEXT)
        self.btn(f"Détection deadlock : {'ON' if self.use_dead else 'OFF'}",
                 20, 268, 320, 34, self.toggle_dead, False, enabled=astar)

        self.text("3. Grille", 20, 320, self.big)
        for n in range(1, NB_LEVELS + 1):
            self.btn(f"Niv {n}", 20 + (n - 1) * 80, 350, 72, 36,
                     lambda n=n: self.set_level(n), n == self.level)

        choice = "BFS" if not astar else f"A* ({H_NAMES[self.h_idx]})"
        self.text(f"Choix : {choice} sur le niveau {self.level}", 20, 410)
        if self.warning:
            self.text(self.warning, 20, 425, self.font, (255, 120, 120))
        self.btn("Lancer la résolution", 20, 450, 400, 52, self.start_play,
                 color=C_GO, enabled=not self.warning)

        self.text("Aperçu de la grille", 470, 70, self.big)
        rows, cols = len(self.preview), len(self.preview[0])
        cell = max(16, min(40, 310 // cols, 260 // rows))
        self.draw_grid(self.preview, 470, 100, cell)

    # -- écran de jeu ----------------------------------------------------
    def draw_play(self):
        self.draw_grid(self.puzzle.grid, self.ox, 0, self.cell)
        y0 = len(self.puzzle.grid) * self.cell
        W = self.screen.get_width()
        pygame.draw.rect(self.screen, C_BG, (0, y0, W, HUD_H))

        total = f"/{len(self.solution)}" if self.solution is not None else ""
        self.text(f"Niveau {self.level} | {self.label} | "
                  f"Mouvements : {self.moves_done}{total}",
                  10, y0 + 8, self.big)

        msg = self.message
        if self.phase == "solving":
            msg += f" ({time.time() - self.t_start:.0f} s)"
        self.text(msg, 10, y0 + 36)

        r = self.result
        if self.phase == "done" and r and r["stats"]:
            s = r["stats"]
            exp, gen = s["expanded"], s["generated"]
            if r["actions"] is not None:
                d = len(r["actions"])
                b = gen / exp if exp else 0
                lines = [
                    f"Coût de la solution : {d} mouvements",
                    f"Complexité temporelle : {exp} nœuds développés, "
                    f"{gen} générés",
                    f"Complexité spatiale : {s['max_nodes']} nœuds en "
                    f"mémoire (max)",
                    f"Branchement effectif b ~ {b:.2f}  ->  O(b^d), d = {d}",
                    f"Temps d'exécution : {r['elapsed']:.3f} s",
                ]
                color = C_OK
            else:
                lines = [
                    "Coût de la solution : aucune solution",
                    f"Complexité temporelle : {exp} nœuds développés, "
                    f"{gen} générés",
                    f"Complexité spatiale : {s['max_nodes']} nœuds en "
                    f"mémoire (max)",
                    f"Temps d'exécution : {r['elapsed']:.3f} s",
                ]
                color = C_TEXT
            for k, line in enumerate(lines):
                self.text(line, 10, y0 + 62 + k * 24, self.font, color)

        can_replay = self.solution is not None and self.phase != "solving"
        self.btn("Rejouer", W - 160, y0 + 62, 140, 36, self.replay,
                 enabled=can_replay)
        self.btn("Menu", W - 160, y0 + 108, 140, 36, self.go_menu)

    def draw(self):
        self.screen.fill(C_BG)
        self.buttons = []
        if self.mode == "menu":
            self.draw_menu()
        else:
            self.draw_play()

    # -- événements ------------------------------------------------------
    def handle_key(self, event):
        key = event.key
        if key == pygame.K_ESCAPE:
            if self.mode == "play":
                self.go_menu()
                return True
            return False
        if self.mode == "menu":
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if not self.warning:
                    self.start_play()
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.start_play()
            elif event.unicode in LEVEL_KEYS:
                self.set_level(LEVEL_KEYS[event.unicode])
        else:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r):
                self.replay()
        return True

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if not self.handle_key(event):
                        running = False
                elif (event.type == pygame.MOUSEBUTTONDOWN
                      and event.button == 1):
                    for rect, cb in list(self.buttons):
                        if rect.collidepoint(event.pos):
                            cb()
                            break

            self.check_results()
            self.animate()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


def run(level=1):
    Game(level).run()