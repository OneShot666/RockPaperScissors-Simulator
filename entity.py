from math import inf, sqrt
from random import randint, choice
# from time import *
from timermanager import TimerManager
from data import Database
import pygame


class Entity:                                                                   # Common class for entities in the game
    def __init__(self, id_value, name, coords=None, image=None, speed=1, range_value=100, size=30, smart=False):
        db = Database()
        # Attribute data
        self.is_smart = smart
        self.id = id_value                                                      # Use to distinguish entities
        self.name = db.ENTITYNAMES[1] if name is None or name == "" else name.lower()
        self.coords = [0, 0] if coords is None else coords
        # Display data
        self.speed = speed                                                      # Speed on screen
        self.range = range_value                                                # Perception of other entities
        self.size = size                                                        # Image's size
        self.EntityImages = db.ENTITYIMAGES
        self.color = db.ENTITYCOLORS[self.name]
        self.image = self.get_image(image)
        # Behaviour data
        self.Predatory = db.FOODCHAIN
        self.Predators = self.get_predators()                                   # List of name
        self.predator: Entity = None
        self.Targets = self.get_targets()                                       # //
        self.target: Entity = None
        self.timer_mutation = TimerManager(1.5)                                 # Time while showing notif to mutation
        self.behaviour = "Nothing"                                              # What entity currently doing

    def __repr__(self):                                                         # Not use yet
        return (f"{self.name.capitalize()} [{int(self.coords[0])}, {int(self.coords[0])}] "
            f"(target: {self.Targets}, predator: {self.Predators}), {self.behaviour}")

    def get_image(self, image=None):                                            # Set image based on name
        if image is None:
            image = self.EntityImages[self.name]
        return pygame.transform.scale(image, (self.size, self.size))

    def get_targets(self):                                                      # Get name of targets based on own name
        return self.Predatory.get(self.name, [])

    def get_predators(self):                                                    # Get name of predators based on own name
        return [e for e, targets in self.Predatory.items() if self.name in targets]

    # ? Change code and use rect.center for get_distance
    def get_distance(self, point1, point2, screen_size=None):                   # Calculate distance between two points
        screen_size = None if not self.is_smart else screen_size
        dx = min(abs(point2[0] - point1[0]), screen_size[0] - abs(point2[0] - point1[0])) \
            if screen_size else point2[0] - point1[0]
        dy = min(abs(point2[1] - point1[1]), screen_size[1] - abs(point2[1] - point1[1])) \
            if screen_size else point2[1] - point1[1]
        return sqrt(dx ** 2 + dy ** 2)

    # ? Same as get_distance (if so, make get_distance dumb, maybe ?)
    @staticmethod
    def get_toroidal_distance(point1, point2, screen_size):                     # Like get_distance in toroidal map
        dx = abs(point1[0] - point2[0])
        dy = abs(point1[1] - point2[1])
        return sqrt(dx ** 2 + dy ** 2) if screen_size is None else (
            sqrt(min(dx, screen_size[0] - dx) ** 2 + min(dy, screen_size[1] - dy) ** 2))

    # Only use for toroidal map to flee predator
    def get_farthest_point(self, screen_size):                                  # Calculate the farthest point on screen (for self)
        if self.predator.coords[0] is not None:
            coords = self.predator.coords
            screen_size = [1, 1] if screen_size is None else screen_size
            width, height = screen_size
            return (coords[0] + width / 2) % width, (coords[1] + height / 2) % height
        return None

    def is_mouse_over(self, mouse_pos):                                         # Check if mouse is hover self
        image_rect = self.image.get_rect(topleft=self.coords)
        return image_rect.collidepoint(mouse_pos)

    def become_smart(self):
        self.is_smart = True
        self.range *= 1.05                                                      # Smart entity see 5% farther

    def become_dumb(self):
        self.is_smart = False
        self.range *= 100 / 105

    def does_collide_with_entity(self, entity):                                 # Check if self collide with an entity
        return self.get_distance(self.coords, entity.coords) <= self.size

    def set_target(self, new_target):                                           # Change value of target
        self.target = new_target

    def set_predator(self, new_predator):                                       # Change value of predator
        self.predator = new_predator

    def look_for_closest_target(self, Entities, screen_size=None, is_range=False):  # Search for the closest target
        target = min((entity for entity in Entities if entity.name in self.Targets),
            key=lambda e: self.get_distance(self.coords, e.coords, screen_size), default=None)

        distance = self.get_distance(self.coords, target.coords, screen_size) \
            if target else inf

        if is_range:
            if distance <= self.range:
                self.set_target(target)
            else:
                self.set_target(None)
        elif target != self:
            self.set_target(target)

    def look_for_closest_predator(self, Entities, screen_size=None, is_range=False):    # Search for the closest predator
        predator = min((entity for entity in Entities if entity.name in self.Predators),
            key=lambda e: self.get_distance(self.coords, e.coords, screen_size), default=None)

        distance = self.get_distance(self.coords, predator.coords, screen_size) \
            if predator else inf

        if is_range:
            if distance <= self.range:
                self.set_predator(predator)
            else:
                self.set_predator(None)
        elif predator != self:
            self.set_predator(predator)

    # Move to closest target if there is any
    def chase_target(self, screen_size, is_map_borders=False, is_infinity_map=False):
        self.move_to_coords(self.target.coords, screen_size, is_map_borders, is_infinity_map)
        self.behaviour = f"Chasing target ({self.target.id})"

    # Move to opposite direction of closest predator
    def flee_predator(self, screen_size=None, is_map_borders=False, is_infinity_map=False):
        self.move_to_reverse_coords(self.predator.coords, screen_size, is_map_borders, is_infinity_map)
        self.behaviour = f"Fleeing predator ({self.predator.id})"

    # Look for shorter way to target (using map borders and inf map to its advantage)
    # [later] Will separate in two groups to take targets in sandwich -> make EntityManager class ?
    # [later] Group will form a line to stuck target in a corner when map has borders
    def move_smart(self, Entities, screen_size=None, is_map_borders=False, is_infinity_map=False):
        testing = False
        if testing:
            print("Moving start :", end=" ")                                    # !!!
        if self.target and self.target.coords[0] is not None:                   # At least one target
            if testing:
                print("Chase target condition", end=" ")                       # !!!
            if is_map_borders:                                                  # ! Not opti
                self.chase_target(screen_size, is_map_borders, is_infinity_map)
                if testing:
                    print("1", end=", ")                                        # !!!
            elif is_infinity_map:                                               # ! Not opti
                self.chase_target(screen_size, is_map_borders, is_infinity_map)
                if testing:
                    print("2", end=", ")                                        # !!!
            else:
                self.chase_target(screen_size, is_map_borders, is_infinity_map)
                if testing:
                    print("3", end=", ")                                        # !!!
        elif self.predator and self.predator.coords[0] is not None:             # At least one predator
            if testing:
                print("Flee predator condition ", end=" ")                      # !!!
            if is_map_borders:                                                  # ! Not opti
                self.flee_predator(screen_size, is_map_borders, is_infinity_map)
                if testing:
                    print("1", end=", ")                                        # !!!
            elif is_infinity_map:
                coords = self.get_farthest_point(screen_size)
                self.move_to_coords(coords, screen_size, is_map_borders, is_infinity_map)
                self.behaviour = f"Fleeing predator ({self.predator.id})"
                if testing:
                    print("2", end=", ")                                        # !!!
            else:
                self.flee_predator(screen_size, is_map_borders, is_infinity_map)
                if testing:
                    print("3", end=", ")                                        # !!!
        else:
            self.move_randomly(3)                                               # Move faster if smart (why ? -> because)
        if testing:
            print("end")                                                        # !!!

    # Manager movements of entity
    def move(self, Entities, screen_size=None, is_map_borders=False, is_infinity_map=False, is_range=False):
        if self.target is None:
            self.look_for_closest_target(Entities, screen_size, is_range)
        if self.predator is None:
            self.look_for_closest_predator(Entities, screen_size, is_range)

        if self.is_smart:
            self.move_smart(Entities, screen_size, is_map_borders, is_infinity_map)
        elif self.target is None:                                               # If even here, no target was found
            self.move_randomly()
        else:
            self.chase_target(screen_size, is_map_borders, is_infinity_map)

    def move_to_coords(self, coords, screen_size=None, is_map_borders=False, is_infinity_map=False):    # Go to point
        if self.is_smart and is_infinity_map:
            distance = self.get_toroidal_distance(self.coords, coords, screen_size)
        else:
            distance = self.get_distance(self.coords, coords, screen_size)
        dir_x = coords[0] - self.coords[0]
        dir_y = coords[1] - self.coords[1]

        if distance >= self.size:
            self.coords[0] += (dir_x / distance) * self.speed
            self.coords[1] += (dir_y / distance) * self.speed

    # Go to opposite direction compare to coords
    def move_to_reverse_coords(self, coords, screen_size=None, is_map_borders=False, is_infinity_map=False):
        if self.is_smart and is_infinity_map:
            distance = self.get_toroidal_distance(self.coords, coords, screen_size)
        else:
            distance = self.get_distance(self.coords, coords, screen_size)
        dir_x = coords[0] - self.coords[0]
        dir_y = coords[1] - self.coords[1]

        if distance >= self.size:
            self.coords[0] -= (dir_x / distance) * self.speed
            self.coords[1] -= (dir_y / distance) * self.speed

    def move_randomly(self, boost_mult=2):
        self.coords[0] += randint(-1, 1) * self.speed * boost_mult
        self.coords[1] += randint(-1, 1) * self.speed * boost_mult
        self.behaviour = "Moving randomly"

    def change_type(self, name=None):                                           # Change type of entity (when beaten)
        self.name = name if name else choice(self.get_predators())              # Before predators are updated
        self.image = self.get_image()
        self.Predators = self.get_predators()
        self.Targets = self.get_targets()
        self.set_predator(None)
        self.set_target(None)

    def die(self):                                                              # Kill itself
        del self
