import pygame
import pygame_gui
import random
from config import Config
from game import Game
from bullet import Bullet
from enemy import Enemy, EnemySquare
from mana import Mana
from particle import Particle
from shop import Shop
from start_menu import StartMenu

def main():
    spawn_timer = 0
    spawn_interval = 0.5
    ui_manager = pygame_gui.UIManager((Config.WIDTH, Config.HEIGHT), 'theme_game.json')
    time_delta = 0

    start_menu = StartMenu(Game.window, ui_manager)
    shop = Shop(ui_manager, Game.player)
    while Game.running:
        time_delta = Game.clock.tick(Config.FPS) / 1000.0
        Game.window.fill((0, 0, 0))

        # Spawn enemies
        spawn_timer += 1 / Config.FPS
        if spawn_timer >= spawn_interval:
            [Enemy(random.choice([0, Config.WIDTH-1]), random.randint(0, Config.HEIGHT-1), (187, 0, 0), 10, speed=random.uniform(1.0, 1.6), health=random.randint(1, 4)) for _ in range(random.randint(1, 5))]
            spawn_timer = 0

        if Game.status == 'start_menu':
            for event in pygame.event.get():
                ui_manager.process_events(event)
                result = start_menu.handle_events(event)
                if result == 'start':
                    print('start game')
                elif result == 'quit':
                    print('quit game')
                    Game.running = False
                    break
        elif not Game.paused:
            # Normal game update logic
            Game.player.update()
            for bullet in Bullet.list:
                bullet.update()
            for enemy in Enemy.list:
                enemy.update()
            for mana in Mana.list:
                mana.update()
            for particle in Particle.list:
                particle.update()
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
