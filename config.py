import pygame

pygame.init()

# Screen (Fullscreen)
FULLSCREEN = True
SCREEN_WIDTH = pygame.display.Info().current_w if FULLSCREEN else 900
SCREEN_HEIGHT = pygame.display.Info().current_h if FULLSCREEN else 600

# World (balanced for fullscreen)
WORLD_WIDTH = 2400
WORLD_HEIGHT = 1600
GRID_SIZE = 50

# Game
FPS = 60

# Colors
BG_COLOR = (20, 25, 30)
BORDER_COLOR = (50, 50, 60)
GRID_COLOR = (30, 35, 40)

# Player (nerfed starting stats)
PLAYER_RADIUS = 20
PLAYER_BASE_HP = {
    'easy': 60,
    'normal': 50,
    'hard': 35
}
PLAYER_ACCELERATION = 0.3  # Slower movement
PLAYER_FRICTION = 0.85  # Less responsive
PLAYER_TURN_SPEED = 0.08  # Slower turning
PLAYER_BULLET_SPEED = 12  # Slower bullets
PLAYER_BULLET_DAMAGE = 7  # Weaker damage
PLAYER_SHOOT_DELAY = 0.25  # Slower fire rate

# Enemy
ENEMY_MIN_RADIUS = 10
ENEMY_MAX_RADIUS = 15
ENEMY_HP = 30
ENEMY_FOLLOW_SPEED = 0.3
ENEMY_STOP_DISTANCE = 100
ENEMY_BULLET_SPEED_MIN = 10
ENEMY_BULLET_SPEED_MAX = 20
ENEMY_BULLET_DAMAGE = 5
ENEMY_SHOOT_DELAY = 2.0
ENEMY_SHOOT_RANGE = 300

# Mana
MANA_RADIUS = 6
MANA_COLLECTION_RADIUS = 150
MANA_COLLECT_SPEED = 200
MANA_DROP_AMOUNT_MIN = 3
MANA_DROP_AMOUNT_MAX = 8

# Upgrades (base costs, increase by 5 per level)
UPGRADE_DAMAGE_BASE_COST = 10
UPGRADE_DAMAGE_COST_INCREASE = 5
UPGRADE_DAMAGE_INCREASE = 5

UPGRADE_SPEED_BASE_COST = 10
UPGRADE_SPEED_COST_INCREASE = 5
UPGRADE_SPEED_INCREASE = 50

UPGRADE_HP_BASE_COST = 15
UPGRADE_HP_COST_INCREASE = 7
UPGRADE_HP_INCREASE = 20
UPGRADE_HP_HEAL = 30

# Player Abilities
ABILITY_DASH_COST = 15
ABILITY_DASH_DISTANCE = 200
ABILITY_DASH_COOLDOWN = 3.0

ABILITY_SHIELD_COST = 25
ABILITY_SHIELD_DURATION = 5.0
ABILITY_SHIELD_COOLDOWN = 15.0

ABILITY_BURST_COST = 20
ABILITY_BURST_DAMAGE = 15
ABILITY_BURST_RADIUS = 150
ABILITY_BURST_COOLDOWN = 8.0

# Difficulty Settings
DIFFICULTY_SETTINGS = {
    'easy': {
        'enemy_speed_multiplier': 0.8,
        'enemy_hp_multiplier': 0.9,
        'enemy_damage_multiplier': 0.8,
        'spawn_rate_multiplier': 0.9,
        'waves_to_win': 10
    },
    'normal': {
        'enemy_speed_multiplier': 1.1,
        'enemy_hp_multiplier': 1.2,
        'enemy_damage_multiplier': 1.2,
        'spawn_rate_multiplier': 1.1,
        'waves_to_win': 15
    },
    'hard': {
        'enemy_speed_multiplier': 1.4,
        'enemy_hp_multiplier': 1.6,
        'enemy_damage_multiplier': 1.7,
        'spawn_rate_multiplier': 1.4,
        'waves_to_win': 20
    }
}

# Enemy Types Configuration
ENEMY_TYPES = {
    'shooter': {
        'color': (255, 80, 80),
        'min_radius': 10,
        'max_radius': 15,
        'hp': 30,
        'follow_speed': 0.3,
        'stop_distance': 100,
        'shoot_delay': 2.0,
        'shoot_range': 300,
        'bullet_damage': 5,
        'bullet_speed_min': 10,
        'bullet_speed_max': 20,
        'shape': 'circle'
    },
    'exploder': {
        'color': (255, 150, 50),
        'min_radius': 12,
        'max_radius': 18,
        'hp': 25,
        'follow_speed': 0.5,
        'stop_distance': 0,
        'explosion_radius': 80,
        'explosion_damage': 20,
        'shape': 'circle'
    },
    'bouncer': {
        'color': (150, 255, 150),
        'min_radius': 10,
        'max_radius': 16,
        'hp': 35,
        'speed_min': 4.5,
        'speed_max': 7.0,
        'bounce_damage': 25,
        'shape': 'triangle'
    },
    'tank': {
        'color': (150, 150, 200),
        'min_radius': 18,
        'max_radius': 25,
        'hp': 60,
        'follow_speed': 0.15,
        'stop_distance': 150,
        'shoot_delay': 3.0,
        'shoot_range': 250,
        'bullet_damage': 8,
        'bullet_speed_min': 8,
        'bullet_speed_max': 15,
        'shape': 'square'
    }
}

# Wave System (more enemies, longer game)
WAVE_BASE_ENEMIES = 5
WAVE_ENEMY_INCREMENT = 3
