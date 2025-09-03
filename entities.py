"""Game entity classes."""

import pygame
from constants import PLAYER_SPEED, ENEMY_SPEED, BLUE, RED, BLACK


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


class Cell:
    """Circular cell that produces units over time.

    A cell has a position and radius describing the circle on the playfield
    as well as an owner (represented by a color) and a numerical value.  The
    value automatically increases every second to model production.  Cells can
    connect to other cells, limited by a capacity derived from their size.
    """

    def __init__(
        self,
        position: tuple[int, int],
        radius: int,
        owner: tuple[int, int, int],
        start_value: int,
    ) -> None:
        self.position = pygame.Vector2(position)
        self.radius = radius
        self.owner = owner
        self.value = start_value
        self.start_value = start_value

        # Track current links to other cells
        self.links: list["Cell"] = []

        # Production handling: increase value every second
        self._production_interval = 1000  # milliseconds
        self._last_production = pygame.time.get_ticks()

        if not pygame.font.get_init():  # ensure fonts are initialised
            pygame.font.init()
        self._font = pygame.font.Font(None, max(12, radius // 2))

    # ------------------------------------------------------------------
    def update(self) -> None:
        """Update the cell's state.

        Currently handles automatic production based on a timer.
        """

        now = pygame.time.get_ticks()
        elapsed = now - self._last_production
        if elapsed >= self._production_interval:
            produced = elapsed // self._production_interval
            self.value += produced
            self._last_production += produced * self._production_interval

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the cell on the given surface."""

        pygame.draw.circle(surface, self.owner, self.position, self.radius)
        text = self._font.render(str(self.value), True, BLACK)
        rect = text.get_rect(center=self.position)
        surface.blit(text, rect)

    # ------------------------------------------------------------------
    def max_links(self) -> int:
        """Return the maximum number of simultaneous links."""

        return max(1, self.radius // 20)

    def has_capacity(self) -> bool:
        """Return True if the cell can create another link."""

        return len(self.links) < self.max_links()

    def capture(self, new_owner: tuple[int, int, int]) -> None:
        """Capture the cell for a new owner and reset its value."""

        self.owner = new_owner
        self.value = self.start_value
        self.links.clear()

    def contains_point(self, point: tuple[int, int]) -> bool:
        """Return True if the given point lies within the cell."""

        dx = point[0] - self.position.x
        dy = point[1] - self.position.y
        return dx * dx + dy * dy <= self.radius * self.radius
