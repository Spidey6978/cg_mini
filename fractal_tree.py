import math

import pygame


pygame.init()

WIDTH, HEIGHT = 1000, 720
FOOTER_HEIGHT = 82
CANVAS_HEIGHT = HEIGHT - FOOTER_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fractal Explorer")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("segoeui", 18)
SMALL_FONT = pygame.font.SysFont("segoeui", 15)
TITLE_FONT = pygame.font.SysFont("segoeui", 25, bold=True)

BACKGROUND = (13, 17, 27)
PANEL = (22, 28, 42)
TEXT = (224, 231, 241)
MUTED = (146, 159, 180)
ACCENT = (101, 216, 190)
PALETTES = [
    [(78, 220, 166), (78, 157, 237), (238, 199, 92), (238, 119, 148)],
    [(255, 188, 110), (245, 112, 117), (185, 118, 242), (97, 191, 231)],
    [(222, 234, 255), (157, 192, 250), (112, 148, 224), (106, 219, 205)],
]

MODES = ("Tree", "Sierpinski", "Koch")
mode_index = 0
depth = 9
branch_angle = 25.0
branch_ratio = 0.72
palette_index = 0
zoom = 1.0
pan_x = 0.0
pan_y = 0.0
auto_rotate = False
rotation = 0.0
dragging = False
last_mouse = (0, 0)


def color_for(level):
    colors = PALETTES[palette_index]
    return colors[level % len(colors)]


def project(point):
    x, y = point
    center_x, center_y = WIDTH / 2, CANVAS_HEIGHT / 2
    x -= center_x
    y -= center_y
    angle = rotation
    rotated_x = x * math.cos(angle) - y * math.sin(angle)
    rotated_y = x * math.sin(angle) + y * math.cos(angle)
    return (
        round(center_x + rotated_x * zoom + pan_x),
        round(center_y + rotated_y * zoom + pan_y),
    )


def draw_tree(surface):
    colors = PALETTES[palette_index]

    def branch(start, length, angle, level):
        radians = math.radians(angle)
        end = (
            start[0] + length * math.sin(radians),
            start[1] - length * math.cos(radians),
        )
        color = colors[min(len(colors) - 1, (depth - level) * len(colors) // depth)]
        width = max(1, round(level * zoom * 0.72))
        pygame.draw.line(surface, color, project(start), project(end), width)

        if level == 0:
            pygame.draw.circle(surface, colors[-1], project(end), max(2, round(3 * zoom)))
            return

        next_length = length * branch_ratio
        branch(end, next_length, angle - branch_angle, level - 1)
        branch(end, next_length, angle + branch_angle, level - 1)

    branch((WIDTH / 2, CANVAS_HEIGHT - 24), 125, 0, depth)


def draw_sierpinski(surface):
    side = min(WIDTH * 0.78, CANVAS_HEIGHT * 0.82)
    height = side * math.sqrt(3) / 2
    points = [
        (WIDTH / 2, (CANVAS_HEIGHT - height) / 2),
        (WIDTH / 2 - side / 2, (CANVAS_HEIGHT + height) / 2),
        (WIDTH / 2 + side / 2, (CANVAS_HEIGHT + height) / 2),
    ]

    def triangle(vertices, level):
        if level == 0:
            pygame.draw.polygon(surface, color_for(depth), [project(point) for point in vertices])
            return

        a, b, c = vertices
        ab = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        bc = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
        ca = ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2)
        triangle((a, ab, ca), level - 1)
        triangle((ab, b, bc), level - 1)
        triangle((ca, bc, c), level - 1)

    triangle(points, depth)


def draw_koch(surface):
    side = min(WIDTH * 0.69, CANVAS_HEIGHT * 0.73)
    height = side * math.sqrt(3) / 2
    vertices = [
        (WIDTH / 2, (CANVAS_HEIGHT - height) / 2),
        (WIDTH / 2 - side / 2, (CANVAS_HEIGHT + height) / 2),
        (WIDTH / 2 + side / 2, (CANVAS_HEIGHT + height) / 2),
    ]
    segment_color = color_for(depth)
    line_width = max(1, round(2 * zoom))

    def edge(start, end, level):
        if level == 0:
            pygame.draw.line(surface, segment_color, project(start), project(end), line_width)
            return

        dx = (end[0] - start[0]) / 3
        dy = (end[1] - start[1]) / 3
        first = (start[0] + dx, start[1] + dy)
        peak = (
            first[0] + dx / 2 - dy * math.sqrt(3) / 2,
            first[1] + dx * math.sqrt(3) / 2 + dy / 2,
        )
        second = (start[0] + 2 * dx, start[1] + 2 * dy)
        edge(start, first, level - 1)
        edge(first, peak, level - 1)
        edge(peak, second, level - 1)
        edge(second, end, level - 1)

    for index in range(3):
        edge(vertices[index], vertices[(index + 1) % 3], depth)


def draw_label(surface, text, position, color=TEXT, font=FONT):
    surface.blit(font.render(text, True, color), position)


def zoom_at(position, factor):
    global zoom, pan_x, pan_y
    new_zoom = max(0.45, min(3.5, zoom * factor))
    pan_x = position[0] - WIDTH / 2 - (position[0] - WIDTH / 2 - pan_x) * new_zoom / zoom
    pan_y = position[1] - CANVAS_HEIGHT / 2 - (position[1] - CANVAS_HEIGHT / 2 - pan_y) * new_zoom / zoom
    zoom = new_zoom


def draw_interface():
    pygame.draw.rect(screen, PANEL, (0, CANVAS_HEIGHT, WIDTH, FOOTER_HEIGHT))
    pygame.draw.line(screen, (43, 53, 72), (0, CANVAS_HEIGHT), (WIDTH, CANVAS_HEIGHT), 1)

    draw_label(screen, "FRACTAL EXPLORER", (20, 18), TEXT, TITLE_FONT)
    if mode_index == 0:
        details = f"Branch angle {branch_angle:.1f}°  ·  Branch ratio {branch_ratio:.2f}  ·  Depth {depth}"
    elif mode_index == 1:
        details = f"Sierpinski triangle  ·  Iterations {depth}"
    else:
        details = f"Koch snowflake  ·  Iterations {depth}"
    draw_label(screen, details, (21, 51), ACCENT, SMALL_FONT)

    button_width, button_height, gap = 142, 42, 10
    start_x = 20
    button_y = CANVAS_HEIGHT + 20
    for index, label in enumerate(MODES):
        rect = pygame.Rect(start_x + index * (button_width + gap), button_y, button_width, button_height)
        selected = index == mode_index
        pygame.draw.rect(screen, (40, 64, 77) if selected else (31, 39, 56), rect, border_radius=8)
        if selected:
            pygame.draw.rect(screen, ACCENT, rect, width=1, border_radius=8)
        text = FONT.render(label, True, TEXT if selected else MUTED)
        screen.blit(text, text.get_rect(center=rect.center))

    draw_label(
        screen,
        f"Palette {palette_index + 1}/3",
        (WIDTH - 151, button_y + 11),
        MUTED,
        SMALL_FONT,
    )


def select_mode(index):
    global mode_index, depth, branch_angle, branch_ratio
    mode_index = index
    if index == 0:
        depth = min(depth, 12)
    else:
        depth = min(depth, 6 if index == 2 else 8)
    branch_angle = 25
    branch_ratio = 0.72


running = True
while running:
    dt = clock.tick(60) / 1000
    if auto_rotate:
        rotation += dt * 0.28
    if mode_index == 0:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            branch_angle -= 60 * dt
        if keys[pygame.K_RIGHT]:
            branch_angle += 60 * dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                select_mode(event.key - pygame.K_1)
            elif event.key in (pygame.K_UP, pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                depth = min(depth + 1, 12 if mode_index == 0 else (6 if mode_index == 2 else 8))
            elif event.key in (pygame.K_DOWN, pygame.K_MINUS, pygame.K_KP_MINUS):
                depth = max(1, depth - 1)
            elif event.key == pygame.K_p:
                palette_index = (palette_index + 1) % len(PALETTES)
            elif event.key == pygame.K_r:
                auto_rotate = not auto_rotate
            elif event.key == pygame.K_c:
                zoom, pan_x, pan_y, rotation = 1.0, 0.0, 0.0, 0.0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and event.pos[1] >= CANVAS_HEIGHT:
                button_width, gap = 142, 10
                for index in range(len(MODES)):
                    rect = pygame.Rect(20 + index * (button_width + gap), CANVAS_HEIGHT + 20, button_width, 42)
                    if rect.collidepoint(event.pos):
                        select_mode(index)
                        break
            elif event.button == 1 and event.pos[1] < CANVAS_HEIGHT:
                dragging = True
                last_mouse = event.pos
            elif event.button == 4:
                zoom_at(event.pos, 1.12)
            elif event.button == 5:
                zoom_at(event.pos, 1 / 1.12)
        elif event.type == pygame.MOUSEWHEEL:
            zoom_at(pygame.mouse.get_pos(), 1.12 ** event.y)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            pan_x += event.pos[0] - last_mouse[0]
            pan_y += event.pos[1] - last_mouse[1]
            last_mouse = event.pos

    screen.fill(BACKGROUND)
    if mode_index == 0:
        draw_tree(screen)
    elif mode_index == 1:
        draw_sierpinski(screen)
    else:
        draw_koch(screen)
    draw_interface()
    pygame.display.flip()

pygame.quit()
