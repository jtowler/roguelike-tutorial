from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

import tcod

import colour

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(entity.name for entity in game_map.entities if entity.x == x and entity.y == y)

    return names.capitalize()


def render_bar(console: Console,
               current_value: int,
               maximum_value: int,
               total_width: int,
               y: int = 45,
               prefix: str = "HP",
               full_colour: Tuple[int, int, int] = colour.hp_bar_filled,
               empty_colour: Tuple[int, int, int] = colour.hp_bar_empty) -> None:

    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=0, y=y, width=20, height=1, ch=1, bg=empty_colour)

    if bar_width > 0:
        console.draw_rect(x=0, y=y, width=bar_width, height=1, ch=1, bg=full_colour)

    console.print(x=1, y=y, string=f"{prefix}: {current_value}/{maximum_value}", fg=colour.bar_text)


def render_dungeon_level(console: Console, dungeon_level: int, location: Tuple[int, int]) -> None:
    """Render the level the player is currently on, at the given location"""
    x, y = location
    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")


def render_names_at_mouse_location(console: Console, x: int, y: int, engine: Engine) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(x=mouse_x, y=mouse_y, game_map=engine.game_map)
    console.print(x=x, y=y, string=names_at_mouse_location)
