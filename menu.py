from config import Config
from pygame_menu import Theme
import pygame_menu


class Menu:
    def __init__(self):
        self.theme = Theme(
        background_color=(30, 30, 30, 255),  # Dark gray background with some transparency
        title_background_color=(15, 15, 15),  # Almost black background for the title
        title_font_color=(200, 230, 255),      # White title font color
        widget_font_color=(200, 230, 255),     # Light gray font color for widgets
        widget_background_color=(18, 18, 18, 255),  # Slightly lighter gray for widget backgrounds
        selection_color=(140, 170, 195),       # White color for selection highlight
        scrollbar_color=(120, 120, 120),       # Medium gray scrollbar color
        scrollbar_slider_color=(200, 200, 200), # Light gray scrollbar slider color
        scrollbar_slider_pad=2,
        scrollbar_thick=20,
        widget_border_color=(0, 0, 0),   # Medium gray border for widgets
        widget_margin=(0, 7),                  # Vertical margin between widgets
        widget_padding=(10, 5),                # Padding inside widgets
        widget_alignment=pygame_menu.locals.ALIGN_CENTER,  # Align widgets to the left
        border_width=2,
        border_color=(200, 200, 200),          # Light gray border color
        title_font=pygame_menu.font.FONT_NEVIS,  # Use a modern font for the title
        title_font_size=55,
        widget_font=pygame_menu.font.FONT_NEVIS,  # Same font for widgets
        widget_font_size=35,
        title_font_shadow=True,                # Enable shadow for title font
        title_font_shadow_offset=2,            # Shadow offset for title font
        title_font_shadow_color=(100, 130, 155),     # Shadow color for title font
        widget_font_shadow=True,               # Enable shadow for widget fonts
        widget_shadow_width = 9,
        widget_shadow_radius = 30,
        widget_font_shadow_offset=2,           # Shadow offset for widget fonts
        widget_font_shadow_color=(100, 130, 155)     # Shadow color for widget fonts
        )

        self.start_menu = pygame_menu.Menu('PVE', Config.WIDTH, Config.HEIGHT, theme=self.theme)
        self.continue_game_menu = pygame_menu.Menu('Continue', Config.WIDTH, Config.HEIGHT, theme=self.theme)
        self.new_game_menu = pygame_menu.Menu('New Game', Config.WIDTH, Config.HEIGHT, theme=self.theme)
        self.settings_menu = pygame_menu.Menu('Quit', Config.WIDTH, Config.HEIGHT, theme=self.theme)

    def create_widgets(self):
        # start_menu
        self.start_menu.add.button('Continue', self.continue_game_menu)
        self.start_menu.add.button('New Game', self.new_game_menu)
        self.start_menu.add.button('Settings', self.settings_menu)
        self.start_menu.add.button('Quit', pygame_menu.events.EXIT)

        # continue_game_menu

        # new_game_menu
        self.new_game_menu.add.selector('Choose a difficulty')
