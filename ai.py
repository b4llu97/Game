"""Simple AI helper functions."""

from entities import Enemy, Player


def chase(enemy: Enemy, target: Player) -> None:
    """Move the enemy one step towards the target player."""
    if enemy.rect.x < target.rect.x:
        enemy.rect.x += enemy.speed
    elif enemy.rect.x > target.rect.x:
        enemy.rect.x -= enemy.speed
    if enemy.rect.y < target.rect.y:
        enemy.rect.y += enemy.speed
    elif enemy.rect.y > target.rect.y:
        enemy.rect.y -= enemy.speed
