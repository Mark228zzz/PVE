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

    def __init__(self, x: int, y: int, color: tuple[int, int, int], health: int | float, speed: float):
        self.x, self.y = x, y
        self.color = color
        self.health = health
        self.speed = speed
        self.angle = 0
        self.turn_speed = 0.038
        self.is_dead = False
        self.__class__.list.append(self)

    def draw(self):
        pass

    def update(self):
        self.draw()
        self.update_angle()
        self.move()
        self.check_health()

    def update_angle(self):
        if not Player.list: return

        player = Player.list[0]
        target_angle = math.atan2(player.y - self.y, player.x - self.x)

        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi

        if angle_diff < -self.turn_speed: self.angle -= self.turn_speed
        elif angle_diff > self.turn_speed: self.angle += self.turn_speed
        else: self.angle = target_angle

    def move(self): ...

    def check_health(self):
        if self.health > 0: return
        self.die()

    def drop_items(self): ...

    def die(self):
        if self.is_dead: return

        self.is_dead = True
        self.drop_items()
        self.__class__.list.remove(self)
        del self


class EnemyCircle(Enemy):
    list = []

    def __init__(self, x: int, y: int, color: tuple[int, int, int], radius: float, health: int | float, speed: float):
        self.radius = radius
        self.shoot_timer = 0
        self.shoot_interval = random.uniform(0.5, 5.0)
        super().__init__(x, y, color, health, speed)

    def draw(self):
        pygame.draw.circle(Game.window, self.color, (self.x, self.y), self.radius, 3)
        target_x = self.x + math.cos(self.angle) * (self.radius * 1.5)
        target_y = self.y + math.sin(self.angle) * (self.radius * 1.5)
        pygame.draw.line(Game.window, self.color, (self.x, self.y), (target_x, target_y), 2)
        return super().draw()

    def update(self):
        self.update_shoot_timer()
        return super().update()

    def update_shoot_timer(self):
        self.shoot_timer += 1 / Config.FPS
        if self.shoot_timer >= self.shoot_interval:
            self.shoot()
            self.shoot_timer = 0

    def shoot(self):
        from bullet import Bullet

        bullet_x = self.x + math.cos(self.angle) * (self.radius * 2)
        bullet_y = self.y + math.sin(self.angle) * (self.radius * 2)
        Bullet(bullet_x, bullet_y, self.angle + random.uniform(-0.05, 0.05), power=1, color=self.color, speed=5)

    def move(self):
        if not Player.list: return

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

    def drop_items(self):
        [Mana(self.x, self.y) for _ in range(random.randint(1, 5))]
        [Particle(self.x, self.y, self.color, time_life=0.1, radius=1) for _ in range(random.randint(5, 15))]
        return super().drop_items()


class EnemySquare(Enemy):
    list = []

    def __init__(self, x: int, y: int, color: tuple[int, int, int], width: int | float, height: int | float, health: int | float, speed: float):
        self.width, self.height = width, height
        super().__init__(x, y, color, health, speed)

    def draw(self):
        pygame.draw.rect(Game.window, self.color, (self.x, self.y, self.width, self.height), 5)
        return super().draw()

    def move(self):
        if not Player.list: return

        player = Player.list[0]
        dx, dy = player.x - self.x, player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        if distance <= 50:
            self.blow_up()

    def blow_up(self):
        from bullet import Bullet

        [Bullet(self.x, self.y, random.uniform(-3.14, 3.14), speed=20, color=self.color, power=2) for _ in range(15)]
        self.die()

    def drop_items(self):
        [Mana(self.x, self.y) for _ in range(random.randint(5, 10))]
        [Particle(self.x, self.y, self.color, radius=1) for _ in range(random.randint(5, 15))]
        return super().drop_items()


class EnemyTriangle(Enemy):
    list = []

    def __init__(self, x: int, y: int, color: tuple[int, int, int], size: float, health: int | float, speed: float, summon_rate: int | float):
        self.size = size
        self.summon_rate = summon_rate
        self.height = size * math.sqrt(3) / 2
        self.points = []
        self.spawn_time = 0
        self.distance = 0
        super().__init__(x, y, color, health, speed)

    def draw(self):
        self.points = [(self.x, self.y - 2/3 * self.height), (self.x - self.size/2, self.y + 1/3 * self.height), (self.x + self.size/2, self.y + 1/3 * self.height)]
        pygame.draw.polygon(Game.window, self.color, self.points, 4)
        return super().draw()

    def update(self):
        self.update_summon()
        self.check_size()
        return super().update()

    def move(self):
        if not Player.list: return

        player = Player.list[0]
        dx, dy = player.x - self.x, player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        self.distance = distance

        if distance >= 110:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

    def update_summon(self):
        self.spawn_time += 1 / Config.FPS
        if self.spawn_time >= self.summon_rate and not self.distance >= 110:
            new_pos = (random.uniform(self.x - 10, self.x + 10), random.uniform(self.y - 10, self.y + 10))
            [EnemyCircle(new_pos[0], new_pos[1], (127, 0, 0), 10.0, 2, 1.0) for _ in range(random.randint(1, 4))]
            self.spawn_time = 0
            self.size -= 6

    def check_size(self):
        if self.size > 0: return
        self.die()

    def drop_items(self):
        [Mana(self.x, self.y) for _ in range(random.randint(15, 30))]
        [Particle(self.x, self.y, self.color) for _ in range(random.randint(15, 25))]
        return super().drop_items()


class EnemyLeaping(Enemy):
    def __init__(self, x: int, y: int, color: tuple[int, int, int], radius: float, push_strength: int | float, health: int | float, speed: float):
        self.radius = radius
        self.push_strength = push_strength
        self.push_timer = 0
        super().__init__(x, y, color, health, speed)

    def draw(self):
        pygame.draw.circle(Game.window, self.color, (self.x, self.y), self.radius)

    def move(self):
        if not Player.list: return

        self.push_timer += 1

        player = Player.list[0]
        dx, dy = player.x - self.x, player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        if distance <= self.radius + player.radius and self.push_timer >= 200:
            self.push()

    def push(self):
        if not Player.list: return

        player = Player.list[0]
        angle = math.atan2(player.y - self.y, player.x - self.x)
        player.vel_x += math.cos(angle) * self.push_strength
        player.vel_y += math.sin(angle) * self.push_strength
        player.health -= random.randint(3, 8)

        self.push_timer = 0

    def drop_items(self):
        [Mana(self.x, self.y) for _ in range(random.randint(25, 40))]
        [Particle(self.x, self.y, self.color, 1.2, 3.8) for _ in range(random.randint(20, 40))]
        return super().drop_items()
