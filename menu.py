"""
Menu system for the game.
Handles main menu, pause menu, settings, and victory screen.
"""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, DIFFICULTY_SETTINGS


class Button:
    """Reusable button class"""

    def __init__(self, x, y, width, height, text, font, color=(100, 100, 100),
                 hover_color=(150, 150, 150), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, surface):
        """Draw button"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Handle mouse events, return True if clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False


class MainMenu:
    """Main menu screen"""

    def __init__(self):
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)

        button_width = 300
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 250

        self.buttons = {
            'start': Button(button_x, start_y, button_width, button_height,
                          'Start Game', self.button_font),
            'settings': Button(button_x, start_y + 80, button_width, button_height,
                             'Settings', self.button_font),
            'quit': Button(button_x, start_y + 160, button_width, button_height,
                         'Quit', self.button_font)
        }

        self.result = None

    def handle_event(self, event):
        """Handle events, return action or None"""
        for action, button in self.buttons.items():
            if button.handle_event(event):
                return action
        return None

    def draw(self, surface):
        """Draw main menu"""
        surface.fill(BG_COLOR)

        # Title
        title = self.title_font.render('PVE ARENA', True, (100, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        surface.blit(title, title_rect)

        # Subtitle
        subtitle = self.subtitle_font.render('Survive the Waves', True, (150, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        surface.blit(subtitle, subtitle_rect)

        # Buttons
        for button in self.buttons.values():
            button.draw(surface)


class DifficultyMenu:
    """Difficulty selection menu when starting a game"""

    def __init__(self):
        self.title_font = pygame.font.Font(None, 64)
        self.button_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 28)

        button_width = 300
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 200

        self.buttons = {
            'easy': Button(button_x, start_y, button_width, button_height,
                         'Easy', self.button_font, color=(50, 150, 50)),
            'normal': Button(button_x, start_y + 100, button_width, button_height,
                           'Normal', self.button_font, color=(150, 150, 50)),
            'hard': Button(button_x, start_y + 200, button_width, button_height,
                         'Hard', self.button_font, color=(150, 50, 50)),
            'back': Button(button_x, start_y + 320, button_width, button_height,
                         'Back', self.button_font)
        }

        self.difficulty_info = {
            'easy': f"Waves to win: {DIFFICULTY_SETTINGS['easy']['waves_to_win']} | Easier enemies",
            'normal': f"Waves to win: {DIFFICULTY_SETTINGS['normal']['waves_to_win']} | Balanced",
            'hard': f"Waves to win: {DIFFICULTY_SETTINGS['hard']['waves_to_win']} | Challenging"
        }

    def handle_event(self, event):
        """Handle events, return difficulty or action"""
        for action, button in self.buttons.items():
            if button.handle_event(event):
                return action
        return None

    def draw(self, surface):
        """Draw difficulty selection menu"""
        surface.fill(BG_COLOR)

        # Title
        title = self.title_font.render('Select Difficulty', True, (100, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title, title_rect)

        # Buttons with info
        for difficulty in ['easy', 'normal', 'hard']:
            button = self.buttons[difficulty]
            button.draw(surface)

            # Draw difficulty info
            info_text = self.info_font.render(
                self.difficulty_info[difficulty], True, (200, 200, 200)
            )
            info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, button.rect.bottom + 20))
            surface.blit(info_text, info_rect)

        self.buttons['back'].draw(surface)


class SettingsMenu:
    """Settings menu for game configuration"""

    def __init__(self):
        self.title_font = pygame.font.Font(None, 64)
        self.button_font = pygame.font.Font(None, 36)
        self.label_font = pygame.font.Font(None, 32)

        button_width = 300
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2

        # Game settings (can be expanded)
        self.show_grid = True
        self.show_health_bars = True
        self.camera_smoothness = 0.1

        # Create buttons
        self.buttons = {
            'toggle_grid': Button(button_x, 200, button_width, 50,
                                'Grid: ON', self.button_font),
            'toggle_health': Button(button_x, 270, button_width, 50,
                                  'Health Bars: ON', self.button_font),
            'back': Button(button_x, 420, button_width, button_height,
                         'Back', self.button_font)
        }

    def handle_event(self, event):
        """Handle events, return action or None"""
        if self.buttons['toggle_grid'].handle_event(event):
            self.show_grid = not self.show_grid
            self.buttons['toggle_grid'].text = f'Grid: {"ON" if self.show_grid else "OFF"}'
            return 'toggle_grid'
        elif self.buttons['toggle_health'].handle_event(event):
            self.show_health_bars = not self.show_health_bars
            self.buttons['toggle_health'].text = f'Health Bars: {"ON" if self.show_health_bars else "OFF"}'
            return 'toggle_health'
        elif self.buttons['back'].handle_event(event):
            return 'back'
        return None

    def draw(self, surface):
        """Draw settings menu"""
        surface.fill(BG_COLOR)

        # Title
        title = self.title_font.render('Settings', True, (100, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title, title_rect)

        # Info text
        info = self.label_font.render('Game Display Options', True, (200, 200, 200))
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, 160))
        surface.blit(info, info_rect)

        # Buttons
        for button in self.buttons.values():
            button.draw(surface)


class PauseMenu:
    """Pause menu overlay"""

    def __init__(self):
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 48)

        button_width = 300
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 250

        self.buttons = {
            'resume': Button(button_x, start_y, button_width, button_height,
                           'Resume', self.button_font, color=(50, 150, 50)),
            'restart': Button(button_x, start_y + 80, button_width, button_height,
                            'Restart', self.button_font),
            'menu': Button(button_x, start_y + 160, button_width, button_height,
                         'Main Menu', self.button_font)
        }

    def handle_event(self, event):
        """Handle events, return action or None"""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'resume'

        for action, button in self.buttons.items():
            if button.handle_event(event):
                return action
        return None

    def draw(self, surface, game_surface):
        """Draw pause menu as overlay"""
        # Draw darkened game background
        surface.blit(game_surface, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render('PAUSED', True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title, title_rect)

        # Buttons
        for button in self.buttons.values():
            button.draw(surface)


class VictoryScreen:
    """Victory screen when player wins"""

    def __init__(self, difficulty, waves_completed):
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 36)

        self.difficulty = difficulty.upper()
        self.waves = waves_completed

        button_width = 300
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 350

        self.buttons = {
            'restart': Button(button_x, start_y, button_width, button_height,
                            'Play Again', self.button_font, color=(50, 150, 50)),
            'menu': Button(button_x, start_y + 80, button_width, button_height,
                         'Main Menu', self.button_font)
        }

    def handle_event(self, event):
        """Handle events, return action or None"""
        for action, button in self.buttons.items():
            if button.handle_event(event):
                return action
        return None

    def draw(self, surface):
        """Draw victory screen"""
        surface.fill(BG_COLOR)

        # Title
        title = self.title_font.render('VICTORY!', True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        surface.blit(title, title_rect)

        # Info
        info_lines = [
            f'Difficulty: {self.difficulty}',
            f'Waves Completed: {self.waves}',
            'You have survived the arena!'
        ]

        y = 220
        for line in info_lines:
            text = self.info_font.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            surface.blit(text, text_rect)
            y += 50

        # Buttons
        for button in self.buttons.values():
            button.draw(surface)


class GameOverScreen:
    """Game over screen when player dies"""

    def __init__(self, waves_survived):
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 36)

        self.waves = waves_survived

        button_width = 300
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 350

        self.buttons = {
            'restart': Button(button_x, start_y, button_width, button_height,
                            'Try Again', self.button_font, color=(150, 50, 50)),
            'menu': Button(button_x, start_y + 80, button_width, button_height,
                         'Main Menu', self.button_font)
        }

    def handle_event(self, event):
        """Handle events, return action or None"""
        for action, button in self.buttons.items():
            if button.handle_event(event):
                return action
        return None

    def draw(self, surface):
        """Draw game over screen"""
        surface.fill(BG_COLOR)

        # Title
        title = self.title_font.render('GAME OVER', True, (255, 80, 80))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title, title_rect)

        # Info
        info = self.info_font.render(f'Waves Survived: {self.waves}', True, (200, 200, 200))
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, 250))
        surface.blit(info, info_rect)

        # Buttons
        for button in self.buttons.values():
            button.draw(surface)
