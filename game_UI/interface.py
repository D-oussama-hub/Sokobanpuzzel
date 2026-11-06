
import game_UI.interface as interface
import time

TILE = 50

# Couleurs
BG = (30, 30, 30)
FLOOR = (255, 218, 177)
GRID = (255, 235, 210)

WALL = (170, 170, 170)
WALL_BORDER = (45, 45, 45)

BOX = (115, 55, 15)
BOX_BORDER = (45, 25, 10)
BOX_LIGHT = (165, 95, 35)

PLAYER_SHIRT = (35, 115, 210)
PLAYER_PANTS = (35, 55, 100)
SKIN = (255, 215, 145)
HAIR = (25, 25, 20)

TARGET_BORDER = (25, 25, 25)


# ==================================================
# 1. DESSINER LES MURS
# ==================================================

def draw_wall(screen, x, y):

    rect = interface.Rect(x, y, TILE, TILE)
    interface.draw.rect(screen, WALL, rect)

    brick_h = 12
    brick_w = 25

    for row in range(5):

        yy = y + row * brick_h

        interface.draw.line(
            screen, WALL_BORDER,
            (x, yy), (x + TILE, yy), 2
        )

        offset = 0 if row % 2 == 0 else brick_w // 2

        for col in range(3):

            xx = x + offset + col * brick_w

            if x < xx < x + TILE:

                interface.draw.line(
                    screen, WALL_BORDER,
                    (xx, yy),
                    (xx, min(yy + brick_h, y + TILE)),
                    2
                )

    interface.draw.rect(screen, WALL_BORDER, rect, 2)


# ==================================================
# 2. DESSINER UNE CAISSE
# ==================================================

def draw_box(screen, x, y):

    box = interface.Rect(x + 5, y + 5, TILE - 10, TILE - 10)

    interface.draw.rect(screen, (55, 35, 20), box.move(3, 3))
    interface.draw.rect(screen, BOX, box)
    interface.draw.rect(screen, BOX_BORDER, box, 3)

    interface.draw.line(
        screen, BOX_LIGHT,
        (box.left + 10, box.top + 3),
        (box.left + 10, box.bottom - 3), 2
    )

    interface.draw.line(
        screen, BOX_BORDER,
        (box.right - 10, box.top + 3),
        (box.right - 10, box.bottom - 3), 2
    )

    interface.draw.line(
        screen, BOX_BORDER,
        (box.left + 3, box.centery),
        (box.right - 3, box.centery), 3
    )

    interface.draw.line(
        screen, BOX_LIGHT,
        (box.left + 3, box.top + 4),
        (box.right - 3, box.top + 4), 2
    )


# ==================================================
# 3. DESSINER LE JOUEUR
# ==================================================

def draw_player(screen, x, y):

    cx = x + TILE // 2

    head_y = y + 12
    body_y = y + 25

    interface.draw.ellipse(
        screen, (120, 100, 80),
        (x + 9, y + 42, 33, 7)
    )

    # Jambes
    interface.draw.rect(
        screen, PLAYER_PANTS,
        (cx - 10, y + 34, 8, 11)
    )

    interface.draw.rect(
        screen, PLAYER_PANTS,
        (cx + 2, y + 34, 8, 11)
    )

    # Chaussures
    interface.draw.ellipse(
        screen, (30, 30, 30),
        (cx - 13, y + 42, 12, 6)
    )

    interface.draw.ellipse(
        screen, (30, 30, 30),
        (cx + 2, y + 42, 12, 6)
    )

    # Bras
    interface.draw.line(
        screen, SKIN,
        (cx - 8, body_y + 3),
        (cx - 17, y + 36), 5
    )

    interface.draw.line(
        screen, SKIN,
        (cx + 8, body_y + 3),
        (cx + 17, y + 36), 5
    )

    # Corps
    interface.draw.rect(
        screen, PLAYER_SHIRT,
        (cx - 10, body_y - 2, 20, 16),
        border_radius=4
    )

    interface.draw.rect(
        screen, (20, 75, 145),
        (cx - 4, body_y - 2, 8, 5)
    )

    # Tête
    interface.draw.ellipse(
        screen, SKIN,
        (cx - 11, head_y - 8, 22, 22)
    )

    # Cheveux
    interface.draw.arc(
        screen, HAIR,
        (cx - 12, head_y - 11, 24, 19),
        0, 3.14, 5
    )

    interface.draw.rect(
        screen, HAIR,
        (cx - 11, head_y - 7, 5, 7)
    )

    interface.draw.rect(
        screen, HAIR,
        (cx + 6, head_y - 7, 5, 7)
    )

    # Yeux
    interface.draw.circle(
        screen, (20, 20, 20),
        (cx - 4, head_y + 1), 2
    )

    interface.draw.circle(
        screen, (20, 20, 20),
        (cx + 4, head_y + 1), 2
    )

    # Bouche
    interface.draw.line(
        screen, (100, 45, 35),
        (cx - 2, head_y + 7),
        (cx + 2, head_y + 7), 1
    )


# ==================================================
# 4. DESSINER UNE CIBLE
# ==================================================

def draw_target(screen, x, y):

    target = interface.Rect(
        x + 6, y + 6,
        TILE - 12, TILE - 12
    )

    interface.draw.rect(screen, FLOOR, target)

    step = 7

    for dx in range(target.left, target.right, step * 2):

        interface.draw.line(
            screen, TARGET_BORDER,
            (dx, target.top),
            (min(dx + step, target.right), target.top), 2
        )

        interface.draw.line(
            screen, TARGET_BORDER,
            (dx, target.bottom),
            (min(dx + step, target.right), target.bottom), 2
        )

    for dy in range(target.top, target.bottom, step * 2):

        interface.draw.line(
            screen, TARGET_BORDER,
            (target.left, dy),
            (target.left, min(dy + step, target.bottom)), 2
        )

        interface.draw.line(
            screen, TARGET_BORDER,
            (target.right, dy),
            (target.right, min(dy + step, target.bottom)), 2
        )

    interface.draw.line(
        screen, (190, 30, 30),
        (target.centerx - 4, target.centery - 4),
        (target.centerx + 4, target.centery + 4), 2
    )

    interface.draw.line(
        screen, (190, 30, 30),
        (target.centerx + 4, target.centery - 4),
        (target.centerx - 4, target.centery + 4), 2
    )


# ==================================================
# 5. DESSINER LA GRILLE
# ==================================================

def draw(screen, grid, font, lines):

    screen.fill(BG)

    for i in range(len(grid)):

        for j in range(len(grid[i])):

            cell = grid[i][j]

            x = j * TILE
            y = i * TILE

            rect = interface.Rect(x, y, TILE, TILE)

            interface.draw.rect(screen, FLOOR, rect)
            interface.draw.rect(screen, GRID, rect, 2)

            if cell == 'O':
                draw_wall(screen, x, y)

            if cell in ('S', '.', '*'):
                draw_target(screen, x, y)

            if cell in ('B', '*'):
                draw_box(screen, x, y)

            if cell == 'R':
                draw_player(screen, x, y)

    # Informations
    y_info = len(grid) * TILE + 8

    for k, line in enumerate(lines):

        text = font.render(
            line, True, (255, 255, 255)
        )

        screen.blit(
            text,
            (10, y_info + 24 * k)
        )


# ==================================================
# 6. INTERFACE PRINCIPALE
# ==================================================

def show_solution(path, cost, stats, algorithm):

    if not path:
        print("Erreur : chemin vide.")
        return

    interface.init()

    # Récupérer la grille
    grid = path[0].grid

    rows = len(grid)
    cols = max(len(row) for row in grid)

    info_height = 110

    width = cols * TILE
    height = rows * TILE + info_height

    screen = interface.display.set_mode((width, height))

    interface.display.set_caption("Sokoban - " + algorithm)

    font = interface.font.SysFont("Arial", 20)

    clock = interface.time.Clock()

    current_step = 0

    paused = False
    running = True

    speed = 1.0
    last_move = time.time()

    while running:

        # Gestion des événements
        for event in interface.event.get():

            if event.type == interface.QUIT:
                running = False

            elif event.type == interface.KEYDOWN:

                if event.key == interface.K_ESCAPE:
                    running = False

                elif event.key == interface.K_SPACE:
                    paused = not paused

                elif event.key == interface.K_RIGHT:
                    current_step = min(
                        current_step + 1,
                        len(path) - 1
                    )

                elif event.key == interface.K_LEFT:
                    current_step = max(
                        current_step - 1,
                        0
                    )

        # Animation automatique
        if not paused and current_step < len(path) - 1:

            if time.time() - last_move >= speed:

                current_step += 1
                last_move = time.time()

        # État actuel
        state = path[current_step]

        grid = state.grid

        lines = [
            f"Algorithme : {algorithm}",
            f"Mouvements : {current_step}/{cost}",
            f"Cout total : {cost}",
            f"Etats developpes : {stats.get('expanded', 0)}",
            "SPACE : Pause | LEFT/RIGHT : Navigation | ESC : Quitter"
        ]

        # Dessiner
        draw(screen, grid, font, lines)

        interface.display.flip()

        clock.tick(60)

    interface.quit()
