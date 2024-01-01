import pygame
import pygame_gui

class StartMenu:
    def __init__(self, screen, ui_manager):
        self.screen = screen
        self.ui_manager = ui_manager
        self.create_menu()

    def create_menu(self):
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((350, 275), (100, 50)),
            text='Start',
            manager=self.ui_manager
        )

        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((350, 350), (100, 50)),
            text='Quit',
            manager=self.ui_manager
        )

    def handle_events(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_button:
                return 'start'
            elif event.ui_element == self.quit_button:
                return 'quit'
        return None
