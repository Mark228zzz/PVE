import pygame
import math
import random
from config import Config
from game import Game


class Particle:
    list = []

    def __init__(self, x: int, y: int, color: tuple, radius: float = 2.0, speed: float = 3.0, time_life: float = 0.5):
        self.x, self.y = x, y
        self.color = color
        self.radius = radius
        self.speed = speed
        self.angle = random.uniform(-3.14, 3.14)
        self.time_life = time_life
        self.timer = 0
        Particle.list.append(self)

    def draw(self):
        pygame.draw.circle(Game.window, self.color, (self.x, self.y), self.radius)

    def update(self):
        self.draw()
        self.move()

        self.timer += 1 / Config.FPS
        if self.timer >= self.time_life:
            self.remove()

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def remove(self):
        Particle.list.remove(self)
        del self
