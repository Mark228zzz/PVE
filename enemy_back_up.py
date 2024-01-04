import pygame
import math
import random
from config import Config
from mana import Mana
from particle import Particle
from player import Player
from game import Game


class Enemy:
    list = []

    def __init__(self, x: int, y: int, color: tuple = (187, 0, 0), radius: float = 9, health=3, speed=1.3):
        self.x, self.y = x, y
        self.color = color
        self.radius = radius
        self.health = health
        self.angle = 0
        self.speed = speed
        self.turn_speed = 0.038
        self.shoot_timer = 0
        self.shoot_interval = random.uniform(0.5, 5.0)
        Enemy.list.append(self)

    def draw(self):
        pygame.draw.circle(Game.window, self.color, (self.x, self.y), self.radius, 3)
        target_x = self.x + math.cos(self.angle) * (self.radius * 1.5)
        target_y = self.y + math.sin(self.angle) * (self.radius * 1.5)
        pygame.draw.line(Game.window, self.color, (self.x, self.y), (target_x, target_y), 2)

    def update(self):
        self.draw()
        self.check_health()
        self.update_angle()
        self.update_shoot_timer()
        self.move()

    def update_angle(self):
        if not Player.list:
            return

        player = Player.list[0]
        target_angle = math.atan2(player.y - self.y, player.x - self.x)

        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        if angle_diff < -self.turn_speed:
            self.angle -= self.turn_speed
        elif angle_diff > self.turn_speed:
            self.angle += self.turn_speed
        else:
            self.angle = target_angle

    def update_shoot_timer(self):
        self.shoot_timer += 1 / Config.FPS
        if self.shoot_timer >= self.shoot_interval:
            self.shoot()
            self.shoot_timer = 0

    def move(self):
        if not Player.list:
            return

        player = Player.list[0]
        dx, dy = player.x - self.x, player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 100:
            dx, dy = dx / distance, dy / distance
            self.x += dx * self.speed
            self.y += dy * self.speed
        else:
            random_angle = random.uniform(2, 5 * math.pi)
            self.x += math.cos(random_angle) * self.speed
            self.y += math.sin(random_angle) * self.speed

    def shoot(self):
        from bullet import Bullet  # Local import to avoid circular dependency

        bullet_x = self.x + math.cos(self.angle) * (self.radius * 2)
        bullet_y = self.y + math.sin(self.angle) * (self.radius * 2)
        Bullet(bullet_x, bullet_y, self.angle + random.uniform(-0.05, 0.05), power=1, color=self.color, speed=5)

    def check_health(self):
        if self.health <= 0:
            self.die()

    def die(self):
        [Mana(self.x, self.y) for _ in range(random.randint(1, 5))]
        [Particle(self.x, self.y, self.color, time_life=0.1, radius=1) for _ in range(random.randint(5, 15))]
        Enemy.list.remove(self)
        del self


class EnemySquare:
    list = []

    def __init__(self, x, y, color=(255, 128, 128), width=24, height=24, health=5, speed=1):
        self.x, self.y = x, y
        self.color = color
        self.width, self.height = width, height
        self.health = health
        self.angle = 0
        self.turn_speed = 0.038
        self.speed = speed
        EnemySquare.list.append(self)

    def draw(self):
        pygame.draw.rect(Game.window, self.color, (self.x, self.y, self.width, self.height), 5)

    def update(self):
        self.draw()
        self.update_angle()
        self.check_health()
        self.move()

    def update_angle(self):
        if not Player.list:
            return

        player = Player.list[0]
        target_angle = math.atan2(player.y - self.y, player.x - self.x)

        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        if angle_diff < -self.turn_speed:
            self.angle -= self.turn_speed
        elif angle_diff > self.turn_speed:
            self.angle += self.turn_speed
        else:
            self.angle = target_angle

    def move(self):
        if not Player.list:
            return

        player = Player.list[0]
        dx, dy = player.x - self.x, player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        if distance <= 50:
            self.blow_up()

    def blow_up(self):
        from bullet import Bullet  # Local import to avoid circular dependency

        [Bullet(self.x, self.y, random.uniform(-3.14, 3.14), speed=20, color=self.color, power=2) for _ in range(15)]
        self.die()

    def check_health(self):
        if not self.health <= 0: return
        self.die()

    def die(self):
        [Mana(self.x, self.y) for _ in range(random.randint(5, 10))]
        [Particle(self.x, self.y, self.color, radius=1) for _ in range(random.randint(5, 15))]
        EnemySquare.list.remove(self)
        del self


class EnemyTriangle:
    list = []

    def __init__(self, x: int, y: int, color: tuple = (210, 200, 0), size: int | float = 32, speed: float = 0.75, health: int = 13, summon_rate: int | float = 3.2):
        self.x, self.y = x, y
        self.color = color
        self.size = size
        self.height = size * math.sqrt(3) / 2
        self.points = []
        self.speed = speed
        self.health = health
        self.angle = 0
        self.turn_speed = 0.038
        self.summon_rate = summon_rate
        self.spawn_time = 0
        self.distance = 0
        self.is_dead = False
        EnemyTriangle.list.append(self)

    def draw(self):
        self.points = [(self.x, self.y - 2/3 * self.height), (self.x - self.size/2, self.y + 1/3 * self.height), (self.x + self.size/2, self.y + 1/3 * self.height)]
        pygame.draw.polygon(Game.window, self.color, self.points, 4)

    def update(self):
        self.draw()
        self.update_angle()
        self.move()
        self.summon()
        self.check_health()
        self.check_size()

    def update_angle(self):
        if not Player.list:
            return

        player = Player.list[0]
        target_angle = math.atan2(player.y - self.y, player.x - self.x)

        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        if angle_diff < -self.turn_speed:
            self.angle -= self.turn_speed
        elif angle_diff > self.turn_speed:
            self.angle += self.turn_speed
        else:
            self.angle = target_angle

    def move(self):
        if not Player.list:
            return

        player = Player.list[0]
        dx, dy = player.x - self.x, player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        self.distance = distance

        if distance >= 110:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

    def summon(self):
        self.spawn_time += 1 / Config.FPS
        if self.spawn_time >= self.summon_rate and not self.distance >= 110:
            new_pos = (random.uniform(self.x - 10, self.x + 10), random.uniform(self.y - 10, self.y + 10))
            [Enemy(new_pos[0], new_pos[1]) for _ in range(random.randint(1, 4))]
            self.spawn_time = 0
            self.size -= 6

    def check_size(self):
        if self.size > 0: return
        self.die()

    def check_health(self):
        if self.health > 0: return
        self.die()

    def die(self):
        if self.is_dead: return
        self.is_dead = True
        [Mana(self.x, self.y) for _ in range(random.randint(15, 30))]
        [Particle(self.x, self.y, self.color) for _ in range(random.randint(15, 25))]
        EnemyTriangle.list.remove(self)
        del self
