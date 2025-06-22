# from math import *
# from random import *
# from time import *
from PIL import Image
from pathlib import Path
from datetime import date, datetime
from humanize import naturaldelta, precisedelta
from timermanager import TimerManager
from graphic import Graphic
from data import Database
import matplotlib.pyplot as plt
import statistics
import pygame
import shutil
import json
import re


# ? Is timer lagging (is a bit early)
# ! Use 'is_on_saves' bool : precise it on 'save' tab and write date and hour on 'screen' and 'sim' tabs
# ! Modify code so simulation is added while running (every 10 secs/turns -> uncompleted but updated)
class DataManager:
    def __init__(self):
        # Boolean data
        self.is_auto_play = False                                               # Play gif of current simulation
        self.is_auto_save = False                                               # Save at the end of the simulation
        self.is_sim_saved = False                                               # If the last simulation was saved
        self.is_on_saves =  False                                               # If is displaying old save or today's sim
        db = Database()
        # Path data
        self.today = date.today().strftime("%d-%m-%Y")                          # Today's date: dd-mm-yyyy
        self.path_log =         db.PATH_LOG
        self.path_save =        db.PATH_SAVE
        self.path_screenshot =  db.PATH_SCREENSHOT
        self.path_graphic =     db.PATH_GRAPHIC
        self.timer = TimerManager(0.5)                                          # A timer for gif animation
        # Graphics data
        self.GraphicNames = ["Number of entity every second", "Average options evolution",
            "Pinnacle for each entity", "Maximum for each option", "Dominance of entities"]
        self.GraphicTypes = [_ for _ in Path(self.path_graphic).iterdir() if _.suffix == ".png"]
        self.Graphics = []
        self.Figures = []
        self.current_graphic = None                                             # Index of graphic
        self.current_pygame_image = None
        # Menu data
        self.Tabs = ["Simulations", "Graphics", "Saves"]                        # Today, Before
        self.current_tab = 0                                                    # Index of tab to display
        self.current_sim = 0                                                    # Index of sim to display
        self.current_turn = 0                                                   # Index of turn to display
        # Simulation data
        self.Saves = []                                                         # Saved data
        self.screen_format = ".gif"
        self.save_format =   ".json"
        self.log_format =    ".md"
        self.Screenshots = [[]]                                                 # Visual status of each sim every second
        self.sim = {"id": int, "time": float, "quantity": list[dict[str:int]],
            "speeds": list[float | int], "ranges": list[float | int], "sizes": list[float | int],
            "smart": bool, "range": bool, "borders": bool, "toroidal": bool}    # Last saved simulation
        self.Simulations = []                                                   # Simulations launch today
        self.nb_saved_screens = self.get_nb_file(self.path_screenshot, self.screen_format)
        self.nb_saved_sims =    self.get_nb_file(self.path_save, self.save_format)
        self.nb_saved_logs =    self.get_nb_file(self.path_log, self.log_format)
        self.nb_sim = 0                                                         # Number of launched simulations
        # Entities data
        self.EntityNames = list(db.ENTITYCOLORS.keys())
        self.EntityQuantity = {name: [] for name in self.EntityNames}           # Quantity of entity every second
        # Options data
        self.Options = db.OPTIONCOLORS
        self.current_option = list(self.Options.keys())[0]                      # Option for graphic n°2
        self.Speeds = []                                                        # Average of all entities every second
        self.Ranges = []
        self.Sizes =  []
        # Basic function
        self.create_graphics()

    def get_nb_file(self, path, format_type):
        full_path = Path(path) / self.today
        if Path(full_path).exists():
            return len([_ for _ in Path(full_path).iterdir() if _.suffix == format_type])
        return 0

    # [later] Will be upgraded to a for loop (with alternately options and no options)
    def create_graphics(self):                                                  # Create graphics
        graphic = Graphic(self.GraphicNames[0], self.GraphicTypes[2])
        self.Graphics.append(graphic)
        graphic = Graphic(self.GraphicNames[1], self.GraphicTypes[2], True)     # With option
        self.Graphics.append(graphic)
        graphic = Graphic(self.GraphicNames[2], self.GraphicTypes[0])
        self.Graphics.append(graphic)
        graphic = Graphic(self.GraphicNames[3], self.GraphicTypes[0], True)
        self.Graphics.append(graphic)
        graphic = Graphic(self.GraphicNames[4], self.GraphicTypes[3])
        self.Graphics.append(graphic)

    def get_nb_turns(self):                                                     # Return nb of turn of current sim
        return len(self.Screenshots[self.current_sim])

    def get_current_option_list(self):
        Option = []
        sim = self.Simulations[self.current_sim]
        if self.current_option == list(self.Options.keys())[0]:
            Option = sim["speeds"]
        elif self.current_option == list(self.Options.keys())[1]:
            Option = sim["ranges"]
        elif self.current_option == list(self.Options.keys())[2]:
            Option = sim["sizes"]
        return {self.current_option: Option}

    def is_current_sim_saved(self):                                             # [later] Change function
        if len(self.Simulations) > 0:
            current = next(sim for sim in self.Simulations if sim['id'] == self.current_sim)
            if current:
                return current['is_saved']
        return False

    @staticmethod
    def resize_image(screensize, image, width=None, height=None):               # Keep image proportional size
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

    def previous_sim(self):                                                     # Change current simulation to display
        if self.nb_sim > 0:
            self.current_sim = (self.current_sim - 1) % self.nb_sim
            self.current_turn = 0
            self.is_sim_saved = self.is_current_sim_saved()

    def next_sim(self):                                                         # Change current simulation to display
        if self.nb_sim > 0:
            self.current_sim = (self.current_sim + 1) % self.nb_sim
            self.current_turn = 0
            self.is_sim_saved = self.is_current_sim_saved()

    def previous_turn(self):                                                    # Change current turn of current sim
        if self.nb_sim > 0:
            self.current_turn -= 1
            if self.current_turn < 0:
                self.current_turn = self.get_nb_turns() - 1

    def next_turn(self):                                                        # Change current turn of current sim
        if self.nb_sim > 0:
            self.current_turn += 1
            if self.current_turn > self.get_nb_turns() - 1:
                self.current_turn = 0

    def reset(self):                                                            # At the start of a simulation
        # Simulations and Screenshots don't reset
        self.EntityQuantity = {name: [] for name in self.EntityNames}
        self.Speeds = []
        self.Ranges = []
        self.Sizes = []

    # Return the name of the file with the highest number in his name
    @staticmethod
    def get_highest_file_nb(path):
        path = Path(path)
        if Path(path).exists():
            try:
                max_folder = max((f for f in path.iterdir() if f.is_dir()),
                    key=lambda x: int(re.search(r'\d+', x.name).group())
                    if re.search(r'\d+', x.name) else -1).name
                return max_folder
            except ValueError:
                return None
        return None

    def get_next_screenshot_name(self, nb_turn=1):
        nb = self.nb_saved_screens + 1
        self.nb_saved_screens = self.get_nb_file(self.path_screenshot, self.screen_format)  # Update number of file
        s = "s" if nb_turn > 1 else ""
        return f"sim {nb} (x{nb_turn} turn{s})" + self.screen_format

    def get_next_save_name(self):
        nb = self.nb_saved_sims + 1
        self.nb_saved_sims = self.get_nb_file(self.path_save, self.save_format)  # Update number of file
        return f"save {nb}" + self.save_format

    def get_next_log_name(self):
        nb = self.nb_saved_logs + 1
        self.nb_saved_logs = self.get_nb_file(self.path_log, self.log_format)   # Update number of file
        return f"log {nb}" + self.log_format

    def add_simulation(self, duration, smart=False, is_range=False, borders=False, toroidal=False): # Save last sim
        self.nb_sim += 1
        self.sim = {"id": self.nb_sim, "time": duration, "quantity": self.EntityQuantity,
            "speeds": self.Speeds, "ranges": self.Ranges, "sizes": self.Sizes,
            "smart": smart, "range": is_range, "borders": borders, "toroidal": toroidal,
            "is_saved": False}
        self.Simulations.append(self.sim)

    # ! Checking of function work (try diff conditions)
    def update_simulation(self, sim_id, duration, smart=False, is_range=False, borders=False, toroidal=False):
        new_sim = {"id": sim_id, "time": duration, "quantity": self.EntityQuantity,
            "speeds": self.Speeds, "ranges": self.Ranges, "sizes": self.Sizes,
            "smart": smart, "range": is_range, "borders": borders, "toroidal": toroidal, "is_saved": False}
        for i, save in enumerate(self.Simulations):
            if save["id"] == new_sim["id"]:
                self.Simulations[i] = new_sim
                return
        self.add_simulation(duration, smart, is_range, borders, toroidal)       # If sim wasn't added

    def take_screenshot(self, screen):                                          # Take a full screenshot but don't save it
        screenshot = screen.copy()
        if len(self.Screenshots) <= self.nb_sim - 1:
            self.Screenshots.append([])                                         # Add list for next sim
        self.Screenshots[self.nb_sim - 1].append(screenshot)

    def save_screenshots(self, screens=None):                                   # Save all taken screenshots
        dir_name = Path(self.path_screenshot) / self.today
        Path(dir_name).mkdir(exist_ok=True)                                    # Create directory if doesn't exist

        Images = [pygame.image.tostring(img, "RGB") for img in screens]
        Images = [Image.frombytes("RGB", img.get_size(), data) for img, data in zip(screens, Images)]
        pause = 4                                                               # Pause of 1s / 250ms (see duration)
        Images.extend([Images[-1]] * pause)                                     # Add copies of last image to create pause

        file_name = self.get_next_screenshot_name(len(screens))
        Images[0].save(Path(dir_name) / file_name, save_all=True,
            append_images=Images[1:], duration=250, loop=0)

    def save_simulation(self, id_sim=0):                                        # Create text file to save data
        dir_name = Path(self.path_save) / self.today
        Path(dir_name).mkdir(exist_ok=True)

        file_name = self.get_next_save_name()
        if not Path(Path(dir_name) / file_name).exists():
            with open(Path(dir_name) / file_name, 'w') as file:                 # Create game data file
                name = file_name.replace(f"{self.today} - ", "").replace(self.save_format, "").capitalize()
                hour = datetime.now().strftime("%H:%M")
                sim = next((s for s in self.Simulations if s['id'] == id_sim), None)
                if sim:
                    sim["is_saved"] = True
                simulation = {"name": name, "hour": hour, "simulation": sim}
                json.dump(simulation, file, indent=4)
                file.close()

    def save_log(self, Sims: list):                                             # Automatically save at the end of each sim
        dir_name = Path(self.path_log) / self.today
        Path(dir_name).mkdir(exist_ok=True)

        file_name = self.get_next_log_name()
        # if not Path(Path(dir_name) / file_name).exists():                     # Check isn't necessary (will just overwrite)
        with open(Path(dir_name) / file_name, 'w') as file:                     # Create game data file
            name = file_name.replace(f"{self.today} - ", "").replace(self.log_format, "").capitalize()
            hour = datetime.now().strftime("%H:%M")
            file.write(f"# {name}\n")
            file.write(f"###### created {self.today} at {hour}\n\n")
            file.write(f"***\n")
            s = "s" if self.nb_sim > 1 else ""
            file.write(f"### There was {self.nb_sim} simulation{s} launched.\n\n")

            WinRate = {name: 0 for name in self.EntityNames}
            file.write(f"##### Simulations : \n\n")

            for sim in Sims:
                nb_turn = len(sim['quantity'][self.EntityNames[0]])
                s = "s" if nb_turn > 1 else ""
                duration = precisedelta(sim['time'])                            # Display text with precise units
                file.write(f"The simulation n°{sim['id']} last {nb_turn} turn{s} and {duration}.\\\n")
                file.write(f"Were entities smart : {'Yes' if sim['smart'] else 'No'}\\\n")
                file.write(f"Did map had borders : {'Yes' if sim['borders'] else 'No'}\\\n")
                file.write(f"Did map was toroidal : {'Yes' if sim['toroidal'] else 'No'}\\\n")
                file.write(f"Were entities had range : {'Yes' if sim['range'] else 'No'}\\\n")
                file.write(f"Average size was **{round(statistics.mean(sim['sizes']), 3)}** pixels\\\n")
                file.write(f"Average range was **{round(statistics.mean(sim['ranges']), 3)}** pixels\\\n")
                file.write(f"Average speed was **{round(statistics.mean(sim['speeds']), 3)}** pixels/sec\\\n")
                last = {name: sim['quantity'][name][-1] for name in self.EntityNames}
                winner = max(last, key=last.get)
                WinRate[winner] += 1
                nb_entity = sum(last.values())
                s = "ies" if nb_entity > 1 else "y"
                file.write(f"The entity '{winner}' won : x{last[winner]} / {nb_entity} entit{s}.\n\n")
            file.write("\n")

            file.write("##### Entity winrate : \n")
            for entity, nb_win in WinRate.items():
                file.write(f"- {entity} : {round(nb_win / self.nb_sim * 100, 2)}%\n")
            file.write("\n")
            file.close()

    def save_current_sim(self):
        self.save_screenshots(self.Screenshots[self.current_sim])
        self.save_simulation(self.current_sim)
        self.save_log([self.Simulations[self.current_sim]])
        self.load_all_saves()                                                   # Update saved files

    def save_all(self):                                                         # Save all collected data
        for screens in self.Screenshots:
            self.save_screenshots(screens)
        for sim in self.Simulations:
            self.save_simulation(sim['id'])
        self.save_log(self.Simulations)
        self.load_all_saves()                                                   # Update saved files

    def display_graphic(self, graphic):                                         # Create graphic with current sim datas
        if len(self.Simulations) > 0:
            for i, g in enumerate(self.Graphics):
                if g == graphic:
                    self.current_graphic = i
                    sim = self.Simulations[self.current_sim]
                    EntityQuantity = sim["quantity"]
                    Speeds = sim["speeds"]
                    Ranges = sim["ranges"]
                    Sizes = sim["sizes"]
                    Options = self.get_current_option_list()
                    self.current_pygame_image, fig = g.show_graphic(EntityQuantity,
                        Speeds, Ranges, Sizes, Options)
                    if fig:
                        for figure in self.Figures:                             # Close all graphics
                            plt.close(figure)
                        self.Figures.append(fig)                                # Add current graphic
                    break

    def update_graphic(self, screensize, graphic=None, size=0.6):
        if graphic is None:
            graphic = self.Graphics[self.current_graphic]
        self.display_graphic(graphic)
        if self.current_pygame_image:
            self.current_pygame_image = self.resize_image(screensize,
                self.current_pygame_image, height=size)

    def check_display_next_turn(self, current_time):
        if self.is_auto_play:                                                   # Show each turn for 0.5 second
            if self.timer.check_loop_end(current_time) > 0:                     # After the loop end
                self.next_turn()

    # ... Testing new save functions
    def load_save(self, name):                                                  # Load a save based on its name
        if name.suffix != self.save_format:
            name = name.with_suffix(self.save_format)

        with open(name, "r", encoding="utf-8") as f:
            result = json.load(f)
            if result not in self.Saves:
                self.Saves.append(result)
            f.close()

    def load_all_saves(self):                                                   # Load all saves
        self.Saves = []
        for directory in Path(self.path_save).iterdir():
            for filename in Path(directory).iterdir():
                self.load_save(filename)

    @staticmethod
    def force_delete(function, path, _):
        Path(path).chmod(0o777)                                                 # Change permission
        function(path)

    def delete_today_saves(self):                                               # Delete screenshots and saves saved today
        dir_name = Path(self.path_screenshot) / self.today
        if Path(dir_name).exists() and Path(dir_name).is_dir():
            shutil.rmtree(dir_name, onerror=self.force_delete)

        dir_name = Path(self.path_save) / self.today
        if Path(dir_name).exists() and Path(dir_name).is_dir():
            shutil.rmtree(dir_name, onerror=self.force_delete)

        self.load_all_saves()                                                   # Update saved files

    def delete_all_saves(self):                                                 # Delete all screenshots and saves (not logs)
        dir_name = self.path_screenshot
        if Path(dir_name).exists() and Path(dir_name).is_dir():
            for item in Path(dir_name).iterdir():
                item_path = Path(dir_name) / item
                if Path(item_path).is_dir():
                    shutil.rmtree(item_path, onerror=self.force_delete)

        dir_name = self.path_save
        if Path(dir_name).exists() and Path(dir_name).is_dir():
            for item in Path(dir_name).iterdir():
                item_path = Path(dir_name) / item
                if Path(item_path).is_dir():
                    shutil.rmtree(item_path, onerror=self.force_delete)

        self.load_all_saves()                                                   # Update saved files
