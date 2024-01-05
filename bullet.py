import pygame
import math
from config import Config
# Avoid top-level imports of Player and Enemy to prevent circular dependencies

class Bullet:
    list = []

    def __init__(self, x, y, angle, power=1, color=(255, 255, 255), speed=5, from_player=False):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = speed
        self.color = color
        self.radius = 2
        self.power = power
        self.from_player = from_player
        self.is_removed = False
        Bullet.list.append(self)

    def draw(self):
        from game import Game  # Local import
        pygame.draw.circle(Game.window, self.color, (self.x, self.y), self.radius)

    def update(self):
        self.draw()
        self.moving()
        self.check_hit()
        if self.is_off_screen():
            self.remove()

    def check_hit(self):
        # Local import to avoid circular dependency
        from player import Player
        from enemy import EnemyCircle, EnemySquare, EnemyTriangle, EnemyLeaping

        if self.from_player:
            for enemy_circle in EnemyCircle.list:
                distance = math.sqrt((self.x - enemy_circle.x) ** 2 + (self.y - enemy_circle.y) ** 2)
                if distance <= self.radius + enemy_circle.radius:
                    enemy_circle.health -= self.power
                    self.remove()
                    break
            for enemy_square in EnemySquare.list:
                distance = math.sqrt((self.x - enemy_square.x) ** 2 + (self.y - enemy_square.y) ** 2)
                if distance <= self.radius + enemy_square.width:
                    enemy_square.health -= self.power
                    self.remove()
                    break
            for enemy_triangle in EnemyTriangle.list:
                distance = math.sqrt((self.x - enemy_triangle.x) ** 2 + (self.y - enemy_triangle.y) ** 2)
                if distance <= self.radius + enemy_triangle.size/1.5:
                    enemy_triangle.health -= self.power
                    self.remove()
                    break
            for enemy_leaping in EnemyLeaping.list:
                distance = math.sqrt((self.x - enemy_leaping.x) ** 2 + (self.y - enemy_leaping.y) ** 2)
                if distance <= self.radius + enemy_leaping.radius:
                    enemy_leaping.health -= self.power
                    self.remove()
                    break
        else:
            for player in Player.list:
                distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
                if distance <= self.radius + player.radius:
                    player.health -= self.power
                    self.remove()
                    break

    def is_off_screen(self):
        return self.x < 0 or self.x > Config.WIDTH or self.y < 0 or self.y > Config.HEIGHT

    def moving(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def remove(self):
        if self.is_removed:
            return
        Bullet.list.remove(self)
        self.is_removed = True
        del self
