"""
Enemy types module - Defines different enemy behaviors and characteristics.
Easy to extend by adding new classes that inherit from BaseEnemy.
"""

import pygame
import math
import random
from entity import Entity
from config import ENEMY_TYPES


class BaseEnemy(Entity):
    """Base class for all enemy types with common functionality"""

    def __init__(self, x, y, enemy_type, difficulty_multipliers):
        self.enemy_type = enemy_type
        self.config = ENEMY_TYPES[enemy_type]
        self.difficulty_multipliers = difficulty_multipliers

        # Random size
        radius = random.uniform(self.config['min_radius'], self.config['max_radius'])
        super().__init__(x, y, radius=radius)

        self.color = self.config['color']
        self.shape = self.config.get('shape', 'circle')

        # Apply difficulty multipliers
        size_multiplier = radius / self.config['max_radius']
        base_hp = int(self.config['hp'] * size_multiplier)
        self.max_hp = int(base_hp * difficulty_multipliers['enemy_hp_multiplier'])
        self.hp = self.max_hp

        self._draw_image()

    def _draw_image(self):
        """Draw enemy based on shape type"""
        self.image.fill((0, 0, 0, 0))
        center = (self.radius, self.radius)

        if self.shape == 'circle':
            pygame.draw.circle(self.image, self.color, center, self.radius)
        elif self.shape == 'square':
            rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
            pygame.draw.rect(self.image, self.color, rect)
        elif self.shape == 'triangle':
            points = [
                (self.radius, 0),
                (self.radius * 2, self.radius * 2),
                (0, self.radius * 2)
            ]
            pygame.draw.polygon(self.image, self.color, points)

    def take_damage(self, damage):
        """Take damage and return True if dead"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            return True
        return False

    def draw(self, surface, camera, show_health_bar=True):
        """Draw enemy and health bar"""
        super().draw(surface, camera)
        if show_health_bar and self.hp < self.max_hp:
            self._draw_health_bar(surface, camera)

    def _draw_health_bar(self, surface, camera):
        """Draw health bar above enemy"""
        bar_width = 30
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 8

        screen_pos = camera.apply(pygame.Rect(bar_x, bar_y, bar_width, bar_height))

        # Background
        pygame.draw.rect(surface, (100, 100, 100), screen_pos)

        # Health
        health_width = int((self.hp / self.max_hp) * bar_width)
        health_rect = pygame.Rect(screen_pos.x, screen_pos.y, health_width, bar_height)
        pygame.draw.rect(surface, self.color, health_rect)


class ShooterEnemy(BaseEnemy):
    """Standard enemy that shoots at player from distance"""

    def __init__(self, x, y, difficulty_multipliers):
        super().__init__(x, y, 'shooter', difficulty_multipliers)

        self.follow_speed = self.config['follow_speed'] * difficulty_multipliers['enemy_speed_multiplier']
        self.stop_distance = self.config['stop_distance']
        self.shoot_cooldown = 0
        self.shoot_delay = self.config['shoot_delay']
        self.shoot_range = self.config['shoot_range']

        base_damage = self.config['bullet_damage']
        self.bullet_damage = int(base_damage * difficulty_multipliers['enemy_damage_multiplier'])
        self.bullet_speed = random.uniform(
            self.config['bullet_speed_min'],
            self.config['bullet_speed_max']
        )

    def update(self, dt, player_pos=None):
        if player_pos:
            self._follow_player(player_pos)
        super().update(dt)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def _follow_player(self, player_pos):
        distance = self.pos.distance_to(player_pos)
        if distance > self.stop_distance:
            direction = (player_pos - self.pos).normalize()
            self.vel += direction * self.follow_speed

    def shoot(self, target_pos):
        """Return bullet if ready to shoot"""
        distance = self.pos.distance_to(target_pos)

        if self.shoot_cooldown <= 0 and distance <= self.shoot_range:
            self.shoot_cooldown = self.shoot_delay

            angle = math.atan2(target_pos.y - self.pos.y, target_pos.x - self.pos.x)
            angle += random.uniform(-0.15, 0.15)

            spawn_distance = self.radius + 5
            spawn_x = self.pos.x + math.cos(angle) * spawn_distance
            spawn_y = self.pos.y + math.sin(angle) * spawn_distance

            from bullet import Bullet
            return Bullet(spawn_x, spawn_y, angle, self.bullet_speed, self.bullet_damage, owner_type='enemy')
        return None


class ExploderEnemy(BaseEnemy):
    """Enemy that rushes player and explodes on contact"""

    def __init__(self, x, y, difficulty_multipliers):
        super().__init__(x, y, 'exploder', difficulty_multipliers)

        self.follow_speed = self.config['follow_speed'] * difficulty_multipliers['enemy_speed_multiplier']
        self.explosion_radius = self.config['explosion_radius']
        base_damage = self.config['explosion_damage']
        self.explosion_damage = int(base_damage * difficulty_multipliers['enemy_damage_multiplier'])
        self.is_exploding = False
        self.explosion_time = 0
        self.explosion_duration = 0.3

    def update(self, dt, player_pos=None):
        if not self.is_exploding and player_pos:
            self._chase_player(player_pos)

        if self.is_exploding:
            self.explosion_time += dt
            if self.explosion_time >= self.explosion_duration:
                self.kill()

        super().update(dt)

    def _chase_player(self, player_pos):
        """Always chase player"""
        direction = (player_pos - self.pos).normalize()
        self.vel += direction * self.follow_speed

    def explode(self):
        """Trigger explosion"""
        self.is_exploding = True
        self.explosion_time = 0

    def draw(self, surface, camera, show_health_bar=True):
        """Draw with pulsing effect when close to player"""
        if self.is_exploding:
            # Draw explosion animation
            progress = self.explosion_time / self.explosion_duration
            radius = int(self.explosion_radius * progress)
            alpha = int(255 * (1 - progress))

            explosion_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            color = (*self.color, alpha)
            pygame.draw.circle(explosion_surface, color, (radius, radius), radius)

            pos = camera.apply(pygame.Rect(
                self.pos.x - radius,
                self.pos.y - radius,
                radius * 2,
                radius * 2
            ))
            surface.blit(explosion_surface, pos)
        else:
            super().draw(surface, camera)


class BouncerEnemy(BaseEnemy):
    """Enemy that bounces around randomly, dealing damage on contact"""

    def __init__(self, x, y, difficulty_multipliers):
        super().__init__(x, y, 'bouncer', difficulty_multipliers)

        # Bouncers don't use friction
        self.friction = 1.0

        self.speed = random.uniform(
            self.config['speed_min'],
            self.config['speed_max']
        ) * difficulty_multipliers['enemy_speed_multiplier']

        angle = random.uniform(0, 2 * math.pi)
        self.vel = pygame.math.Vector2(
            math.cos(angle) * self.speed,
            math.sin(angle) * self.speed
        )

        base_damage = self.config['bounce_damage']
        self.bounce_damage = int(base_damage * difficulty_multipliers['enemy_damage_multiplier'])
        self.last_bounce_time = 0
        self.bounce_cooldown = 0.5

    def update(self, dt, player_pos=None):
        """Update with bouncing behavior"""
        from config import WORLD_WIDTH, WORLD_HEIGHT

        # Bounce off walls
        if self.pos.x <= self.radius or self.pos.x >= WORLD_WIDTH - self.radius:
            self.vel.x *= -1
            self.pos.x = max(self.radius, min(self.pos.x, WORLD_WIDTH - self.radius))
        if self.pos.y <= self.radius or self.pos.y >= WORLD_HEIGHT - self.radius:
            self.vel.y *= -1
            self.pos.y = max(self.radius, min(self.pos.y, WORLD_HEIGHT - self.radius))

        # Maintain constant speed
        if self.vel.length() > 0:
            self.vel = self.vel.normalize() * self.speed

        super().update(dt)
        self.last_bounce_time += dt


class TankEnemy(BaseEnemy):
    """Slow, tanky enemy with high HP"""

    def __init__(self, x, y, difficulty_multipliers):
        super().__init__(x, y, 'tank', difficulty_multipliers)

        self.follow_speed = self.config['follow_speed'] * difficulty_multipliers['enemy_speed_multiplier']
        self.stop_distance = self.config['stop_distance']
        self.shoot_cooldown = 0
        self.shoot_delay = self.config['shoot_delay']
        self.shoot_range = self.config['shoot_range']

        base_damage = self.config['bullet_damage']
        self.bullet_damage = int(base_damage * difficulty_multipliers['enemy_damage_multiplier'])
        self.bullet_speed = random.uniform(
            self.config['bullet_speed_min'],
            self.config['bullet_speed_max']
        )

    def update(self, dt, player_pos=None):
        if player_pos:
            self._follow_player(player_pos)
        super().update(dt)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def _follow_player(self, player_pos):
        distance = self.pos.distance_to(player_pos)
        if distance > self.stop_distance:
            direction = (player_pos - self.pos).normalize()
            self.vel += direction * self.follow_speed

    def shoot(self, target_pos):
        """Return bullet if ready to shoot"""
        distance = self.pos.distance_to(target_pos)

        if self.shoot_cooldown <= 0 and distance <= self.shoot_range:
            self.shoot_cooldown = self.shoot_delay

            angle = math.atan2(target_pos.y - self.pos.y, target_pos.x - self.pos.x)
            angle += random.uniform(-0.1, 0.1)

            spawn_distance = self.radius + 5
            spawn_x = self.pos.x + math.cos(angle) * spawn_distance
            spawn_y = self.pos.y + math.sin(angle) * spawn_distance

            from bullet import Bullet
            return Bullet(spawn_x, spawn_y, angle, self.bullet_speed, self.bullet_damage, owner_type='enemy')
        return None


def create_enemy(enemy_type, x, y, difficulty_multipliers):
    """
    Factory function to create enemies.

    To add a new enemy type:
    1. Add config to ENEMY_TYPES in config.py
    2. Create new class inheriting from BaseEnemy
    3. Add mapping here
    """
    enemy_classes = {
        'shooter': ShooterEnemy,
        'exploder': ExploderEnemy,
        'bouncer': BouncerEnemy,
        'tank': TankEnemy
    }

    enemy_class = enemy_classes.get(enemy_type, ShooterEnemy)
    return enemy_class(x, y, difficulty_multipliers)
