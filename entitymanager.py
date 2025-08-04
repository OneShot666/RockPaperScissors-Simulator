from collections import defaultdict
from random import randint, choice, shuffle
from soundmanager import SoundManager
from entity import Entity
from data import Database


class EntityManager:
    def __init__(self, screen_size, balanced=True, nb_entities=100, entity_speed=1,
            entity_range=100, entity_size=30, db=None):
        # Booleans data
        self.balanced =     balanced                                            # If same nb of entity for each kind
        self.is_sheldon =   False                                               # If using Sheldon rules
        self.is_mutating =  False                                               # If entity can mutate (modify attributs)
        # Variables data
        self.db: Database = db                                                  # Stored to be transferred to entities
        self.mutate_chance = 10                                                 # Percent of chance for an entity to mutate
        self.screen_size: tuple[int, int] | None = screen_size
        self.SoundManager = SoundManager(db)
        self.EntityNames: list[str] = db.ENTITYNAMES
        self.nb_entities = nb_entities
        self.nb_max = 150
        # Entity data
        self.BaseNames: list[str] = db.BASENAMES
        self.entity_speed = entity_speed
        self.entity_range = entity_range
        self.entity_size =  entity_size
        self.max_entity_speed = self.entity_speed * 3
        self.max_entity_range = self.entity_range * 3
        self.max_entity_size =  self.entity_size * 3
        self.Entities: list[Entity] = []
        # Parameters data
        self.is_smart_entity =      False                                       # If all entities flee nearest enemies
        self.is_entity_range =      False                                       # If entity detection range is infinite
        self.is_follow_mouse =      False                                       # Type of entity follows mouse position
        self.is_spawn_with_click =  False                                       # Check that left click spawns an entity
        self.entity_to_follow_mouse: str | None =   None                        # Name of entities that follow the mouse
        self.entity_to_spawn: str | None =          None                        # Name of entities that spawn with click

    def create_entities(self):                                                  # Create a number of entities
        Entities = self.EntityNames if self.is_sheldon else self.BaseNames
        shuffle(Entities)                                                       # Shuffle entities
        portion = len(Entities)

        self.Entities = []
        for i in range(self.nb_entities):
            coords = [randint(0, self.screen_size[0]), randint(0, self.screen_size[1])] # Random coordinates
            name = Entities[i % portion] if self.balanced else choice(Entities)
            entity = Entity((i + 1), name, coords, None, self.entity_speed,
                self.entity_range, self.entity_size, self.is_smart_entity, self.db)
            self.Entities.append(entity)

    def set_nb_entities(self, new_value: int):                                  # Change number of entities
        self.nb_entities = new_value

    def get_number_entities(self) -> defaultdict[str, int]:                     # Return a dict with entities' name and quantity
        NumberEntities = defaultdict(int)
        for entity in self.Entities:
            NumberEntities[entity.name] += 1
        NumberEntities = dict(sorted(dict(NumberEntities).items(),
            key=lambda x: x[1], reverse=True))                                  # Sorted dict by quantity
        return NumberEntities

    def check_spawn_entity(self, simulating: bool, pausing: bool, click: bool, mouse: tuple[int, int]):
        """Spawn selected entity at mouse coords"""
        if simulating and (not pausing and click and self.is_spawn_with_click and self.entity_to_spawn is not None):
            entity = Entity(len(self.Entities) + 1, self.entity_to_spawn,
                list(mouse), smart=self.is_smart_entity, db=self.db)
            self.Entities.append(entity)
            self.SoundManager.play_entity_sound("pop")                          # Play spawn sound

    def increase_nb_entities(self):                                             # Increase number of entities by one
        self.set_nb_entities(min(self.nb_max, self.nb_entities + 1))

    def reduce_nb_entities(self):                                               # Reduce number of entities by one
        self.set_nb_entities(max(0, self.nb_entities - 1))

    def empty_entities(self):
        self.Entities = []

    def increase_speed(self):                                                   # Increase entity speed
        value = min(self.max_entity_speed, self.entity_speed + 0.1)
        self.update_speed(value)

    def reduce_speed(self):                                                     # Reduce entity speed
        value = max(0, self.entity_speed - 0.1)
        self.update_speed(value)

    def increase_range(self):                                                   # Increase entity range
        value = min(self.max_entity_range, self.entity_range + 1)
        self.update_range(value)

    def reduce_range(self):                                                     # Reduce entity range
        value = max(0, self.entity_range - 1)
        self.update_range(value)

    def increase_size(self):                                                   # Increase entity size
        value = min(self.max_entity_size, self.entity_size + 1)
        self.update_size(value)

    def reduce_size(self):                                                     # Reduce entity size
        value = max(1, self.entity_size - 1)
        self.update_size(value)

    def increase_mutate_chance(self):                                           # Increase mutate chance
        self.mutate_chance = min(100, self.mutate_chance + 1)

    def reduce_mutate_chance(self):                                             # Reduce mutate chance
        self.mutate_chance = max(0, self.mutate_chance - 1)

    def update_speed(self, new_speed: int):
        diff = new_speed - self.entity_speed
        if diff != 0:
            self.entity_speed = new_speed
            for entity in self.Entities:
                entity.speed += diff                                            # Modify velocity

    def update_range(self, new_range: int):
        diff = new_range - self.entity_range
        if diff != 0:
            self.entity_range = new_range
            for entity in self.Entities:
                entity.range += diff                                            # Modify sight

    def update_size(self, new_size: int):
        diff = new_size - self.entity_size
        if diff != 0:
            self.entity_size = new_size
            for entity in self.Entities:
                entity.size += diff                                             # Modify body
                entity.image = entity.get_image()                               # Also change image size

    def update_smartness(self):
        if self.is_smart_entity:
            for entity in self.Entities:                                        # Make all entities smart
                entity.become_smart()
        else:
            for entity in self.Entities:                                        # Make all entities dumb
                entity.become_dumb()

    def move_entities(self, screen_size, mouse, is_map_borders=False, is_infinity_map=False):  # Move every entity on screen
        screen_size = screen_size if self.is_smart_entity else None

        Mutated = []
        for entity in self.Entities:                                            # Behaviour parameters
            if self.is_mutating:
                have_mutated = self.mutate_entity(entity)
                if have_mutated:
                    Mutated.append(have_mutated)

            if self.is_follow_mouse and entity.name == self.entity_to_follow_mouse:
                entity.move_to_coords(mouse)                                    # Make entity follow mouse
            else:                                                               # Default movement
                entity.move(self.Entities, screen_size, is_map_borders, is_infinity_map, self.is_entity_range)

            if is_map_borders:                                                  # Borders parameters
                self.keep_entity_on_screen(entity)
            elif is_infinity_map:
                self.make_entity_move_toroidal(entity)

        # Entity behavior (change target)
        for entity1 in self.Entities:
            for entity2 in self.Entities:                                       # If entity beaten
                if (entity1 != entity2 and entity1.does_collide_with_entity(entity2) and
                        entity1.Predators and entity2.name in entity1.Predators):
                    # All predators that pursue this entity stop (list below)
                    [entity3.set_target(None) for entity3 in self.Entities if entity3.target == entity1]
                    # All targets that fleeing this entity stops (list below)
                    [entity3.set_predator(None) for entity3 in self.Entities if entity3.predator == entity1]
                    self.SoundManager.play_entity_sound(entity1.name)           # Play entity's beaten sound
                    entity1.change_type(entity2.name)                           # Being convert to predator type
                    entity2.set_target(None)

        return Mutated

    def mutate_entity(self, entity: Entity) -> Entity | None:                   # Lot of hazard in mutations
        chance = randint(0, 100_000)                                            # '100_000' : purposely high
        if chance <= self.mutate_chance:
            mutation = randint(0, 100)
            sense = choice([1, -1])

            if mutation < 30:                                                   # 30% chance to mutate speed
                entity.speed += sense * 0.25
            elif 30 <= mutation < 60:                                           # 30% chance to mutate range
                entity.range += sense * 3
            elif 60 <= mutation < 90:                                           # 30% chance to mutate size
                entity.size += sense * 2
                entity.size = max(entity.size, 1)                               # '1' : Avoid become invisible
            elif 90 <= mutation < 99:                                           # 9% chance to mutate smart
                if entity.is_smart:
                    entity.become_dumb()
                else:
                    entity.become_smart()
            else:                                                               # 1% to randomly change type
                name = choice(self.EntityNames if self.is_sheldon else self.BaseNames)
                if name != entity.name:
                    entity.change_type(name)
            return entity
        return None

    def keep_entity_on_screen(self, entity: Entity):                            # If entity out of screen
        if entity.coords[0] < 0:
            entity.coords[0] = 0
        elif entity.coords[0] > self.screen_size[0] - entity.size:
            entity.coords[0] = self.screen_size[0] - entity.size

        if entity.coords[1] < 0:
            entity.coords[1] = 0
        elif entity.coords[1] > self.screen_size[1] - entity.size:
            entity.coords[1] = self.screen_size[1] - entity.size

    def make_entity_move_toroidal(self, entity: Entity):                        # Move entity on the other side of screen
        if entity.coords[0] + entity.size <= 0:
            entity.coords[0] = self.screen_size[0] - entity.size
        elif entity.coords[0] >= self.screen_size[0]:
            entity.coords[0] = 0

        if entity.coords[1] + entity.size <= 0:
            entity.coords[1] = self.screen_size[1] - entity.size
        elif entity.coords[1] >= self.screen_size[1]:
            entity.coords[1] = 0
