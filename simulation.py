# -*- coding: cp1252 -*-
# from math import *
# from random import *
# from time import *
from pathlib import Path
from copy import deepcopy
from datetime import date, datetime
from PIL import Image, ImageSequence
from dataclasses import dataclass, field, asdict
from graphic import Graphic
from data import Database
import matplotlib.pyplot as plt
import matplotlib
import pygame
import shutil
import glob
import json
import re
import os


@dataclass                                                                      # All attributes to display are here
class Simulation:
    # Simulation data (id, duration of simulation, number of turns and some parameters)
    id: int = 1
    duration: int = 0
    nb_turn: int = 0
    is_smart: bool =    field(default=False)
    is_range: bool =    field(default=False)
    is_borders: bool =  field(default=False)
    is_toroidal: bool = field(default=False)
    is_sheldon: bool =  field(default=False)
    # Other data
    is_saved =      None
    is_loaded =     None
    path_save =     None
    path_sim =      None
    EntityQuantity: dict = field(default_factory=dict)
    Speeds: list =  field(default_factory=list)
    Ranges: list =  field(default_factory=list)
    Sizes: list =   field(default_factory=list)
    Screenshots =   None                                                        # Attributes without type aren't saved
    Graphics =      None

    def __post_init__(self):                                                    # Setting of attributes that aren't display
        matplotlib.use("Agg")                                                   # Use non-interactive back-end
        db = Database()
        # Save data
        self.is_saved =     False
        self.is_loaded =    False
        self.save_format = db.SAVE_FORMAT
        # Path data
        self.today = date.today().strftime(db.DATE_FORMAT)
        self.path_save = Path(db.PATH_SAVE) / self.today
        self.path_sim = Path(self.path_save) / f"save {self.id}"
        # Simulation data
        self.BaseNames =    db.BASENAMES
        self.EntityNames =  db.ENTITYNAMES
        if self.EntityQuantity is None or self.EntityQuantity == {}:
            Entities = self.EntityNames if self.is_sheldon else self.BaseNames
            self.EntityQuantity = {name: [] for name in Entities}               # Quantity of entity every second
        if self.Speeds is None:
            self.Speeds = []
        if self.Ranges is None:
            self.Ranges = []
        if self.Sizes is None:
            self.Sizes =  []
        # Screenshot data
        self.screen_format = db.SCREEN_FORMAT
        self.Screenshots = []
        # Graphic data
        self.graphic_format = db.IMAGE_FORMAT
        self.GraphicNames = db.GRAPHICS_NAMES
        self.GraphicTypes = db.GRAPHICS_TYPES
        self.OptionNames =  list(db.OPTIONCOLORS.keys())                        # Options for graphic n°2
        self.current_options = deepcopy(self.OptionNames)
        self.Graphics = []
        # Basic function
        self.create_graphics()

    def create_graphics(self):                                                  # Create graphics
        self.Graphics.append(Graphic(self.GraphicNames[0], self.GraphicTypes[2], True)) # True : about entity
        self.Graphics.append(Graphic(self.GraphicNames[1], self.GraphicTypes[2]))
        self.Graphics.append(Graphic(self.GraphicNames[2], self.GraphicTypes[0], True))
        self.Graphics.append(Graphic(self.GraphicNames[3], self.GraphicTypes[0]))
        self.Graphics.append(Graphic(self.GraphicNames[4], self.GraphicTypes[3], True))
        self.update_graphics()

    def set_path_sim(self, path_sim):
        self.path_save = path_sim.parent
        self.path_sim = path_sim

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def get_dict(self):                                                         # Return a json version of this instance
        return asdict(self)

    def get_id_bonus(self):                                                     # Based on names of other saves
        max_id = 0
        if Path(self.path_save).exists():                                       # If save file exists
            for save in Path(self.path_save).iterdir():
                if save.is_dir():
                    Numbers = re.findall(r'\d+', save.name)                     # Find numbers among name
                    if Numbers:
                        num = max(map(int, Numbers))                            # Get max number from name
                        max_id = max(max_id, num)
        return max_id

    def get_nb_saves_today(self):                                               # Based on number of save files
        if Path(self.path_save).exists():                                       # If save file exists
            return sum(1 for f in Path(self.path_save).iterdir() if f.is_dir())
        return 0

    def get_image_from_graphic(self, graphic):
        graphic.update_image(self.EntityQuantity, self.Speeds, self.Ranges, self.Sizes)
        return graphic.image

    def get_next_screenshot_name(self, nb_turn=1):
        s = "s" if nb_turn > 1 else ""
        return f"sim {self.id} (x{nb_turn} turn{s})" + self.screen_format

    def get_next_save_name(self):
        return f"data {self.id}" + self.save_format

    def get_next_graphic_name(self, nb):
        return f"graphic {nb}" + self.graphic_format

    def add_entity(self, name, value):                                          # Add an entity name and a value
        if name in self.EntityQuantity:
            self.EntityQuantity[name].append(value)

    def add_range(self, range_value):                                           # Add average range of entities
        self.Ranges.append(range_value)

    def add_speed(self, speed):                                                 # Add average speed of entities
        self.Speeds.append(speed)

    def add_size(self, size):                                                   # Add average size of entities
        self.Sizes.append(size)

    def update_id(self, bonus=1, was_saved=True):                               # Id either depends on nb saves or names
        if was_saved:
            self.id = self.get_nb_saves_today() + bonus
        else:
            self.id += self.get_id_bonus()
        self.path_sim = Path(self.path_save) / f"save {self.id}"

    def update_graphics(self):                                                  # Update the graphics with current datas
        if not self.is_loaded:                                                  # If graphics images don't already exist
            for graphic in self.Graphics:
                graphic.update_image(self.EntityQuantity, self.Speeds, self.Ranges, self.Sizes)

    def take_screenshot(self, screen):                                          # Take full screenshot but don't save it
        self.Screenshots.append(screen.copy())
        self.nb_turn = len(self.Screenshots)

    def save_screenshots(self):                                                 # Saves all taken screenshots into a gif
        if len(self.Screenshots) > 0:
            Images = [pygame.image.tostring(img, "RGB") for img in self.Screenshots]
            Images = [Image.frombytes("RGB", img.get_size(), data)
                for img, data in zip(self.Screenshots, Images)]
            pause = 4                                                           # Pause of 1s / 250ms (see for duration)
            Images.extend([Images[-1]] * pause)                                 # Add copies of last image to mark pause

            file_name = self.get_next_screenshot_name(len(self.Screenshots))
            Images[0].save(Path(self.path_sim) / file_name, save_all=True,
                append_images=Images[1:], duration=250, loop=0)

    @staticmethod
    def load_screenshots(path):
        return [pygame.image.frombuffer(frame.convert("RGBA").tobytes(), frame.size, "RGBA").copy()
            for frame in ImageSequence.Iterator(Image.open(path))]              # copy() : Pillow use same memory

    def save_simulation(self):                                                  # Create text file to save data
        file_name = self.get_next_save_name()
        with open(Path(self.path_sim) / file_name, 'w') as file:                # Create game data file
            hour = datetime.now().strftime("%H:%M")
            simulation = {"name": f"Simulation {self.id}", "saved at": hour,
                "date": self.today, "simulation": self.get_dict()}
            json.dump(simulation, file, indent=4)
            file.close()

    def save_graphics(self):                                                     # Only save graphics images
        self.update_graphics()
        for i, graphic in enumerate(self.Graphics):
            name = Path(self.path_sim) / self.get_next_graphic_name(i + 1)
            graphic.save_image(name)

    def create_save(self):
        self.path_save.mkdir(exist_ok=True)                                     # Create directories if doesn't exist
        self.path_sim.mkdir(exist_ok=True)
        self.save_screenshots()
        self.save_simulation()
        self.save_graphics()
        self.is_saved = True

    def load_save(self, save_dir_name):
        yield                                                                   # Take a break
        self.set_path_sim(save_dir_name)                                        # Update path of save
        yield                                                                   # Take a break
        Files = [_ for _ in os.listdir(save_dir_name) if _.endswith(self.graphic_format)]
        yield                                                                   # Take a break
        Images = [pygame.image.load(Path(save_dir_name) / _) for _ in Files]    # Only load images
        if Images:
            yield                                                               # Take a break
            for i, graphic in enumerate(self.Graphics):
                yield                                                           # Take a break
                graphic.image = Images[i]
        yield                                                                   # Take a break
        sim_name = next(iter(glob.glob(f"{save_dir_name}/*{self.screen_format}")), None)
        if sim_name:                                                            # If screenshots file exists
            yield                                                                   # Take a break
            self.Screenshots = self.load_screenshots(sim_name)                  # Only load gif image frames
            self.nb_turn = len(self.Screenshots)
        yield                                                                   # Take a break
        self.is_saved = True
        self.is_loaded = True
        yield                                                                   # Take a break

    def delete_save(self):
        shutil.rmtree(self.path_sim, onerror=self.force_delete)                 # Remove the entire save directory
        self.is_saved = False
        self.is_loaded = False

    @staticmethod
    def force_delete(function, path, _):
        Path(path).chmod(0o777)                                                 # Change permission
        function(path)
