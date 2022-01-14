from __future__ import annotations

import lzma
import pickle
from typing import TYPE_CHECKING

from tcod.console import Console

import colour
import exceptions
from message_log import MessageLog
import render_functions
from tcod.map import compute_fov

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8
        )

        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)

        render_functions.render_bar(console=console,
                                    current_value=self.player.fighter.hp,
                                    maximum_value=self.player.fighter.max_hp,
                                    total_width=20)

        render_functions.render_dungeon_level(console,
                                              dungeon_level=self.game_world.current_floor,
                                              location=(0, 47))

        render_functions.render_bar(console=console,
                                    current_value=self.player.level.current_xp,
                                    maximum_value=self.player.level.experience_to_next_level,
                                    total_width=20,
                                    y=49,
                                    prefix="XP",
                                    full_colour=colour.xp_bar_filled)

        render_functions.render_names_at_mouse_location(console, x=21, y=44, engine=self)

    def save_as(self, filename: str) -> None:
        """Save this engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)
