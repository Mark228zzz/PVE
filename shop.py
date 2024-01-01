import pygame
import pygame_gui
from game import Game
from player import Player

class Shop:
    def __init__(self, manager, player):
        self.manager = manager
        self.player = player
        self.items = [
            {"name": "Health +1", "description": "Increase Health by 1", "price": 200, "effect": self.increase_health},
            {"name": "Speed +1", "description": "Increase Speed by 1", "price": 300, "effect": self.increase_speed}
        ]
        self.buttons = []
        self.texts = []
        self.create_shop_buttons()
        self.hide()

    def create_shop_buttons(self):
        for i, item in enumerate(self.items):
            text = pygame_gui.elements.UILabel(text=f'{item["name"]} - {item["price"]} mana', relative_rect=pygame.Rect((75 + i * 150, 10), (120, 30)), manager=self.manager)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((75 + i * 150, 50), (120, 30)),
                text='buy',
                manager=self.manager,
                visible=0
            )
            self.buttons.append(button)
            self.texts.append(text)

    def handle_events(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for i, button in enumerate(self.buttons):
                if event.ui_element == button:
                    item = self.items[i]
                    if self.player.mana >= item['price']:
                        item['effect']()
                        self.player.mana -= item['price']
                        item['price'] = round(item['price'] * 1.5)

    def show(self):
        for button in self.buttons:
            button.show()
        for text in self.texts:
            text.show()

    def hide(self):
        for button in self.buttons:
            button.hide()
        for text in self.texts:
            text.hide()

    def increase_health(self):
        self.player.health += 1
        self.player.max_health += 1

    def increase_speed(self):
        self.player.speed += 0.1

    def increase_power(self):
        self.player.power += 1
