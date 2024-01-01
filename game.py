import pygame
from config import Config

class Game:
    window = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
    clock = pygame.time.Clock()
    running = True
    paused = False
    status = 'start_menu'

    player = None
    enemies = []
    enemy_squares = []
    manas = []
    bullets = []
    particles = []
    shop = None

    @classmethod
    def initialize(cls):
        # Import classes here to avoid circular dependency
        from player import Player
        from enemy import Enemy, EnemySquare
        from mana import Mana
        from bullet import Bullet
        from particle import Particle
        from shop import Shop
        import pygame_gui

        cls.player = Player()
        cls.ui_manager = pygame_gui.UIManager((Config.WIDTH, Config.HEIGHT), 'theme.json')
        cls.shop = Shop(cls.ui_manager, cls.player)

    @classmethod
    def update_game_elements(cls):
        # Update each game element
        cls.player.update()
        for enemy in cls.enemies:
            enemy.update()
        for enemy_square in cls.enemy_squares:
            enemy_square.update()
        for mana in cls.manas:
            mana.update()
        for bullet in cls.bullets:
            bullet.update()
        for particle in cls.particles:
            particle.update()

    @classmethod
    def handle_events(cls, event):
        if cls.paused:
            cls.shop.manager.process_events(event)
            cls.shop.handle_events(event)
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cls.player.shoot()

    @classmethod
    def draw_ui(cls):
        if cls.paused:
            cls.shop.manager.update(cls.clock.get_time() / 1000.0)
            cls.shop.manager.draw_ui(cls.window)

# Call initialize at the end of the file to set up the game elements
Game.initialize()
