import pygame
import math
from config import MANA_RADIUS, MANA_COLLECTION_RADIUS, MANA_COLLECT_SPEED


class ManaDrop(pygame.sprite.Sprite):
    def __init__(self, x, y, amount=5):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.amount = amount
        self.radius = MANA_RADIUS
        self.collection_radius = MANA_COLLECTION_RADIUS
        self.collect_speed = MANA_COLLECT_SPEED

        # Animation
        self.spawn_time = 0
        self.spawn_duration = 0.5
        self.initial_y = y - 30
        self.target_y = y
        self.pulse_time = 0

        # Visual
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.being_collected = False

    def update(self, dt, player_pos=None):
        self.pulse_time += dt

        # Drop animation
        if self.spawn_time < self.spawn_duration:
            self.spawn_time += dt
            progress = min(self.spawn_time / self.spawn_duration, 1.0)
            # Ease out
            progress = 1 - (1 - progress) ** 3
            self.pos.y = self.initial_y + (self.target_y - self.initial_y) * progress

        # Attraction to player
        elif player_pos:
            distance = self.pos.distance_to(player_pos)

            if distance < self.collection_radius:
                self.being_collected = True
                # Move towards player
                direction = (player_pos - self.pos).normalize()
                speed = self.collect_speed * (1 + (self.collection_radius - distance) / self.collection_radius)
                self.pos += direction * speed * dt

        self.rect.center = self.pos

    def draw(self, surface, camera):
        # Pulsing effect
        pulse = math.sin(self.pulse_time * 5) * 0.2 + 1.0
        current_radius = int(self.radius * pulse)

        # Redraw image with pulse
        self.image.fill((0, 0, 0, 0))

        # Outer glow
        glow_color = (100, 200, 255, 100)
        pygame.draw.circle(self.image, glow_color, (self.radius, self.radius), current_radius + 2)

        # Core
        core_color = (150, 230, 255)
        pygame.draw.circle(self.image, core_color, (self.radius, self.radius), current_radius)

        surface.blit(self.image, camera.apply(self.rect))
