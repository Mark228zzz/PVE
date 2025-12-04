import pygame

pygame.init()

class Config:
    info_object = pygame.display.Info()
    WIDTH, HEIGHT = info_object.current_w, info_object.current_h  # Full resolution
    FPS = 60
