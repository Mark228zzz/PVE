import pygame
import math
import random
from config import Config
from game import Game
from player import Player

class Mana:
    list = []

    def __init__(self, x: int, y: int, color: tuple = (128, 0, 128)):
        self.x, self.y = x + random.randint(-10, 10), y + random.randint(-10, 10)
        self.color = color
        self.radius = random.uniform(2.0, 4.0)
        self.mana = random.randint(1, 5)
        Mana.list.append(self)

    def draw(self):
        pygame.draw.circle(Game.window, self.color, (self.x, self.y), self.radius)

    def update(self):
        self.draw()

        self.check_near()

    def check_near(self):
        if not Player.list:
            return

        for player in Player.list:
            distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
            if distance <= self.radius + player.radius:
                player.mana += self.mana
                self.remove()
            elif distance <= 300:
                dx, dy = player.x - self.x, player.y - self.y
                attraction_speed = 1 + (300 - distance) / 200
                dx, dy = dx / distance, dy / distance

                self.x += dx * attraction_speed
                self.y += dy * attraction_speed

    def remove(self):
        Mana.list.remove(self)
        del self
