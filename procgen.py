from __future__ import annotations

import math
import random
from itertools import product
from typing import Tuple, Iterator, List, TYPE_CHECKING, Dict, Optional
import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

max_items_by_floor = [
    (1, 1),
    (4, 2)
]
max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5)
]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25), (entity_factories.sword, 5)],
    6: [(entity_factories.fireball_scroll, 25), (entity_factories.chain_mail, 15)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
}


def get_max_value_for_floor(max_value_by_floor: List[Tuple[int, int]], floor: int) -> int:
    current_value = 0
    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value
    return current_value


def get_entities_at_random(weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
                           number_of_entities: int,
                           floor: int) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]
                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    return random.choices(entities, weights=entity_weighted_chance_values, k=number_of_entities)


class Room:
    x1: int
    y1: int
    x2: int
    y2: int

    def center(self) -> Tuple[int, int]:
        raise NotImplementedError()

    def place_player_coordinate(self) -> Tuple[int, int]:
        raise NotImplementedError()

    def intersects(self, other: Room) -> bool:
        """Return true if this room overlaps with another"""
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1


class RectangularRoom(Room):
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def place_player_coordinate(self) -> Tuple[int, int]:
        return self.center

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index"""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)


class CircularRoom(Room):
    def __init__(self, x: int, y: int, radius: int):
        self.x = x
        self.y = y
        self.x1 = x - radius
        self.x2 = x + radius
        self.y1 = y - radius
        self.y2 = y + radius
        self.radius = radius

    def place_player_coordinate(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def center(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def inner(self) -> List[Tuple[int, int]]:
        """Return the inner area of this room as a 2D array index"""
        diameter = range(-self.radius, self.radius + 1)
        return [(x + self.x, y + self.y) for x, y in product(diameter, repeat=2)
                if math.sqrt(x ** 2 + y ** 2) < self.radius]


class RingRoom(CircularRoom):
    def __init__(self, x: int, y: int, radius: int, inner_radius: Optional[int] = None):
        super().__init__(x, y, radius)
        if inner_radius is None:
            self.inner_radius = radius // 2
        else:
            self.inner_radius = inner_radius
        self.inner_circle = CircularRoom(x, y, self.inner_radius)

    @property
    def inner(self) -> List[Tuple[int, int]]:
        """Return the inner area of this room as a 2D array index"""
        return [tile for tile in super().inner if tile not in self.inner_circle.inner]

    def place_player_coordinate(self) -> Tuple[int, int]:
        return self.x, self.y - self.inner_radius - (self.radius - self.inner_radius) // 2


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int) -> None:
    number_of_monsters = random.randint(0, get_max_value_for_floor(max_monsters_by_floor, floor_number))
    number_of_items = random.randint(0, get_max_value_for_floor(max_items_by_floor, floor_number))

    monsters: List[Entity] = get_entities_at_random(enemy_chances, number_of_monsters, floor_number)
    items: List[Entity] = get_entities_at_random(item_chances, number_of_items, floor_number)

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)


def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points"""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:
        # Move horiz then vert
        corner_x, corner_y = x2, y1
    else:
        corner_x, corner_y = x1, y2

    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(max_rooms: int, room_min_size: int, room_max_size: int, map_width: int,
                     map_height: int, engine: Engine) -> GameMap:
    """Generate a new dungeon map"""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue

        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            player.place(*new_room.center, dungeon)
        else:
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor
            center_of_last_room = new_room.center

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

        rooms.append(new_room)

    return dungeon


def test_dungeon(max_rooms: int, room_min_size: int, room_max_size: int, map_width: int,
                 map_height: int, engine: Engine) -> GameMap:
    """Generate a new dungeon map"""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[Room] = []

    center_of_last_room = (0, 0)

    for r in range(max_rooms):

        room_type_check = random.random()

        if room_type_check < 0.6:

            room_width = random.randint(room_min_size, room_max_size)
            room_height = random.randint(room_min_size, room_max_size)
            x = random.randint(0, dungeon.width - room_width - 1)
            y = random.randint(0, dungeon.height - room_height - 1)
            new_room = RectangularRoom(x, y, room_width, room_height)

        elif room_type_check < 0.9:
            radius = random.randint(room_min_size // 2, room_max_size // 2)
            x = random.randint(radius, dungeon.width - radius)
            y = random.randint(radius, dungeon.height - radius)

            new_room = CircularRoom(x, y, radius)
        else:
            radius = random.randint(room_min_size // 2, room_max_size // 2)
            inner_radius = random.randint(1, radius)
            x = random.randint(radius, dungeon.width - radius)
            y = random.randint(radius, dungeon.height - radius)

            new_room = RingRoom(x, y, radius, inner_radius=inner_radius)

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue

        if isinstance(new_room, RectangularRoom):
            dungeon.tiles[new_room.inner] = tile_types.floor
        else:
            for xy in new_room.inner:
                dungeon.tiles[xy] = tile_types.floor

        if len(rooms) == 0:
            player.place(*new_room.place_player_coordinate(), dungeon)
        else:
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor
            center_of_last_room = new_room.center

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

        rooms.append(new_room)

    return dungeon
