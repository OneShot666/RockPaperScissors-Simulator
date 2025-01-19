# from math import *
from random import randint, choice, shuffle
# from time import *
from entity import Entity
from collections import defaultdict
# import pygame


# ! Parameter is_entity_range is not use yet
class EntityManager:
    def __init__(self, screen_size, nb_entities=100, balanced=True):
        # Booleans
        self.balanced = balanced                                                # If same nb of entity of each kind
        # Parameters
        self.is_smart_entity = False                                            # Entity flee enemy
        self.is_entity_range = False                                            # Entity detection range isn't infinite
        self.is_follow_mouse = False                                            # Type of entity follows mouse position
        self.entity_to_follow_mouse: Entity/str = None                          # What entity follow mouse
        self.is_spawn_with_click = False                                        # If clicking spawns an entity
        self.entity_to_spawn: Entity/str = None                                 # What entity to spawn with click
        # Variables
        self.screen_size = screen_size
        self.EntityNames = ["rock", "paper", "scissors"]
        self.nb_entities = nb_entities
        self.nb_max = 150
        self.Entities = []
        # Functions
        self.create_entities()

    def create_entities(self):                                                  # Create a number of entities
        shuffle(self.EntityNames)                                               # Shuffle entities in case not nb / 3
        third = int(self.nb_entities / 3)

        self.Entities = []
        for i in range(self.nb_entities):
            coords = [randint(0, self.screen_size[0]), randint(0, self.screen_size[1])]
            if self.balanced:
                if i <= third:
                    entity = Entity((i + 1), self.EntityNames[0], coords, smart=self.is_smart_entity)
                elif third < i <= third * 2:
                    entity = Entity((i + 1), self.EntityNames[1], coords, smart=self.is_smart_entity)
                else:
                    entity = Entity((i + 1), self.EntityNames[2], coords, smart=self.is_smart_entity)
            else:
                entity = Entity((i + 1), choice(self.EntityNames), coords, smart=self.is_smart_entity)
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

    def move_entities(self, screen_size, mouse, is_map_borders=False, is_infinity_map=False):  # Move every entity on screen
        screen_size = screen_size if self.is_smart_entity else None
        for entity in self.Entities:
            # Behaviour parameters
            if (self.is_follow_mouse and self.entity_to_follow_mouse is not None and
                    entity.name == self.entity_to_follow_mouse):
                entity.move_to_coords(mouse)                                    # Make entity follow mouse
            else:                                                               # Default movement
                entity.move(self.Entities, screen_size, is_map_borders, is_infinity_map, self.is_entity_range)
            # Borders parameters
            if is_map_borders:
                self.keep_entity_on_screen(entity)
            elif is_infinity_map:
                self.make_entity_move_toroidal(entity)
        # Entity behavior (change target)
        for entity1 in self.Entities:
            for entity2 in self.Entities:
                if (entity1 != entity2 and entity1.does_collide_with_entity(entity2) and
                        entity1.predator_name and entity1.predator_name == entity2.name):
                    # All predators that pursue this entity stops (list below)
                    [entity3.set_target(None) for entity3 in self.Entities if entity3.target == entity1]
                    # All targets that fleeing this entity stops (list below)
                    [entity3.set_predator(None) for entity3 in self.Entities if entity3.predator == entity1]
                    entity1.change_type()                                       # Being convert to predator type
                    entity2.set_target(None)

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
