"""
Particle system for visual effects.
"""

import pygame
import random
import math


class Particle(pygame.sprite.Sprite):
    """Single particle"""

    def __init__(self, x, y, color, velocity, lifetime=1.0):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = velocity
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)

        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt):
        """Update particle"""
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.kill()
            return

        # Move
        self.pos += self.vel * dt
        self.vel *= 0.95  # Slow down

        # Gravity
        self.vel.y += 200 * dt

        self.rect.center = self.pos

    def draw(self, surface, camera):
        """Draw particle with fade"""
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color, alpha)

        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, color, (self.size, self.size), self.size)

        surface.blit(self.image, camera.apply(self.rect))


def create_death_particles(x, y, color, count=15):
    """Create explosion of particles"""
    particles = pygame.sprite.Group()

    for _ in range(count):
        # Random direction and speed
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 300)

        velocity = pygame.math.Vector2(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )

        lifetime = random.uniform(0.5, 1.2)

        # Slight color variation
        r = max(0, min(255, color[0] + random.randint(-30, 30)))
        g = max(0, min(255, color[1] + random.randint(-30, 30)))
        b = max(0, min(255, color[2] + random.randint(-30, 30)))

        particle = Particle(x, y, (r, g, b), velocity, lifetime)
        particles.add(particle)

    return particles
