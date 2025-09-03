"""Main game loop and logic."""

import pygame
from constants import SCREEN_SIZE, FPS, BLACK
from entities import Player, Enemy
from ai import chase
from levels import load_level


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Game")
        self.clock = pygame.time.Clock()

        self.player = Player((SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 50))
        self.enemies = pygame.sprite.Group()
        level_data = load_level(1)
        for pos in level_data["enemies"]:
            self.enemies.add(Enemy(pos))

        self.all_sprites = pygame.sprite.Group(self.player, *self.enemies)
        self.running = True

    def run(self):
        """Run the main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            self.player.update(keys)
            for enemy in self.enemies:
                chase(enemy, self.player)

            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
