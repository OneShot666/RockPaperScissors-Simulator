from math import inf, sqrt
from typing import Optional
from random import randint, choice
from timermanager import TimerManager
import pygame


class Entity:                                                                   # Common class for entities in the game
    def __init__(self, id_value, name, coords=None, image=None, speed=1,
            range_value=100, size=30, smart=False, db=None):
        # Attribute data
        self.is_smart = smart
        self.id: int = id_value                                                 # Use to distinguish entities
        self.name: str = db.ENTITYNAMES[1] if db and (name is None or name == "") else name.lower()
        self.coords = [0, 0] if coords is None else coords
        # Display data
        self.speed = speed                                                      # Speed on screen
        self.range = range_value                                                # Perception of other entities
        self.size = size                                                        # Image's size
        self.EntityImages: dict[str, pygame.Surface] = db.ENTITYIMAGES
        self.color: tuple[int] = db.ENTITYCOLORS[self.name]
        self.image = self.get_image(image)
        # Behaviour data
        self.Predatory: dict[str, list[str]] = db.FOODCHAIN
        self.Predators = self.get_predators()                                   # List of name
        self.predator: Entity = None
        self.Targets = self.get_targets()                                       # //
        self.target: Entity = None
        self.timer_mutation = TimerManager(1.5)                                 # Time while showing notif to mutation
        self.behaviour = "Nothing"                                              # What entity currently doing

    # [Unused] Print infos about entity
    def __repr__(self):
        return (f"{self.name.capitalize()} [{int(self.coords[0])}, {int(self.coords[1])}] "
                f"(target: {self.Targets}{f'({self.target.id})' if self.target else ''}, "
                f"predator: {self.Predators}{f'({self.predator.id})' if self.predator else ''}), {self.behaviour}")

    def get_image(self, image: Optional[pygame.Surface] = None) -> pygame.Surface:  # Set image based on name
        if image is None:
            image = self.EntityImages[self.name]
        return pygame.transform.scale(image, (self.size, self.size))

    def get_targets(self) -> list[str]:                                         # Get name of targets based on own name
        return self.Predatory.get(self.name, [])

    def get_predators(self) -> list[str]:                                       # Get name of predators based on own name
        return [e for e, targets in self.Predatory.items() if self.name in targets]

    def get_distance(self, point1, point2, screen_size=None, is_infinity_map=False) -> float:
        """ Calculate distance between two points """
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        if self.is_smart and screen_size and is_infinity_map:
            w, h = screen_size
            dx = (dx + w / 2) % w - w / 2
            dy = (dy + h / 2) % h - h / 2
        return sqrt(dx ** 2 + dy ** 2)

    def get_vectors_and_distance(self, target_coords, screen_size, is_infinity_map=False) -> [float, float, float]:
        """ Similar to get_distance() but only for target and also give directions in result """
        dx = target_coords[0] - self.coords[0]
        dy = target_coords[1] - self.coords[1]
        if self.is_smart and screen_size and is_infinity_map:
            w, h = screen_size
            dx = (dx + w / 2) % w - w / 2
            dy = (dy + h / 2) % h - h / 2
        return dx, dy, sqrt(dx ** 2 + dy ** 2)

    # Only use for toroidal map to flee predator
    def get_farthest_point(self, screen_size: list[int]):                  # Calculate the farthest point on screen (for self)
        if self.predator.coords[0] is not None:
            coords = self.predator.coords
            screen_size = [1, 1] if screen_size is None else screen_size
            width, height = screen_size
            return (coords[0] + width / 2) % width, (coords[1] + height / 2) % height
        return None

    def is_mouse_over(self, mouse_pos: tuple[int, int]) -> bool:                # Check if mouse is hover self
        image_rect = self.image.get_rect(topleft=self.coords)
        return image_rect.collidepoint(mouse_pos)

    def become_smart(self):
        self.is_smart = True
        self.range *= 1.05                                                      # Smart entity see 5% farther

    def become_dumb(self):
        self.is_smart = False
        self.range *= 100 / 105

    def does_collide_with_entity(self, entity: "Entity") -> bool:               # Check if self collide with an entity
        return self.get_distance(self.coords, entity.coords) <= self.size

    def set_target(self, new_target: Optional["Entity"]):                       # Change value of target
        self.target = new_target

    def set_predator(self, new_predator: Optional["Entity"]):                   # Change value of predator
        self.predator = new_predator

    def look_for_closest_target(self, Entities, screen_size=None, is_range=False, is_infinity_map=False):
        """ Search for the closest target """
        PotentialTargets = [e for e in Entities if e.name in self.Targets and e != self]

        if not PotentialTargets:
            self.set_target(None)
            return

        target = min(PotentialTargets, key=lambda e: self.get_distance(self.coords, e.coords, screen_size, is_infinity_map))
        distance = self.get_distance(self.coords, target.coords, screen_size, is_infinity_map)

        if is_range and distance > self.range: self.set_target(None)
        else: self.set_target(target)

    def look_for_closest_predator(self, Entities, screen_size=None, is_range=False, is_infinity_map=False):
        """ Search for the closest predator """
        PotentialPredators = [e for e in Entities if e.name in self.Predators and e != self]

        if not PotentialPredators:
            self.set_predator(None)
            return

        predator = min(PotentialPredators, key=lambda e: self.get_distance(self.coords, e.coords, screen_size, is_infinity_map))
        distance = self.get_distance(self.coords, predator.coords, screen_size, is_infinity_map)

        if is_range and distance > self.range: self.set_predator(None)
        else: self.set_predator(predator)

    def chase_target(self, screen_size: list[int], is_infinity_map=False):
        """ Move to closest target if there is any """
        self.move_to_coords(self.target.coords, screen_size, is_infinity_map)
        self.behaviour = f"Chasing target ({self.target.id})"

    def flee_predator(self, screen_size: Optional[list[int]], is_infinity_map=False):
        """ Move to opposite direction of closest predator """
        self.move_to_reverse_coords(self.predator.coords, screen_size, is_infinity_map)
        self.behaviour = f"Fleeing predator ({self.predator.id})"

    # Look for shorter way to target (using map borders and inf map to its advantage)
    # [later] Will separate in two groups to take targets in sandwich
    # [later] Group will form a line to stuck target in a corner if map has borders
    def move_smart(self, Entities, screen_size: Optional[list[int]], is_infinity_map=False):
        if self.predator:
            self.flee_predator(screen_size, is_infinity_map)
        elif self.target:
            self.chase_target(screen_size, is_infinity_map)
        else:
            self.move_randomly(2)                                               # Move faster if smart (why ? -> because)

    # Manager movements of entity
    def move(self, Entities, screen_size=None, is_infinity_map=False, is_range=False):
        self.look_for_closest_target(Entities, screen_size, is_range, is_infinity_map)
        self.look_for_closest_predator(Entities, screen_size, is_range, is_infinity_map)

        if self.is_smart:
            self.move_smart(Entities, screen_size, is_infinity_map)
        elif self.target:
            self.chase_target(screen_size, is_infinity_map)
        else:                                                                   # If even here, no target was found
            self.move_randomly()

    def move_to_coords(self, coords, screen_size=None, is_infinity_map=False):    # Go to point
        dx, dy, distance = self.get_vectors_and_distance(coords, screen_size, is_infinity_map)

        if distance >= self.size:
            self.coords[0] += (dx / distance) * self.speed
            self.coords[1] += (dy / distance) * self.speed

    # Go to opposite direction compare to coords
    def move_to_reverse_coords(self, coords, screen_size=None, is_infinity_map=False):
        dx, dy, distance = self.get_vectors_and_distance(coords, screen_size, is_infinity_map)

        if distance >= self.size:
            self.coords[0] -= (dx / distance) * self.speed
            self.coords[1] -= (dy / distance) * self.speed

    def move_randomly(self, boost_mult=1):
        self.coords[0] += randint(-1, 1) * self.speed * boost_mult
        self.coords[1] += randint(-1, 1) * self.speed * boost_mult
        self.behaviour = "Moving randomly"

    def change_type(self, name: Optional[str] = None):                          # Change type of entity (when beaten)
        self.name = name if name else choice(self.get_predators())              # Before predators are updated
        self.image = self.get_image()
        self.Predators = self.get_predators()
        self.Targets = self.get_targets()
        self.set_predator(None)
        self.set_target(None)

    # [Unused] Delete itself
    def die(self):
        del self
