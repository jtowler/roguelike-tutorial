from components.ai import HostileEnemy
from components.fighter import Fighter
from components import consumable, equippable
from components.equipment import Equipment
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

player = Actor(char="@",
               colour=(255, 255, 255),
               name="Player",
               ai_cls=HostileEnemy,
               equipment=Equipment(),
               fighter=Fighter(hp=30, base_defense=1, base_power=2),
               inventory=Inventory(capacity=26),
               level=Level(level_up_base=200))

orc = Actor(char="o",
            colour=(63, 127, 63),
            name="Orc",
            ai_cls=HostileEnemy,
            equipment=Equipment(),
            fighter=Fighter(hp=10, base_defense=0, base_power=3),
            inventory=Inventory(capacity=0),
            level=Level(xp_given=35))

troll = Actor(char="T",
              colour=(255, 127, 0),
              name="Troll",
              ai_cls=HostileEnemy,
              equipment=Equipment(),
              fighter=Fighter(hp=16, base_defense=1, base_power=4),
              inventory=Inventory(capacity=0),
              level=Level(xp_given=100))

health_potion = Item(char="!",
                     colour=(127, 0, 255),
                     name="Health Potion",
                     consumable=consumable.HealingConsumable(amount=4))

lightning_scroll = Item(char="~",
                        colour=(255, 255, 0),
                        name="Lightning Scroll",
                        consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5))

confusion_scroll = Item(char="~",
                        colour=(207, 63, 255),
                        name="Confusion Scroll",
                        consumable=consumable.ConfusionConsumable(number_of_turns=10))

fireball_scroll = Item(char="~",
                       colour=(255, 0, 0),
                       name="Fireball Scroll",
                       consumable=consumable.FireballDamageConsumable(damage=12, radius=3))

dagger = Item(char="/", colour=(0, 191, 255), name="Dagger", equippable=equippable.Dagger())
sword = Item(char="/", colour=(0, 191, 255), name="Sword", equippable=equippable.Sword())
leather_armour = Item(char="[", colour=(139, 69, 19), name="Leather Armour", equippable=equippable.LeatherArmour())
chain_mail = Item(char="[", colour=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail())
