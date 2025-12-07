"""
Main game class integrating all systems.
Manages game states, menus, gameplay, and win/lose conditions.
"""

import pygame
import random
import math
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, FPS,
                    BG_COLOR, BORDER_COLOR, GRID_COLOR, GRID_SIZE,
                    MANA_DROP_AMOUNT_MIN, MANA_DROP_AMOUNT_MAX, FULLSCREEN,
                    ABILITY_DASH_COST, ABILITY_DASH_COOLDOWN,
                    ABILITY_SHIELD_COST, ABILITY_SHIELD_COOLDOWN,
                    ABILITY_BURST_COST, ABILITY_BURST_COOLDOWN)
from camera import Camera
from player import Player
from mana import ManaDrop
from enemy_types import create_enemy
from wave_manager import WaveManager
from menu import MainMenu, SettingsMenu, DifficultyMenu, PauseMenu, VictoryScreen, GameOverScreen
from particles import create_death_particles


class GameState:
    """Game state enum"""
    MAIN_MENU = 'main_menu'
    SETTINGS = 'settings'
    DIFFICULTY = 'difficulty'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'
    VICTORY = 'victory'


class Game:
    """Main game class"""

    def __init__(self):
        if FULLSCREEN:
            self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('PVE Arena')
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = GameState.MAIN_MENU
        self.difficulty = 'normal'

        # Initialize fonts
        self._init_fonts()

        # Initialize menus
        self.main_menu = MainMenu()
        self.settings_menu = SettingsMenu()
        self.difficulty_menu = DifficultyMenu()
        self.pause_menu = None
        self.victory_screen = None
        self.game_over_screen = None

        # Game components (initialized when game starts)
        self.camera = None
        self.player = None
        self.wave_manager = None
        self.all_sprites = None
        self.enemies = None
        self.player_bullets = None
        self.enemy_bullets = None
        self.mana_drops = None
        self.particles = None

        # Wave transition (10 second timer before next wave)
        self.wave_transition = False
        self.wave_timer = 0
        self.wave_timer_duration = 10.0  # 10 seconds between waves

        # Game surface for pause overlay
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def _init_fonts(self):
        """Initialize fonts"""
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)

    def start_new_game(self):
        """Initialize a new game session"""
        self.state = GameState.PLAYING

        # Initialize sprite groups
        self.camera = Camera()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.mana_drops = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        # Create player with difficulty-based HP
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, self.difficulty)
        self.all_sprites.add(self.player)

        # Initialize wave manager
        self.wave_manager = WaveManager(self.difficulty)

        # Start with wave transition
        self.wave_transition = True
        self.wave_timer = self.wave_timer_duration

    def _start_next_wave(self):
        """Start the next wave"""
        wave_info = self.wave_manager.start_wave()
        spawn_list = self.wave_manager.get_enemy_spawn_list()

        # Spawn enemies
        for enemy_type in spawn_list:
            self._spawn_enemy(enemy_type)

        print(f"Wave {wave_info['wave_number']}/{wave_info['total_waves']} - " +
              f"Enemies: {wave_info['enemies_count']}")

    def _spawn_enemy(self, enemy_type):
        """Spawn a single enemy"""
        x, y = self.wave_manager.get_spawn_position(self.player.pos)
        multipliers = self.wave_manager.get_difficulty_multipliers()

        enemy = create_enemy(enemy_type, x, y, multipliers)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self):
        """Handle events based on game state"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # State-specific event handling
            if self.state == GameState.MAIN_MENU:
                self._handle_main_menu_event(event)
            elif self.state == GameState.SETTINGS:
                self._handle_settings_event(event)
            elif self.state == GameState.DIFFICULTY:
                self._handle_difficulty_event(event)
            elif self.state == GameState.PLAYING:
                self._handle_playing_event(event)
            elif self.state == GameState.PAUSED:
                self._handle_pause_event(event)
            elif self.state == GameState.VICTORY:
                self._handle_victory_event(event)
            elif self.state == GameState.GAME_OVER:
                self._handle_game_over_event(event)

    def _handle_main_menu_event(self, event):
        """Handle main menu events"""
        action = self.main_menu.handle_event(event)
        if action == 'start':
            self.difficulty_menu = DifficultyMenu()
            self.state = GameState.DIFFICULTY
        elif action == 'settings':
            self.state = GameState.SETTINGS
        elif action == 'quit':
            self.running = False

    def _handle_settings_event(self, event):
        """Handle settings menu events"""
        action = self.settings_menu.handle_event(event)
        if action == 'back':
            self.state = GameState.MAIN_MENU
        # Settings are applied immediately when toggled

    def _handle_difficulty_event(self, event):
        """Handle difficulty selection events"""
        action = self.difficulty_menu.handle_event(event)
        if action in ['easy', 'normal', 'hard']:
            self.difficulty = action
            self.start_new_game()
        elif action == 'back':
            self.state = GameState.MAIN_MENU

    def _handle_playing_event(self, event):
        """Handle playing state events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.pause_menu = PauseMenu()
                self.state = GameState.PAUSED
            # Upgrades
            elif event.key == pygame.K_1:
                if self.player.upgrade_damage():
                    print(f"Damage upgraded to level {self.player.damage_level}!")
            elif event.key == pygame.K_2:
                if self.player.upgrade_speed():
                    print(f"Bullet speed upgraded to level {self.player.speed_level}!")
            elif event.key == pygame.K_3:
                if self.player.upgrade_hp():
                    print(f"HP upgraded to level {self.player.hp_level}!")
            # Abilities
            elif event.key == pygame.K_q:
                self.player.use_dash()
            elif event.key == pygame.K_e:
                self.player.use_shield()
            elif event.key == pygame.K_r:
                burst = self.player.use_burst()
                if burst:
                    self._handle_burst(burst)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                bullet = self.player.shoot()
                if bullet:
                    self.player_bullets.add(bullet)
                    self.all_sprites.add(bullet)

    def _handle_pause_event(self, event):
        """Handle pause menu events"""
        action = self.pause_menu.handle_event(event)
        if action == 'resume':
            self.state = GameState.PLAYING
        elif action == 'restart':
            self.start_new_game()
        elif action == 'menu':
            self.state = GameState.MAIN_MENU
            self.main_menu = MainMenu()

    def _handle_victory_event(self, event):
        """Handle victory screen events"""
        action = self.victory_screen.handle_event(event)
        if action == 'restart':
            self.start_new_game()
        elif action == 'menu':
            self.state = GameState.MAIN_MENU
            self.main_menu = MainMenu()

    def _handle_game_over_event(self, event):
        """Handle game over screen events"""
        action = self.game_over_screen.handle_event(event)
        if action == 'restart':
            self.start_new_game()
        elif action == 'menu':
            self.state = GameState.MAIN_MENU
            self.main_menu = MainMenu()

    def _update(self, dt):
        """Update game based on state"""
        if self.state == GameState.PLAYING:
            self._update_gameplay(dt)

    def _update_gameplay(self, dt):
        """Update gameplay logic"""
        # Handle wave transition timer
        if self.wave_transition:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self._start_next_wave()
                self.wave_transition = False
            # Don't update entities during transition - game is paused
            return

        # Update game only when not in transition
        self._update_entities(dt)
        self._handle_collisions()
        self._check_wave_completion()

        self.camera.follow(self.player)
        self._check_game_state()

    def _update_entities(self, dt):
        """Update all entities"""
        self.player.update(dt, self.camera)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player.pos)

            # Enemy shooting
            if hasattr(enemy, 'shoot'):
                bullet = enemy.shoot(self.player.pos)
                if bullet:
                    self.enemy_bullets.add(bullet)
                    self.all_sprites.add(bullet)

        # Update bullets, mana, and particles
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)
        for mana in self.mana_drops:
            mana.update(dt, self.player.pos)
        self.particles.update(dt)

    def _handle_collisions(self):
        """Handle all collisions"""
        self._handle_bullet_enemy_collision()
        self._handle_bullet_player_collision()
        self._handle_enemy_player_collision()
        self._handle_mana_collection()

    def _handle_bullet_enemy_collision(self):
        """Handle bullets hitting enemies"""
        for bullet in self.player_bullets:
            hit_enemies = pygame.sprite.spritecollide(
                bullet, self.enemies, False, pygame.sprite.collide_circle
            )
            if hit_enemies:
                bullet.kill()
                for enemy in hit_enemies:
                    if enemy.take_damage(bullet.damage):
                        # Create death particles
                        particles = create_death_particles(enemy.pos.x, enemy.pos.y, enemy.color)
                        self.particles.add(particles)

                        self._spawn_mana(enemy.pos.x, enemy.pos.y)
                        enemy.kill()
                        self.wave_manager.enemy_killed()

    def _handle_bullet_player_collision(self):
        """Handle enemy bullets hitting player"""
        for bullet in self.enemy_bullets:
            distance = bullet.pos.distance_to(self.player.pos)
            if distance < bullet.radius + self.player.radius:
                self.player.take_damage(bullet.damage)
                bullet.kill()

    def _handle_enemy_player_collision(self):
        """Handle enemies colliding with player"""
        for enemy in self.enemies:
            distance = enemy.pos.distance_to(self.player.pos)
            if distance < enemy.radius + self.player.radius:
                # Handle exploder
                if hasattr(enemy, 'explode') and not enemy.is_exploding:
                    enemy.explode()
                    # Check if player is in explosion radius
                    if distance < enemy.explosion_radius:
                        self.player.take_damage(enemy.explosion_damage)

                # Handle bouncer
                elif hasattr(enemy, 'bounce_damage'):
                    if enemy.last_bounce_time >= enemy.bounce_cooldown:
                        self.player.take_damage(enemy.bounce_damage)
                        enemy.last_bounce_time = 0

    def _handle_burst(self, burst_data):
        """Handle player burst ability damage"""
        burst_pos = burst_data['pos']
        burst_radius = burst_data['radius']
        burst_damage = burst_data['damage']

        # Create visual effect
        from particles import create_death_particles
        for _ in range(30):
            particles = create_death_particles(burst_pos.x, burst_pos.y, (255, 200, 100), count=5)
            self.particles.add(particles)

        # Damage enemies in radius
        for enemy in self.enemies:
            distance = enemy.pos.distance_to(burst_pos)
            if distance < burst_radius:
                if enemy.take_damage(burst_damage):
                    particles = create_death_particles(enemy.pos.x, enemy.pos.y, enemy.color)
                    self.particles.add(particles)
                    self._spawn_mana(enemy.pos.x, enemy.pos.y)
                    enemy.kill()
                    self.wave_manager.enemy_killed()

    def _handle_mana_collection(self):
        """Handle player collecting mana"""
        for mana in self.mana_drops:
            distance = mana.pos.distance_to(self.player.pos)
            if distance < 20:
                self.player.collect_mana(mana.amount)
                mana.kill()

    def _spawn_mana(self, x, y):
        """Spawn mana at position"""
        amount = random.randint(MANA_DROP_AMOUNT_MIN, MANA_DROP_AMOUNT_MAX)
        mana = ManaDrop(x, y, amount=amount)
        self.mana_drops.add(mana)
        self.all_sprites.add(mana)

    def _check_wave_completion(self):
        """Check if wave is complete and start next"""
        if self.wave_manager.is_wave_complete() and len(self.enemies) == 0:
            if self.wave_manager.is_game_won():
                self.victory_screen = VictoryScreen(
                    self.difficulty, self.wave_manager.current_wave
                )
                self.state = GameState.VICTORY
            else:
                # Start wave transition (10 second wait before next wave)
                self.wave_transition = True
                self.wave_timer = self.wave_timer_duration

    def _check_game_state(self):
        """Check for game over condition"""
        if self.player.hp <= 0:
            self.game_over_screen = GameOverScreen(self.wave_manager.current_wave)
            self.state = GameState.GAME_OVER

    def _draw(self):
        """Draw based on game state"""
        if self.state == GameState.MAIN_MENU:
            self.main_menu.draw(self.window)
        elif self.state == GameState.SETTINGS:
            self.settings_menu.draw(self.window)
        elif self.state == GameState.DIFFICULTY:
            self.difficulty_menu.draw(self.window)
        elif self.state == GameState.PLAYING:
            self._draw_gameplay()
        elif self.state == GameState.PAUSED:
            self.pause_menu.draw(self.window, self.game_surface)
        elif self.state == GameState.VICTORY:
            self.victory_screen.draw(self.window)
        elif self.state == GameState.GAME_OVER:
            self.game_over_screen.draw(self.window)

        pygame.display.flip()

    def _draw_gameplay(self):
        """Draw gameplay elements"""
        self.game_surface.fill(BG_COLOR)
        if self.settings_menu.show_grid:
            self._draw_grid()
        self._draw_world_border()
        self._draw_sprites()
        self._draw_ui()
        self.window.blit(self.game_surface, (0, 0))

    def _draw_grid(self):
        """Draw world grid"""
        start_x = max(0, int(self.camera.x // GRID_SIZE) * GRID_SIZE)
        start_y = max(0, int(self.camera.y // GRID_SIZE) * GRID_SIZE)
        end_x = min(WORLD_WIDTH, int((self.camera.x + SCREEN_WIDTH) // GRID_SIZE + 1) * GRID_SIZE)
        end_y = min(WORLD_HEIGHT, int((self.camera.y + SCREEN_HEIGHT) // GRID_SIZE + 1) * GRID_SIZE)

        for x in range(start_x, end_x + GRID_SIZE, GRID_SIZE):
            screen_x = x - self.camera.x
            pygame.draw.line(self.game_surface, GRID_COLOR, (screen_x, 0), (screen_x, SCREEN_HEIGHT))

        for y in range(start_y, end_y + GRID_SIZE, GRID_SIZE):
            screen_y = y - self.camera.y
            pygame.draw.line(self.game_surface, GRID_COLOR, (0, screen_y), (SCREEN_WIDTH, screen_y))

    def _draw_world_border(self):
        """Draw world boundary"""
        rect = self.camera.apply(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))
        pygame.draw.rect(self.game_surface, BORDER_COLOR, rect, 3)

    def _draw_sprites(self):
        """Draw all sprites"""
        for sprite in self.all_sprites:
            # Pass health bar setting to enemies
            if hasattr(sprite, 'enemy_type'):
                sprite.draw(self.game_surface, self.camera, self.settings_menu.show_health_bars)
            else:
                sprite.draw(self.game_surface, self.camera)

        # Draw particles on top
        for particle in self.particles:
            particle.draw(self.game_surface, self.camera)

    def _draw_ui(self):
        """Draw UI elements"""
        self._draw_hp_bar()
        self._draw_mana_counter()

        # Draw wave transition or wave info
        if self.wave_transition:
            self._draw_wave_transition()
        else:
            self._draw_wave_info()

        self._draw_upgrades()
        self._draw_controls()

    def _draw_hp_bar(self):
        """Draw health bar"""
        bar_width, bar_height = 200, 25
        bar_x, bar_y = 20, 20

        pygame.draw.rect(self.game_surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        hp_ratio = max(0, self.player.hp / self.player.max_hp)
        current_width = int(hp_ratio * bar_width)
        pygame.draw.rect(self.game_surface, (100, 200, 255), (bar_x, bar_y, current_width, bar_height))

        pygame.draw.rect(self.game_surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        hp_text = self.small_font.render(
            f'HP: {int(self.player.hp)}/{int(self.player.max_hp)}',
            True, (255, 255, 255)
        )
        self.game_surface.blit(hp_text, (bar_x + 5, bar_y + 3))

    def _draw_mana_counter(self):
        """Draw mana counter"""
        mana_text = self.font.render(f'Mana: {int(self.player.mana)}', True, (150, 230, 255))
        self.game_surface.blit(mana_text, (20, 60))

    def _draw_wave_info(self):
        """Draw wave information"""
        wave_text = self.font.render(
            f'Wave: {self.wave_manager.current_wave}/{self.wave_manager.waves_to_win}',
            True, (255, 200, 100)
        )
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.game_surface.blit(wave_text, wave_rect)

        # Enemies remaining
        enemies_text = self.small_font.render(
            f'Enemies: {len(self.enemies)}',
            True, (200, 200, 200)
        )
        enemies_rect = enemies_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.game_surface.blit(enemies_text, enemies_rect)

    def _draw_wave_transition(self):
        """Draw wave transition timer"""
        # Semi-transparent panel
        panel_width = 350
        panel_height = 120
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = 50

        # Background panel
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 30, 40, 200), (0, 0, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(panel, (100, 200, 255, 100), (0, 0, panel_width, panel_height), 3, border_radius=15)
        self.game_surface.blit(panel, (panel_x, panel_y))

        # Wave text
        wave_text = self.font.render('Next Wave In...', True, (150, 200, 255))
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 30))
        self.game_surface.blit(wave_text, wave_rect)

        # Timer with pulsing effect
        seconds = math.ceil(self.wave_timer)
        pulse = abs(math.sin(self.wave_timer * 4)) * 10
        timer_size = 48 + int(pulse)
        timer_font = pygame.font.Font(None, timer_size)
        timer_text = timer_font.render(str(seconds), True, (255, 200, 100))
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 70))
        self.game_surface.blit(timer_text, timer_rect)

        # Progress bar
        bar_width = 280
        bar_height = 8
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = panel_y + panel_height - 20

        # Background
        pygame.draw.rect(self.game_surface, (40, 50, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

        # Progress
        progress = 1 - (self.wave_timer / self.wave_timer_duration)
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            pygame.draw.rect(self.game_surface, (100, 200, 255), (bar_x, bar_y, progress_width, bar_height), border_radius=4)

    def _draw_upgrades(self):
        """Draw upgrade info"""
        upgrade_y = SCREEN_HEIGHT - 200
        title = self.small_font.render('Upgrades:', True, (200, 200, 200))
        self.game_surface.blit(title, (20, upgrade_y))

        # Get current costs
        damage_cost = self.player.get_damage_upgrade_cost()
        speed_cost = self.player.get_speed_upgrade_cost()
        hp_cost = self.player.get_hp_upgrade_cost()

        upgrades = [
            (f'[1] Damage Lv.{self.player.damage_level} ({damage_cost})', 25),
            (f'[2] Speed Lv.{self.player.speed_level} ({speed_cost})', 50),
            (f'[3] HP Lv.{self.player.hp_level} ({hp_cost})', 75)
        ]

        for text, y_offset in upgrades:
            upgrade_text = self.small_font.render(text, True, (255, 200, 100))
            self.game_surface.blit(upgrade_text, (20, upgrade_y + y_offset))

    def _draw_controls(self):
        """Draw controls and abilities"""
        # Abilities panel
        abilities_y = SCREEN_HEIGHT - 110
        panel_width = 600
        panel_height = 60
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 30, 40, 180), (0, 0, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(panel, (100, 200, 255, 80), (0, 0, panel_width, panel_height), 2, border_radius=10)
        self.game_surface.blit(panel, (20, abilities_y))

        # Ability info
        abilities = [
            (f'[Q] Dash ({ABILITY_DASH_COST})', self.player.dash_cooldown, ABILITY_DASH_COOLDOWN),
            (f'[E] Shield ({ABILITY_SHIELD_COST})', self.player.shield_cooldown, ABILITY_SHIELD_COOLDOWN),
            (f'[R] Burst ({ABILITY_BURST_COST})', self.player.burst_cooldown, ABILITY_BURST_COOLDOWN)
        ]

        x_offset = 30
        for text, cooldown, max_cooldown in abilities:
            # Cooldown indicator
            if cooldown > 0:
                color = (150, 150, 150)
                cd_text = f' ({int(cooldown)}s)'
                text += cd_text
            else:
                color = (255, 200, 100)

            ability_text = self.small_font.render(text, True, color)
            self.game_surface.blit(ability_text, (x_offset, abilities_y + 20))
            x_offset += 190

        # Controls hint
        hint = 'WASD: Move | Click: Shoot | 1,2,3: Upgrade | ESC: Pause'
        hint_text = self.small_font.render(hint, True, (120, 120, 120))
        self.game_surface.blit(hint_text, (20, SCREEN_HEIGHT - 35))
