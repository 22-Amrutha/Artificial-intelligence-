import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hill Climb Game")
clock = pygame.time.Clock()

font     = pygame.font.SysFont("arial", 24)
font_big = pygame.font.SysFont("arial", 38, bold=True)

# ---------- Generate hills ----------
def make_hills(start_x, count=300):
    points = []
    y = 300
    x = start_x
    for _ in range(count):
        y += random.randint(-12, 12)
        y = max(200, min(400, y))
        points.append((x, y))
        x += 8
    return points

hills = make_hills(0)

def get_ground_y(world_x):
    for i in range(len(hills) - 1):
        x0, y0 = hills[i]
        x1, y1 = hills[i + 1]
        if x0 <= world_x <= x1:
            t = (world_x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return 300

def get_angle(world_x):
    for i in range(len(hills) - 1):
        x0, y0 = hills[i]
        x1, y1 = hills[i + 1]
        if x0 <= world_x <= x1:
            return math.degrees(math.atan2(-(y1 - y0), x1 - x0))
    return 0

# ---------- Spawn coins and fuel cans ----------
def spawn_items(from_x, to_x):
    items = []
    x = from_x
    while x < to_x:
        x += random.randint(180, 320)
        wy = get_ground_y(x)
        kind = 'coin'
        items.append({'x': x, 'y': wy, 'kind': kind, 'alive': True})
    return items

# ---------- Draw car + girl ----------
def draw_car_girl(sx, sy):
    # Car body
    pygame.draw.ellipse(screen, (220, 50, 50),  (sx - 45, sy - 20, 90, 30))
    pygame.draw.rect(screen,   (220, 50, 50),   (sx - 30, sy - 38, 60, 22))
    # Window
    pygame.draw.rect(screen, (150, 210, 255),   (sx - 26, sy - 36, 52, 18), border_radius=4)
    # Wheels
    pygame.draw.circle(screen, (40, 40, 40),    (sx - 25, sy + 12), 14)
    pygame.draw.circle(screen, (40, 40, 40),    (sx + 25, sy + 12), 14)
    pygame.draw.circle(screen, (160, 160, 160), (sx - 25, sy + 12), 8)
    pygame.draw.circle(screen, (160, 160, 160), (sx + 25, sy + 12), 8)
    # Girl head
    pygame.draw.circle(screen, (255, 200, 160), (sx, sy - 30), 10)
    # Hair
    pygame.draw.arc(screen, (80, 40, 10), (sx - 10, sy - 40, 20, 16), 0, math.pi, 4)
    # Eyes
    pygame.draw.circle(screen, (0, 0, 0), (sx - 4, sy - 31), 2)
    pygame.draw.circle(screen, (0, 0, 0), (sx + 4, sy - 31), 2)
    # Smile
    pygame.draw.arc(screen, (180, 80, 80), (sx - 5, sy - 28, 10, 7), math.pi, 2 * math.pi, 2)

# ---------- Draw coin ----------
def draw_coin(sx, sy):
    pygame.draw.circle(screen, (255, 210, 0), (sx, sy - 20), 13)
    pygame.draw.circle(screen, (255, 170, 0), (sx, sy - 20), 10)
    c = font.render("$", True, (180, 100, 0))
    screen.blit(c, (sx - c.get_width() // 2, sy - 20 - c.get_height() // 2))


# ---------- Pop-up text ----------
popups = []

def add_popup(text, sx, sy, color):
    popups.append({'text': text, 'x': sx, 'y': sy, 'timer': 60, 'color': color})

# ---------- Game state ----------
def reset():
    global hills, car_x, car_vx, camera_x, fuel, score, coins, items, next_spawn, game_over
    hills       = make_hills(0)
    car_x       = 200
    car_vx      = 0
    camera_x    = 0
    fuel        = 100.0
    score       = 0
    coins       = 0
    game_over   = False
    items       = spawn_items(300, 2000)
    next_spawn  = 2000

reset()

# ---------- Main loop ----------
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset()

    keys = pygame.key.get_pressed()

    if not game_over:
        # Controls
        if keys[pygame.K_RIGHT]:
            car_vx += 0.4
            fuel   -= 0.05
        if keys[pygame.K_LEFT]:
            car_vx -= 0.5

        # Slope gravity
        angle   = get_angle(car_x)
        slope   = math.sin(math.radians(-angle))
        car_vx -= slope * 0.5
        car_vx *= 0.97
        car_vx  = max(-8, min(8, car_vx))
        car_x  += car_vx

        fuel  -= 0.012
        score  = int(car_x)

        if fuel <= 0:
            fuel = 0
            game_over = True

        # Extend hills
        if hills[-1][0] < car_x + WIDTH:
            last = hills[-1]
            hills += make_hills(last[0] + 8, 120)

        # Spawn more items ahead
        if car_x + 1500 > next_spawn:
            items += spawn_items(next_spawn, next_spawn + 1500)
            next_spawn += 1500

        # Collect items
        car_sy = get_ground_y(car_x)
        for item in items:
            if not item['alive']:
                continue
            if abs(item['x'] - car_x) < 38 and abs(item['y'] - car_sy) < 50:
                item['alive'] = False
                sx = int(item['x'] - camera_x)
                sy = int(item['y'])
                if item['kind'] == 'coin':
                    coins += 1
                    add_popup("+1 Coin!", sx, sy - 30, (255, 210, 0))

    camera_x = car_x - 250

    # -------- Draw --------
    screen.fill((135, 206, 250))  # sky

    # Sun
    pygame.draw.circle(screen, (255, 220, 50), (700, 60), 35)

    # Hills
    pts = []
    for wx, wy in hills:
        sx = wx - camera_x
        if -10 < sx < WIDTH + 10:
            pts.append((int(sx), int(wy)))

    if len(pts) >= 2:
        poly = pts + [(pts[-1][0], HEIGHT), (pts[0][0], HEIGHT)]
        pygame.draw.polygon(screen, (80, 160, 60), poly)
        dirt = [(x, y + 8) for x, y in pts]
        dirt += [(pts[-1][0], HEIGHT), (pts[0][0], HEIGHT)]
        pygame.draw.polygon(screen, (140, 100, 50), dirt)

    # Draw items
    for item in items:
        if not item['alive']:
            continue
        sx = int(item['x'] - camera_x)
        sy = int(item['y'])
        if -20 < sx < WIDTH + 20:
            if item['kind'] == 'coin':
                draw_coin(sx, sy)

    # Car + girl
    car_sy = get_ground_y(car_x)
    car_sx = int(car_x - camera_x)
    draw_car_girl(car_sx, int(car_sy) - 18)

    # Pop-up texts (float upward)
    for p in popups[:]:
        txt = font.render(p['text'], True, p['color'])
        screen.blit(txt, (p['x'] - txt.get_width() // 2, p['y'] - (60 - p['timer'])))
        p['timer'] -= 1
        if p['timer'] <= 0:
            popups.remove(p)

    # HUD — Fuel bar
    pygame.draw.rect(screen, (50, 50, 50), (10, 10, 154, 22))
    fc = (60, 200, 60) if fuel > 40 else (255, 140, 0) if fuel > 20 else (220, 40, 40)
    pygame.draw.rect(screen, fc,           (11, 11, int(fuel * 1.52), 20))
    screen.blit(font.render("FUEL", True, (255, 255, 255)), (12, 34))

    # Coins display
    screen.blit(font.render(f"Coins: {coins}", True, (255, 210, 0)), (10, 60))

    # Distance
    dist_txt = font.render(f"Distance: {score} m", True, (255, 255, 255))
    screen.blit(dist_txt, (WIDTH // 2 - dist_txt.get_width() // 2, 10))

    # Controls hint
    hint = pygame.font.SysFont("arial", 16).render(
        "RIGHT = Go    LEFT = Brake    R = Restart", True, (50, 50, 50))
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 26))

    # Game over screen
    if game_over:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        screen.blit(ov, (0, 0))
        msg1 = font_big.render("OUT OF FUEL!", True, (220, 50, 50))
        msg2 = font.render(f"Distance: {score} m   Coins: {coins}", True, (255, 255, 255))
        msg3 = font.render("Press  R  to Restart", True, (200, 200, 200))
        screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 70))
        screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2))
        screen.blit(msg3, (WIDTH // 2 - msg3.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()