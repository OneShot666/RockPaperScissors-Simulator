import math
from math import *
from random import *
from time import *
import pygame


class Entity:                                                                   # Common class for entities in the game
    def __init__(self, name, coords=None, image=None, speed=1, smart=False):
        self.is_smart = smart
        self.id = None                                                          # !! Not use yet
        self.name = "paper" if name is None or name == "" else name
        self.size = 30
        self.speed = speed
        self.coords = [0, 0] if coords is None else coords
        # ! Change code and use rect.center for get_distance
        self.image = self.get_image(image)
        self.predator_name = self.get_predator_name()
        self.predator: Entity = None
        self.target_name = self.get_target_name()
        self.target: Entity = None

    def __repr__(self):
        return (f"{self.name.capitalize()} [{int(self.coords[0])}, {int(self.coords[0])}] "
                f"(target: {self.target_name.capitalize()})")

    def get_image(self, image=None):                                            # Set image based on name
        if image is None:
            image = pygame.image.load(f"images/{self.name}.png").convert_alpha()
        return pygame.transform.scale(image, (self.size, self.size))

    def get_predator_name(self):                                                # Get name of predator based on own name
        if self.name == "rock":
            return "paper"
        elif self.name == "scissors":
            return "rock"
        elif self.name == "paper":
            return "scissors"
        else:
            return None

    def get_target_name(self):                                                  # Get name of target based on own name
        if self.name == "rock":
            return "scissors"
        elif self.name == "scissors":
            return "paper"
        elif self.name == "paper":
            return "rock"
        else:
            return None

    def get_distance(self, point1, point2, screen_size=None):                   # Calculate distance between two points
        screen_size = None if not self.is_smart else screen_size
        dx = min(abs(point2[0] - point1[0]), screen_size[0] - abs(point2[0] - point1[0])) \
            if screen_size else point2[0] - point1[0]
        dy = min(abs(point2[1] - point1[1]), screen_size[1] - abs(point2[1] - point1[1])) \
            if screen_size else point2[1] - point1[1]
        return math.sqrt(dx ** 2 + dy ** 2)

    def set_id(self, id_value):
        self.id = id_value

    def is_mouse_over(self, mouse_pos):
        image_rect = self.image.get_rect(topleft=self.coords)
        return image_rect.collidepoint(mouse_pos)

    def become_smart(self):
        self.is_smart = True

    def become_dumb(self):
        self.is_smart = False

    def does_collide_with_entity(self, entity):
        return self.get_distance(self.coords, entity.coords) <= self.size

    def set_target(self, new_target):
        self.target = new_target

    def set_predator(self, new_predator):
        self.predator = new_predator

    def look_for_closest_target(self, Entities, screen_size=None):              # Search for the closest target
        distance_min = math.inf
        target = None

        for entity in Entities:
            if entity.name == self.target_name:
                distance = self.get_distance(self.coords, entity.coords, screen_size)
                if distance < distance_min:
                    distance_min = distance
                    target = entity

        if target != self:
            self.set_target(target)

    def look_for_closest_predator(self, Entities, screen_size=None):            # Search for the closest predator
        distance_min = math.inf
        predator = None

        for entity in Entities:
            if entity.name == self.predator_name:
                distance = self.get_distance(self.coords, entity.coords, screen_size)
                if distance < distance_min:
                    distance_min = distance
                    predator = entity

        if predator != self:
            self.set_predator(predator)

    # Look for shorter way to target (using map borders and inf map to its advantage)
    # [later] Will separate in two groups to take targets in sandwich -> make EntityManager class ?
    # [later] Group will form a line to stuck target in a corner when map has borders
    def move_smart(self, Entities, screen_size=None, is_map_borders=False, is_infinity_map=False):
        self.look_for_closest_target(Entities)
        if self.target and self.target.coords[0] is not None:                   # Target still exists
            if is_map_borders:
                pass
            elif is_infinity_map:
                pass
            else:
                self.move_to_coords(self.target.coords, screen_size)
        else:
            if is_map_borders:
                pass
            elif is_infinity_map:
                pass
            else:
                self.flee_predator(Entities)

    def flee_predator(self, Entities, screen_size=None):
        if self.predator is None:
            self.look_for_closest_predator(Entities)

        if self.predator:
            self.move_to_reverse_coords(self.predator.coords, screen_size)

    def move(self, Entities, screen_size=None):                                 # Move manager of entity
        if self.is_smart:
            self.move_smart(Entities, screen_size)
        elif self.target and self.target.coords[0] is not None:
            self.move_to_coords(self.target.coords, screen_size)
        else:                                                                   # Losers run randomly faster (x2)
            self.move_randomly()

    def move_to_coords(self, coords, screen_size=None):                         # Go to point
        distance = self.get_distance(self.coords, coords, screen_size)
        dir_x = coords[0] - self.coords[0]
        dir_y = coords[1] - self.coords[1]

        if distance >= self.size:
            self.coords[0] += (dir_x / distance) * self.speed
            self.coords[1] += (dir_y / distance) * self.speed

    # ... Testing
    def move_to_reverse_coords(self, coords, screen_size=None):                 # Go to opposite point compare to entity coords
        distance = self.get_distance(self.coords, coords, screen_size)
        dir_x = coords[0] - self.coords[0]
        dir_y = coords[1] - self.coords[1]

        if distance >= self.size:
            self.coords[0] -= (dir_x / distance) * self.speed
            self.coords[1] -= (dir_y / distance) * self.speed

    def move_randomly(self, boost_mult=2):
        self.coords[0] += randint(-1, 1) * self.speed * boost_mult
        self.coords[1] += randint(-1, 1) * self.speed * boost_mult

    def change_type(self):                                                      # Change type of entity (when beaten)
        self.name = self.get_predator_name()
        self.image = self.get_image()
        self.predator_name = self.get_predator_name()
        self.target_name = self.get_target_name()
        self.target = None

    def die(self):                                                              # kill itself
        del self
