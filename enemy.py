from entity import Entity
from config import (ENEMY_MIN_RADIUS, ENEMY_MAX_RADIUS, ENEMY_HP, ENEMY_FOLLOW_SPEED,
                    ENEMY_STOP_DISTANCE, ENEMY_BULLET_SPEED_MIN, ENEMY_BULLET_SPEED_MAX,
                    ENEMY_BULLET_DAMAGE, ENEMY_SHOOT_DELAY, ENEMY_SHOOT_RANGE)
import pygame
import math
import random


class Enemy(Entity):
    def __init__(self, x, y, radius=None):
        # Random size variation
        if radius is None:
            radius = random.uniform(ENEMY_MIN_RADIUS, ENEMY_MAX_RADIUS)

        super().__init__(x, y, radius=radius)
        self.color = (255, 80, 80)

        # Health scales with size
        size_multiplier = radius / ENEMY_MAX_RADIUS
        self.max_hp = int(ENEMY_HP * size_multiplier)
        self.hp = self.max_hp

        # AI
        self.follow_speed = ENEMY_FOLLOW_SPEED
        self.stop_distance = ENEMY_STOP_DISTANCE

        # Shooting
        self.shoot_cooldown = 0
        self.shoot_delay = ENEMY_SHOOT_DELAY
        self.shoot_range = ENEMY_SHOOT_RANGE
        self.bullet_damage = ENEMY_BULLET_DAMAGE
        self.bullet_speed = random.uniform(ENEMY_BULLET_SPEED_MIN, ENEMY_BULLET_SPEED_MAX)

        self._draw_image()

    def _draw_image(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

    def update(self, dt, player_pos=None):
        if player_pos:
            self._follow_player(player_pos)

        super().update(dt)

        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def _follow_player(self, player_pos):
        distance = self.pos.distance_to(player_pos)

        if distance > self.stop_distance:
            # Move towards player
            direction = (player_pos - self.pos).normalize()
            self.vel += direction * self.follow_speed

    def shoot(self, target_pos):
        """Returns a bullet if ready to shoot and in range, otherwise None"""
        distance = self.pos.distance_to(target_pos)

        if self.shoot_cooldown <= 0 and distance <= self.shoot_range:
            self.shoot_cooldown = self.shoot_delay

            # Calculate angle to target
            angle = math.atan2(target_pos.y - self.pos.y, target_pos.x - self.pos.x)

            # Add slight randomness
            angle_variance = random.uniform(-0.15, 0.15)
            angle += angle_variance

            # Spawn bullet at edge of enemy
            spawn_distance = self.radius + 5
            spawn_x = self.pos.x + math.cos(angle) * spawn_distance
            spawn_y = self.pos.y + math.sin(angle) * spawn_distance

            from bullet import Bullet
            return Bullet(spawn_x, spawn_y, angle, self.bullet_speed, self.bullet_damage, owner_type='enemy')
        return None

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            return True  # Enemy is dead
        return False

    def draw(self, surface, camera):
        super().draw(surface, camera)

        # Draw health bar
        if self.hp < self.max_hp:
            bar_width = 30
            bar_height = 4
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 8

            # Apply camera offset
            screen_pos = camera.apply(pygame.Rect(bar_x, bar_y, bar_width, bar_height))

            # Background
            pygame.draw.rect(surface, (100, 100, 100), screen_pos)

            # Health
            health_width = int((self.hp / self.max_hp) * bar_width)
            health_rect = pygame.Rect(screen_pos.x, screen_pos.y, health_width, bar_height)
            pygame.draw.rect(surface, (255, 80, 80), health_rect)
