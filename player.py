import pygame
import math
from config import Config
from random import uniform


class Player:
    list = []

    def __init__(self):
        self.x, self.y = Config.WIDTH // 2, Config.HEIGHT // 2
        self.color = (255, 255, 255)
        self.radius = 10
        self.speed = 1
        self.angle = 0
        self.default_speed = 0.5
        self.run_speed = 1.2
        self.turn_speed = 0.125
        self.health = 5
        self.max_health = 5
        self.mana = 0
        self.is_dead = False
        self.vel_x, self.vel_y = 0, 0
        self.friction = 0.02
        self.acceleration = 0.05
        self.timer_add_health = 0
        self.timer_flicker = 0
        self.percent_health = 0
        Player.list.append(self)

    def draw(self):
        from game import Game

        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(Game.window, self.color, (self.x, self.y), self.radius, 3)
        pygame.draw.line(Game.window, self.color, (self.x, self.y),
                         (self.x + math.cos(self.angle) * (self.radius * 1.75),
                          self.y + math.sin(self.angle) * (self.radius * 1.75)), 3)

    def draw_health(self):
        from game import Game

        font = pygame.font.SysFont('notosanscjksc', 28)
        text = font.render(f'hp: {self.health}/{self.max_health}', True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.bottomleft = (65, Config.HEIGHT - 10)
        Game.window.blit(text, text_rect)

    def draw_mana(self):
        from game import Game

        font = pygame.font.SysFont('notosanscjksc', 28)
        text = font.render(f'mana: {self.mana}', True, (128, 0, 128))
        text_rect = text.get_rect()
        text_rect.bottomleft = (65, Config.HEIGHT - 40)
        Game.window.blit(text, text_rect)

    def update(self):
        from game import Game

        self.draw()
        self.draw_health()
        self.draw_mana()
        self.update_angle()
        self.check_health()
        self.percent_health = round(self.health / self.max_health, 2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.speed = self.run_speed
        else:
            self.speed = self.default_speed

        if keys[pygame.K_w]:
            self.y = max(0 + self.radius, self.y - self.speed)
            self.vel_y -= self.acceleration
        elif keys[pygame.K_s]:
            self.y = min(Config.HEIGHT - self.radius, self.y + self.speed)
            self.vel_y += self.acceleration
        if keys[pygame.K_a]:
            self.x = max(0 + self.radius, self.x - self.speed)
            self.vel_x -= self.acceleration
        elif keys[pygame.K_d]:
            self.x = min(Config.WIDTH - self.radius, self.x + self.speed)
            self.vel_x += self.acceleration

        self.vel_x *= (1 - self.friction)
        self.vel_y *= (1 - self.friction)

        self.x += self.vel_x
        self.y += self.vel_y

        self.x = max(self.radius, min(Config.WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(Config.HEIGHT - self.radius, self.y))

    def update_angle(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        target_angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi

        if angle_diff < -self.turn_speed:
            self.angle -= self.turn_speed
        elif angle_diff > self.turn_speed:
            self.angle += self.turn_speed
        else:
            self.angle = target_angle

    def shoot(self):
        from bullet import Bullet  # Local import

        bullet_x = self.x + math.cos(self.angle) * (self.radius * 2)
        bullet_y = self.y + math.sin(self.angle) * (self.radius * 2)
        [Bullet(bullet_x, bullet_y, self.angle + uniform(-0.05, 0.05), power=1, from_player=True, speed=7) for _ in range(1)]

    def check_health(self):
        self.percent_health = round(self.health / self.max_health, 2)

        if self.health <= 0:
            self.die()
        else:
            if self.health < self.max_health:
                if not self.timer_add_health >= 200:
                    self.timer_add_health += 1
                else:
                    self.health += 1
                    self.timer_add_health = 0

    def get_pos(self):
        return (self.x, self.y)

    def die(self):
        if self.is_dead: return
        Player.list.remove(self)
        self.is_dead = True
        del self
