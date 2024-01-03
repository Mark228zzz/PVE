import pygame
import pygame_gui
import random
from config import Config
from game import Game
from bullet import Bullet
from enemy import Enemy, EnemySquare, EnemyTriangle
from mana import Mana
from particle import Particle
from shop import Shop

def main():
    spawn_timer = 0
    #speed_timer = 0
    spawn_interval = 2.8
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
            random_enemy = random.choice(['Enemy', 'EnemySquare', 'EnemyTriangle'])
            match random_enemy:
                case 'Enemy': [Enemy(random.choice([0, Config.WIDTH-1]), random.randint(0, Config.HEIGHT-1), (187, 0, 0), 9, speed=random.uniform(1.0, 1.6), health=random.randint(1, 4)) for _ in range(random.randint(1, 5))]
                case 'EnemySquare': [EnemySquare(random.choice([0, Config.WIDTH-1]), random.randint(0, Config.HEIGHT-1)) for _ in range(random.randint(1, 2))]
                case 'EnemyTriangle': [EnemyTriangle(random.choice([0, Config.WIDTH-1]), random.randint(0, Config.HEIGHT-1)) for _ in range(1)]
            spawn_timer = 0

        if not Game.paused:
            # Normal game update logic
            Game.player.update()
            for particle in Particle.list:
                particle.update()
            for bullet in Bullet.list:
                bullet.update()
            for mana in Mana.list:
                mana.update()
            for enemy_triangle in EnemyTriangle.list:
                enemy_triangle.update()
            for enemy in Enemy.list:
                enemy.update()
            for enemy_square in EnemySquare.list:
                enemy_square.update()
        else:
            # Draw shop interface
            pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
                    EnemySquare(mouse_pos[0], mouse_pos[1], speed=random.uniform(1.0, 1.6))

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
