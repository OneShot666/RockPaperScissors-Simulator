# from math import *
from random import randint, choice, shuffle
# from time import *
from collections import defaultdict
from soundmanager import SoundManager
from entity import Entity
from data import Database
# import pygame


class EntityManager:
    def __init__(self, screen_size, balanced=True, nb_entities=100, entity_speed=1, entity_range=100, entity_size=30):
        # Booleans data
        self.balanced = balanced                                                # If same nb of entity for each kind
        self.is_mutating = False                                                # If entity can mutate (modify attributs)
        # Variables data
        self.mutate_chance = 10                                                 # Percent of chance for an entity to mutate
        self.screen_size = screen_size
        self.SoundManager = SoundManager()
        self.EntityNames = list(Database().ENTITYCOLORS.keys())
        self.nb_entities = nb_entities
        self.nb_max = 150
        # Entity data
        self.entity_speed = entity_speed
        self.entity_range = entity_range
        self.entity_size =  entity_size
        self.max_entity_speed = self.entity_speed * 3
        self.max_entity_range = self.entity_range * 3
        self.max_entity_size =  self.entity_size * 3
        self.Entities = []
        # Parameters data
        self.is_smart_entity =      False                                       # Entity flee enemy
        self.is_entity_range =      False                                       # Entity detection range isn't infinite
        self.is_follow_mouse =      False                                       # Type of entity follows mouse position
        self.is_spawn_with_click =  False                                       # If clicking spawns an entity
        self.entity_to_follow_mouse: Entity/str =   None                        # What entity follow mouse
        self.entity_to_spawn: Entity/str =          None                        # What entity to spawn with click
        # Based function
        self.create_entities()

    def create_entities(self):                                                  # Create a number of entities
        shuffle(self.EntityNames)                                               # Shuffle entities in case not nb / 3
        third = int(self.nb_entities / 3)

        self.Entities = []
        for i in range(self.nb_entities):
            coords = [randint(0, self.screen_size[0]), randint(0, self.screen_size[1])]
            if self.balanced:
                if i <= third:
                    name = self.EntityNames[0]
                elif third < i <= third * 2:
                    name = self.EntityNames[1]
                else:
                    name = self.EntityNames[2]
            else:                                                               # Random entity
                name = choice(self.EntityNames)
            entity = Entity((i + 1), name, coords, None, self.entity_speed,
                self.entity_range, self.entity_size, self.is_smart_entity)
            self.Entities.append(entity)

    def change_balance(self):                                                   # Change if nb of types are equal
        self.balanced = not self.balanced

    def set_nb_entities(self, new_value):                                       # Change number of entities
        self.nb_entities = new_value

    def increase_nb_entities(self):                                             # Increase number of entities by one
        self.nb_entities = min(self.nb_max, self.nb_entities + 1)

    def reduce_nb_entities(self):                                               # Reduce number of entities by one
        self.nb_entities = max(0, self.nb_entities - 1)

    def empty_entities(self):
        self.Entities = []

    def increase_speed(self):                                                   # Increase entity speed
        self.entity_speed = min(self.max_entity_speed, self.entity_speed + 1)

    def reduce_speed(self):                                                     # Reduce entity speed
        self.entity_speed = max(0, self.entity_speed - 1)

    def increase_range(self):                                                   # Increase entity range
        self.entity_range = min(self.max_entity_range, self.entity_range + 1)

    def reduce_range(self):                                                     # Reduce entity range
        self.entity_range = max(0, self.entity_range - 1)

    def increase_size(self):                                                   # Increase entity size
        self.entity_size = min(self.max_entity_size, self.entity_size + 1)

    def reduce_size(self):                                                     # Reduce entity size
        self.entity_size = max(1, self.entity_size - 1)

    def increase_mutate_chance(self):                                           # Increase mutate chance
        self.mutate_chance = min(100, self.mutate_chance + 1)

    def reduce_mutate_chance(self):                                             # Reduce mutate chance
        self.mutate_chance = max(0, self.mutate_chance - 1)

    def get_number_entities(self):                                              # Return a dict with entities' name and quantity
        NumberEntities = defaultdict(int)
        for entity in self.Entities:
            NumberEntities[entity.name] += 1
        NumberEntities = dict(sorted(dict(NumberEntities).items(),
                                     key=lambda x: x[1], reverse=True))         # Sorted dict by quantity
        return NumberEntities

    def check_spawn_entity(self, simulating, pausing, click, mouse):            # Spawn selected entity at mouse coords
        if simulating and (not pausing and click and self.is_spawn_with_click and self.entity_to_spawn is not None):
            entity = Entity(len(self.Entities) + 1, self.entity_to_spawn, list(mouse), smart=self.is_smart_entity)
            self.Entities.append(entity)
            self.SoundManager.play_entity_sound("pop")                          # Play spawn sound

    def move_entities(self, screen_size, mouse, is_map_borders=False, is_infinity_map=False):  # Move every entity on screen
        screen_size = screen_size if self.is_smart_entity else None

        Mutated = []
        for entity in self.Entities:                                            # Behaviour parameters
            if self.is_mutating:
                have_mutated = self.mutate_entity(entity)
                if have_mutated:
                    Mutated.append(have_mutated)

            if (self.is_follow_mouse and self.entity_to_follow_mouse is not None and
                    entity.name == self.entity_to_follow_mouse):
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
                        entity1.predator_name and entity1.predator_name == entity2.name):
                    # All predators that pursue this entity stop (list below)
                    [entity3.set_target(None) for entity3 in self.Entities if entity3.target == entity1]
                    # All targets that fleeing this entity stops (list below)
                    [entity3.set_predator(None) for entity3 in self.Entities if entity3.predator == entity1]
                    self.SoundManager.play_entity_sound(entity1.name)           # Play entity's beaten sound
                    entity1.change_type()                                       # Being convert to predator type
                    entity2.set_target(None)

        return Mutated

    def mutate_entity(self, entity):                                            # Lot of hazard in mutations
        chance = randint(0, 100_000)                                              # '100_000' : purposely high
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
                name = choice(self.EntityNames)
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

    def make_entities_smart(self):                                              # Make all entities smart
        for entity in self.Entities:
            entity.become_smart()

    def make_entities_dumb(self):                                               # Make all entities dumb
        for entity in self.Entities:
            entity.become_dumb()
