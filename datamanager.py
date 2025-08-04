from pathlib import Path
from humanize import precisedelta
from datetime import date, datetime
from timermanager import TimerManager
from simulation import Simulation
from graphic import Graphic
from data import Database
import matplotlib.pyplot as plt
import matplotlib
import statistics
import pygame
import shutil
import json
import os
import re


class DataManager:
    def __init__(self, db):
        matplotlib.use("Agg")                                                   # Use non-interactive back-end
        # Boolean data
        self.was_today_saves =  False                                           # If saves from today already exists
        self.is_loading =       False                                           # When loading saves
        self.is_auto_play =     False                                           # Play gif of current simulation
        self.is_auto_save =     False                                           # Save at the end of the simulation
        self.is_sim_saved =     False                                           # If the last simulation was saved
        self.is_on_saves =      False                                           # If on saves or today's sims
        # Path data
        self.db: Database = db
        self.today = date.today().strftime(db.DATE_FORMAT)
        self.path_log: Path =           db.PATH_LOG
        self.path_save: Path =          db.PATH_SAVE
        self.path_image: Path =         db.PATH_IMAGE
        self.path_icon_graphic: Path =  db.PATH_ICON_GRAPHIC
        self.anim_timer = TimerManager(0.5)                                     # A timer for gif animation
        # Graphics data
        self.Graphics: list[Graphic] = []
        self.current_graphic: int = None                                        # Index of graphic
        self.current_graphic_image: pygame.Surface = None
        # Menu data
        self.Tabs = ["Simulations", "Graphics", "Saves"]                        # Today, Before
        self.current_tab =  2                                                   # Index of tab to display
        self.current_sim =  0                                                   # Index of sim to display
        self.current_save = 0                                                   # Index of save to display
        self.current_turn = 0                                                   # Index of turn to display
        # Simulation data
        self.sim: Simulation = None                                             # Last simulation created
        self.nb_sim = 0                                                         # Number of launched simulations
        self.Simulations: list[Simulation] = []                                 # Simulations launch today
        self.nb_saved_logs = 0
        self.log_format: str = db.LOG_FORMAT
        # Save data
        self.save: Simulation = None                                            # Last save loaded
        self.nb_save = 0                                                        # Number of loaded saves
        self.Saves: list[Simulation] = []                                       # Saved data
        self.loader = None
        self.load_timer = TimerManager(0.01)                                    # A timer for loading saves
        self.save_format: str = db.SAVE_FORMAT
        self.image_size: int = db.FONTS[2].get_height()
        bin_image = pygame.image.load(Path(self.path_image / "bin.png")).convert_alpha()    # Delete icon for saves
        self.bin_image = pygame.transform.scale(bin_image, (self.image_size, self.image_size))
        self.EntityNames: list[str] = db.ENTITYNAMES

    def get_nb_file(self, path: Path, format_type: str):
        full_path = Path(path) / self.today
        if Path(full_path).exists():
            return len([_ for _ in Path(full_path).iterdir() if _.suffix == format_type])
        return 0

    def get_next_log_name(self):
        self.nb_saved_logs = self.get_nb_file(self.path_log, self.log_format)
        return f"log {self.nb_saved_logs + 1}" + self.log_format

    def get_current_sim(self) -> Simulation:
        return self.Simulations[self.current_sim]

    def get_current_save(self) -> Simulation:
        return self.Saves[self.current_save]["simulation"]

    def get_nb_turns(self):                                                     # Return nb of turn of current sim
        return self.get_current_sim().nb_turn if len(self.Simulations) > 0 else (
            self.get_current_save().nb_turn) if self.is_on_saves and len(self.Saves) > 0 else 0

    def set_option(self, value: str):                                           # Change option of graphics with options
        graphic = self.Graphics[self.current_graphic]
        if value in graphic.Options:
            graphic.Options.remove(value)
        else:
            graphic.Options.append(value)
        self.update_all_graphics()

    def set_save(self, index: int):                                             # Change the current save loaded
        if len(self.Saves) > index:
            if self.save == self.Saves[index]:                                  # Can unselect current save
                self.current_save = 0
                self.save = None
                self.is_on_saves = False
            else:
                self.current_turn = 0
                self.current_save = index
                self.save = self.Saves[index]
                self.is_on_saves = True
            self.update_all_graphics()

    def is_current_sim_saved(self):
        if len(self.Simulations) > 0:
            return self.get_current_sim().is_saved
        return False

    @staticmethod
    def resize_image(screensize: tuple[int, int], image: pygame.Surface, width: float = None, height: float = None):
        """Keep image proportional size"""
        new_size = [image.get_height(), image.get_width()]
        if width and height:
            new_size = (screensize[0] * width, screensize[1] * height)
        elif width:
            new_size[0] = screensize[0] * width
            new_size[1] = new_size[0] / image.get_width() * image.get_height()
        elif height:
            new_size[1] = screensize[1] * height
            new_size[0] = new_size[1] / image.get_height() * image.get_width()

        image = pygame.transform.scale(image, new_size)
        return image

    def previous_tab(self):                                                     # Change current tab of save screen
        self.current_tab = (self.current_tab - 1) % len(self.Tabs)

    def next_tab(self):                                                         # Change current tab of save screen
        self.current_tab = (self.current_tab + 1) % len(self.Tabs)

    def previous_sim(self):                                                     # Change current sim/save to display
        if self.is_on_saves and self.nb_save > 0:
            self.current_save = (self.current_save - 1) % self.nb_save
            self.current_turn = 0
        elif self.nb_sim > 0:
            self.current_sim = (self.current_sim - 1) % self.nb_sim
            self.current_turn = 0
            self.is_sim_saved = self.is_current_sim_saved()

    def next_sim(self):                                                         # Change current sim/save to display
        if self.is_on_saves and self.nb_save > 0:
            self.current_save = (self.current_save + 1) % self.nb_save
            self.current_turn = 0
        elif self.nb_sim > 0:
            self.current_sim = (self.current_sim + 1) % self.nb_sim
            self.current_turn = 0
            self.is_sim_saved = self.is_current_sim_saved()

    def previous_turn(self):                                                    # Change current turn of current sim
        if self.nb_save > 0 if self.is_on_saves else self.nb_sim > 0:
            self.current_turn -= 1
            if self.current_turn < 0:
                self.current_turn = self.get_nb_turns() - 1

    def next_turn(self):                                                        # Change current turn of current sim
        if self.nb_save > 0 if self.is_on_saves else self.nb_sim > 0:
            self.current_turn += 1
            if self.current_turn > self.get_nb_turns() - 1:
                self.current_turn = 0

    def add_simulation(self, duration: float | int, smart=False, is_range=False,
            borders=False, toroidal=False, sheldon=False):                      # Save last sim
        self.sim = Simulation(self.nb_sim + 1, duration, 0, smart, is_range,
            borders, toroidal, sheldon, self.db)
        self.sim.update_id(was_saved=True)                                      # Update id
        self.Graphics = self.sim.Graphics
        self.is_on_saves = False
        self.Simulations.append(self.sim)
        if len(self.Simulations) > 1:                                           # Also update current simulation index
            self.current_sim += 1
        self.nb_sim = len(self.Simulations)

    def update_simulation(self, sim_id: int, duration: float | int, smart=False, is_range=False,
            borders=False, toroidal=False, sheldon=False):
        for i, save in enumerate(self.Simulations):
            if save.id == sim_id:
                self.Simulations[i].duration = duration
                self.Simulations[i].is_smart = smart
                self.Simulations[i].is_range = is_range
                self.Simulations[i].is_borders = borders
                self.Simulations[i].is_toroidal = toroidal
                self.Simulations[i].is_sheldon = sheldon
                return
        self.add_simulation(duration, smart, is_range, borders, toroidal, sheldon)  # If sim wasn't added

    def add_entity_value(self, name: str, value: int):
        if len(self.Simulations) > 0:
            self.get_current_sim().add_entity(name, value)

    def add_speed(self, speed: float | int):
        if len(self.Simulations) > 0:
            self.get_current_sim().add_speed(speed)

    def add_range(self, range_value: float | int):
        if len(self.Simulations) > 0:
            self.get_current_sim().add_range(range_value)

    def add_size(self, size: float | int):
        if len(self.Simulations) > 0:
            self.get_current_sim().add_size(size)

    def take_screenshot(self, screen: pygame.Surface):
        if len(self.Simulations) > 0:
            self.get_current_sim().take_screenshot(screen)

    def update_all_graphics(self):
        if self.is_on_saves and len(self.Saves) > 0:
            self.get_current_save().update_graphics()
            self.Graphics = self.get_current_save().Graphics
        elif len(self.Simulations) > 0:
            self.get_current_sim().update_graphics()
            self.Graphics = self.get_current_sim().Graphics

    def save_log(self, error: Exception = None):                                # Automatically save when quiting program
        dir_name = Path(self.path_log) / self.today
        Path(dir_name).mkdir(exist_ok=True)

        file_name = self.get_next_log_name()
        with open(Path(dir_name) / file_name, 'w') as file:                     # Create game data file
            name = file_name.replace(self.log_format, "").capitalize()
            hour = datetime.now().strftime("%H:%M")
            file.write(f"# {name}\n")
            file.write(f"###### created {self.today} at {hour}\n\n")
            file.write(f"***\n")
            nb = self.nb_sim if self.nb_sim > 1 else "no"
            s = "s" if self.nb_sim > 1 else ""
            file.write(f"### There was {nb} simulation{s} launched today.\n\n")

            if len(self.Simulations) > 0:
                file.write(f"##### Simulations : \n\n")
                WinRate = {name: 0 for name in self.EntityNames}

                for sim in self.Simulations:
                    s = "s" if sim.nb_turn > 1 else ""
                    duration = precisedelta(sim.duration)                       # Display text with precise units
                    file.write(f"The simulation n°{sim.id} last {sim.nb_turn} turn{s} and {duration}.\\\n")
                    file.write(f"Were entities smart :     {'Yes' if sim.is_smart else 'No'}\\\n")
                    file.write(f"Did map had borders :     {'Yes' if sim.is_borders else 'No'}\\\n")
                    file.write(f"Did map was toroidal :    {'Yes' if sim.is_toroidal else 'No'}\\\n")
                    file.write(f"Were entities had range : {'Yes' if sim.is_range else 'No'}\\\n")
                    file.write(f"With Sheldon rules :      {'Yes' if sim.is_sheldon else 'No'}\\\n")
                    if sim.nb_turn > 0:
                        file.write(f"Average speed was **{round(statistics.mean(sim.Speeds), 3)}** pixels/sec\\\n")
                        file.write(f"Average range was **{round(statistics.mean(sim.Ranges), 3)}** pixels\\\n")
                        file.write(f"Average size was **{round(statistics.mean(sim.Sizes), 3)}** pixels\\\n")
                        last = {name: sim.EntityQuantity[name][-1] for name in sim.EntityQuantity.keys()}
                        winner = max(last, key=last.get)
                        WinRate[winner] += 1
                        nb_entity = sum(last.values())
                        s = "ies" if nb_entity > 1 else "y"
                        file.write(f"The entity '{winner}' won : x{last[winner]} / {nb_entity} entit{s}.\n\n")
                    else:
                        file.write(f"The simulation didn't last a single turn or there was a problem with the data collecting.\n\n")
                file.write("\n")

                file.write("##### Entity winrate : \n")
                for entity, nb_win in WinRate.items():
                    file.write(f"- {entity} : {round(nb_win / self.nb_sim * 100, 2)}%\n")
                file.write("\n")

            if error:
                file.write("The program was stop prematurely for the following reason : \\\n")
                file.write(f"{type(error).__name__} : {error}\n")

            file.close()

    def save_current_sim(self, current_time: float):
        if len(self.Simulations) > 0:
            self.get_current_sim().create_save()
            if len(self.Saves) > 0:                                             # If saves were loaded before
                self.begin_loading(current_time)

    def save_all(self, current_time: float):                                           # Save all collected data
        for sim in self.Simulations:
            sim.create_save()
        if len(self.Saves) > 0:                                                 # If saves were loaded before
            self.begin_loading(current_time)

    def display_graphic(self, graphic):                                         # Create graphic with current sim datas
        if self.is_on_saves and len(self.Saves) > 0:
            self.current_graphic_image = self.get_current_save().get_image_from_graphic(graphic)
        elif len(self.Simulations) > 0:
            self.current_graphic_image = self.get_current_sim().get_image_from_graphic(graphic)

    def update_graphic(self, screensize, graphic=None, size=0.6):
        if graphic is None:
            graphic = self.Graphics[self.current_graphic]
        self.display_graphic(graphic)
        if self.current_graphic_image:
            self.current_graphic_image = self.resize_image(screensize,
                self.current_graphic_image, height=size)

    def check_display_next_turn(self, current_time: float):
        if self.is_auto_play:                                                   # Show each turn for 0.5 second
            if self.anim_timer.check_loop_end(current_time) > 0:                # After the loop end
                self.next_turn()

    def begin_loading(self, current_time: float):                               # Prepare program to load saves
        self.is_loading = True
        self.Saves.clear()
        self.loader = self.progressive_load()                                   # Asynchrone function to load saves
        self.load_timer.start(current_time)

    def progressive_load(self):                                                 # Asynchrone function (avoid freezes)
        for directory in Path(self.path_save).iterdir():                        # In every dir in saves/
            if self.today == directory.name:
                self.was_today_saves = True
            for save_dir in Path(directory).iterdir():                          # For every day
                for filename in Path(save_dir).iterdir():                       # In all simulations launch that day
                    if filename.suffix == self.save_format:
                        result = self.load_save(filename)
                        yield from result

    def load_save(self, name: Path):                                            # Load a save based on its name
        yield                                                                   # Take a break in case it's too long
        with open(name, "r", encoding="utf-8") as f:
            yield                                                               # Take another break
            result = json.load(f)
            yield                                                               # And another break
        result["simulation"] = Simulation.from_dict(result["simulation"])       # Turn data into instance of class
        yield                                                                   # And another one
        yield from result["simulation"].load_save(name.parent)                  # Load/update most data
        yield                                                                   # And another one
        self.Saves.append(result)
        yield                                                                   # Another one by the dust !

    def load_all_saves(self, current_time: float):                              # Load all saves
        if self.load_timer.check_loop_end(current_time):                        # Load every 10 ms
            try:
                next(self.loader)                                               # Load saves one by one
            except StopIteration:
                self.is_loading = False
                self.load_timer.pause(current_time)
                self.load_timer.reset(current_time)
            self.nb_save = len(self.Saves)                                      # Only update when all saves are loaded

    @staticmethod
    def force_delete(function, path: Path, _):
        Path(path).chmod(0o777)                                                 # Change permission
        function(path)

    def delete_today_saves(self, current_time: float):                          # Delete saves saved today
        item_path = Path(self.path_save) / self.today
        if Path(item_path).exists() and Path(item_path).is_dir():               # Delete today save directory
            shutil.rmtree(item_path, onerror=self.force_delete)
            if len(self.Simulations) > 0:                                       # If sims were launched, update their id
                for i, sim in enumerate(self.Simulations):
                    sim.update_id(i + 1)
        self.was_today_saves = False
        self.begin_loading(current_time)

    def delete_save(self, index: int, current_time: float):                     # Delete saves saved today
        save = self.Saves[index]["simulation"]
        if save.is_saved:                                                       # If save exists and was saved
            self.current_save = 0
            self.is_on_saves = False
            save.delete_save()
            self.Saves.pop(index)
            self.nb_save = len(self.Saves)

    def delete_all_saves(self, current_time: float):                            # Delete all saves (but not logs)
        if Path(self.path_save).exists() and Path(self.path_save).is_dir():
            for item in Path(self.path_save).iterdir():
                item_path = Path(self.path_save) / item
                if Path(item_path).is_dir():
                    shutil.rmtree(item_path, onerror=self.force_delete)
            if len(self.Simulations) > 0:                                       # If sims were launched, update their id
                for i, sim in enumerate(self.Simulations):
                    if sim.is_saved:                                            # If sim is saved, delete its save
                        sim.delete_save()
                    sim.update_id(i + 1)
        self.was_today_saves = False
        self.Saves.clear()
        self.nb_save = 0
