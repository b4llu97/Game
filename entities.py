"""Game entity classes."""

import pygame
from constants import PLAYER_SPEED, ENEMY_SPEED, BLUE, RED


class Entity(pygame.sprite.Sprite):
    """Base class for all moving objects in the game."""

    def __init__(self, position: tuple[int, int], size: tuple[int, int], color: tuple[int, int, int]):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=position)


class Player(Entity):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position, (50, 50), BLUE)
        self.speed = PLAYER_SPEED

    def update(self, keys: pygame.key.ScancodeWrapper):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed


class Enemy(Entity):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position, (40, 40), RED)
        self.speed = ENEMY_SPEED

    def update(self):
        self.rect.y += self.speed
