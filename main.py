import pygame
import random
import math
import wave
import struct
import tempfile
import os

pygame.init()

WIDTH = 1000
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEURAL FRONTIER")
clock = pygame.time.Clock()

# ============================================================
# AUDIO
# ============================================================

AUDIO_AVAILABLE = False
sfx_enabled = True
sound_cache = {}
audio_temp_files = []

try:
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False


def create_tone(
    name,
    frequency,
    duration,
    volume=0.25,
    end_frequency=None,
    wave_type="sine"
):
    if not AUDIO_AVAILABLE:
        return None

    if name in sound_cache:
        return sound_cache[name]

    sample_rate = 44100
    samples = int(sample_rate * duration)

    if end_frequency is None:
        end_frequency = frequency

    data = bytearray()

    for i in range(samples):

        t = i / sample_rate
        progress = i / max(1, samples - 1)

        freq = frequency + (
            end_frequency - frequency
        ) * progress

        phase = 2 * math.pi * freq * t

        if wave_type == "square":
            value = 1 if math.sin(phase) >= 0 else -1
        elif wave_type == "triangle":
            value = (
                2
                * abs(
                    2
                    * (
                        t * freq
                        - math.floor(t * freq + 0.5)
                    )
                )
                - 1
            )
        else:
            value = math.sin(phase)

        envelope = 1.0

        if t < 0.02:
            envelope = t / 0.02

        if duration - t < 0.08:
            envelope = max(
                0,
                (duration - t) / 0.08
            )

        sample = int(
            value
            * volume
            * envelope
            * 32767
        )

        data.extend(
            struct.pack("<h", sample)
        )

    try:

        temp = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )

        temp.close()

        with wave.open(
            temp.name,
            "wb"
        ) as wav:

            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(data)

        sound = pygame.mixer.Sound(
            temp.name
        )

        sound_cache[name] = sound
        audio_temp_files.append(
            temp.name
        )

        return sound

    except Exception:
        return None


def setup_audio():

    if not AUDIO_AVAILABLE:
        return

    create_tone(
        "shoot",
        850,
        0.055,
        0.18,
        1300,
        "square"
    )

    create_tone(
        "hit",
        180,
        0.08,
        0.18,
        90
    )

    create_tone(
        "destroy",
        180,
        0.18,
        0.22,
        60
    )

    create_tone(
        "powerup",
        500,
        0.22,
        0.22,
        1100
    )

    create_tone(
        "damage",
        130,
        0.15,
        0.25,
        60
    )

    create_tone(
        "boss",
        100,
        0.55,
        0.28,
        40
    )

    create_tone(
        "boss_attack",
        180,
        0.16,
        0.20,
        60
    )

    create_tone(
        "victory",
        450,
        0.7,
        0.22,
        1000
    )

    create_tone(
        "laser",
        110,
        0.35,
        0.25,
        520
    )

    create_tone(
        "laser_pulse",
        420,
        0.08,
        0.12,
        700
    )


def play_sound(name):

    if not AUDIO_AVAILABLE:
        return

    if not sfx_enabled:
        return

    sound = sound_cache.get(name)

    if sound:

        try:
            sound.play()
        except pygame.error:
            pass


setup_audio()

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

FONT_SMALL = pygame.font.SysFont(
    "consolas",
    16
)

FONT = pygame.font.SysFont(
    "consolas",
    22
)

FONT_MEDIUM = pygame.font.SysFont(
    "consolas",
    30,
    bold=True
)

FONT_BIG = pygame.font.SysFont(
    "consolas",
    48,
    bold=True
)

FONT_HUGE = pygame.font.SysFont(
    "consolas",
    70,
    bold=True
)

# ============================================================
# CONSTANTS
# ============================================================

MAX_LEVEL = 10

PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 200

BULLET_SPEED = 10
BULLET_DAMAGE = 25
MAX_BOUNCES = 3

LASER_DURATION = 5 * FPS
LASER_TICK_RATE = 10
LASER_ENEMY_DAMAGE = 20
LASER_BOSS_DAMAGE = 38
LASER_WIDTH = 22

NORMAL_CONTACT_DAMAGE = 10
FLANKER_CONTACT_DAMAGE = 8
TANK_CONTACT_DAMAGE = 18

NORMAL_BULLET_DAMAGE = 8
FLANKER_BULLET_DAMAGE = 10
TANK_BULLET_DAMAGE = 14

BOSS_CONTACT_DAMAGE = 20

# ============================================================
# STATES
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

player_angle = 0
player_pulse = 0

laser_active_timer = 0
laser_damage_timer = 0
laser_angle = 0
laser_pulse = 0

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
# LEVELS
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

def rect_hits_wall(rect):

    for wall in obstacles:

        if rect.colliderect(wall):
            return True

    return False


def spawn_particles(
    x,
    y,
    color,
    amount=8
):

    for _ in range(amount):

        angle = random.uniform(
            0,
            math.tau
        )

        speed = random.uniform(
            1,
            5
        )

        particles.append({

            "x": x,
            "y": y,

            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,

            "life": random.randint(
                20,
                45
            ),

            "max_life": 45,

            "color": color,

            "size": random.randint(
                2,
                5
            )
        })


def find_safe_spawn():

    for _ in range(1000):

        x = random.randint(
            80,
            WIDTH - 80
        )

        y = random.randint(
            80,
            HEIGHT - 80
        )

        test = pygame.Rect(
            x - 20,
            y - 20,
            40,
            40
        )

        if rect_hits_wall(test):
            continue

        if test.colliderect(
            player.inflate(
                180,
                180
            )
        ):
            continue

        return x, y

    return WIDTH // 2, HEIGHT // 2


def get_spawn_position(
    side,
    size
):

    margin = size + 20

    if side == "top":

        return (
            random.randint(
                margin,
                WIDTH - margin
            ),
            -size
        )

    if side == "bottom":

        return (
            random.randint(
                margin,
                WIDTH - margin
            ),
            HEIGHT + size
        )

    if side == "left":

        return (
            -size,
            random.randint(
                margin,
                HEIGHT - margin
            )
        )

    return (
        WIDTH + size,
        random.randint(
            margin,
            HEIGHT - margin
        )
    )


def line_circle_hit(
    x1,
    y1,
    dx,
    dy,
    cx,
    cy,
    radius
):

    vx = cx - x1
    vy = cy - y1

    projection = (
        vx * dx
        + vy * dy
    )

    if projection < 0:
        return False

    closest_x = (
        x1
        + dx * projection
    )

    closest_y = (
        y1
        + dy * projection
    )

    distance = math.hypot(
        cx - closest_x,
        cy - closest_y
    )

    return distance <= radius


# ============================================================
# LASER TARGET DETECTION
# ============================================================

def get_first_laser_target():

    """
    Finds the FIRST enemy/boss along the laser direction.

    This is the important part:
    the laser can hit only the nearest target.
    """

    dx = math.cos(
        laser_angle
    )

    dy = math.sin(
        laser_angle
    )

    origin_x = player.centerx
    origin_y = player.centery

    closest_distance = float("inf")
    closest_target = None

    # Check enemies.
    for enemy in enemies:

        vx = enemy.x - origin_x
        vy = enemy.y - origin_y

        projection = (
            vx * dx
            + vy * dy
        )

        if projection < 0:
            continue

        closest_x = (
            origin_x
            + dx * projection
        )

        closest_y = (
            origin_y
            + dy * projection
        )

        distance = math.hypot(
            enemy.x - closest_x,
            enemy.y - closest_y
        )

        hit_radius = (
            enemy.size / 2
            + LASER_WIDTH / 2
        )

        if distance <= hit_radius:

            # Approximate front edge of target.
            hit_distance = max(
                0,
                projection
                - enemy.size / 2
            )

            if hit_distance < closest_distance:

                closest_distance = hit_distance

                closest_target = (
                    "enemy",
                    enemy,
                    hit_distance
                )

    # Check boss.
    if boss is not None:

        vx = boss.x - origin_x
        vy = boss.y - origin_y

        projection = (
            vx * dx
            + vy * dy
        )

        if projection >= 0:

            closest_x = (
                origin_x
                + dx * projection
            )

            closest_y = (
                origin_y
                + dy * projection
            )

            distance = math.hypot(
                boss.x - closest_x,
                boss.y - closest_y
            )

            hit_radius = (
                boss.size / 2
                + LASER_WIDTH / 2
            )

            if distance <= hit_radius:

                hit_distance = max(
                    0,
                    projection
                    - boss.size / 2
                )

                if hit_distance < closest_distance:

                    closest_distance = (
                        hit_distance
                    )

                    closest_target = (
                        "boss",
                        boss,
                        hit_distance
                    )

    return closest_target


# ============================================================
# ENEMY
# ============================================================

class Enemy:

    def __init__(
        self,
        enemy_type
    ):

        self.type = enemy_type

        if enemy_type == "normal":

            self.size = 34

            self.health = (
                50
                + level * 8
            )

            self.speed = (
                0.8
                + level * 0.01
            )

            self.color = RED
            self.points = 100

            self.contact_damage = (
                NORMAL_CONTACT_DAMAGE
            )

            self.bullet_damage = (
                NORMAL_BULLET_DAMAGE
            )

        elif enemy_type == "flanker":

            self.size = 28

            self.health = (
                35
                + level * 6
            )

            self.speed = (
                1.0
                + level * 0.01
            )

            self.color = PURPLE
            self.points = 150

            self.contact_damage = (
                FLANKER_CONTACT_DAMAGE
            )

            self.bullet_damage = (
                FLANKER_BULLET_DAMAGE
            )

        else:

            self.size = 44

            self.health = (
                100
                + level * 12
            )

            self.speed = (
                0.6
                + level * 0.008
            )

            self.color = ORANGE
            self.points = 250

            self.contact_damage = (
                TANK_CONTACT_DAMAGE
            )

            self.bullet_damage = (
                TANK_BULLET_DAMAGE
            )

        side = random.choice(
            spawn_sides
        )

        self.x, self.y = get_spawn_position(
            side,
            self.size
        )

        self.angle = 0

        self.shoot_timer = random.randint(
            90,
            180
        )

        self.wobble = random.random() * math.tau

    def update(self):

        dx = (
            player.centerx
            - self.x
        )

        dy = (
            player.centery
            - self.y
        )

        distance = math.hypot(
            dx,
            dy
        )

        if distance > 0:

            dx /= distance
            dy /= distance

        if self.type == "flanker":

            side_x = -dy
            side_y = dx

            wave = math.sin(
                pygame.time.get_ticks()
                * 0.004
                + self.wobble
            )

            dx += (
                side_x
                * 0.45
                * wave
            )

            dy += (
                side_y
                * 0.45
                * wave
            )

            length = math.hypot(
                dx,
                dy
            )

            if length > 0:

                dx /= length
                dy /= length

        new_x = (
            self.x
            + dx * self.speed
        )

        new_y = (
            self.y
            + dy * self.speed
        )

        test = pygame.Rect(
            int(
                new_x
                - self.size / 2
            ),
            int(
                new_y
                - self.size / 2
            ),
            self.size,
            self.size
        )

        if not rect_hits_wall(test):

            self.x = new_x
            self.y = new_y

        self.angle = math.atan2(
            player.centery - self.y,
            player.centerx - self.x
        )

        self.shoot_timer -= 1

        if self.shoot_timer <= 0:

            self.shoot()

            self.shoot_timer = random.randint(
                max(60, 130 - level * 5),
                max(100, 200 - level * 4)
            )

    def shoot(self):

        dx = math.cos(
            self.angle
        )

        dy = math.sin(
            self.angle
        )

        enemy_bullets.append({

            "x": self.x,
            "y": self.y,

            "vx": dx * 4,
            "vy": dy * 4,

            "life": 180,

            "damage": self.bullet_damage,

            "color": self.color
        })

    def draw(self, surface):

        x = int(self.x)
        y = int(self.y)

        pulse = math.sin(
            pygame.time.get_ticks()
            * 0.006
            + self.wobble
        )

        if self.type == "normal":

            points = []

            for i in range(6):

                angle = (
                    self.angle
                    + i * math.tau / 6
                )

                radius = self.size / 2

                points.append((
                    int(
                        x
                        + math.cos(angle)
                        * radius
                    ),
                    int(
                        y
                        + math.sin(angle)
                        * radius
                    )
                ))

            pygame.draw.polygon(
                surface,
                DARK,
                points
            )

            pygame.draw.polygon(
                surface,
                self.color,
                points,
                3
            )

            pygame.draw.circle(
                surface,
                self.color,
                (x, y),
                7 + int(
                    pulse * 2
                )
            )

            pygame.draw.circle(
                surface,
                WHITE,
                (x, y),
                3
            )

        elif self.type == "flanker":

            points = [

                (
                    int(
                        x
                        + math.cos(self.angle)
                        * 22
                    ),
                    int(
                        y
                        + math.sin(self.angle)
                        * 22
                    )
                ),

                (
                    int(
                        x
                        + math.cos(
                            self.angle + 2.5
                        ) * 18
                    ),
                    int(
                        y
                        + math.sin(
                            self.angle + 2.5
                        ) * 18
                    )
                ),

                (
                    int(
                        x
                        + math.cos(
                            self.angle + math.pi
                        ) * 13
                    ),
                    int(
                        y
                        + math.sin(
                            self.angle + math.pi
                        ) * 13
                    )
                ),

                (
                    int(
                        x
                        + math.cos(
                            self.angle - 2.5
                        ) * 18
                    ),
                    int(
                        y
                        + math.sin(
                            self.angle - 2.5
                        ) * 18
                    )
                )
            ]

            pygame.draw.polygon(
                surface,
                DARK,
                points
            )

            pygame.draw.polygon(
                surface,
                self.color,
                points,
                3
            )

            pygame.draw.circle(
                surface,
                WHITE,
                (x, y),
                4
            )

        else:

            radius = self.size // 2

            pygame.draw.circle(
                surface,
                DARK,
                (x, y),
                radius
            )

            pygame.draw.circle(
                surface,
                self.color,
                (x, y),
                radius,
                4
            )

            pygame.draw.rect(
                surface,
                self.color,
                (
                    x - 12,
                    y - 12,
                    24,
                    24
                ),
                3
            )

            pygame.draw.line(
                surface,
                self.color,
                (
                    x - 20,
                    y
                ),
                (
                    x + 20,
                    y
                ),
                4
            )

            pygame.draw.line(
                surface,
                self.color,
                (
                    x,
                    y - 20
                ),
                (
                    x,
                    y + 20
                ),
                4
            )

            pygame.draw.circle(
                surface,
                ORANGE,
                (x, y),
                6 + int(pulse)
            )


# ============================================================
# BOSS
# ============================================================

class Boss:

    def __init__(
        self,
        name,
        health,
        speed,
        color,
        power
    ):

        self.name = name
        self.max_health = health
        self.health = health

        self.speed = (
            speed
            + level * 0.025
        )

        self.color = color
        self.power = power

        self.size = 76

        self.x, self.y = find_safe_spawn()

        self.angle = 0
        self.anim = 0

        self.orbit_direction = random.choice(
            [-1, 1]
        )

        self.orbit_distance = random.randint(
            190,
            300
        )

        self.attack_timer = random.randint(
            45,
            90
        )

        self.attack_phase = 0
        self.dash_timer = 0

    def update(self):

        self.anim += 1

        dx = (
            player.centerx
            - self.x
        )

        dy = (
            player.centery
            - self.y
        )

        distance = math.hypot(
            dx,
            dy
        )

        if distance > 0:

            to_player_x = dx / distance
            to_player_y = dy / distance

        else:

            to_player_x = 1
            to_player_y = 0

        desired_distance = (
            self.orbit_distance
        )

        if distance < desired_distance - 30:

            move_x = -to_player_x
            move_y = -to_player_y

        elif distance > desired_distance + 50:

            move_x = to_player_x
            move_y = to_player_y

        else:

            move_x = (
                -to_player_y
                * self.orbit_direction
            )

            move_y = (
                to_player_x
                * self.orbit_direction
            )

        wobble = math.sin(
            self.anim * 0.025
        )

        move_x += (
            -to_player_y
            * wobble
            * 0.12
        )

        move_y += (
            to_player_x
            * wobble
            * 0.12
        )

        length = math.hypot(
            move_x,
            move_y
        )

        if length > 0:

            move_x /= length
            move_y /= length

        new_x = (
            self.x
            + move_x * self.speed
        )

        new_y = (
            self.y
            + move_y * self.speed
        )

        test = pygame.Rect(
            int(
                new_x
                - self.size / 2
            ),
            int(
                new_y
                - self.size / 2
            ),
            self.size,
            self.size
        )

        if not rect_hits_wall(test):

            self.x = new_x
            self.y = new_y

        else:

            self.orbit_direction *= -1

        self.x = max(
            self.size / 2 + 5,
            min(
                WIDTH
                - self.size / 2
                - 5,
                self.x
            )
        )

        self.y = max(
            self.size / 2 + 5,
            min(
                HEIGHT
                - self.size / 2
                - 5,
                self.y
            )
        )

        self.angle = math.atan2(
            player.centery - self.y,
            player.centerx - self.x
        )

        self.attack_timer -= 1

        if self.attack_timer <= 0:

            self.attack()

            self.attack_timer = max(
                38,
                105 - level * 6
                + random.randint(-8, 10)
            )

        if self.dash_timer > 0:

            self.dash_timer -= 1

    def attack(self):

        play_sound(
            "boss_attack"
        )

        self.attack_phase += 1

        if self.power == "BURST":

            self.burst_attack()

        elif self.power == "DASH":

            self.dash_attack()

        elif self.power == "FIRE":

            self.fire_attack()

        elif self.power == "RING":

            self.ring_attack()

        elif self.power == "TELEPORT":

            self.teleport_attack()

        elif self.power == "MISSILES":

            self.missile_attack()

        elif self.power == "SPREAD":

            self.spread_attack()

        elif self.power == "CHAOS":

            self.chaos_attack()

        if level >= 4:

            if random.random() < 0.35:

                random.choice([
                    self.burst_attack,
                    self.ring_attack,
                    self.spread_attack
                ])()

        if level >= 7:

            if random.random() < 0.25:

                self.burst_attack()

    def burst_attack(self):

        count = 8 + level // 2

        speed = (
            3.2
            + level * 0.12
        )

        for i in range(count):

            angle = (
                i * math.tau / count
                + self.anim * 0.01
            )

            enemy_bullets.append({

                "x": self.x,
                "y": self.y,

                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,

                "life": 220,

                "damage": 7 + level // 2,

                "color": self.color
            })

    def dash_attack(self):

        spawn_particles(
            self.x,
            self.y,
            self.color,
            18
        )

        self.dash_timer = 18

        distance = (
            100
            + level * 7
        )

        new_x = (
            self.x
            + math.cos(self.angle)
            * distance
        )

        new_y = (
            self.y
            + math.sin(self.angle)
            * distance
        )

        test = pygame.Rect(
            int(
                new_x
                - self.size / 2
            ),
            int(
                new_y
                - self.size / 2
            ),
            self.size,
            self.size
        )

        if (
            0 < new_x < WIDTH
            and 0 < new_y < HEIGHT
            and not rect_hits_wall(test)
        ):

            self.x = new_x
            self.y = new_y

        for i in range(5):

            angle = (
                self.angle
                + math.pi
                + random.uniform(
                    -0.3,
                    0.3
                )
            )

            enemy_bullets.append({

                "x": self.x,
                "y": self.y,

                "vx": math.cos(angle) * 4,
                "vy": math.sin(angle) * 4,

                "life": 160,

                "damage": 10 + level // 2,

                "color": self.color
            })

    def fire_attack(self):

        count = 5 + level // 3

        spread = (
            0.7
            + level * 0.02
        )

        for i in range(count):

            if count == 1:

                shot_angle = self.angle

            else:

                shot_angle = (
                    self.angle
                    - spread / 2
                    + spread
                    * i
                    / (count - 1)
                )

            speed = (
                4
                + level * 0.12
            )

            enemy_bullets.append({

                "x": self.x,
                "y": self.y,

                "vx": math.cos(
                    shot_angle
                ) * speed,

                "vy": math.sin(
                    shot_angle
                ) * speed,

                "life": 220,

                "damage": 9 + level // 2,

                "color": ORANGE
            })

    def ring_attack(self):

        count = 12 + level

        speed = (
            2.7
            + level * 0.1
        )

        rotation = (
            self.attack_phase
            * 0.25
        )

        for i in range(count):

            angle = (
                i * math.tau / count
                + rotation
            )

            enemy_bullets.append({

                "x": self.x,
                "y": self.y,

                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,

                "life": 240,

                "damage": 8 + level // 2,

                "color": YELLOW
            })

    def teleport_attack(self):

        old_x = self.x
        old_y = self.y

        self.x, self.y = find_safe_spawn()

        spawn_particles(
            old_x,
            old_y,
            PURPLE,
            25
        )

        spawn_particles(
            self.x,
            self.y,
            PURPLE,
            30
        )

        self.angle = math.atan2(
            player.centery - self.y,
            player.centerx - self.x
        )

        self.burst_attack()

    def missile_attack(self):

        count = 3 + level // 3

        for _ in range(count):

            angle = (
                self.angle
                + random.uniform(
                    -0.4,
                    0.4
                )
            )

            speed = (
                2.5
                + level * 0.12
            )

            enemy_bullets.append({

                "x": self.x,
                "y": self.y,

                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,

                "life": 280,

                "damage": 12 + level // 2,

                "color": ORANGE
            })

    def spread_attack(self):

        count = 7 + level // 2

        spread = (
            1.1
            + level * 0.03
        )

        for i in range(count):

            angle = (
                self.angle
                - spread / 2
                + spread
                * i
                / max(
                    1,
                    count - 1
                )
            )

            speed = (
                3.5
                + level * 0.13
            )

            enemy_bullets.append({

                "x": self.x,
                "y": self.y,

                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,

                "life": 230,

                "damage": 9 + level // 2,

                "color": BLUE
            })

    def chaos_attack(self):

        count = 16 + level

        for i in range(count):

            angle = (
                i * math.tau / count
                + self.anim * 0.03
            )

            speed = (
                2.8
                + level * 0.12
            )

            enemy_bullets.append({

                "x": self.x,
                "y": self.y,

                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,

                "life": 250,

                "damage": 10 + level // 2,

                "color": GREEN
            })

        self.fire_attack()

    def draw(self, surface):

        x = int(self.x)
        y = int(self.y)

        pulse = math.sin(
            self.anim * 0.08
        )

        for ring in range(3):

            radius = int(
                48
                + ring * 9
                + pulse * 5
            )

            pygame.draw.circle(
                surface,
                self.color,
                (x, y),
                radius,
                2
            )

        points = []

        for i in range(8):

            angle = (
                self.angle
                + i * math.tau / 8
            )

            radius = (
                38
                if i % 2 == 0
                else 28
            )

            points.append((
                int(
                    x
                    + math.cos(angle)
                    * radius
                ),
                int(
                    y
                    + math.sin(angle)
                    * radius
                )
            ))

        pygame.draw.polygon(
            surface,
            DARK,
            points
        )

        pygame.draw.polygon(
            surface,
            self.color,
            points,
            4
        )

        pygame.draw.circle(
            surface,
            self.color,
            (x, y),
            18 + int(
                abs(pulse) * 4
            )
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (x, y),
            7
        )

        end_x = (
            x
            + int(
                math.cos(self.angle)
                * 32
            )
        )

        end_y = (
            y
            + int(
                math.sin(self.angle)
                * 32
            )
        )

        pygame.draw.line(
            surface,
            WHITE,
            (x, y),
            (end_x, end_y),
            4
        )


# ============================================================
# PLAYER BULLET
# ============================================================

class Bullet:

    def __init__(
        self,
        x,
        y,
        angle
    ):

        self.x = x
        self.y = y

        self.vx = (
            math.cos(angle)
            * BULLET_SPEED
        )

        self.vy = (
            math.sin(angle)
            * BULLET_SPEED
        )

        self.bounces = 0
        self.life = 180

    def update(self):

        self.x += self.vx
        self.y += self.vy

        bounced = False

        if (
            self.x <= 0
            or self.x >= WIDTH
        ):

            self.vx *= -1

            self.x = max(
                1,
                min(
                    WIDTH - 1,
                    self.x
                )
            )

            bounced = True

        if (
            self.y <= 0
            or self.y >= HEIGHT
        ):

            self.vy *= -1

            self.y = max(
                1,
                min(
                    HEIGHT - 1,
                    self.y
                )
            )

            bounced = True

        rect = pygame.Rect(
            int(self.x - 3),
            int(self.y - 3),
            6,
            6
        )

        for wall in obstacles:

            if rect.colliderect(wall):

                if abs(self.vx) > abs(self.vy):

                    self.vx *= -1

                else:

                    self.vy *= -1

                bounced = True
                break

        if bounced:

            self.bounces += 1

            spawn_particles(
                self.x,
                self.y,
                CYAN,
                3
            )

        self.life -= 1

    def draw(self, surface):

        pygame.draw.circle(
            surface,
            WHITE,
            (
                int(self.x),
                int(self.y)
            ),
            5
        )

        pygame.draw.circle(
            surface,
            CYAN,
            (
                int(self.x),
                int(self.y)
            ),
            3
        )


# ============================================================
# POWERUP
# ============================================================

class PowerUp:

    def __init__(
        self,
        x,
        y,
        kind
    ):

        self.x = x
        self.y = y
        self.kind = kind
        self.life = 600

        self.anim = (
            random.random()
            * math.tau
        )

    def update(self):

        self.life -= 1
        self.anim += 0.08

    def draw(self, surface):

        x = int(self.x)
        y = int(self.y)

        radius = (
            14
            + int(
                math.sin(self.anim)
                * 2
            )
        )

        if self.kind == "health":

            color = GREEN
            symbol = "+"

        elif self.kind == "rapid":

            color = YELLOW
            symbol = "R"

        elif self.kind == "damage":

            color = RED
            symbol = "D"

        elif self.kind == "shield":

            color = BLUE
            symbol = "S"

        else:

            color = PURPLE
            symbol = "3"

        pygame.draw.circle(
            surface,
            color,
            (x, y),
            radius,
            2
        )

        pygame.draw.circle(
            surface,
            color,
            (x, y),
            4
        )

        text = FONT_SMALL.render(
            symbol,
            True,
            color
        )

        surface.blit(
            text,
            text.get_rect(
                center=(x, y)
            )
        )


# ============================================================
# SPAWN ENEMY
# ============================================================

def spawn_enemy():

    global enemies_spawned

    if enemies_spawned >= enemies_to_spawn:
        return

    roll = random.random()

    if (
        level >= 7
        and roll < 0.15
    ):

        enemy_type = "tank"

    elif (
        level >= 3
        and roll < 0.40
    ):

        enemy_type = "flanker"

    else:

        enemy_type = "normal"

    enemies.append(
        Enemy(enemy_type)
    )

    enemies_spawned += 1


# ============================================================
# START LEVEL
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
    global laser_active_timer
    global laser_damage_timer

    obstacles = LEVEL_LAYOUTS[
        level - 1
    ]

    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    particles.clear()
    powerups.clear()

    boss = None
    boss_was_defeated = False

    enemies_spawned = 0

    enemies_to_spawn = (
        3 + level
    )

    spawn_sides = random.sample(
        [
            "top",
            "bottom",
            "left",
            "right"
        ],
        2
    )

    x, y = find_safe_spawn()

    player.center = (
        int(x),
        int(y)
    )

    laser_active_timer = 0
    laser_damage_timer = 0

    level_message_timer = 180
    boss_warning_timer = 0


# ============================================================
# PLAYER MOVEMENT
# ============================================================

def move_player():

    keys = pygame.key.get_pressed()

    dx = 0
    dy = 0

    if (
        keys[pygame.K_w]
        or keys[pygame.K_UP]
    ):
        dy -= 1

    if (
        keys[pygame.K_s]
        or keys[pygame.K_DOWN]
    ):
        dy += 1

    if (
        keys[pygame.K_a]
        or keys[pygame.K_LEFT]
    ):
        dx -= 1

    if (
        keys[pygame.K_d]
        or keys[pygame.K_RIGHT]
    ):
        dx += 1

    if dx == 0 and dy == 0:
        return

    length = math.hypot(
        dx,
        dy
    )

    dx /= length
    dy /= length

    new_rect = player.copy()

    new_rect.x += int(
        dx * PLAYER_SPEED
    )

    if (
        new_rect.left >= 0
        and new_rect.right <= WIDTH
        and not rect_hits_wall(
            new_rect
        )
    ):

        player.x = new_rect.x

    new_rect = player.copy()

    new_rect.y += int(
        dy * PLAYER_SPEED
    )

    if (
        new_rect.top >= 0
        and new_rect.bottom <= HEIGHT
        and not rect_hits_wall(
            new_rect
        )
    ):

        player.y = new_rect.y


# ============================================================
# SHOOT
# ============================================================

def shoot():

    global fire_timer

    if fire_timer > 0:
        return

    mx, my = pygame.mouse.get_pos()

    angle = math.atan2(
        my - player.centery,
        mx - player.centerx
    )

    if triple_timer > 0:

        angles = [
            angle - 0.16,
            angle,
            angle + 0.16
        ]

    else:

        angles = [angle]

    for shot_angle in angles:

        bullets.append(
            Bullet(
                player.centerx,
                player.centery,
                shot_angle
            )
        )

    spawn_particles(
        player.centerx
        + math.cos(angle) * 25,
        player.centery
        + math.sin(angle) * 25,
        CYAN,
        3
    )

    play_sound("shoot")

    if rapid_timer > 0:
        fire_timer = 4
    else:
        fire_timer = 10


# ============================================================
# LASER ACTIVATION
# ============================================================

def activate_neural_laser():

    global laser_active_timer
    global laser_damage_timer
    global laser_angle
    global screen_shake

    if laser_active_timer > 0:
        return

    mx, my = pygame.mouse.get_pos()

    laser_angle = math.atan2(
        my - player.centery,
        mx - player.centerx
    )

    laser_active_timer = (
        LASER_DURATION
    )

    laser_damage_timer = 0

    screen_shake = max(
        screen_shake,
        8
    )

    play_sound("laser")

    spawn_particles(
        player.centerx,
        player.centery,
        CYAN,
        30
    )


# ============================================================
# LASER DAMAGE
# ============================================================

def damage_laser_target():

    global score
    global boss
    global boss_was_defeated
    global screen_shake

    target = get_first_laser_target()

    if target is None:
        return

    target_type, target_object, _ = target

    # --------------------------------------------------------
    # FIRST ENEMY ONLY
    # --------------------------------------------------------

    if target_type == "enemy":

        enemy = target_object

        damage = LASER_ENEMY_DAMAGE

        if damage_timer > 0:
            damage *= 2

        enemy.health -= damage

        spawn_particles(
            enemy.x,
            enemy.y,
            CYAN,
            7
        )

        play_sound("hit")

        if enemy.health <= 0:

            score += enemy.points

            spawn_particles(
                enemy.x,
                enemy.y,
                enemy.color,
                20
            )

            play_sound("destroy")

            if random.random() < 0.18:

                powerups.append(
                    PowerUp(
                        enemy.x,
                        enemy.y,
                        random.choice([
                            "health",
                            "rapid",
                            "damage",
                            "shield",
                            "triple"
                        ])
                    )
                )

            if enemy in enemies:

                enemies.remove(
                    enemy
                )

    # --------------------------------------------------------
    # BOSS FIRST TARGET
    # --------------------------------------------------------

    elif target_type == "boss":

        target_boss = target_object

        damage = LASER_BOSS_DAMAGE

        if damage_timer > 0:
            damage *= 2

        target_boss.health -= damage

        spawn_particles(
            target_boss.x,
            target_boss.y,
            target_boss.color,
            10
        )

        screen_shake = max(
            screen_shake,
            5
        )

        play_sound("hit")

        if target_boss.health <= 0:

            score += (
                3000
                + level * 500
            )

            spawn_particles(
                target_boss.x,
                target_boss.y,
                target_boss.color,
                50
            )

            play_sound("destroy")

            boss = None
            boss_was_defeated = True


# ============================================================
# LASER UPDATE
# ============================================================

def update_laser():

    global laser_active_timer
    global laser_damage_timer
    global laser_angle
    global laser_pulse

    if laser_active_timer <= 0:
        return

    laser_active_timer -= 1

    laser_pulse += 0.25

    mx, my = pygame.mouse.get_pos()

    laser_angle = math.atan2(
        my - player.centery,
        mx - player.centerx
    )

    laser_damage_timer -= 1

    if laser_damage_timer <= 0:

        damage_laser_target()

        laser_damage_timer = (
            LASER_TICK_RATE
        )

        play_sound(
            "laser_pulse"
        )


# ============================================================
# LASER END POINT
# ============================================================

def get_laser_end():

    dx = math.cos(
        laser_angle
    )

    dy = math.sin(
        laser_angle
    )

    target = get_first_laser_target()

    if target is not None:

        _, _, distance = target

        # Stop directly at the target.
        return (
            int(
                player.centerx
                + dx * distance
            ),
            int(
                player.centery
                + dy * distance
            )
        )

    # No target: extend across screen.
    distance = 1400

    return (
        int(
            player.centerx
            + dx * distance
        ),
        int(
            player.centery
            + dy * distance
        )
    )


# ============================================================
# DRAW LASER
# ============================================================

def draw_laser(surface):

    if laser_active_timer <= 0:
        return

    x1 = player.centerx
    y1 = player.centery

    x2, y2 = get_laser_end()

    pulse = (
        math.sin(
            laser_pulse
        ) + 1
    ) / 2

    # Outer energy.
    pygame.draw.line(
        surface,
        (0, 60, 100),
        (x1, y1),
        (x2, y2),
        52
    )

    pygame.draw.line(
        surface,
        (0, 120, 180),
        (x1, y1),
        (x2, y2),
        34
    )

    pygame.draw.line(
        surface,
        BLUE,
        (x1, y1),
        (x2, y2),
        25
    )

    pygame.draw.line(
        surface,
        CYAN,
        (x1, y1),
        (x2, y2),
        15
    )

    pygame.draw.line(
        surface,
        WHITE,
        (x1, y1),
        (x2, y2),
        6
    )

    pygame.draw.line(
        surface,
        (230, 255, 255),
        (x1, y1),
        (x2, y2),
        2
    )

    # Moving energy particles.
    dx = math.cos(
        laser_angle
    )

    dy = math.sin(
        laser_angle
    )

    laser_length = math.hypot(
        x2 - x1,
        y2 - y1
    )

    for i in range(1, 12):

        distance = (
            i * 70
            + (
                pygame.time.get_ticks()
                % 70
            )
        )

        if distance >= laser_length:
            break

        px = int(
            x1
            + dx * distance
        )

        py = int(
            y1
            + dy * distance
        )

        size = (
            4
            + int(
                pulse * 3
            )
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (px, py),
            size
        )

        pygame.draw.circle(
            surface,
            CYAN,
            (px, py),
            size + 5,
            2
        )

    pygame.draw.circle(
        surface,
        CYAN,
        (x1, y1),
        26 + int(
            pulse * 5
        ),
        3
    )

    pygame.draw.circle(
        surface,
        WHITE,
        (x1, y1),
        11
    )

    pygame.draw.circle(
        surface,
        CYAN,
        (x1, y1),
        7
    )


# ============================================================
# PLAYER BULLETS
# ============================================================

def update_bullets():

    global score
    global boss
    global boss_was_defeated

    for bullet in bullets[:]:

        bullet.update()

        if (
            bullet.life <= 0
            or bullet.bounces > MAX_BOUNCES
        ):

            if bullet in bullets:
                bullets.remove(bullet)

            continue

        bullet_rect = pygame.Rect(
            int(bullet.x - 5),
            int(bullet.y - 5),
            10,
            10
        )

        hit_enemy = False

        for enemy in enemies[:]:

            enemy_rect = pygame.Rect(
                int(
                    enemy.x
                    - enemy.size / 2
                ),
                int(
                    enemy.y
                    - enemy.size / 2
                ),
                enemy.size,
                enemy.size
            )

            if bullet_rect.colliderect(
                enemy_rect
            ):

                damage = BULLET_DAMAGE

                if damage_timer > 0:
                    damage *= 2

                enemy.health -= damage

                spawn_particles(
                    enemy.x,
                    enemy.y,
                    enemy.color,
                    5
                )

                play_sound("hit")

                hit_enemy = True

                if enemy.health <= 0:

                    score += enemy.points

                    spawn_particles(
                        enemy.x,
                        enemy.y,
                        enemy.color,
                        20
                    )

                    play_sound("destroy")

                    if random.random() < 0.16:

                        powerups.append(
                            PowerUp(
                                enemy.x,
                                enemy.y,
                                random.choice([
                                    "health",
                                    "rapid",
                                    "damage",
                                    "shield",
                                    "triple"
                                ])
                            )
                        )

                    enemies.remove(
                        enemy
                    )

                break

        if hit_enemy:

            if bullet in bullets:
                bullets.remove(bullet)

            continue

        if boss is not None:

            boss_rect = pygame.Rect(
                int(
                    boss.x
                    - boss.size / 2
                ),
                int(
                    boss.y
                    - boss.size / 2
                ),
                boss.size,
                boss.size
            )

            if bullet_rect.colliderect(
                boss_rect
            ):

                damage = BULLET_DAMAGE

                if damage_timer > 0:
                    damage *= 2

                boss.health -= damage

                spawn_particles(
                    boss.x,
                    boss.y,
                    boss.color,
                    5
                )

                play_sound("hit")

                if bullet in bullets:
                    bullets.remove(bullet)

                if boss.health <= 0:

                    score += (
                        3000
                        + level * 500
                    )

                    spawn_particles(
                        boss.x,
                        boss.y,
                        boss.color,
                        50
                    )

                    play_sound("destroy")

                    boss = None
                    boss_was_defeated = True


# ============================================================
# ENEMIES
# ============================================================

def update_enemies():

    for enemy in enemies[:]:

        enemy.update()

        enemy_rect = pygame.Rect(
            int(
                enemy.x
                - enemy.size / 2
            ),
            int(
                enemy.y
                - enemy.size / 2
            ),
            enemy.size,
            enemy.size
        )

        if enemy_rect.colliderect(
            player
        ):

            damage_player(
                enemy.contact_damage
            )

            dx = (
                enemy.x
                - player.centerx
            )

            dy = (
                enemy.y
                - player.centery
            )

            distance = math.hypot(
                dx,
                dy
            )

            if distance > 0:

                enemy.x += (
                    dx / distance
                ) * 20

                enemy.y += (
                    dy / distance
                ) * 20


# ============================================================
# ENEMY BULLETS
# ============================================================

def update_enemy_bullets():

    for bullet in enemy_bullets[:]:

        bullet["x"] += bullet["vx"]
        bullet["y"] += bullet["vy"]

        bullet["life"] -= 1

        if (
            bullet["life"] <= 0
            or bullet["x"] < -30
            or bullet["x"] > WIDTH + 30
            or bullet["y"] < -30
            or bullet["y"] > HEIGHT + 30
        ):

            enemy_bullets.remove(
                bullet
            )

            continue

        rect = pygame.Rect(
            int(
                bullet["x"] - 5
            ),
            int(
                bullet["y"] - 5
            ),
            10,
            10
        )

        if rect.colliderect(
            player
        ):

            damage_player(
                bullet.get(
                    "damage",
                    8
                )
            )

            spawn_particles(
                bullet["x"],
                bullet["y"],
                bullet.get(
                    "color",
                    RED
                ),
                8
            )

            enemy_bullets.remove(
                bullet
            )


# ============================================================
# DAMAGE PLAYER
# ============================================================

def damage_player(amount):

    global player_health
    global screen_shake

    if shield_timer > 0:
        return

    player_health -= amount

    screen_shake = 8

    play_sound("damage")

    spawn_particles(
        player.centerx,
        player.centery,
        RED,
        10
    )

    if player_health <= 0:

        player_health = 0


# ============================================================
# POWERUPS
# ============================================================

def update_powerups():

    global player_health
    global rapid_timer
    global damage_timer
    global shield_timer
    global triple_timer

    for powerup in powerups[:]:

        powerup.update()

        if powerup.life <= 0:

            powerups.remove(
                powerup
            )

            continue

        distance = math.hypot(
            powerup.x
            - player.centerx,
            powerup.y
            - player.centery
        )

        if distance < 30:

            if powerup.kind == "health":

                player_health = min(
                    PLAYER_MAX_HEALTH,
                    player_health + 60
                )

            elif powerup.kind == "rapid":

                rapid_timer = 600

            elif powerup.kind == "damage":

                damage_timer = 600

            elif powerup.kind == "shield":

                shield_timer = 500

            elif powerup.kind == "triple":

                triple_timer = 500

            play_sound("powerup")

            spawn_particles(
                powerup.x,
                powerup.y,
                GREEN,
                15
            )

            powerups.remove(
                powerup
            )


# ============================================================
# PARTICLES
# ============================================================

def update_particles():

    for particle in particles[:]:

        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]

        particle["vx"] *= 0.96
        particle["vy"] *= 0.96

        particle["life"] -= 1

        if particle["life"] <= 0:

            particles.remove(
                particle
            )


def draw_particles(surface):

    for particle in particles:

        ratio = (
            particle["life"]
            / particle["max_life"]
        )

        size = max(
            1,
            int(
                particle["size"]
                * ratio
            )
        )

        pygame.draw.circle(
            surface,
            particle["color"],
            (
                int(
                    particle["x"]
                ),
                int(
                    particle["y"]
                )
            ),
            size
        )


# ============================================================
# BOSS SPAWN
# ============================================================

def spawn_boss():

    global boss
    global boss_warning_timer

    data = BOSS_DATA[
        level - 1
    ]

    boss = Boss(
        data[0],
        data[1],
        data[2],
        data[3],
        data[4]
    )

    boss_warning_timer = 180

    play_sound("boss")


# ============================================================
# GAME UPDATE
# ============================================================

def update_game():

    global fire_timer
    global rapid_timer
    global damage_timer
    global shield_timer
    global triple_timer

    global level_message_timer
    global boss_warning_timer

    global level
    global game_state

    move_player()

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

    if (
        enemies_spawned
        < enemies_to_spawn
        and len(enemies) < 4
    ):

        if random.random() < 0.075:

            spawn_enemy()

    update_enemies()
    update_enemy_bullets()
    update_bullets()
    update_powerups()
    update_particles()
    update_laser()

    if boss is not None:

        boss.update()

        boss_rect = pygame.Rect(
            int(
                boss.x
                - boss.size / 2
            ),
            int(
                boss.y
                - boss.size / 2
            ),
            boss.size,
            boss.size
        )

        if boss_rect.colliderect(
            player
        ):

            damage_player(
                BOSS_CONTACT_DAMAGE
            )

    if (
        enemies_spawned
        >= enemies_to_spawn
        and len(enemies) == 0
        and boss is None
        and not boss_was_defeated
    ):

        spawn_boss()

    if (
        boss_was_defeated
        and boss is None
    ):

        if level < MAX_LEVEL:

            level += 1

            start_level()

        else:

            game_state = VICTORY

            play_sound("victory")


# ============================================================
# PLAYER DRAW
# ============================================================

def draw_player(surface):

    global player_angle
    global player_pulse

    mx, my = pygame.mouse.get_pos()

    player_angle = math.atan2(
        my - player.centery,
        mx - player.centerx
    )

    player_pulse += 0.12

    x = player.centerx
    y = player.centery

    pulse = (
        math.sin(
            player_pulse
        ) + 1
    ) / 2

    pygame.draw.circle(
        surface,
        (0, 80, 100),
        (x, y),
        29 + int(
            pulse * 4
        ),
        2
    )

    pygame.draw.circle(
        surface,
        CYAN,
        (x, y),
        23,
        2
    )

    if shield_timer > 0:

        pygame.draw.circle(
            surface,
            BLUE,
            (x, y),
            31 + int(
                pulse * 3
            ),
            3
        )

    points = []

    for angle_offset, radius in [

        (0, 25),
        (2.3, 17),
        (math.pi, 20),
        (-2.3, 17)

    ]:

        angle = (
            player_angle
            + angle_offset
        )

        points.append((
            int(
                x
                + math.cos(angle)
                * radius
            ),
            int(
                y
                + math.sin(angle)
                * radius
            )
        ))

    pygame.draw.polygon(
        surface,
        DARK,
        points
    )

    pygame.draw.polygon(
        surface,
        CYAN,
        points,
        3
    )

    left_angle = (
        player_angle
        + math.pi / 2
    )

    right_angle = (
        player_angle
        - math.pi / 2
    )

    pygame.draw.line(
        surface,
        BLUE,
        (
            int(
                x
                + math.cos(left_angle)
                * 5
            ),
            int(
                y
                + math.sin(left_angle)
                * 5
            )
        ),
        (
            int(
                x
                + math.cos(left_angle)
                * 24
            ),
            int(
                y
                + math.sin(left_angle)
                * 24
            )
        ),
        5
    )

    pygame.draw.line(
        surface,
        BLUE,
        (
            int(
                x
                + math.cos(right_angle)
                * 5
            ),
            int(
                y
                + math.sin(right_angle)
                * 5
            )
        ),
        (
            int(
                x
                + math.cos(right_angle)
                * 24
            ),
            int(
                y
                + math.sin(right_angle)
                * 24
            )
        ),
        5
    )

    rear_angle = (
        player_angle
        + math.pi
    )

    for offset in [
        -0.35,
        0.35
    ]:

        angle = (
            rear_angle
            + offset
        )

        pygame.draw.line(
            surface,
            GREEN,
            (x, y),
            (
                int(
                    x
                    + math.cos(angle)
                    * 17
                ),
                int(
                    y
                    + math.sin(angle)
                    * 17
                )
            ),
            4
        )

    engine_x = int(
        x
        + math.cos(rear_angle)
        * 16
    )

    engine_y = int(
        y
        + math.sin(rear_angle)
        * 16
    )

    pygame.draw.circle(
        surface,
        ORANGE,
        (
            engine_x,
            engine_y
        ),
        5 + int(
            pulse * 2
        )
    )

    pygame.draw.circle(
        surface,
        GREEN,
        (x, y),
        10 + int(
            pulse * 2
        )
    )

    pygame.draw.circle(
        surface,
        WHITE,
        (x, y),
        4
    )


# ============================================================
# BACKGROUND
# ============================================================

def draw_background(surface):

    surface.fill(BLACK)

    for x in range(
        0,
        WIDTH,
        50
    ):

        pygame.draw.line(
            surface,
            GRID,
            (x, 0),
            (x, HEIGHT),
            1
        )

    for y in range(
        0,
        HEIGHT,
        50
    ):

        pygame.draw.line(
            surface,
            GRID,
            (0, y),
            (WIDTH, y),
            1
        )


# ============================================================
# WALLS
# ============================================================

def draw_walls(surface):

    for wall in obstacles:

        pygame.draw.rect(
            surface,
            (8, 20, 30),
            wall
        )

        pygame.draw.rect(
            surface,
            CYAN,
            wall,
            2
        )

        if wall.width > wall.height:

            pygame.draw.line(
                surface,
                (0, 90, 110),
                (
                    wall.left + 5,
                    wall.centery
                ),
                (
                    wall.right - 5,
                    wall.centery
                ),
                1
            )

        else:

            pygame.draw.line(
                surface,
                (0, 90, 110),
                (
                    wall.centerx,
                    wall.top + 5
                ),
                (
                    wall.centerx,
                    wall.bottom - 5
                ),
                1
            )


# ============================================================
# HUD
# ============================================================

def draw_hud(surface):

    pygame.draw.rect(
        surface,
        DARK,
        (
            20,
            20,
            250,
            25
        )
    )

    health_width = int(
        250
        * player_health
        / PLAYER_MAX_HEALTH
    )

    pygame.draw.rect(
        surface,
        GREEN if player_health > 60 else RED,
        (
            20,
            20,
            health_width,
            25
        )
    )

    pygame.draw.rect(
        surface,
        WHITE,
        (
            20,
            20,
            250,
            25
        ),
        2
    )

    health_text = FONT_SMALL.render(
        f"HP {player_health}/{PLAYER_MAX_HEALTH}",
        True,
        WHITE
    )

    surface.blit(
        health_text,
        (28, 23)
    )

    score_text = FONT.render(
        f"SCORE {score}",
        True,
        WHITE
    )

    surface.blit(
        score_text,
        (20, 60)
    )

    level_text = FONT.render(
        f"SECTOR {level}/{MAX_LEVEL}",
        True,
        CYAN
    )

    surface.blit(
        level_text,
        (20, 92)
    )

    hostile_text = FONT_SMALL.render(
        f"HOSTILES {len(enemies)}",
        True,
        RED
    )

    surface.blit(
        hostile_text,
        (20, 128)
    )

    y = 155

    if rapid_timer > 0:

        text = FONT_SMALL.render(
            f"RAPID {rapid_timer / FPS:.1f}s",
            True,
            YELLOW
        )

        surface.blit(
            text,
            (20, y)
        )

        y += 22

    if damage_timer > 0:

        text = FONT_SMALL.render(
            f"DAMAGE {damage_timer / FPS:.1f}s",
            True,
            RED
        )

        surface.blit(
            text,
            (20, y)
        )

        y += 22

    if shield_timer > 0:

        text = FONT_SMALL.render(
            f"SHIELD {shield_timer / FPS:.1f}s",
            True,
            BLUE
        )

        surface.blit(
            text,
            (20, y)
        )

        y += 22

    if triple_timer > 0:

        text = FONT_SMALL.render(
            f"TRIPLE {triple_timer / FPS:.1f}s",
            True,
            PURPLE
        )

        surface.blit(
            text,
            (20, y)
        )

    if laser_active_timer > 0:

        laser_text = FONT.render(
            f"NEURAL LASER {laser_active_timer / FPS:.1f}s",
            True,
            CYAN
        )

    else:

        laser_text = FONT_SMALL.render(
            "ENTER  NEURAL LASER [READY]",
            True,
            CYAN
        )

    surface.blit(
        laser_text,
        (
            WIDTH - 300,
            25
        )
    )

    if boss is not None:

        bar_width = 500

        bar_x = (
            WIDTH // 2
            - bar_width // 2
        )

        bar_y = HEIGHT - 40

        pygame.draw.rect(
            surface,
            DARK,
            (
                bar_x,
                bar_y,
                bar_width,
                22
            )
        )

        health_width = int(
            bar_width
            * max(
                0,
                boss.health
            )
            / boss.max_health
        )

        pygame.draw.rect(
            surface,
            boss.color,
            (
                bar_x,
                bar_y,
                health_width,
                22
            )
        )

        pygame.draw.rect(
            surface,
            WHITE,
            (
                bar_x,
                bar_y,
                bar_width,
                22
            ),
            2
        )

        boss_text = FONT_SMALL.render(
            f"{boss.name}  LV.{level} COMBAT",
            True,
            WHITE
        )

        surface.blit(
            boss_text,
            (
                bar_x,
                bar_y - 23
            )
        )


# ============================================================
# MENU
# ============================================================

def draw_button(
    surface,
    text,
    rect,
    active=False
):

    color = CYAN if active else BLUE

    pygame.draw.rect(
        surface,
        (8, 18, 30),
        rect
    )

    pygame.draw.rect(
        surface,
        color,
        rect,
        2
    )

    label = FONT_MEDIUM.render(
        text,
        True,
        WHITE
    )

    surface.blit(
        label,
        label.get_rect(
            center=rect.center
        )
    )


def draw_menu(surface):

    surface.fill(BLACK)

    title = FONT_HUGE.render(
        "NEURAL FRONTIER",
        True,
        CYAN
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                150
            )
        )
    )

    subtitle = FONT.render(
        "TACTICAL NEURAL COMBAT SYSTEM",
        True,
        GREEN
    )

    surface.blit(
        subtitle,
        subtitle.get_rect(
            center=(
                WIDTH // 2,
                215
            )
        )
    )

    draw_button(
        surface,
        "START MISSION",
        pygame.Rect(
            350,
            300,
            300,
            60
        ),
        True
    )

    draw_button(
        surface,
        "CONTROLS",
        pygame.Rect(
            350,
            380,
            300,
            60
        )
    )

    draw_button(
        surface,
        "QUIT",
        pygame.Rect(
            350,
            460,
            300,
            60
        )
    )

    info = FONT_SMALL.render(
        "WASD / ARROWS MOVE | MOUSE AIM | SPACE FIRE",
        True,
        WHITE
    )

    surface.blit(
        info,
        info.get_rect(
            center=(
                WIDTH // 2,
                570
            )
        )
    )

    laser_info = FONT_SMALL.render(
        "ENTER = NEURAL LASER • 5 SECOND ATTACK",
        True,
        CYAN
    )

    surface.blit(
        laser_info,
        laser_info.get_rect(
            center=(
                WIDTH // 2,
                600
            )
        )
    )


# ============================================================
# CONTROLS
# ============================================================

def draw_controls(surface):

    surface.fill(BLACK)

    title = FONT_BIG.render(
        "CONTROL SYSTEM",
        True,
        CYAN
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                80
            )
        )
    )

    controls = [

        ("W A S D", "MOVE"),
        ("ARROW KEYS", "MOVE"),
        ("MOUSE", "AIM"),
        ("SPACE", "FIRE"),
        ("ENTER", "NEURAL LASER - 5 SEC"),
        ("P", "PAUSE"),
        ("C", "CONTROLS"),
        ("ESC", "MENU"),
        ("R", "RESTART"),

    ]

    y = 150

    for key, action in controls:

        key_text = FONT_MEDIUM.render(
            key,
            True,
            CYAN
        )

        action_text = FONT.render(
            action,
            True,
            WHITE
        )

        surface.blit(
            key_text,
            (220, y)
        )

        surface.blit(
            action_text,
            (500, y)
        )

        y += 48

    back = FONT.render(
        "Press C or ESC to return",
        True,
        GREEN
    )

    surface.blit(
        back,
        back.get_rect(
            center=(
                WIDTH // 2,
                640
            )
        )
    )


# ============================================================
# PAUSE
# ============================================================

def draw_pause(surface):

    overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (
            0,
            0,
            0,
            190
        )
    )

    surface.blit(
        overlay,
        (0, 0)
    )

    title = FONT_HUGE.render(
        "PAUSED",
        True,
        CYAN
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                250
            )
        )
    )

    info = FONT.render(
        "Press P to continue",
        True,
        WHITE
    )

    surface.blit(
        info,
        info.get_rect(
            center=(
                WIDTH // 2,
                340
            )
        )
    )


# ============================================================
# GAME OVER
# ============================================================

def draw_game_over(surface):

    surface.fill(BLACK)

    title = FONT_HUGE.render(
        "SYSTEM FAILURE",
        True,
        RED
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                220
            )
        )
    )

    score_text = FONT_BIG.render(
        f"FINAL SCORE {score}",
        True,
        WHITE
    )

    surface.blit(
        score_text,
        score_text.get_rect(
            center=(
                WIDTH // 2,
                320
            )
        )
    )

    level_text = FONT.render(
        f"REACHED SECTOR {level}",
        True,
        CYAN
    )

    surface.blit(
        level_text,
        level_text.get_rect(
            center=(
                WIDTH // 2,
                370
            )
        )
    )

    info = FONT.render(
        "Press R to restart",
        True,
        GREEN
    )

    surface.blit(
        info,
        info.get_rect(
            center=(
                WIDTH // 2,
                460
            )
        )
    )

    info2 = FONT_SMALL.render(
        "Press ESC for menu",
        True,
        WHITE
    )

    surface.blit(
        info2,
        info2.get_rect(
            center=(
                WIDTH // 2,
                510
            )
        )
    )


# ============================================================
# VICTORY
# ============================================================

def draw_victory(surface):

    surface.fill(BLACK)

    title = FONT_HUGE.render(
        "NEURAL FRONTIER",
        True,
        GREEN
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                180
            )
        )
    )

    completed = FONT_BIG.render(
        "MISSION COMPLETE",
        True,
        CYAN
    )

    surface.blit(
        completed,
        completed.get_rect(
            center=(
                WIDTH // 2,
                280
            )
        )
    )

    score_text = FONT_BIG.render(
        f"FINAL SCORE {score}",
        True,
        WHITE
    )

    surface.blit(
        score_text,
        score_text.get_rect(
            center=(
                WIDTH // 2,
                360
            )
        )
    )

    info = FONT.render(
        "ALL 10 SECTORS CLEARED",
        True,
        GREEN
    )

    surface.blit(
        info,
        info.get_rect(
            center=(
                WIDTH // 2,
                430
            )
        )
    )

    restart = FONT.render(
        "Press R to play again",
        True,
        WHITE
    )

    surface.blit(
        restart,
        restart.get_rect(
            center=(
                WIDTH // 2,
                510
            )
        )
    )


# ============================================================
# DRAW GAME
# ============================================================

def draw_game(surface):

    draw_background(surface)

    draw_walls(surface)

    for powerup in powerups:
        powerup.draw(surface)

    for bullet in bullets:
        bullet.draw(surface)

    for enemy in enemies:
        enemy.draw(surface)

    for bullet in enemy_bullets:

        pygame.draw.circle(
            surface,
            bullet.get(
                "color",
                RED
            ),
            (
                int(
                    bullet["x"]
                ),
                int(
                    bullet["y"]
                )
            ),
            5
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (
                int(
                    bullet["x"]
                ),
                int(
                    bullet["y"]
                )
            ),
            2
        )

    if boss is not None:

        boss.draw(surface)

    # Laser is drawn AFTER walls,
    # so it visually penetrates walls.
    # But its endpoint is the FIRST enemy/boss.
    draw_laser(surface)

    draw_particles(surface)

    draw_player(surface)

    draw_hud(surface)

    if level_message_timer > 0:

        alpha = min(
            255,
            level_message_timer * 2
        )

        text = FONT_BIG.render(
            f"SECTOR {level} DEPLOYED",
            True,
            CYAN
        )

        text.set_alpha(alpha)

        surface.blit(
            text,
            text.get_rect(
                center=(
                    WIDTH // 2,
                    100
                )
            )
        )

    if boss_warning_timer > 0:

        if (
            boss_warning_timer // 10
        ) % 2 == 0:

            warning = FONT_BIG.render(
                "WARNING // BOSS DETECTED",
                True,
                RED
            )

            surface.blit(
                warning,
                warning.get_rect(
                    center=(
                        WIDTH // 2,
                        HEIGHT // 2
                    )
                )
            )


# ============================================================
# RESET
# ============================================================

def reset_game():

    global level
    global score
    global player_health
    global game_state

    level = 1
    score = 0

    player_health = PLAYER_MAX_HEALTH

    game_state = PLAYING

    start_level()


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    clock.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if (
                event.key == pygame.K_RETURN
                and game_state == PLAYING
            ):

                activate_neural_laser()

            elif (
                event.key == pygame.K_SPACE
                and game_state == PLAYING
            ):

                shoot()

            elif event.key == pygame.K_p:

                if game_state == PLAYING:

                    game_state = PAUSED

                elif game_state == PAUSED:

                    game_state = PLAYING

            elif event.key == pygame.K_c:

                if game_state == PLAYING:

                    game_state = CONTROLS

                elif game_state == CONTROLS:

                    game_state = PLAYING

            elif event.key == pygame.K_ESCAPE:

                if game_state in [
                    PLAYING,
                    PAUSED,
                    CONTROLS
                ]:

                    game_state = MENU

            elif event.key == pygame.K_r:

                if game_state in [
                    GAME_OVER,
                    VICTORY
                ]:

                    reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if (
                event.button == 1
                and game_state == MENU
            ):

                mouse = pygame.mouse.get_pos()

                start_rect = pygame.Rect(
                    350,
                    300,
                    300,
                    60
                )

                controls_rect = pygame.Rect(
                    350,
                    380,
                    300,
                    60
                )

                quit_rect = pygame.Rect(
                    350,
                    460,
                    300,
                    60
                )

                if start_rect.collidepoint(
                    mouse
                ):

                    reset_game()

                elif controls_rect.collidepoint(
                    mouse
                ):

                    game_state = CONTROLS

                elif quit_rect.collidepoint(
                    mouse
                ):

                    running = False

    if game_state == PLAYING:

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:

            shoot()

    if game_state == PLAYING:

        update_game()

        if player_health <= 0:

            game_state = GAME_OVER

    if game_state == MENU:

        draw_menu(screen)

    elif game_state == CONTROLS:

        draw_controls(screen)

    elif game_state == PLAYING:

        draw_game(screen)

    elif game_state == PAUSED:

        draw_game(screen)
        draw_pause(screen)

    elif game_state == GAME_OVER:

        draw_game_over(screen)

    elif game_state == VICTORY:

        draw_victory(screen)

    pygame.display.flip()


pygame.quit()

for filename in audio_temp_files:

    try:
        os.remove(filename)
    except OSError:
        pass