import pygame
from entity import Entity
from config import (PLAYER_RADIUS, PLAYER_BASE_HP, PLAYER_ACCELERATION, PLAYER_FRICTION,
                    PLAYER_TURN_SPEED, PLAYER_BULLET_SPEED, PLAYER_BULLET_DAMAGE,
                    PLAYER_SHOOT_DELAY, UPGRADE_DAMAGE_BASE_COST, UPGRADE_DAMAGE_COST_INCREASE,
                    UPGRADE_DAMAGE_INCREASE, UPGRADE_SPEED_BASE_COST, UPGRADE_SPEED_COST_INCREASE,
                    UPGRADE_SPEED_INCREASE, UPGRADE_HP_BASE_COST, UPGRADE_HP_COST_INCREASE,
                    UPGRADE_HP_INCREASE, UPGRADE_HP_HEAL,
                    ABILITY_DASH_COST, ABILITY_DASH_DISTANCE, ABILITY_DASH_COOLDOWN,
                    ABILITY_SHIELD_COST, ABILITY_SHIELD_DURATION, ABILITY_SHIELD_COOLDOWN,
                    ABILITY_BURST_COST, ABILITY_BURST_DAMAGE, ABILITY_BURST_RADIUS, ABILITY_BURST_COOLDOWN)
import math
import random


class Player(Entity):
    def __init__(self, x, y, difficulty='normal'):
        super().__init__(x, y, radius=PLAYER_RADIUS)
        self.color = (100, 200, 255)
        self.acceleration = PLAYER_ACCELERATION
        self.friction = PLAYER_FRICTION
        self.angle = 0
        self.turn_speed = PLAYER_TURN_SPEED

        # Health based on difficulty
        self.max_hp = PLAYER_BASE_HP[difficulty]
        self.hp = self.max_hp

        # Shooting
        self.shoot_cooldown = 0
        self.shoot_delay = PLAYER_SHOOT_DELAY
        self.bullet_damage = PLAYER_BULLET_DAMAGE
        self.bullet_speed = PLAYER_BULLET_SPEED
        self.mana = 0

        # Upgrades
        self.damage_level = 1
        self.speed_level = 1
        self.hp_level = 1

        # Abilities
        self.dash_cooldown = 0
        self.shield_cooldown = 0
        self.shield_active = False
        self.shield_time = 0
        self.burst_cooldown = 0

        self._draw_image()

    def _draw_image(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, width=4)

    def update(self, dt, camera=None):
        self._handle_input()
        self._update_angle(camera)
        super().update(dt)

        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        if self.shield_cooldown > 0:
            self.shield_cooldown -= dt
        if self.burst_cooldown > 0:
            self.burst_cooldown -= dt

        # Update shield
        if self.shield_active:
            self.shield_time -= dt
            if self.shield_time <= 0:
                self.shield_active = False

    def _handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]: self.vel.y -= self.acceleration
        if keys[pygame.K_s]: self.vel.y += self.acceleration
        if keys[pygame.K_a]: self.vel.x -= self.acceleration
        if keys[pygame.K_d]: self.vel.x += self.acceleration

    def _update_angle(self, camera=None):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Convert screen mouse position to world position
        if camera:
            world_mouse_x = mouse_x + camera.x
            world_mouse_y = mouse_y + camera.y
        else:
            world_mouse_x = mouse_x
            world_mouse_y = mouse_y

        target_angle = math.atan2(world_mouse_y - self.pos.y, world_mouse_x - self.pos.x)
        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi

        if angle_diff < -self.turn_speed:
            self.angle -= self.turn_speed
        elif angle_diff > self.turn_speed:
            self.angle += self.turn_speed
        else:
            self.angle = target_angle

    def shoot(self):
        """Returns a bullet if ready to shoot, otherwise None"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_delay

            # Add randomness to angle and speed
            angle_variance = random.uniform(-0.1, 0.1)  # +/- ~6 degrees
            speed_variance = random.uniform(0.9, 1.1)

            bullet_angle = self.angle + angle_variance
            bullet_speed = self.bullet_speed * speed_variance

            # Spawn bullet at the edge of player
            spawn_distance = self.radius + 5
            spawn_x = self.pos.x + math.cos(self.angle) * spawn_distance
            spawn_y = self.pos.y + math.sin(self.angle) * spawn_distance

            from bullet import Bullet
            return Bullet(spawn_x, spawn_y, bullet_angle, bullet_speed, self.bullet_damage, owner_type='player')
        return None

    def draw(self, surface, camera):
        # Draw shield if active
        if self.shield_active:
            shield_radius = self.radius + 10
            pulse = abs(math.sin(self.shield_time * 5)) * 5
            current_radius = shield_radius + pulse

            screen_pos = camera.apply_pos(self.pos.x, self.pos.y)

            # Outer glow
            alpha = int(100 * (self.shield_time / ABILITY_SHIELD_DURATION))
            shield_surface = pygame.Surface((current_radius * 2 + 20, current_radius * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (100, 200, 255, alpha), (current_radius + 10, current_radius + 10), current_radius, 3)
            shield_rect = shield_surface.get_rect(center=screen_pos)
            surface.blit(shield_surface, shield_rect)

        # Draw the player
        super().draw(surface, camera)

        # Draw the direction line
        line_length = self.radius + 15
        end_x = self.pos.x + math.cos(self.angle) * line_length
        end_y = self.pos.y + math.sin(self.angle) * line_length

        start_pos = camera.apply_pos(self.pos.x, self.pos.y)
        end_pos = camera.apply_pos(end_x, end_y)

        pygame.draw.line(surface, (255, 255, 255), start_pos, end_pos, 4)

    def take_damage(self, damage):
        # Shield blocks damage
        if self.shield_active:
            return
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def collect_mana(self, amount):
        self.mana += amount

    # Abilities
    def use_dash(self):
        """Dash forward quickly (Q key)"""
        if self.mana >= ABILITY_DASH_COST and self.dash_cooldown <= 0:
            self.mana -= ABILITY_DASH_COST
            self.dash_cooldown = ABILITY_DASH_COOLDOWN

            # Dash in current facing direction
            dash_x = math.cos(self.angle) * ABILITY_DASH_DISTANCE
            dash_y = math.sin(self.angle) * ABILITY_DASH_DISTANCE

            from config import WORLD_WIDTH, WORLD_HEIGHT
            self.pos.x = max(self.radius, min(self.pos.x + dash_x, WORLD_WIDTH - self.radius))
            self.pos.y = max(self.radius, min(self.pos.y + dash_y, WORLD_HEIGHT - self.radius))

            return True
        return False

    def use_shield(self):
        """Activate damage shield (E key)"""
        if self.mana >= ABILITY_SHIELD_COST and self.shield_cooldown <= 0:
            self.mana -= ABILITY_SHIELD_COST
            self.shield_cooldown = ABILITY_SHIELD_COOLDOWN
            self.shield_active = True
            self.shield_time = ABILITY_SHIELD_DURATION
            return True
        return False

    def use_burst(self):
        """Return enemies in burst radius for damage (R key)"""
        if self.mana >= ABILITY_BURST_COST and self.burst_cooldown <= 0:
            self.mana -= ABILITY_BURST_COST
            self.burst_cooldown = ABILITY_BURST_COOLDOWN
            return {'pos': self.pos.copy(), 'radius': ABILITY_BURST_RADIUS, 'damage': ABILITY_BURST_DAMAGE}
        return None

    def get_damage_upgrade_cost(self):
        """Calculate current damage upgrade cost"""
        return UPGRADE_DAMAGE_BASE_COST + (self.damage_level - 1) * UPGRADE_DAMAGE_COST_INCREASE

    def get_speed_upgrade_cost(self):
        """Calculate current speed upgrade cost"""
        return UPGRADE_SPEED_BASE_COST + (self.speed_level - 1) * UPGRADE_SPEED_COST_INCREASE

    def get_hp_upgrade_cost(self):
        """Calculate current HP upgrade cost"""
        return UPGRADE_HP_BASE_COST + (self.hp_level - 1) * UPGRADE_HP_COST_INCREASE

    def upgrade_damage(self):
        """Upgrade damage"""
        cost = self.get_damage_upgrade_cost()
        if self.mana >= cost:
            self.mana -= cost
            self.damage_level += 1
            self.bullet_damage += UPGRADE_DAMAGE_INCREASE
            return True
        return False

    def upgrade_speed(self):
        """Upgrade bullet speed"""
        cost = self.get_speed_upgrade_cost()
        if self.mana >= cost:
            self.mana -= cost
            self.speed_level += 1
            self.bullet_speed += UPGRADE_SPEED_INCREASE
            return True
        return False

    def upgrade_hp(self):
        """Upgrade max HP and restore health"""
        cost = self.get_hp_upgrade_cost()
        if self.mana >= cost:
            self.mana -= cost
            self.hp_level += 1
            self.max_hp += UPGRADE_HP_INCREASE
            self.hp = min(self.hp + UPGRADE_HP_HEAL, self.max_hp)
            return True
        return False

