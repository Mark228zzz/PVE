import pygame
import pygame_gui
from random import randint, uniform, choice
from config import Config
from game import Game
from bullet import Bullet
from enemy import EnemyCircle, EnemySquare, EnemyTriangle, EnemyLeaping
from mana import Mana
from particle import Particle
from shop import Shop

def main():
    spawn_timer = 0
    #speed_timer = 0
    spawn_interval = 2
    ui_manager = pygame_gui.UIManager((Config.WIDTH, Config.HEIGHT), 'theme_game.json')
    time_delta = 0

    shop = Shop(ui_manager, Game.player)
    while Game.running:
        #speed_timer += 1
        #if speed_timer == 1:
        #    first_pos = Game.player.get_pos()
        #elif speed_timer == Config.FPS:
        #    second_pos = Game.player.get_pos()

        #    dx, dy = second_pos[0] - first_pos[0], second_pos[1] - first_pos[1]
        #    distance = (dx**2 + dy**2)**0.5
        #    print(f'{distance} p/s') # pixels per second

        #    speed_timer = 0

        #if Game.status != 'playing': continue

        time_delta = Game.clock.tick(Config.FPS) / 1000.0
        Game.window.fill((0, 0, 0))

        # Spawn enemies
        spawn_timer += 1 / Config.FPS
        if spawn_timer >= spawn_interval:
            random_enemy = choice(['EnemyCircle', 'EnemySquare', 'EnemyTriangle', 'EnemyLeaping'])
            match random_enemy:
                case 'EnemyCircle': [EnemyCircle(x=choice([0, Config.WIDTH-1]), y=randint(0, Config.HEIGHT-1), color=(127, 0, 0), radius=10.0, health=randint(1, 3),speed=uniform(0.9, 1.5)) for _ in range(randint(3, 5))]
                case 'EnemySquare': [EnemySquare(x=choice([0, Config.WIDTH-1]), y=randint(0, Config.HEIGHT-1), color=(255, 128, 128), width=24, height=23, health=randint(3, 7),speed=uniform(0.7, 1.3)) for _ in range(randint(1, 3))]
                case 'EnemyTriangle': [EnemyTriangle(x=choice([0, Config.WIDTH-1]), y=randint(0, Config.HEIGHT-1), color=(210, 200, 0), size=32, summon_rate=2.0, health=randint(10, 15),speed=uniform(0.65, 1.0)) for _ in range(1)]
                case 'EnemyLeaping': [EnemyLeaping(x=choice([0, Config.WIDTH-1]), y=randint(0, Config.HEIGHT-1), color=(10, 182, 10), radius=15, push_strength=randint(10, 18), health=randint(22, 30),speed=uniform(0.4, 0.8)) for _ in range(1)]
            spawn_timer = 0

        if not Game.paused:
            # Normal game update logic
            for particle in Particle.list:
                particle.update()
            for bullet in Bullet.list:
                bullet.update()
            for mana in Mana.list:
                mana.update()
            for enemy_triangle in EnemyTriangle.list:
                enemy_triangle.update()
            for enemy_circle in EnemyCircle.list:
                enemy_circle.update()
            for enemy_square in EnemySquare.list:
                enemy_square.update()
            for enemy_leaping in EnemyLeaping.list:
                enemy_leaping.update()
            Game.player.update()
        else:
            # Draw shop interface
            pass

        for event in pygame.event.get():
            from player import Player
            if event.type == pygame.QUIT or not Player.list:
                Game.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    Game.paused = not Game.paused
                    if Game.paused:
                        shop.show()
                    else:
                        shop.hide()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not Game.paused:
                    Game.player.shoot()
                elif event.button == 3 and not Game.paused:
                    mouse_pos = pygame.mouse.get_pos()
                    #EnemySquare(mouse_pos[0], mouse_pos[1], speed=uniform(1.0, 1.6))

            # shop run
            if Game.paused:
                shop.manager.process_events(event)
                shop.handle_events(event)

        if Game.paused:
            shop.manager.update(time_delta)
            shop.manager.draw_ui(Game.window)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
