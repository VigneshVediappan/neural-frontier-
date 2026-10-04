import pygame
import random
import math

pygame.init()

# ============================================================
# NEURAL FRONTIER
# Final polish build
# ============================================================

WIDTH = 1000
HEIGHT = 700
FPS = 60

MAX_LEVEL = 10
CELL_SIZE = 50

PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 200

BULLET_SPEED = 10
BULLET_DAMAGE = 25
MAX_BOUNCES = 3

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEURAL FRONTIER")
clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (5, 8, 15)
DARK = (10, 16, 28)
GRID = (20, 32, 48)
WHITE = (235, 245, 255)

CYAN = (0, 220, 255)
BLUE = (50, 130, 255)
GREEN = (40, 255, 150)
RED = (255, 70, 90)
ORANGE = (255, 150, 50)
YELLOW = (255, 230, 70)
PURPLE = (190, 70, 255)

# ============================================================
# FONTS
# ============================================================

FONT_SMALL = pygame.font.SysFont("consolas", 16)
FONT = pygame.font.SysFont("consolas", 22)
FONT_BIG = pygame.font.SysFont("consolas", 38, bold=True)
FONT_HUGE = pygame.font.SysFont("consolas", 64, bold=True)

# ============================================================
# GAME STATES
# ============================================================

MENU = "menu"
CONTROLS = "controls"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
VICTORY = "victory"

game_state = MENU

# ============================================================
# GAME VARIABLES
# ============================================================

level = 1
score = 0
player_health = PLAYER_MAX_HEALTH

fire_timer = 0
rapid_timer = 0
damage_timer = 0
shield_timer = 0
triple_timer = 0

enemies = []
bullets = []
enemy_bullets = []
particles = []
powerups = []

boss = None
boss_was_defeated = False

enemies_spawned = 0
enemies_to_spawn = 0
spawn_sides = []
obstacles = []

screen_shake = 0
level_message_timer = 0
boss_warning_timer = 0
transition_timer = 0

player_angle = 0
player_pulse = 0

# ============================================================
# PLAYER
# ============================================================

player = pygame.Rect(
    WIDTH // 2 - 18,
    HEIGHT // 2 - 18,
    36,
    36
)

# ============================================================
# LEVEL LAYOUTS
# ============================================================

LEVEL_LAYOUTS = [
    [
        pygame.Rect(250, 330, 500, 30),
        pygame.Rect(485, 150, 30, 180),
        pygame.Rect(485, 360, 30, 190),
    ],
    [
        pygame.Rect(160, 130, 220, 30),
        pygame.Rect(620, 130, 220, 30),
        pygame.Rect(160, 540, 220, 30),
        pygame.Rect(620, 540, 220, 30),
    ],
    [
        pygame.Rect(150, 100, 30, 220),
        pygame.Rect(150, 320, 250, 30),
        pygame.Rect(400, 180, 30, 170),
        pygame.Rect(570, 180, 30, 170),
        pygame.Rect(600, 320, 250, 30),
        pygame.Rect(820, 350, 30, 220),
        pygame.Rect(150, 570, 250, 30),
        pygame.Rect(400, 400, 30, 170),
        pygame.Rect(570, 400, 30, 170),
    ],
    [
        pygame.Rect(300, 200, 400, 30),
        pygame.Rect(300, 470, 400, 30),
        pygame.Rect(300, 230, 30, 240),
        pygame.Rect(670, 230, 30, 240),
    ],
    [
        pygame.Rect(100, 180, 300, 30),
        pygame.Rect(600, 180, 300, 30),
        pygame.Rect(100, 340, 220, 30),
        pygame.Rect(680, 340, 220, 30),
        pygame.Rect(100, 500, 300, 30),
        pygame.Rect(600, 500, 300, 30),
    ],
    [
        pygame.Rect(270, 150, 180, 30),
        pygame.Rect(550, 150, 180, 30),
        pygame.Rect(180, 300, 180, 30),
        pygame.Rect(640, 300, 180, 30),
        pygame.Rect(270, 450, 180, 30),
        pygame.Rect(550, 450, 180, 30),
    ],
    [
        pygame.Rect(120, 120, 180, 30),
        pygame.Rect(400, 120, 200, 30),
        pygame.Rect(700, 120, 180, 30),
        pygame.Rect(120, 300, 180, 30),
        pygame.Rect(400, 300, 200, 30),
        pygame.Rect(700, 300, 180, 30),
        pygame.Rect(120, 480, 180, 30),
        pygame.Rect(400, 480, 200, 30),
        pygame.Rect(700, 480, 180, 30),
    ],
    [
        pygame.Rect(470, 100, 60, 170),
        pygame.Rect(250, 220, 170, 30),
        pygame.Rect(580, 220, 170, 30),
        pygame.Rect(150, 350, 220, 30),
        pygame.Rect(630, 350, 220, 30),
        pygame.Rect(250, 480, 170, 30),
        pygame.Rect(580, 480, 170, 30),
        pygame.Rect(470, 500, 60, 100),
    ],
    [
        pygame.Rect(120, 120, 300, 30),
        pygame.Rect(500, 120, 380, 30),
        pygame.Rect(120, 280, 180, 30),
        pygame.Rect(380, 280, 220, 30),
        pygame.Rect(680, 280, 200, 30),
        pygame.Rect(120, 440, 300, 30),
        pygame.Rect(500, 440, 380, 30),
        pygame.Rect(300, 120, 30, 160),
        pygame.Rect(670, 280, 30, 160),
    ],
    [
        pygame.Rect(180, 120, 250, 30),
        pygame.Rect(570, 120, 250, 30),
        pygame.Rect(180, 550, 250, 30),
        pygame.Rect(570, 550, 250, 30),
        pygame.Rect(180, 150, 30, 180),
        pygame.Rect(790, 150, 30, 180),
        pygame.Rect(180, 370, 30, 180),
        pygame.Rect(790, 370, 30, 180),
        pygame.Rect(380, 270, 240, 30),
        pygame.Rect(380, 400, 240, 30),
    ],
]

# ============================================================
# BOSS DATA
# ============================================================

BOSS_DATA = [
    ("GUARDIAN-01", 500, 1.2, CYAN, "BURST"),
    ("PHANTOM-02", 600, 1.4, PURPLE, "DASH"),
    ("PYRO-03", 700, 1.1, ORANGE, "FIRE"),
    ("VOLT-04", 800, 1.3, YELLOW, "RING"),
    ("VOID-05", 900, 1.0, PURPLE, "TELEPORT"),
    ("TITAN-06", 1000, 0.8, ORANGE, "MISSILES"),
    ("STORM-07", 1100, 1.3, BLUE, "SPREAD"),
    ("REAPER-08", 1200, 1.5, RED, "DASH"),
    ("OVERLORD-09", 1400, 1.0, PURPLE, "RING"),
    ("NEURAL-X", 1800, 1.2, GREEN, "CHAOS"),
]

# ============================================================
# HELPERS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def rect_hits_wall(rect):
    for wall in obstacles:
        if rect.colliderect(wall):
            return True
    return False


def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


def spawn_particles(x, y, color, amount=12, speed=4):
    for _ in range(amount):
        angle = random.uniform(0, math.pi * 2)
        velocity = random.uniform(1, speed)

        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * velocity,
            "vy": math.sin(angle) * velocity,
            "life": random.randint(20, 45),
            "size": random.randint(2, 5),
            "color": color
        })


def update_particles():
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]

        p["vx"] *= 0.96
        p["vy"] *= 0.96

        p["life"] -= 1

        if p["life"] <= 0:
            particles.remove(p)


def draw_particles():
    for p in particles:
        radius = max(1, int(p["size"] * p["life"] / 35))
        pygame.draw.circle(
            screen,
            p["color"],
            (int(p["x"]), int(p["y"])),
            radius
        )


# ============================================================
# SAFE SPAWNING
# ============================================================

def player_can_escape(x, y):
    test_rect = pygame.Rect(
        int(x - 18),
        int(y - 18),
        36,
        36
    )

    if rect_hits_wall(test_rect):
        return False

    directions = [
        (150, 0),
        (-150, 0),
        (0, 150),
        (0, -150),
    ]

    for dx, dy in directions:
        check_rect = pygame.Rect(
            int(x + dx - 18),
            int(y + dy - 18),
            36,
            36
        )

        if (
            check_rect.left >= 0
            and check_rect.right <= WIDTH
            and check_rect.top >= 0
            and check_rect.bottom <= HEIGHT
            and not rect_hits_wall(check_rect)
        ):
            return True

    return False


def find_safe_spawn():
    candidates = []

    for _ in range(1000):
        x = random.randint(70, WIDTH - 70)
        y = random.randint(70, HEIGHT - 70)

        if player_can_escape(x, y):
            candidates.append((x, y))

            if len(candidates) >= 10:
                break

    if candidates:
        return random.choice(candidates)

    fallback = [
        (70, 70),
        (WIDTH - 70, 70),
        (70, HEIGHT - 70),
        (WIDTH - 70, HEIGHT - 70),
        (WIDTH // 2, 80),
        (WIDTH // 2, HEIGHT - 80),
    ]

    for position in fallback:
        if player_can_escape(*position):
            return position

    return WIDTH // 2, HEIGHT // 2


def get_spawn_position(side, size):
    margin = size + 15

    for _ in range(100):
        if side == "top":
            x = random.randint(margin, WIDTH - margin)
            y = margin

        elif side == "bottom":
            x = random.randint(margin, WIDTH - margin)
            y = HEIGHT - margin

        elif side == "left":
            x = margin
            y = random.randint(margin, HEIGHT - margin)

        else:
            x = WIDTH - margin
            y = random.randint(margin, HEIGHT - margin)

        test = pygame.Rect(
            int(x - size / 2),
            int(y - size / 2),
            size,
            size
        )

        if not rect_hits_wall(test):
            return x, y

    return WIDTH // 2, HEIGHT // 2


# ============================================================
# ENEMY
# ============================================================

class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type

        if enemy_type == "normal":
            self.size = 34
            self.max_health = 50 + level * 8
            self.speed = 0.8 + level * 0.01
            self.color = RED
            self.points = 100

        elif enemy_type == "flanker":
            self.size = 28
            self.max_health = 35 + level * 6
            self.speed = 1.0 + level * 0.01
            self.color = PURPLE
            self.points = 150

        else:
            self.size = 44
            self.max_health = 100 + level * 12
            self.speed = 0.6 + level * 0.008
            self.color = ORANGE
            self.points = 250

        side = random.choice(spawn_sides)
        x, y = get_spawn_position(side, self.size)

        self.x = x
        self.y = y

        self.health = self.max_health

        self.shoot_timer = random.randint(50, 140)
        self.anim = random.random() * 10
        self.strafe_dir = random.choice([-1, 1])

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size
        )

    def update(self):
        self.anim += 0.08
        self.shoot_timer -= 1

        dx = player.centerx - self.x
        dy = player.centery - self.y

        distance = math.hypot(dx, dy)

        if distance > 1:
            nx = dx / distance
            ny = dy / distance
        else:
            nx = ny = 0

        if self.type == "flanker":
            side_x = -ny * self.strafe_dir
            side_y = nx * self.strafe_dir

            move_x = nx * 0.65 + side_x * 0.75
            move_y = ny * 0.65 + side_y * 0.75

        elif self.type == "tank":
            move_x = nx
            move_y = ny

        else:
            move_x = nx
            move_y = ny

        new_rect = self.rect.copy()
        new_rect.x += int(move_x * self.speed)

        if (
            new_rect.left >= 0
            and new_rect.right <= WIDTH
            and not rect_hits_wall(new_rect)
        ):
            self.x = new_rect.centerx

        new_rect = self.rect.copy()
        new_rect.y += int(move_y * self.speed)

        if (
            new_rect.top >= 0
            and new_rect.bottom <= HEIGHT
            and not rect_hits_wall(new_rect)
        ):
            self.y = new_rect.centery

        if self.shoot_timer <= 0 and distance < 650:
            self.shoot()
            self.shoot_timer = random.randint(90, 170)

    def shoot(self):
        dx = player.centerx - self.x
        dy = player.centery - self.y

        angle = math.atan2(dy, dx)

        enemy_bullets.append({
            "x": self.x,
            "y": self.y,
            "vx": math.cos(angle) * 4,
            "vy": math.sin(angle) * 4,
            "life": 180,
            "color": self.color
        })

    def draw(self):
        cx = int(self.x)
        cy = int(self.y)

        pulse = math.sin(self.anim) * 2

        # Shadow / energy ring
        pygame.draw.circle(
            screen,
            (15, 25, 40),
            (cx, cy),
            int(self.size * 0.65),
            2
        )

        if self.type == "normal":
            # Angular hunter drone
            points = [
                (cx + self.size // 2, cy),
                (cx + 7, cy - self.size // 2),
                (cx - self.size // 2 + 4, cy - 9),
                (cx - self.size // 2 + 4, cy + 9),
                (cx + 7, cy + self.size // 2),
            ]

            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)

            pygame.draw.line(
                screen,
                YELLOW,
                (cx - 8, cy),
                (cx + 12, cy),
                3
            )

            pygame.draw.circle(
                screen,
                (255, 180, 180),
                (cx + 7, cy),
                4
            )

        elif self.type == "flanker":
            # Fast assassin
            points = [
                (cx, cy - self.size // 2),
                (cx + self.size // 2, cy),
                (cx + 8, cy + 5),
                (cx, cy + self.size // 2),
                (cx - 8, cy + 5),
                (cx - self.size // 2, cy),
            ]

            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)

            wing = int(15 + pulse)

            pygame.draw.line(
                screen,
                PURPLE,
                (cx - 6, cy),
                (cx - wing - 10, cy + 10),
                4
            )

            pygame.draw.line(
                screen,
                PURPLE,
                (cx + 6, cy),
                (cx + wing + 10, cy + 10),
                4
            )

            pygame.draw.circle(screen, CYAN, (cx, cy), 4)

        else:
            # Heavy armored tank
            outer = pygame.Rect(
                cx - self.size // 2,
                cy - self.size // 2,
                self.size,
                self.size
            )

            pygame.draw.rect(
                screen,
                self.color,
                outer,
                border_radius=7
            )

            pygame.draw.rect(
                screen,
                WHITE,
                outer,
                2,
                border_radius=7
            )

            inner = outer.inflate(-12, -12)

            pygame.draw.rect(
                screen,
                DARK,
                inner,
                border_radius=4
            )

            pygame.draw.line(
                screen,
                ORANGE,
                (cx - 10, cy),
                (cx + 10, cy),
                5
            )

            pygame.draw.line(
                screen,
                ORANGE,
                (cx, cy - 10),
                (cx, cy + 10),
                5
            )

        # Health bar
        bar_width = self.size + 10

        pygame.draw.rect(
            screen,
            (35, 40, 50),
            (
                cx - bar_width // 2,
                cy - self.size // 2 - 12,
                bar_width,
                5
            )
        )

        health_width = int(
            bar_width * max(0, self.health) / self.max_health
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                cx - bar_width // 2,
                cy - self.size // 2 - 12,
                health_width,
                5
            )
        )


# ============================================================
# BOSS
# ============================================================

class Boss:
    def __init__(self):
        data = BOSS_DATA[level - 1]

        self.name = data[0]
        self.max_health = data[1]
        self.speed = data[2]
        self.color = data[3]
        self.power = data[4]

        self.health = self.max_health

        self.x = WIDTH // 2
        self.y = 110

        self.size = 76
        self.anim = 0
        self.attack_timer = 100
        self.teleport_timer = 240

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size
        )

    def update(self):
        self.anim += 0.06

        dx = player.centerx - self.x
        dy = player.centery - self.y

        distance = math.hypot(dx, dy)

        if distance > 1:
            nx = dx / distance
            ny = dy / distance

            new_rect = self.rect.copy()
            new_rect.x += int(nx * self.speed)

            if not rect_hits_wall(new_rect):
                self.x = new_rect.centerx

            new_rect = self.rect.copy()
            new_rect.y += int(ny * self.speed)

            if not rect_hits_wall(new_rect):
                self.y = new_rect.centery

        self.attack_timer -= 1
        self.teleport_timer -= 1

        if self.attack_timer <= 0:
            self.attack()
            self.attack_timer = max(45, 115 - level * 4)

        if (
            self.power == "TELEPORT"
            and self.teleport_timer <= 0
        ):
            self.teleport()
            self.teleport_timer = 240

    def attack(self):
        angle = math.atan2(
            player.centery - self.y,
            player.centerx - self.x
        )

        if self.power == "BURST":
            for offset in [-0.25, -0.12, 0, 0.12, 0.25]:
                a = angle + offset
                enemy_bullets.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(a) * 5,
                    "vy": math.sin(a) * 5,
                    "life": 180,
                    "color": self.color
                })

        elif self.power == "DASH":
            self.x += math.cos(angle) * 100
            self.y += math.sin(angle) * 100

        elif self.power == "FIRE":
            for _ in range(4):
                a = angle + random.uniform(-0.35, 0.35)

                enemy_bullets.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(a) * 5,
                    "vy": math.sin(a) * 5,
                    "life": 180,
                    "color": ORANGE
                })

        elif self.power == "RING":
            for i in range(12):
                a = math.pi * 2 * i / 12

                enemy_bullets.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(a) * 3.5,
                    "vy": math.sin(a) * 3.5,
                    "life": 220,
                    "color": YELLOW
                })

        elif self.power == "MISSILES":
            for _ in range(3):
                a = angle + random.uniform(-0.2, 0.2)

                enemy_bullets.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(a) * 4,
                    "vy": math.sin(a) * 4,
                    "life": 240,
                    "color": ORANGE
                })

        elif self.power == "SPREAD":
            for i in range(9):
                a = angle - 0.6 + i * 0.15

                enemy_bullets.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(a) * 4,
                    "vy": math.sin(a) * 4,
                    "life": 200,
                    "color": BLUE
                })

        else:
            for i in range(10):
                a = math.pi * 2 * i / 10

                enemy_bullets.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(a) * 3.8,
                    "vy": math.sin(a) * 3.8,
                    "life": 210,
                    "color": self.color
                })

    def teleport(self):
        x, y = find_safe_spawn()

        self.x = x
        self.y = y

        spawn_particles(
            self.x,
            self.y,
            self.color,
            35,
            6
        )

    def draw(self):
        cx = int(self.x)
        cy = int(self.y)

        pulse = math.sin(self.anim * 2) * 5

        # Large energy rings
        pygame.draw.circle(
            screen,
            self.color,
            (cx, cy),
            int(55 + pulse),
            2
        )

        pygame.draw.circle(
            screen,
            self.color,
            (cx, cy),
            44,
            2
        )

        # Boss core
        points = []

        for i in range(8):
            angle = self.anim + i * math.pi / 4

            radius = 38 if i % 2 == 0 else 28

            points.append((
                int(cx + math.cos(angle) * radius),
                int(cy + math.sin(angle) * radius)
            ))

        pygame.draw.polygon(
            screen,
            self.color,
            points
        )

        pygame.draw.polygon(
            screen,
            WHITE,
            points,
            2
        )

        pygame.draw.circle(
            screen,
            DARK,
            (cx, cy),
            20
        )

        pygame.draw.circle(
            screen,
            self.color,
            (cx, cy),
            10
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (cx, cy),
            4
        )

        # Boss name
        draw_text(
            self.name,
            FONT,
            self.color,
            cx,
            cy - 65,
            True
        )


# ============================================================
# POWERUPS
# ============================================================

def spawn_powerup(x, y):
    power_type = random.choice([
        "health",
        "rapid",
        "damage",
        "shield",
        "triple"
    ])

    powerups.append({
        "x": x,
        "y": y,
        "type": power_type,
        "life": 600,
        "angle": random.random() * 6
    })


def draw_powerup(power):
    x = int(power["x"])
    y = int(power["y"])

    power["angle"] += 0.05

    colors = {
        "health": GREEN,
        "rapid": YELLOW,
        "damage": RED,
        "shield": BLUE,
        "triple": PURPLE
    }

    color = colors[power["type"]]

    pygame.draw.circle(
        screen,
        color,
        (x, y),
        17,
        2
    )

    pygame.draw.circle(
        screen,
        color,
        (x, y),
        7
    )

    symbols = {
        "health": "+",
        "rapid": "R",
        "damage": "D",
        "shield": "S",
        "triple": "3"
    }

    draw_text(
        symbols[power["type"]],
        FONT,
        WHITE,
        x,
        y,
        True
    )


def collect_powerups():
    global player_health
    global rapid_timer
    global damage_timer
    global shield_timer
    global triple_timer

    for power in powerups[:]:
        distance = math.hypot(
            power["x"] - player.centerx,
            power["y"] - player.centery
        )

        if distance < 30:
            if power["type"] == "health":
                player_health = min(
                    PLAYER_MAX_HEALTH,
                    player_health + 60
                )

            elif power["type"] == "rapid":
                rapid_timer = 600

            elif power["type"] == "damage":
                damage_timer = 600

            elif power["type"] == "shield":
                shield_timer = 500

            elif power["type"] == "triple":
                triple_timer = 500

            spawn_particles(
                power["x"],
                power["y"],
                GREEN,
                25,
                5
            )

            powerups.remove(power)


# ============================================================
# PLAYER
# ============================================================

def move_player():
    keys = pygame.key.get_pressed()

    dx = 0
    dy = 0

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy -= 1

    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy += 1

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx -= 1

    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx += 1

    if dx == 0 and dy == 0:
        return

    length = math.hypot(dx, dy)

    dx /= length
    dy /= length

    new_rect = player.copy()
    new_rect.x += int(dx * PLAYER_SPEED)

    if (
        new_rect.left >= 0
        and new_rect.right <= WIDTH
        and not rect_hits_wall(new_rect)
    ):
        player.x = new_rect.x

    new_rect = player.copy()
    new_rect.y += int(dy * PLAYER_SPEED)

    if (
        new_rect.top >= 0
        and new_rect.bottom <= HEIGHT
        and not rect_hits_wall(new_rect)
    ):
        player.y = new_rect.y


def draw_player():
    global player_angle
    global player_pulse

    player_angle += 0.035
    player_pulse += 0.08

    cx = player.centerx
    cy = player.centery

    mouse_x, mouse_y = pygame.mouse.get_pos()

    angle = math.atan2(
        mouse_y - cy,
        mouse_x - cx
    )

    pulse = (math.sin(player_pulse) + 1) * 2

    ring_radius = int(28 + pulse)

    # Energy ring
    pygame.draw.circle(
        screen,
        (0, 90, 120),
        (cx, cy),
        ring_radius,
        1
    )

    pygame.draw.circle(
        screen,
        (0, 140, 180),
        (cx, cy),
        34,
        1
    )

    # Shield
    if shield_timer > 0:
        pygame.draw.circle(
            screen,
            BLUE,
            (cx, cy),
            36,
            3
        )

        pygame.draw.circle(
            screen,
            (40, 150, 255),
            (cx, cy),
            42,
            1
        )

    forward = pygame.Vector2(
        math.cos(angle),
        math.sin(angle)
    )

    right = pygame.Vector2(
        -forward.y,
        forward.x
    )

    def point(f, r):
        return (
            int(cx + forward.x * f + right.x * r),
            int(cy + forward.y * f + right.y * r)
        )

    # Rear engine glow
    for radius in range(13, 3, -3):
        pygame.draw.circle(
            screen,
            ORANGE,
            point(-15, 0),
            radius,
            1
        )

    # Main drone
    body = [
        point(25, 0),
        point(5, 13),
        point(-14, 11),
        point(-8, 0),
        point(-14, -11),
        point(5, -13),
    ]

    pygame.draw.polygon(
        screen,
        CYAN,
        body
    )

    pygame.draw.polygon(
        screen,
        WHITE,
        body,
        2
    )

    # Energy wings
    wing1 = [
        point(3, 10),
        point(-8, 25),
        point(-18, 18),
        point(-9, 5)
    ]

    wing2 = [
        point(3, -10),
        point(-8, -25),
        point(-18, -18),
        point(-9, -5)
    ]

    pygame.draw.polygon(
        screen,
        BLUE,
        wing1
    )

    pygame.draw.polygon(
        screen,
        BLUE,
        wing2
    )

    pygame.draw.polygon(
        screen,
        WHITE,
        wing1,
        1
    )

    pygame.draw.polygon(
        screen,
        WHITE,
        wing2,
        1
    )

    # Central neural core
    pygame.draw.circle(
        screen,
        DARK,
        (cx, cy),
        10
    )

    pygame.draw.circle(
        screen,
        GREEN,
        (cx, cy),
        int(6 + pulse / 2)
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (cx, cy),
        2
    )

    # Rear fins
    pygame.draw.line(
        screen,
        GREEN,
        point(-8, 8),
        point(-25, 13),
        3
    )

    pygame.draw.line(
        screen,
        GREEN,
        point(-8, -8),
        point(-25, -13),
        3
    )


# ============================================================
# SHOOTING
# ============================================================

def shoot():
    global fire_timer

    if fire_timer > 0:
        return

    mouse_x, mouse_y = pygame.mouse.get_pos()

    dx = mouse_x - player.centerx
    dy = mouse_y - player.centery

    angle = math.atan2(dy, dx)

    angles = [angle]

    if triple_timer > 0:
        angles = [
            angle - 0.15,
            angle,
            angle + 0.15
        ]

    for a in angles:
        bullets.append({
            "x": player.centerx,
            "y": player.centery,
            "vx": math.cos(a) * BULLET_SPEED,
            "vy": math.sin(a) * BULLET_SPEED,
            "bounces": 0,
            "damage": BULLET_DAMAGE * (2 if damage_timer > 0 else 1),
            "life": 180
        })

    spawn_particles(
        player.centerx + math.cos(angle) * 20,
        player.centery + math.sin(angle) * 20,
        CYAN,
        5,
        2
    )

    if rapid_timer > 0:
        fire_timer = 5
    else:
        fire_timer = 10


# ============================================================
# BULLETS
# ============================================================

def update_bullets():
    global score
    global boss
    global boss_was_defeated

    for bullet in bullets[:]:
        old_x = bullet["x"]
        old_y = bullet["y"]

        bullet["x"] += bullet["vx"]
        bullet["y"] += bullet["vy"]

        bullet["life"] -= 1

        bounced = False

        if bullet["x"] <= 3 or bullet["x"] >= WIDTH - 3:
            bullet["vx"] *= -1
            bullet["bounces"] += 1
            bounced = True

        if bullet["y"] <= 3 or bullet["y"] >= HEIGHT - 3:
            bullet["vy"] *= -1
            bullet["bounces"] += 1
            bounced = True

        if bounced:
            spawn_particles(
                bullet["x"],
                bullet["y"],
                CYAN,
                3,
                1
            )

        bullet_rect = pygame.Rect(
            int(bullet["x"] - 4),
            int(bullet["y"] - 4),
            8,
            8
        )

        hit_wall = False

        for wall in obstacles:
            if bullet_rect.colliderect(wall):
                hit_wall = True

                bullet["x"] = old_x
                bullet["y"] = old_y

                if abs(bullet["vx"]) > abs(bullet["vy"]):
                    bullet["vx"] *= -1
                else:
                    bullet["vy"] *= -1

                bullet["bounces"] += 1

                spawn_particles(
                    bullet["x"],
                    bullet["y"],
                    CYAN,
                    5,
                    2
                )

                break

        if (
            bullet["bounces"] > MAX_BOUNCES
            or bullet["life"] <= 0
        ):
            if bullet in bullets:
                bullets.remove(bullet)

            continue

        # Enemy collision
        removed = False

        for enemy in enemies[:]:
            if bullet_rect.colliderect(enemy.rect):
                enemy.health -= bullet["damage"]

                spawn_particles(
                    bullet["x"],
                    bullet["y"],
                    enemy.color,
                    8,
                    3
                )

                if bullet in bullets:
                    bullets.remove(bullet)

                removed = True

                if enemy.health <= 0:
                    score += enemy.points

                    spawn_particles(
                        enemy.x,
                        enemy.y,
                        enemy.color,
                        25,
                        6
                    )

                    if random.random() < 0.16:
                        spawn_powerup(
                            enemy.x,
                            enemy.y
                        )

                    enemies.remove(enemy)

                break

        if removed:
            continue

        # Boss collision
        if boss is not None:
            if bullet_rect.colliderect(boss.rect):
                boss.health -= bullet["damage"]

                spawn_particles(
                    bullet["x"],
                    bullet["y"],
                    boss.color,
                    10,
                    3
                )

                if bullet in bullets:
                    bullets.remove(bullet)

                if boss.health <= 0:
                    score += 2000 + level * 500

                    spawn_particles(
                        boss.x,
                        boss.y,
                        boss.color,
                        70,
                        8
                    )

                    boss = None
                    boss_was_defeated = True

                continue


# ============================================================
# ENEMY BULLETS
# ============================================================

def update_enemy_bullets():
    global player_health
    global screen_shake

    for bullet in enemy_bullets[:]:
        bullet["x"] += bullet["vx"]
        bullet["y"] += bullet["vy"]

        bullet["life"] -= 1

        if (
            bullet["x"] < -20
            or bullet["x"] > WIDTH + 20
            or bullet["y"] < -20
            or bullet["y"] > HEIGHT + 20
            or bullet["life"] <= 0
        ):
            enemy_bullets.remove(bullet)
            continue

        bullet_rect = pygame.Rect(
            int(bullet["x"] - 5),
            int(bullet["y"] - 5),
            10,
            10
        )

        blocked = False

        for wall in obstacles:
            if bullet_rect.colliderect(wall):
                blocked = True
                break

        if blocked:
            spawn_particles(
                bullet["x"],
                bullet["y"],
                bullet["color"],
                4,
                2
            )

            enemy_bullets.remove(bullet)
            continue

        if bullet_rect.colliderect(player):
            if shield_timer <= 0:
                player_health -= 10
                screen_shake = 7

            spawn_particles(
                bullet["x"],
                bullet["y"],
                bullet["color"],
                8,
                3
            )

            enemy_bullets.remove(bullet)


# ============================================================
# ENEMY SPAWNING
# ============================================================

def spawn_enemy():
    global enemies_spawned

    choices = ["normal", "normal", "normal"]

    if level >= 2:
        choices.append("flanker")

    if level >= 4:
        choices.append("tank")

    enemy_type = random.choice(choices)

    enemies.append(
        Enemy(enemy_type)
    )

    enemies_spawned += 1


# ============================================================
# DAMAGE / COLLISIONS
# ============================================================

def handle_enemy_collisions():
    global player_health
    global screen_shake

    for enemy in enemies:
        if player.colliderect(enemy.rect):
            if shield_timer <= 0:
                player_health -= 0.35
                screen_shake = 4

            dx = enemy.x - player.centerx
            dy = enemy.y - player.centery

            distance = max(1, math.hypot(dx, dy))

            enemy.x += dx / distance * 1.5
            enemy.y += dy / distance * 1.5


def handle_boss_collision():
    global player_health
    global screen_shake

    if boss is not None and player.colliderect(boss.rect):
        if shield_timer <= 0:
            player_health -= 0.7
            screen_shake = 6


# ============================================================
# LEVEL MANAGEMENT
# ============================================================

def start_level():
    global obstacles
    global boss
    global boss_was_defeated
    global enemies_spawned
    global enemies_to_spawn
    global spawn_sides
    global level_message_timer
    global boss_warning_timer

    obstacles = LEVEL_LAYOUTS[level - 1]

    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    particles.clear()
    powerups.clear()

    boss = None
    boss_was_defeated = False

    enemies_spawned = 0
    enemies_to_spawn = 3 + level

    spawn_sides = random.sample(
        ["top", "bottom", "left", "right"],
        2
    )

    x, y = find_safe_spawn()

    player.center = (
        int(x),
        int(y)
    )

    level_message_timer = 180
    boss_warning_timer = 0


def reset_game():
    global level
    global score
    global player_health
    global rapid_timer
    global damage_timer
    global shield_timer
    global triple_timer
    global fire_timer
    global game_state
    global transition_timer

    level = 1
    score = 0

    player_health = PLAYER_MAX_HEALTH

    rapid_timer = 0
    damage_timer = 0
    shield_timer = 0
    triple_timer = 0
    fire_timer = 0

    transition_timer = 0

    start_level()

    game_state = PLAYING


# ============================================================
# UPDATE GAME
# ============================================================

def update_game():
    global fire_timer
    global rapid_timer
    global damage_timer
    global shield_timer
    global triple_timer
    global player_health
    global boss
    global boss_warning_timer
    global level
    global game_state
    global screen_shake
    global level_message_timer
    global transition_timer

    if fire_timer > 0:
        fire_timer -= 1

    if rapid_timer > 0:
        rapid_timer -= 1

    if damage_timer > 0:
        damage_timer -= 1

    if shield_timer > 0:
        shield_timer -= 1

    if triple_timer > 0:
        triple_timer -= 1

    if level_message_timer > 0:
        level_message_timer -= 1

    if boss_warning_timer > 0:
        boss_warning_timer -= 1

    if screen_shake > 0:
        screen_shake -= 1

    move_player()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        shoot()

    # Spawn enemies slowly
    if (
        enemies_spawned < enemies_to_spawn
        and len(enemies) < 4
    ):
        if random.random() < 0.025:
            spawn_enemy()

    for enemy in enemies:
        enemy.update()

    if (
        enemies_spawned >= enemies_to_spawn
        and len(enemies) == 0
        and boss is None
        and not boss_was_defeated
    ):
        boss = Boss()
        boss_warning_timer = 180

    if boss is not None:
        boss.update()

    update_bullets()
    update_enemy_bullets()
    update_particles()

    collect_powerups()

    for power in powerups[:]:
        power["life"] -= 1

        if power["life"] <= 0:
            powerups.remove(power)

    handle_enemy_collisions()
    handle_boss_collision()

    if player_health <= 0:
        player_health = 0
        game_state = GAME_OVER
        return

    # Level complete
    if (
        boss_was_defeated
        and boss is None
        and len(enemies) == 0
    ):
        if level >= MAX_LEVEL:
            game_state = VICTORY
        else:
            level += 1
            transition_timer = 150
            start_level()


# ============================================================
# BACKGROUND
# ============================================================

def draw_background():
    screen.fill(BLACK)

    # Grid
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(
            screen,
            GRID,
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(
            screen,
            GRID,
            (0, y),
            (WIDTH, y)
        )

    # Decorative border
    pygame.draw.rect(
        screen,
        (25, 80, 105),
        (8, 8, WIDTH - 16, HEIGHT - 16),
        2
    )


def draw_obstacles():
    for wall in obstacles:
        pygame.draw.rect(
            screen,
            (12, 30, 45),
            wall
        )

        pygame.draw.rect(
            screen,
            CYAN,
            wall,
            1
        )

        # Wall energy line
        if wall.width > wall.height:
            y = wall.centery

            pygame.draw.line(
                screen,
                (0, 80, 100),
                (wall.left + 8, y),
                (wall.right - 8, y),
                1
            )
        else:
            x = wall.centerx

            pygame.draw.line(
                screen,
                (0, 80, 100),
                (x, wall.top + 8),
                (x, wall.bottom - 8),
                1
            )


# ============================================================
# HUD
# ============================================================

def draw_health_bar():
    x = 25
    y = 25

    width = 240
    height = 20

    pygame.draw.rect(
        screen,
        (30, 35, 45),
        (x, y, width, height)
    )

    health_width = int(
        width * player_health / PLAYER_MAX_HEALTH
    )

    health_color = GREEN

    if player_health < 80:
        health_color = RED
    elif player_health < 130:
        health_color = YELLOW

    pygame.draw.rect(
        screen,
        health_color,
        (x, y, health_width, height)
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (x, y, width, height),
        2
    )

    draw_text(
        f"HP {int(player_health)}/{PLAYER_MAX_HEALTH}",
        FONT_SMALL,
        WHITE,
        x + 8,
        y + 2
    )


def draw_hud():
    draw_health_bar()

    draw_text(
        f"SCORE {score}",
        FONT,
        WHITE,
        WIDTH - 190,
        22
    )

    draw_text(
        f"LEVEL {level}/{MAX_LEVEL}",
        FONT,
        CYAN,
        WIDTH // 2,
        20,
        True
    )

    # Power indicators
    x = 25
    y = 55

    powers = [
        ("RAPID", rapid_timer, YELLOW),
        ("DMG", damage_timer, RED),
        ("SHIELD", shield_timer, BLUE),
        ("TRIPLE", triple_timer, PURPLE)
    ]

    for name, timer, color in powers:
        if timer > 0:
            seconds = timer // 60

            pygame.draw.rect(
                screen,
                color,
                (x, y, 90, 20),
                1
            )

            draw_text(
                f"{name} {seconds}s",
                FONT_SMALL,
                color,
                x + 5,
                y + 2
            )

            x += 98

    # Enemy counter
    remaining = len(enemies)

    if boss is None:
        draw_text(
            f"HOSTILES {remaining}",
            FONT_SMALL,
            WHITE,
            WIDTH - 180,
            HEIGHT - 35
        )


def draw_boss_bar():
    if boss is None:
        return

    width = 600
    height = 24

    x = WIDTH // 2 - width // 2
    y = HEIGHT - 55

    pygame.draw.rect(
        screen,
        (35, 20, 30),
        (x, y, width, height)
    )

    health_width = int(
        width * max(0, boss.health) / boss.max_health
    )

    pygame.draw.rect(
        screen,
        boss.color,
        (x, y, health_width, height)
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (x, y, width, height),
        2
    )

    draw_text(
        boss.name,
        FONT_SMALL,
        WHITE,
        WIDTH // 2,
        y - 22,
        True
    )


# ============================================================
# MENUS
# ============================================================

def draw_menu():
    draw_background()

    # Decorative circles
    pygame.draw.circle(
        screen,
        (0, 50, 70),
        (WIDTH // 2, 280),
        130,
        2
    )

    pygame.draw.circle(
        screen,
        CYAN,
        (WIDTH // 2, 280),
        70,
        2
    )

    pygame.draw.circle(
        screen,
        GREEN,
        (WIDTH // 2, 280),
        25
    )

    draw_text(
        "NEURAL FRONTIER",
        FONT_HUGE,
        CYAN,
        WIDTH // 2,
        125,
        True
    )

    draw_text(
        "TACTICAL NEURAL COMBAT SYSTEM",
        FONT,
        WHITE,
        WIDTH // 2,
        180,
        True
    )

    draw_text(
        "ENTER  //  DEPLOY",
        FONT_BIG,
        GREEN,
        WIDTH // 2,
        450,
        True
    )

    draw_text(
        "C  //  CONTROLS",
        FONT,
        WHITE,
        WIDTH // 2,
        500,
        True
    )

    draw_text(
        "ESC  //  EXIT",
        FONT,
        WHITE,
        WIDTH // 2,
        535,
        True
    )

    draw_text(
        "10 LEVELS  •  10 BOSSES  •  NEURAL WARFARE",
        FONT_SMALL,
        (100, 150, 170),
        WIDTH // 2,
        620,
        True
    )


def draw_controls():
    draw_background()

    draw_text(
        "CONTROL SYSTEM",
        FONT_HUGE,
        CYAN,
        WIDTH // 2,
        100,
        True
    )

    controls = [
        ("W A S D / ARROWS", "MOVE"),
        ("MOUSE", "AIM"),
        ("HOLD SPACE", "FIRE"),
        ("P", "PAUSE"),
        ("ESC", "MENU"),
    ]

    y = 220

    for key, action in controls:
        draw_text(
            key,
            FONT_BIG,
            GREEN,
            320,
            y,
            True
        )

        draw_text(
            action,
            FONT,
            WHITE,
            600,
            y,
            True
        )

        y += 65

    draw_text(
        "PRESS C OR ESC TO RETURN",
        FONT,
        WHITE,
        WIDTH // 2,
        590,
        True
    )


def draw_pause():
    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 180))

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_text(
        "SYSTEM PAUSED",
        FONT_HUGE,
        CYAN,
        WIDTH // 2,
        280,
        True
    )

    draw_text(
        "PRESS P TO RESUME",
        FONT_BIG,
        WHITE,
        WIDTH // 2,
        360,
        True
    )

    draw_text(
        "ESC TO RETURN TO MENU",
        FONT,
        WHITE,
        WIDTH // 2,
        420,
        True
    )


def draw_game_over():
    draw_background()

    draw_text(
        "SYSTEM FAILURE",
        FONT_HUGE,
        RED,
        WIDTH // 2,
        200,
        True
    )

    draw_text(
        f"FINAL SCORE  {score}",
        FONT_BIG,
        WHITE,
        WIDTH // 2,
        310,
        True
    )

    draw_text(
        f"REACHED LEVEL  {level}",
        FONT,
        CYAN,
        WIDTH // 2,
        360,
        True
    )

    draw_text(
        "R  //  RESTART",
        FONT_BIG,
        GREEN,
        WIDTH // 2,
        450,
        True
    )

    draw_text(
        "ESC  //  MENU",
        FONT,
        WHITE,
        WIDTH // 2,
        500,
        True
    )


def draw_victory():
    draw_background()

    draw_text(
        "NEURAL FRONTIER",
        FONT_HUGE,
        GREEN,
        WIDTH // 2,
        150,
        True
    )

    draw_text(
        "MISSION COMPLETE",
        FONT_BIG,
        CYAN,
        WIDTH // 2,
        250,
        True
    )

    draw_text(
        "ALL 10 NEURAL SECTORS CLEARED",
        FONT,
        WHITE,
        WIDTH // 2,
        320,
        True
    )

    draw_text(
        f"FINAL SCORE  {score}",
        FONT_BIG,
        YELLOW,
        WIDTH // 2,
        390,
        True
    )

    draw_text(
        "R  //  PLAY AGAIN",
        FONT_BIG,
        GREEN,
        WIDTH // 2,
        480,
        True
    )

    draw_text(
        "ESC  //  MENU",
        FONT,
        WHITE,
        WIDTH // 2,
        530,
        True
    )


# ============================================================
# GAME DRAW
# ============================================================

def draw_game():
    draw_background()
    draw_obstacles()

    # Powerups
    for power in powerups:
        draw_powerup(power)

    # Bullets
    for bullet in bullets:
        pygame.draw.circle(
            screen,
            CYAN,
            (int(bullet["x"]), int(bullet["y"])),
            4
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(bullet["x"]), int(bullet["y"])),
            2
        )

    # Enemy bullets
    for bullet in enemy_bullets:
        pygame.draw.circle(
            screen,
            bullet["color"],
            (int(bullet["x"]), int(bullet["y"])),
            5
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(bullet["x"]), int(bullet["y"])),
            2
        )

    # Enemies
    for enemy in enemies:
        enemy.draw()

    # Boss
    if boss is not None:
        boss.draw()

    # Player
    draw_player()

    draw_particles()

    draw_hud()
    draw_boss_bar()

    # Level announcement
    if level_message_timer > 0:
        alpha = min(
            255,
            level_message_timer * 2
        )

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, min(120, alpha))
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        draw_text(
            f"SECTOR {level}",
            FONT_HUGE,
            CYAN,
            WIDTH // 2,
            HEIGHT // 2 - 35,
            True
        )

        draw_text(
            "NEURAL DEPLOYMENT",
            FONT,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 + 30,
            True
        )

    # Boss warning
    if boss_warning_timer > 0:
        if (boss_warning_timer // 10) % 2 == 0:
            draw_text(
                "!! BOSS DETECTED !!",
                FONT_BIG,
                RED,
                WIDTH // 2,
                120,
                True
            )


# ============================================================
# MAIN LOOP
# ============================================================

reset_game()

game_state = MENU

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if game_state == MENU:

                if event.key == pygame.K_RETURN:
                    reset_game()

                elif event.key == pygame.K_c:
                    game_state = CONTROLS

                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif game_state == CONTROLS:

                if event.key in (
                    pygame.K_c,
                    pygame.K_ESCAPE
                ):
                    game_state = MENU

            elif game_state == PLAYING:

                if event.key == pygame.K_p:
                    game_state = PAUSED

                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

            elif game_state == PAUSED:

                if event.key == pygame.K_p:
                    game_state = PLAYING

                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

            elif game_state == GAME_OVER:

                if event.key == pygame.K_r:
                    reset_game()

                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

            elif game_state == VICTORY:

                if event.key == pygame.K_r:
                    reset_game()

                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    if game_state == PLAYING:
        update_game()

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    if game_state == MENU:
        draw_menu()

    elif game_state == CONTROLS:
        draw_controls()

    elif game_state == PLAYING:
        draw_game()

    elif game_state == PAUSED:
        draw_game()
        draw_pause()

    elif game_state == GAME_OVER:
        draw_game_over()

    elif game_state == VICTORY:
        draw_victory()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()