# from math import *
from random import randint, shuffle
from time import time
from copy import copy
from entity import Entity
from webcolors import name_to_rgb
from collections import defaultdict
from pathlib import Path
import datetime
import pygame
import os

""" Auto-imported by ProjectMaker """
# . Make Mahjong game for Fynn's return

# ... Upgrade flee method for Entity ->
# ! Make overlay for entity remain fully on screen (if mouse is too close to borders)
# . Add step by step moves (add parameter)


# [v0.0.1] Basic functions
# [v0.0.2] Create class for entity (rock, paper, scissors)
# [v0.0.3] Look for game files (fonts, images) online
# [v0.0.4] Test entities
# [v0.0.5] Avoid entities to move away from the map
# [v0.0.6] Display data on screen + had percent bg for nb entity
# [v0.0.7] Make simulation personalized in game (add parameters)
# [v0.0.8] Add pause screen + key shortcuts + make entity with no target flee enemy
# ... [v0.0.9] Add range for entity (detection for target and enemy) + add overlay for entities
# ! [v0.1.0] Add lots of options for simulations (map borders, inf map, smart, follow mouse, appear with click, bait)
# ! [v0.1.1] Add menus (use greetings() as main menu) + end of simulation if only one type remaining (add auto-end option)
# ! [v0.1.2] Add sounds (when entity been beaten) + mutation option (can change type randomly)
# ! [v0.1.3] Add graphics + saves result + scoreboard
# ! [v0.1.4] Add possibility to add more entity type (Sheldon rps)
# ! [v0.9.9] Make documentations and complete functions description (purpose, args descr, args type)
# ! [v1.0.0] Final tasks
class RPSSimulator:                                                             # Main class
    def __init__(self, name=None):
        self.name = self.get_project_name(name)                                 # Get name of the game/program
        self.creator = "One Shot"
        self.version = "v0.0.8"
        self.birthday: str = None           # "15/10/24"                        # Day of creation
        # Initializers
        pygame.init()
        pygame.display.init()
        pygame.mixer.init()
        pygame.font.init()
        # Booleans data
        self.running = True                                                     # Program running
        self.parametering = False                                               # On parameter menu
        self.simulating = False                                                 # If on simulation (including pause menu)
        self.pausing = False                                                    # On pause menu
        self.asking_restart = False                                             # Asking player if want to restart sim
        self.balanced = True                                                    # If same nb of entity of each kind
        # [pygame.display.Info().current_w, pygame.display.Info().current_h]
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_size = self.screen.get_size()                               # Full screen by default
        pygame.display.set_caption(self.name)                                   # Give window a title
        # File data
        # self.path = os.getcwd()
        self.path = str(Path(__file__).parent)                                  # Current programm path
        self.Files = ["data", "fonts", "images", "musics", "saves", "sounds"]   # All files to create at first launch
        # Game data
        self.pressed = pygame.key.get_pressed()                                 # Keyboard inputs
        self.mouse = pygame.mouse.get_pos()                                     # Mouse coordinates
        self.horloge = pygame.time.Clock()                                      # Limit nb of fps
        self.left_click = False                                                 # If has left-clicked on this turn
        self.fps = 60
        # Colors data
        # self.bg_color = name_to_rgb("white")
        self.ColorNames = ["red", "orange", "wheat", "yellow", "green", "cyan",
                           "blue", "purple", "deeppink", "brown", "lightgrey",
                           "grey", "white", "black"]
        self.Colors = {color: name_to_rgb(color) for color in self.ColorNames}
        self.bg_color = self.Colors["lightgrey"]
        self.borders_color = self.Colors["grey"]
        self.font_color = self.Colors["black"]
        # Entities data
        self.EntityNames = ["rock", "paper", "scissors"]
        self.EntityColors = {"rock": self.Colors["grey"], "paper": self.Colors["wheat"],
                             "scissors": self.Colors["red"]}
        self.Entities = []
        self.nb_entities = 100
        # Parameters data
        self.is_display_turn = False
        self.turn = 1                                                           # Number of turns
        self.is_map_borders = False                                             # Allow entities to exit the screen
        self.is_infinity_map = False                                            # Make screen toroidal
        self.is_nb_in_percent = False                                           # Display nb of entities in percent
        self.is_ui_on_front = False                                             # Display UI on front of entities
        self.is_ui_hide = False                                                 # If UI is displayed
        self.is_smart_entity = False                                            # Entity flee enemy
        self.is_follow_mouse = False                                            # Type of entity follows mouse position
        self.entity_to_follow_mouse: Entity/str = None                          # What entity follow mouse
        self.is_spawn_with_click = False                                        # If clicking spawns an entity
        self.entity_to_spawn: Entity/str = None                                 # What entity to spawn with click
        # Fonts data
        self.Fonts = []
        self.FontSizes = {"small": 25, "middle": 40, "big": 60, "giant": 80}
        self.font_name: str = None
        self.main_font: pygame.font.Font = None
        # Timers data
        self.start_time = 0                                                     # When simulation begin
        self.current_time = 0
        self.simulation_timer = 0                                               # Time since simulation start (exclude pause)
        self.paused_time = 0                                                    # Time simulation was paused
        self.turn_timer = 0
        self.turn_duration = 0                                                  # Time a turn last
        # Sounds data
        self.volume = 0.5
        self.Sounds = []
        self.sound1: pygame.mixer.Sound = None
        # Main function
        self.first_launch_game()
        self.run()

    @staticmethod
    def get_project_name(name):                                                 # Return directory name of project
        return str(os.path.basename(Path(__file__).parent)) if name is None else name

    @staticmethod
    def get_current_date():                                                     # Return today's date
        return datetime.datetime.now().strftime("%d/%m/%Y")

    def first_launch_game(self):                                                # Configure some project data
        self.create_files()
        self.look_for_birthday()
        self.fill_data_lists()
        self.save_game_data()

    def create_files(self):                                                     # Create files if doesn't exist
        for file in self.Files:
            path = f"{self.path}/{file}"
            if not os.path.exists(path):
                os.makedirs(path)
        with open(f"{self.path}/data/data.txt", 'w') as file:                   # Create game data file
            file.write("")

    def look_for_birthday(self):
        if self.birthday is None:                                               # If first launch
            with open(f"{self.path}/data/data.txt", 'r') as file:
                lines = file.readlines()                                        # !! Return empty lines
                birthday = lines[3].strip() if len(lines) >= 4 else None        # Check if data saved
                # print(line) # !!!
            self.birthday = self.get_current_date() if birthday is None else birthday

    def fill_data_lists(self):                                                  # Fill game lists with data from files
        # Fill game fonts
        self.Fonts = [_ for _ in os.listdir(f"{self.path}/fonts") if _.endswith(".ttf")]
        if len(self.Fonts) > 0:
            self.font_name = self.Fonts[0]
            font_path = f"{self.path}/fonts/{self.font_name}"
        else:
            self.font_name = None
            font_path = None
        self.main_font = pygame.font.Font(font_path, 80)

        # Fill game sounds
        self.Sounds = [_ for _ in os.listdir(f"{self.path}/sounds") if _.endswith(".mp3")]
        if len(self.Sounds) > 0:
            self.sound1 = pygame.mixer.Sound(f"{self.path}/sounds/{self.Sounds[0]}.mp3")
            self.sound1.set_volume(self.volume)

    def save_game_data(self):                                                   # Write most of the game data
        with open(f"{self.path}/data/data.txt", 'w') as file:
            file.write(self.name + "\n")
            file.write(self.creator + "\n")
            file.write(self.version + "\n")
            file.write(self.birthday + "\n")

    @staticmethod
    def modify_file_line(filename, line_number, text):                          # Modify a specific line of a file
        with open(filename, 'r') as file:
            lines = file.readlines()

        if line_number <= len(lines):                                           # Modify line
            lines[line_number - 1] = text + '\n'
        else:
            lines.extend(['\n'] * (line_number - len(lines) - 1))               # Eventually add blank lines
            lines.append(text + '\n')                                           # End of file

        with open(filename, 'w') as file:                                       # Update
            file.writelines(lines)

    def set_font_color(self, new_color_name="black"):
        if new_color_name in self.Colors.keys():
            self.font_color = self.Colors[new_color_name]

    def set_font_size(self, new_size=30):                                       # Change current font size
        font_path = f"{self.path}/fonts/{self.font_name}" if self.font_name else None
        self.main_font = pygame.font.Font(font_path, new_size)

    def get_number_entities(self):                                              # Return a dict with entities' name and quantity
        NumberEntities = defaultdict(int)
        for entity in self.Entities:
            NumberEntities[entity.name] += 1
        NumberEntities = dict(sorted(dict(NumberEntities).items(),
                                     key=lambda x: x[1], reverse=True))         # Sorted dict by quantity
        return NumberEntities

    def get_mouse_hover_position(self, pos):
        return pos[0] <= self.mouse[0] <= pos[0] + pos[2] and pos[1] <= self.mouse[1] <= pos[1] + pos[3]

    def get_click_on_position(self, pos):
        return self.get_mouse_hover_position(pos) and self.left_click

    def get_not_click_on_position(self, pos):
        return not self.get_mouse_hover_position(pos) and self.left_click

    def run(self):                                                              # Main function
        while self.running:                                                     # While playing
            self.current_time = time()
            self.pressed = pygame.key.get_pressed()
            self.mouse = pygame.mouse.get_pos()
            self.left_click = False

            for event in pygame.event.get():                                    # Get keyboard events
                if event.type == pygame.QUIT:
                    self.close_game()

                if event.type == pygame.MOUSEBUTTONDOWN:                        # If left click
                    if event.button == 1:
                        self.left_click = True

                if event.type == pygame.KEYDOWN:                                # Keyboard entries
                    if event.key == pygame.K_q:
                        self.simulating = False

                    if event.key == pygame.K_ESCAPE:                            # Close simulation
                        self.close_game()

                    if event.key == pygame.K_SPACE:
                        if not self.simulating:                                 # Main menu
                            self.start_simulation()
                        else:
                            self.pausing = not self.pausing
                            if self.pausing:
                                self.paused_time = self.current_time - self.simulation_timer
                            else:
                                self.simulation_timer = self.current_time - self.paused_time

                    if event.key == pygame.K_h:                                 # Hide/show UI
                        self.is_ui_hide = not self.is_ui_hide

                    if event.key == pygame.K_r:                                 # Restart simulation
                        if self.simulating:
                            self.asking_restart = True
                            self.pausing = True                                 # Paused when alert messages
                            self.paused_time = self.current_time - self.simulation_timer
                        else:
                            self.start_simulation()

                    if event.key == pygame.K_p:
                        self.parametering = not self.parametering
                        if self.parametering:                                   # Pause simulation when open parameters
                            self.pausing = True

            self.check_spawn_entity()
            self.display_manager()

            pygame.display.flip()                                               # Update window
            self.horloge.tick(self.fps)

            if not self.pausing:
                if self.current_time - self.turn_timer > self.turn_duration:
                    self.turn_timer = time()
                    self.turn += 1                                              # Go to next turn

    def check_spawn_entity(self):                                               # Spawn selected entity at mouse coords
        if self.simulating:
            if (not self.pausing and self.left_click and self.is_spawn_with_click and
                    self.entity_to_spawn is not None):
                entity = Entity(self.entity_to_spawn, list(self.mouse))
                self.Entities.append(entity)

    def display_manager(self):                                                  # Display everything on screen
        self.screen.fill(self.bg_color)

        if not self.simulating:                                                 # Main menu
            self.display_menu()
        else:                                                                   # On simulation
            self.display_bg_name()

            if self.is_ui_on_front:
                self.display_entities()
                if not self.is_ui_hide:
                    self.display_ui()
            else:                                                               # Display UI on the back
                if not self.is_ui_hide:
                    self.display_ui()
                self.display_entities()

            if self.pausing:                                                    # Display in front of almost everything...
                self.display_pause()
            else:
                self.move_entities()

        if self.parametering:                                                   # ...except for parameters menu...
            self.display_parameters_screen()

        if self.asking_restart:                                                 # ...and alert messages
            result = self.display_ask_box(0.35, 0.35, "Restart simulation",
                                          "Are you sure you want to restart the ongoing simulation ?", "Yes restart", "Cancel")
            if result is None:
                pass
            elif result:
                self.asking_restart = False
                self.start_simulation()
            else:
                self.asking_restart = False
                self.pausing = False
                self.simulation_timer = self.current_time - self.paused_time

    def display_menu(self):                                                        # Main menu
        self.display_message(0.5, 0.35, self.name, "giant")

        self.display_message(0.5, 0.45, f"Made by {self.creator}", "big")

        self.display_message(0.02, 0.95, f"Created {self.birthday}", "middle", "left")

        self.display_message(0.98, 0.95, self.version, "middle", "right")

        if self.display_button(f"Start simulation", (0.41, 0.55, 0.18, 0.1), self.borders_color, True, self.bg_color):
            self.start_simulation()

        if self.display_button(f"Quit", (0.41, 0.66, 0.18, 0.1), self.bg_color, bg_color_hover=(222, 222, 222)):
            self.close_game()

        Commands = ["Space : Start", "P : Parameters", "Echap : Quit"]
        for i, command in enumerate(Commands):
            self.display_message(0.98, 0.3 + 0.03 * (i + 1), command, None, "right")

    def display_bg_name(self):
        self.set_font_color("grey")
        self.display_message(message=self.name, font_name="giant")              # Simulation name in the bg
        self.set_font_color()                                                   # Default color

    def display_entities(self):                                                 # Display entities on screen
        for entity in self.Entities:
            self.screen.blit(entity.image, entity.coords)

        if not self.is_ui_hide:
            for entity in self.Entities:                                        # Not in same loop to avoid overlay being beyond entities
                if entity.is_mouse_over(self.mouse):
                    self.display_entity_infos(entity)
                    break                                                       # Only display one at a time

    # Default screen's position : top right of the mouse
    def display_entity_infos(self, entity):
        pos = (self.mouse[0], self.mouse[1] - self.screen_size[1] * 0.1 - 10,
               self.screen_size[0] * 0.2, self.screen_size[1] * 0.28 - 10)
        self.display_screen(pos)

        coords = ((pos[0] + pos[2] * 0.5) / self.screen_size[0], (pos[1] + pos[3] * 0.1) / self.screen_size[1])
        self.display_message(*coords, entity.name.capitalize(), "middle")

        target_coords = f"{int(entity.target.coords[0])}:{int(entity.target.coords[1])}" \
            if entity.target else "no target found"
        Infos = [f"Smart : {entity.is_smart}", f"Coords : {int(entity.coords[0])}:{int(entity.coords[1])}",
                 f"Size : {entity.size} pixels", f"Speed : {entity.speed} px/turn",
                 f"Target type : {entity.target_name.capitalize()}", f"Target coords : {target_coords}"]
        size = self.FontSizes["small"] + 2
        for i, info in enumerate(Infos):
            coords = ((pos[0] + pos[2] * 0.05) / self.screen_size[0],
                      (pos[1] + pos[3] * 0.25 + (i * size)) / self.screen_size[1])
            self.display_message(*coords, info, "small", "left")

    def display_ui(self):                                                       # Data of simulation
        # Display number of entities in simulation (up left corner)
        self.display_message(0.02, 0.05, f"Entities (x{len(self.Entities)})", "middle", "left")
        NumberEntities = self.get_number_entities()
        for i, (name, quantity) in enumerate(NumberEntities.items()):
            value = (quantity / len(self.Entities)) * 100
            percent = round(value, 2) if round(value, 2) % 1 else int(value)
            pos = (0.02 * self.screen_size[0], (0.05 + 0.03 * (i + 1)) * self.screen_size[1],
                   percent * 2, 0.03 * self.screen_size[1])
            pygame.draw.rect(self.screen, self.EntityColors[name], pos)
            text = f"{percent}%" if self.is_nb_in_percent else f"x{quantity}"
            self.display_message(0.02, 0.05 + 0.03 * (i + 1),
                                 f"- {name.capitalize()} ({text})", None, "left")

        # Display simulation timer (up middle)
        time_past = round(self.paused_time if self.pausing
                          else self.current_time - self.simulation_timer, 1)
        self.display_message(0.5, 0.05, f"{time_past}s", None)

        # Display commands for simulation (middle right)
        Commands = ["H : Hide UI", "R : Restart", "Space : Pause", "P : Parameters",
                    "Q : Return to menu", "Echap : Quit"]
        for i, command in enumerate(Commands):
            self.display_message(0.98, 0.3 + 0.03 * (i + 1), command, None, "right")

        # Display entity informations (bottom left corner)
        self.display_message(0.02, 0.8, f"Entity data : ", None, "left")
        self.display_message(0.02, 0.83, f"- size : {Entity(None).size}", None, "left")
        self.display_message(0.02, 0.86, f"- speed : {Entity(None).speed}", None, "left")
        if self.is_smart_entity:
            self.display_message(0.02, 0.89, f"- smart : {self.is_smart_entity}", None, "left")

        # Display turn (bottom middle)
        if self.is_display_turn:
            self.display_message(0.5, 0.98, f"Turn n°{self.turn}", None)

    def display_pause(self):                                                    # Pause menu
        self.display_message(0.5, 0.25, f"Pause", "big")

    def display_parameters_screen(self):                                        # Display parameters screen
        pos = self.display_box()
        if self.get_not_click_on_position(pos):
            self.parametering = False

        self.display_message(0.5, 0.18, f"Parameters", "big")

        # First column
        self.is_display_turn, _ = self.display_parameter(0.15, 0.3,
                                                         self.is_display_turn, "Display number of turns : ")
        if self.is_display_turn:                                                # Select pause for each turn
            self.display_message(0.15, 0.35, f"Turn pause : {self.turn_duration} sec", "middle", "left")
            if (self.display_button("-", (0.35, 0.35, 0.025, 0.04), "lightgrey", True) and
                    self.turn_duration > 0):
                self.turn_duration -= 1
            if (self.display_button("+", (0.4, 0.35, 0.025, 0.04), "lightgrey", True) and
                    self.turn_duration < 10):
                self.turn_duration += 1
            percent = (self.turn_duration / 10) * (self.screen_size[0] * 0.28)
            pos = (self.screen_size[0] * 0.15, self.screen_size[1] * 0.4, percent, 10)
            pygame.draw.rect(self.screen, self.borders_color, pos, border_radius=int(pos[3] * 0.5))

        self.is_map_borders, as_change = self.display_parameter(0.15, 0.44,
                                                                self.is_map_borders, "Entities can exit the screen : ")
        if as_change and self.is_map_borders:
            self.is_infinity_map = False
        self.is_infinity_map, as_change = self.display_parameter(0.15, 0.5,
                                                                 self.is_infinity_map, "Screen is toroidal : ")
        if as_change and self.is_infinity_map:
            self.is_map_borders = False
        self.is_nb_in_percent, _ = self.display_parameter(0.15, 0.57,
                                                          self.is_nb_in_percent, "Quantity is in percent : ")
        self.is_ui_on_front, _ = self.display_parameter(0.15, 0.64,
                                                        self.is_ui_on_front, "UI is on front : ")
        self.is_ui_hide, _ = self.display_parameter(0.15, 0.7,
                                                    self.is_ui_hide, "UI is hide : ")

        # Second column
        self.is_smart_entity, as_change = self.display_parameter(0.55, 0.3,
                                                                 self.is_smart_entity, "Entities are smart : ")
        if as_change:
            if self.is_smart_entity:
                self.make_entities_smart()
            else:
                self.make_entities_dumb()

        self.is_follow_mouse, _ = self.display_parameter(0.55, 0.5,
                                                         self.is_follow_mouse, "Entities follow mouse : ")
        if self.is_follow_mouse:                                                # Select following entity
            self.display_message(0.55, 0.55, f"Entity to follow : {self.entity_to_follow_mouse}",
                                 "middle", "left")
            entity = self.display_entities_button(self.screen_size[0] * 0.55, self.screen_size[1] * 0.6)
            if entity is not None:
                self.entity_to_follow_mouse = entity
        self.is_spawn_with_click, _ = self.display_parameter(0.55, 0.7,
                                                             self.is_spawn_with_click, "Spawn entity on click : ")
        if self.is_spawn_with_click:                                            # Select entity to spawn
            self.display_message(0.55, 0.75, f"Entity to spawn : {self.entity_to_spawn}",
                                 "middle", "left")
            entity = self.display_entities_button(self.screen_size[0] * 0.55, self.screen_size[1] * 0.8)
            if entity is not None:
                self.entity_to_spawn = entity

    def display_message(self, percent_x=0.5, percent_y=0.5, message="", font_name=None, position=None, percent_size=None):
        if font_name is not None:                                               # Change font size if a new one is required
            self.set_font_size(self.FontSizes[font_name])

        if percent_size is None:                                                # If no size limit for message
            text = self.main_font.render(str(message), True, self.font_color)
            coords = [int(self.screen_size[0] * percent_x), int(self.screen_size[1] * percent_y)]
            size = text.get_size()

            if position == "up":                                                # Text in up-left corner by default
                coords[1] += 0
            elif position == "down":
                coords[1] -= int(size[1])
            elif position == "left":
                coords[0] += 0
            elif position == "right":
                coords[0] -= int(size[0])
            else:
                coords[0] = int(coords[0] - size[0] * 0.5)
                coords[1] = int(coords[1] - size[1] * 0.5)

            self.screen.blit(text, coords)
            return [coords[0], coords[1], size[0], size[1]]                     # Return pos of button
        else:
            Words = message.split()
            Lines = []
            current_line = ""
            pos = [int(self.screen_size[0] * percent_x), int(self.screen_size[1] * percent_y),
                   int(self.screen_size[0] * percent_size[0]), int(self.screen_size[1] * percent_size[1])]

            for word in Words:                                                  # Get lines based on message's lenght
                test_line = current_line + (" " if current_line else "") + word
                # The '+ 5' is just to leave some margin
                if self.main_font.size(test_line)[0] <= pos[2] + 5:             # If line is under max lenght
                    current_line = test_line
                else:
                    Lines.append(current_line)                                  # Add full line
                    current_line = word                                         # Start a new line

            if current_line:                                                    # Add last line
                Lines.append(current_line)

            # "Tg" : in order to mesure full height of font with uppercase and low char like 'g' or 'y'
            total_text_height = len(Lines) * self.main_font.size("Tg")[1]       # Text's height
            start_y = pos[1] + (pos[3] - total_text_height) // 2

            for i, line in enumerate(Lines):                                    # Draw each line
                line_surface = self.main_font.render(line, True, self.font_color)
                line_width, line_height = line_surface.get_size()
                x = pos[0] + (pos[2] - line_width) // 2                         # Center text
                y = start_y + i * line_height
                self.screen.blit(line_surface, (x, y))

            return pos

    def display_parameter(self, percent_x=0.5, percent_y=0.5, param=False, message="Parameter : "):
        pos = self.display_message(percent_x, percent_y, f"{message} {'On' if param else 'Off'}",
                                   "middle", "left")
        if self.get_click_on_position(pos):
            return not param, True
        return param, False

    def display_screen(self, pos, bg_color=None, border_width=None, border_radius=20):
        if bg_color is None:
            bg_color = self.Colors["white"]
        pygame.draw.rect(self.screen, bg_color, pos, border_radius=border_radius)
        if border_width:
            pygame.draw.rect(self.screen, self.borders_color, pos, border_width, border_radius)

    def display_box(self, x_percent=0.8, y_percent=0.8, bg_color=None, border_width=10, border_radius=20):
        if bg_color is None:
            bg_color = self.Colors["white"]
        pos = (self.screen_size[0] * (1 - x_percent) / 2, self.screen_size[1] * (1 - y_percent) / 2,
               self.screen_size[0] * x_percent, self.screen_size[1] * y_percent)
        pygame.draw.rect(self.screen, bg_color, pos, border_radius=border_radius)
        pygame.draw.rect(self.screen, self.borders_color, pos, border_width, border_radius)
        return pos

    # Return a boolean when click on one of the 2 button : True is the first option, False the second one
    def display_ask_box(self, x_percent=0.35, y_percent=0.35, title="Question ?", text='Text', button1="Yes", button2="No"):
        pos = self.display_box(x_percent, y_percent)
        pos_percent = [x / self.screen_size[i % 2] for i, x in enumerate(pos)]
        size = None
        self.display_message(pos_percent[0] + pos_percent[2] * 0.5,
                             pos_percent[1] + self.FontSizes["big"] / self.screen_size[1], title, "big")
        if text is not None:
            text_pos = (pos_percent[0] + pos_percent[2] * 0.1, pos_percent[1] + pos_percent[3] * 0.3,
                        pos_percent[2] * 0.8, pos_percent[3] * 0.4)
            self.display_message(text_pos[0], text_pos[1], text, "middle",
                                 percent_size=(text_pos[2], text_pos[3]))
        button_pos = [pos_percent[0] + pos_percent[2] * 0.05, pos_percent[1] + pos_percent[3] * 0.7,
                      pos_percent[2] * 0.4, pos_percent[3] * 0.25]
        if self.display_button(button1, button_pos, self.borders_color, True, self.bg_color):
            return True
        button_pos[0] += (pos_percent[2] * 0.5)                               # Second button is more to the right
        if (self.display_button(button2, button_pos, self.borders_color, True, self.bg_color) or
                self.get_not_click_on_position(pos_percent)):
            return False
        return None

    def display_button(self, name="", pos_percent=(0, 0, 0, 0), bg_color=None, has_border=False, bg_color_hover=None):
        pos = (self.screen_size[0] * pos_percent[0], self.screen_size[1] * pos_percent[1],
               self.screen_size[0] * pos_percent[2], self.screen_size[1] * pos_percent[3])
        radius = int(pos[3] * 0.1)
        if bg_color_hover and self.get_mouse_hover_position(pos):
            bg_color = bg_color_hover
        elif bg_color is None:
            bg_color = self.bg_color
        if type(bg_color) is str:
            bg_color = self.Colors[bg_color]
        pygame.draw.rect(self.screen, bg_color, pos, border_radius=radius)
        if has_border:
            pygame.draw.rect(self.screen, self.borders_color, pos, int(pos[2] * 0.025), radius)
        self.display_message(pos_percent[0] + pos_percent[2] * 0.5,
                             pos_percent[1] + pos_percent[3] * 0.5, name, "middle")
        return self.get_click_on_position(pos)

    def display_entities_button(self, x, y, image_size=50, gap=10):             # A button with an image of an entity (no text)
        width = 3                                                               # Border width
        Each = [Entity(name) for name in self.EntityNames]
        for i, entity in enumerate(Each):
            image = pygame.transform.scale(entity.image, (image_size, image_size))
            coords = (x + (image_size + gap) * i, y)
            pos = (coords[0] - width, coords[1] - width,
                   image_size + width * 2, image_size + width * 2)
            pygame.draw.rect(self.screen, self.borders_color, pos, width, width)
            self.screen.blit(image, coords)
            if self.get_click_on_position(pos):
                return entity.name
        return None

    def start_simulation(self):
        self.simulating = True
        self.create_entities()
        self.simulation_timer = 0
        self.paused_time = 0
        self.turn_timer = 0
        self.turn = 0

    def create_entities(self):                                                  # Create a number of entities
        shuffle(self.EntityNames)                                               # Shuffle entities in case not nb / 3
        third = int(self.nb_entities / 3)

        self.Entities = []
        for i in range(self.nb_entities):
            coords = [randint(0, self.screen_size[0]), randint(0, self.screen_size[1])]
            if self.balanced:
                if i <= third:
                    entity = Entity(self.EntityNames[0], coords)
                elif third < i <= third * 2:
                    entity = Entity(self.EntityNames[1], coords)
                else:
                    entity = Entity(self.EntityNames[2], coords)
            else:
                entity = Entity(choice(self.EntityNames), coords)
            self.Entities.append(entity)

    def move_entities(self):                                                    # Move every entity on screen
        screen_size = self.screen_size if self.is_smart_entity else None
        for entity in self.Entities:
            # Behaviour parameters
            if (self.is_follow_mouse and self.entity_to_follow_mouse is not None and
                    entity.name == self.entity_to_follow_mouse):
                entity.move_to_coords(self.mouse)                               # Make entity follow mouse
            else:                                                               # Default movement
                entity.look_for_closest_target(self.Entities)
                entity.move(self.Entities, screen_size)
            # Borders parameters
            if self.is_map_borders:
                self.keep_entity_on_screen(entity)
            elif self.is_infinity_map:
                self.make_entity_move_toroidal(entity)
        # Entity behavior (change target)
        for entity1 in self.Entities:
            for entity2 in self.Entities:
                if (entity1 != entity2 and entity1.does_collide_with_entity(entity2) and
                        entity1.predator_name and entity1.predator_name == entity2.name):
                    entity1.change_type()

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

    def make_entities_smart(self):
        for entity in self.Entities:
            entity.become_smart()

    def make_entities_dumb(self):
        for entity in self.Entities:
            entity.become_dumb()

    def close_game(self):                                                       # Exit program
        pygame.time.delay(200)
        self.running = False
        pygame.quit()
        quit()


if __name__ == "__main__":
    game = RPSSimulator()
