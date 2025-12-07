import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.smoothness = 0.1

    def follow(self, target):
        target_x = target.pos.x - SCREEN_WIDTH // 2
        target_y = target.pos.y - SCREEN_HEIGHT // 2

        self.x += (target_x - self.x) * self.smoothness
        self.y += (target_y - self.y) * self.smoothness

        self.x = max(0, min(self.x, WORLD_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, WORLD_HEIGHT - SCREEN_HEIGHT))

    def apply(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

    def apply_pos(self, x, y):
        return x - self.x, y - self.y
