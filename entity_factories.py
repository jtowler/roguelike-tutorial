from entity import Entity

player = Entity(char="@", colour=(255, 255, 255), name="Player", blocks_movement=True)

orc = Entity(char="o", colour=(63, 127, 63), name="Orc", blocks_movement=True)
troll = Entity(char="T", colour=(255, 127, 0), name="Troll", blocks_movement=True)