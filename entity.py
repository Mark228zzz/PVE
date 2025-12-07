import pygame
from config import WORLD_WIDTH, WORLD_HEIGHT


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=20):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.radius = radius
        self.acceleration = 0.5
        self.friction = 0.9

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def apply_force(self, fx, fy):
        self.vel.x += fx
        self.vel.y += fy

    def update(self, dt):
        self.vel *= self.friction
        self.pos += self.vel

        self.pos.x = max(self.radius, min(self.pos.x, WORLD_WIDTH - self.radius))
        self.pos.y = max(self.radius, min(self.pos.y, WORLD_HEIGHT - self.radius))

        self.rect.center = self.pos

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))
