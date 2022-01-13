from components.ai import HostileEnemy
from components.fighter import Fighter
from components.consumable import HealingConsumable
from components.inventory import Inventory
from entity import Actor, Item

player = Actor(char="@",
               colour=(255, 255, 255),
               name="Player",
               ai_cls=HostileEnemy,
               fighter=Fighter(hp=30, defense=2, power=5),
               inventory=Inventory(capacity=26))

orc = Actor(char="o",
            colour=(63, 127, 63),
            name="Orc",
            ai_cls=HostileEnemy,
            fighter=Fighter(hp=10, defense=0, power=3),
            inventory=Inventory(capacity=0))
troll = Actor(char="T",
              colour=(255, 127, 0),
              name="Troll",
              ai_cls=HostileEnemy,
              fighter=Fighter(hp=16, defense=1, power=4),
              inventory=Inventory(capacity=0))

health_potion = Item(char="!",
                     colour=(127, 0, 255),
                     name="Health Potion",
                     consumable=HealingConsumable(amount=4))
