"""Level definitions for the game."""


def load_level(level: int) -> dict:
    """Return a simple level description.

    Currently returns positions for enemy spawn points.
    """
    if level == 1:
        return {"enemies": [(100, 100), (200, 150), (300, 200)]}
    return {"enemies": []}
