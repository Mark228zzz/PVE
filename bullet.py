import pygame
import math
from config import WORLD_WIDTH, WORLD_HEIGHT


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage, owner_type='player'):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.owner_type = owner_type
        self.radius = 4

        self.vel = pygame.math.Vector2(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )

        # Visual
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        if owner_type == 'player':
            self.color = (255, 255, 100)
        else:
            self.color = (255, 100, 100)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt):
        self.pos += self.vel
        self.rect.center = self.pos

        # Check if bullet is outside world bounds
        if (self.pos.x < 0 or self.pos.x > WORLD_WIDTH or
            self.pos.y < 0 or self.pos.y > WORLD_HEIGHT):
            self.kill()

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))
