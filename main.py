# from math import *
from random import randint
from time import time
# from copy import copy
from pathlib import Path
from webcolors import name_to_rgb
from PIL import Image, ImageSequence
from parameterscreen import ParameterScreen
from entitymanager import EntityManager
from timermanager import TimerManager
from textmanager import TextManager
from datamanager import DataManager
from graphic import Graphic
from entity import Entity
from data import Database
import statistics
import datetime
import pygame

""" Auto-imported by ProjectMaker """
# . Upgrade ProjectMaker functions before starting new project GraphicalDance (below)
# . Make GraphicalDance (pretty clicker: points turning around circle and merging)

# ... Saves duplicate if 'save' button is spam (change saves functions) → json resolved it ?
# ? Also save graphics for each sim → don't need with DataManager.Saves
# . Since saving functions aren't asynchrone, use K_v to test them (with loading icon)
# . Divide graphics into 2 categories (entity & option) and add graphics types (box plot) → make one of each
# [next update] Make icons disappear whe ui is hide but show again if mouse on them
# [later] Upgrade flee method → Entities movements are weird because of furthest point ?


# [v0.0.1] Basic functions
# [v0.0.2] Create class for entity (rock, paper, scissors)
# [v0.0.3] Look for game files (fonts, images) online
# [v0.0.4] Test and adjust entities
# [v0.0.5] Avoid entities to move away from the map
# [v0.0.6] Display data on screen + add percent bg for nb entity
# [v0.0.7] Make simulation personalized in game → add parameters
# [v0.0.8] Add pause screen + key shortcuts + make entity with no target flee enemy
# [v0.0.9] Add lots of options for simulations (map borders, inf map, smart, follow mouse, appear with click)
# [v0.1.0] Add range for entity (detection for target and predator) + add overlay for entities
# [v0.1.1] Add menus + end of simulation if only one type remaining → add auto_end parameter
# [v0.1.2] Add sounds + chill music + mutation option (can change type randomly) -> create soundmanager class
# ... [v0.1.3] Add graphics + saves result + save menu → create datamanager class (+ take screenshots each turn)
# . [v0.1.4] Add possibility to add more entity type (Sheldon rps) -> add Sheldon parameter
# . [v0.1.5] Add tutorial + gamma + remove Echap shortcut + finish '!', '?' and '[later]' comments
# . [v0.9.9] Make documentations and complete functions description (purpose, args descr, args type)
# . [v1.0.0] Make the code into a .exe → create executioner class
class RPSSimulator:                                                             # Main class
    def __init__(self, name=None):
        # Program data
        self.name = self.get_project_name(name)                                 # Get name of the program
        self.creator = "One Shot"
        self.version = "v0.1.2"
        self.birthday: str = None                                               # Day of creation (15/10/2024)
        # Initializers
        pygame.init()
        pygame.display.init()
        # pygame.mixer.init()                                                   # Already in SoundManager
        pygame.font.init()
        db = Database()                                                         # Import important items
        # Booleans data
        self.is_fullscreen =    True
        self.is_saving =        False                                           # If program is saving today's sims
        self.running =          True                                            # Program running
        self.simulating =       False                                           # If on simulation (including pause menu)
        self.parametering =     False                                           # On parameter menu
        self.helping =          False                                           # On help menu
        self.save_menuing =     False                                           # On saves menu
        self.pausing =          False                                           # On pause menu
        self.asking_restart =   False                                           # Ask player if want to restart sim
        self.asking_goback =    False                                           # Ask player if want to go back to menu
        self.asking_saving =    False                                           # Ask player if want to save sim data
        # File data
        # self.path = Path.cwd()
        self.path =         db.PATH
        self.path_data =    db.PATH_DATA
        self.path_font =    db.PATH_FONT
        self.path_image =   db.PATH_IMAGE
        self.Files = ["data", "data/texts", "fonts", "images", "images/graphics",
            "images/screenshots", "logs", "musics", "saves", "screenshots", "sounds"]   # All files to create at first launch
        # Window data
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.full_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
        self.screen_size = self.screen.get_size()                               # Full screen by default
        pygame.display.set_caption(self.name)                                   # Give window a title
        pygame.display.set_icon(Entity(-1, "scissors").image)                   # Give window an icon
        self.gamma = 50
        # Game data
        self.pressed =  pygame.key.get_pressed()                                # Keyboard inputs
        self.mouse =    pygame.mouse.get_pos()                                  # Mouse coordinates
        self.horloge =  pygame.time.Clock()                                     # Limit nb of fps
        self.left_click = False                                                 # If has left-clicked on this turn
        self.fps = 60
        # Datas data
        self.DataManager = DataManager()
        # Colors data
        self.ColorNames = db.COLORNAMES
        self.Colors = db.COLORS
        self.bg_hover_color =   db.BG_HOVER_COLOR
        self.bg_color =         db.BG_COLOR
        self.borders_color =    db.BORDER_COLOR
        self.font_color =       db.FONT_COLOR
        self.selected_color =   db.SELECTED_COLOR
        # Entities data
        self.EntityManager = EntityManager(self.screen_size)
        self.EntityNames = list(db.ENTITYCOLORS.keys())
        self.EntityColors = db.ENTITYCOLORS
        self.Mutated_Entities = []                                              # Last entities to have mutated
        # Icons & Parameters data
        self.icon_size = 50
        self.icon_save = pygame.image.load(Path(self.path_image) / "save.png").convert_alpha()
        self.icon_save = pygame.transform.scale(self.icon_save, (self.icon_size, self.icon_size))
        self.icon_help = pygame.image.load(Path(self.path_image) / "help.png").convert_alpha()
        self.icon_help = pygame.transform.scale(self.icon_help, (self.icon_size, self.icon_size))
        self.icon_parameter = pygame.image.load(Path(self.path_image) / "parameter.png").convert_alpha()
        self.icon_parameter = pygame.transform.scale(self.icon_parameter, (self.icon_size, self.icon_size))
        gif = Image.open(Path(self.path_image) / "loading.gif")                 # Use for saving and loading
        self.LoadingIcon = [pygame.image.fromstring(frame.convert("RGBA").tobytes(), frame.size, "RGBA")
            for frame in ImageSequence.Iterator(gif)]                           # Each image of loading gif
        self.LoadingIcon = [pygame.transform.scale(frame, (self.icon_size * 3, self.icon_size * 3))
            for frame in self.LoadingIcon]
        self.current_frame = 0                                                  # Current image of loading gif
        self.ParametersManager = ParameterScreen()
        # Project initializer
        self.first_launch_game()                                                # Create files and stuff to avoid error
        db.create_texts()
        # Help screen data
        self.HelpTabs = db.HELPTABS
        self.HelpTexts = db.HELPTEXTS
        self.current_help_screen = 0                                            # Between 0-[nb -1]
        self.max_help_screen = len(self.HelpTabs)
        # Fonts data
        self.TextManager = TextManager(self.screen_size)
        self.Fonts = []
        self.FontSizes = db.FONTSIZES
        self.font_name: str = None
        self.main_font: pygame.font.Font = None
        # Timers data
        self.current_time = 0                                                   # Always give current time
        self.timer_simulation =     TimerManager()                              # Manage time elapsed since sim start
        self.timer_entity_infos =   TimerManager(3)                             # Timer for more infos : 3s
        self.timer_turn =           TimerManager(0, 0, 10)                      # Manage turn duration
        self.timer_one_sec =        TimerManager(1)                             # Used to collect sim datas every second
        # [later] replace by TimerManager
        self.event_loading = pygame.USEREVENT + 1                               # Personalized event for loading icon ...
        pygame.time.set_timer(self.event_loading, 100)                          # ...linked to a timer (trigger every 0.1s)
        # Main function
        self.run()

    @staticmethod
    def get_project_name(name):                                                 # Return directory name of project
        return str(Path(__file__).parent.name) if name is None else name

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
            if not Path(path).exists():
                Path(path).mkdir(parents=True, exist_ok=True)
        if not Path(f"{self.path_data}/data.txt").exists():
            with open(f"{self.path_data}/data.txt", 'w') as file:               # Create game data file
                file.write("")

    def look_for_birthday(self):
        if self.birthday is None:                                               # If first launch
            with open(f"{self.path_data}/data.txt", 'r') as file:
                lines = file.readlines()
                birthday = lines[3].strip() if len(lines) >= 4 else None        # Check if data saved
            self.birthday = self.get_current_date() if birthday is None else birthday

    def fill_data_lists(self):                                                  # Fill game lists with data from files
        # Fill game fonts
        self.Fonts = [_ for _ in Path(self.path_font).iterdir() if _.suffix == ".ttf"]
        if len(self.Fonts) > 0:
            self.font_name = self.Fonts[0]
            font_path = f"{self.path_font}/{self.font_name}"
        else:
            self.font_name = None
            font_path = None
        self.main_font = pygame.font.Font(font_path, 80)

    def save_game_data(self):                                                   # Write most of the game data
        with open(f"{self.path_data}/data.txt", 'w') as file:
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

    def get_mouse_hover_position(self, pos):
        return pos[0] <= self.mouse[0] <= pos[0] + pos[2] and pos[1] <= self.mouse[1] <= pos[1] + pos[3]

    def get_click_on_position(self, pos):
        return self.get_mouse_hover_position(pos) and self.left_click

    def get_not_click_on_position(self, pos):
        return not self.get_mouse_hover_position(pos) and self.left_click

    def run(self):                                                              # Main function
        self.EntityManager.SoundManager.play_music()                            # Play random music

        while self.running:                                                     # While playing
            self.current_time = time()
            self.pressed = pygame.key.get_pressed()
            self.mouse = pygame.mouse.get_pos()
            self.left_click = False

            self.input_manager()                                                # Keyboard, mouse, arrows, etc.

            self.EntityManager.check_spawn_entity(self.simulating, self.pausing, self.left_click, self.mouse)
            self.display_manager()

            if self.simulating and not self.pausing:
                self.timer_turn.check_loop_end(self.current_time)

            pygame.display.flip()                                               # Update window
            self.horloge.tick(self.fps)

    def input_manager(self):
        for event in pygame.event.get():                                        # Get keyboard events
            if event.type == pygame.QUIT:
                self.close_game()

            if event.type == self.event_loading:
                if self.is_saving:
                    self.current_frame = (self.current_frame + 1) % len(self.LoadingIcon)   # Next frame

            if event.type == pygame.MOUSEBUTTONUP:                              # If left click (release button)
                if event.button == 1:
                    self.left_click = True

            if event.type == pygame.KEYDOWN:                                    # Keyboard entries
                if event.key == pygame.K_ESCAPE:                                # Close simulation
                    self.close_game()

                if event.key == pygame.K_SPACE:
                    if not self.simulating:                                     # Main menu
                        self.start_simulation()
                    elif not (self.parametering or self.save_menuing or
                            self.asking_goback or self.asking_restart):
                        self.pausing = not self.pausing
                        if self.pausing:
                            self.pause_simulation()
                        else:
                            self.resume_simulation()

                if event.key == pygame.K_UP:
                    if self.save_menuing:
                        self.DataManager.next_turn()                            # Display next turn of simulation
                elif event.key == pygame.K_DOWN:
                    if self.save_menuing:
                        self.DataManager.previous_turn()                        # Display previous turn of simulation

                if event.key == pygame.K_LEFT:
                    if self.parametering:                                       # Display previous tab
                        self.ParametersManager.previous_tab()
                    elif self.save_menuing:
                        self.DataManager.previous_tab()
                    elif self.helping:
                        self.previous_help_screen()
                elif event.key == pygame.K_RIGHT:
                    if self.parametering:                                       # Display next tab
                        self.ParametersManager.next_tab()
                    elif self.save_menuing:
                        self.DataManager.next_tab()
                    elif self.helping:
                        self.next_help_screen()

                if event.key == pygame.K_h:                                     # Hide/show UI
                    self.ParametersManager.is_ui_hide = not self.ParametersManager.is_ui_hide

                # Warnings
                if event.key == pygame.K_r:                                     # (Re)start simulation
                    if self.simulating:
                        self.asking_restart = True
                        self.pause_simulation()                                 # Paused when alert messages
                    else:
                        self.start_simulation()

                if event.key == pygame.K_q:                                     # Quit simulation
                    if self.simulating:
                        if self.DataManager.is_sim_saved:
                            self.asking_goback = True
                        else:
                            self.asking_saving = True
                        self.pause_simulation()

                # Screens
                if event.key == pygame.K_p:                                     # Open/close parameters screen
                    self.parametering = not self.parametering
                    if self.parametering:
                        self.open_parameters()
                    else:
                        self.close_parameters()

                if event.key == pygame.K_s:                                     # Open/close saves screen
                    self.save_menuing = not self.save_menuing
                    if self.save_menuing:
                        self.open_saves()
                    else:
                        self.close_saves()

                if event.key == pygame.K_i:                                     # Open/close help screen
                    self.helping = not self.helping
                    if self.helping:
                        self.open_help()
                    else:
                        self.close_help()

    def display_manager(self):                                                  # Display everything on screen
        self.screen.fill(self.bg_color)

        if not self.simulating:                                                 # Main menu
            self.display_menu()
        else:                                                                   # On simulation
            self.TextManager.display_bg_name(self.screen, self.name)

            if self.ParametersManager.is_ui_on_front:
                self.display_entities()
                self.display_ui()
            else:                                                               # Display UI on the back
                self.display_ui()
                self.display_entities()

            self.display_icons()

            self.check_end_simulation()                                         # Display if only one type of entity remain

            if self.pausing:                                                    # Display in front of almost everything...
                self.display_pause()
            else:
                self.Mutated_Entities += self.EntityManager.move_entities(self.screen_size, self.mouse,
                    self.ParametersManager.is_map_borders, self.ParametersManager.is_infinity_map)

                self.display_mutated_entities()

            self.collect_datas()                                                # Collect data for DataManager

        # Works everywhere
        if self.helping:                                                        # ...except for menus...
            self.display_help_screen()

        if self.save_menuing:
            self.display_data_screen()

        if self.parametering:
            self.display_parameters_screen()

        self.display_alert_messages()                                           # ...and alert messages

        if self.is_saving:
            self.display_loading_icon()

    def display_menu(self):                                                     # Main menu
        self.TextManager.display_message(self.screen, 0.5, 0.35, self.name, "giant")

        if not self.ParametersManager.is_ui_hide:                               # Program data
            self.TextManager.display_message(self.screen, 0.5, 0.45, f"Made by {self.creator}", "big")
            self.TextManager.display_message(self.screen, 0.02, 0.95, f"Created {self.birthday}", "middle", "left")
            self.TextManager.display_message(self.screen, 0.98, 0.95, self.version, "middle", "right")

        trio = (self.screen, self.mouse, self.left_click)
        condition = not (self.parametering or self.save_menuing or self.helping)
        if self.TextManager.display_button(*trio, f"Start simulation", (0.41, 0.55, 0.18, 0.1),
                self.borders_color, True, self.bg_color) and condition:
            self.left_click = False                                             # Prevent any side effects
            self.start_simulation()

        hover_color = (222, 222, 222)
        if self.TextManager.display_button(*trio, f"Options", (0.41, 0.66, 0.18, 0.1),
                self.bg_color, bg_color_hover=hover_color) and condition:
            self.open_parameters()

        if self.TextManager.display_button(*trio, f"Quit", (0.41, 0.77, 0.18, 0.1),
                self.bg_color, bg_color_hover=hover_color) and condition:
            self.close_game()

        self.display_icons()

        if not self.ParametersManager.is_ui_hide:
            Commands = ["Space : Start", "S : Save menu", "H : Hide UI",
                "I : Informations", "P : Parameters", "Echap : Quit"]
            for i, command in enumerate(Commands):
                self.TextManager.display_message(self.screen, 0.98, 0.35 + 0.05 * i, command, None, "right")
        else:
            self.TextManager.display_message(self.screen, 0.98, 0.45, "H : Show UI", None, "right")

    def display_entities(self):                                                 # Display entities on screen
        for entity in self.EntityManager.Entities:
            self.screen.blit(entity.image, entity.coords)

        if not self.ParametersManager.is_ui_hide:
            for entity in self.EntityManager.Entities:                          # In another loop to avoid overlay beyond entities
                if entity.is_mouse_over(self.mouse):
                    if self.left_click:                                         # Display more infos (circles)
                        self.timer_entity_infos.start(self.current_time)

                    if self.timer_entity_infos.check_loop_end(self.current_time) > 0:   # After the loop end
                        self.timer_entity_infos.pause(self.current_time)
                    elif self.timer_entity_infos.check_loop_end(self.current_time) < 0: # Display while timer is on
                        self.display_entity_more_infos(entity)

                    self.display_entity_infos(entity)                           # Display in front of more infos

                    break                                                       # Only display one at a time

    def display_entity_infos(self, entity):
        gap = 5                                                                 # Mouse size
        width = self.screen_size[0] * 0.2
        height = self.screen_size[1] * 0.45 - gap
        pos = [self.mouse[0], self.mouse[1] - height, width, height]            # Top right
        if pos[0] + pos[2] > self.screen_size[0] + gap:
            pos[0] -= width + gap                                               # Go left
        if pos[1] < gap:
            pos[1] += height + gap * 2                                          # Go down
        self.TextManager.display_screen(self.screen, pos, border_radius=20)

        coords = ((pos[0] + pos[2] * 0.5) / self.screen_size[0],
        (pos[1] + pos[3] * 0.1) / self.screen_size[1])
        self.TextManager.display_message(self.screen, *coords, entity.name.capitalize(), "middle")

        target_coords = f"{int(entity.target.coords[0])}:{int(entity.target.coords[1])}" \
            if entity.target else "no target found"
        predator_coords = f"{int(entity.predator.coords[0])}:{int(entity.predator.coords[1])}" \
            if entity.predator else "no predator found"
        Infos = (f"Id : {entity.id}", f"Smart : {'On' if entity.is_smart else 'Off'}",
        f"Coords : {int(entity.coords[0])}:{int(entity.coords[1])}",
        f"Size : {entity.size} pixels", f"Range : {entity.range} pixels",
        f"Speed : {entity.speed * self.fps} px/sec",
        f"Target type : {entity.target_name.capitalize()}", f"Target coords : {target_coords}",
        f"Predator type : {entity.predator_name.capitalize()}", f"Predator coords : {predator_coords}",
        f"Behaviour : {entity.behaviour}")
        size = self.FontSizes["small"] + 2
        for i, info in enumerate(Infos):
            coords = ((pos[0] + pos[2] * 0.05) / self.screen_size[0],
            (pos[1] + pos[3] * 0.2 + (i * size)) / self.screen_size[1])
            self.TextManager.display_message(self.screen, *coords, info, "small", "left")

        self.TextManager.set_font_color(self.bg_color)
        coords = ((pos[0] + pos[2] * 0.95) / self.screen_size[0],
        (pos[1] + pos[3] * 0.2) / self.screen_size[1])
        self.TextManager.display_message(self.screen, *coords, "Click to see more", "small", "right")
        self.TextManager.set_font_color()
        self.TextManager.set_font_size()

    # Default screen's position : top right of the mouse
    def display_entity_more_infos(self, entity):                                # Draw circles
        center = entity.image.get_rect(topleft=entity.coords).center
        if self.EntityManager.is_entity_range:                                  # Only show range if option is active
            pygame.draw.circle(self.screen, self.Colors["wheat"], center, entity.range, 3)

        if entity.target:                                                       # Show current target
            for target in self.EntityManager.Entities:
                if target == entity.target:
                    center = target.image.get_rect(topleft=target.coords).center
                    pygame.draw.circle(self.screen, self.Colors["cyan"],
                        center, target.size + 5, 5)

        if entity.predator:                                                     # Show current predator
            for predator in self.EntityManager.Entities:
                if predator == entity.predator:
                    center = predator.image.get_rect(topleft=predator.coords).center
                    pygame.draw.circle(self.screen, self.Colors["yellow"], center, predator.size + 5, 5)

    def display_ui(self):                                                       # Data of simulation
        if not self.ParametersManager.is_ui_hide:
            # Display number of entities in simulation (up left corner)
            self.TextManager.display_message(self.screen, 0.02, 0.1,
                f"Entities (x{len(self.EntityManager.Entities)})", "middle", "left")
            NumberEntities = self.EntityManager.get_number_entities()
            for i, (name, quantity) in enumerate(NumberEntities.items()):
                value = (quantity / len(self.EntityManager.Entities)) * 100
                percent = round(value, 2) if round(value, 2) % 1 else int(value)
                pos = (0.02 * self.screen_size[0], (0.1 + 0.03 * (i + 1)) * self.screen_size[1],
                percent * 2, 0.03 * self.screen_size[1])
                pygame.draw.rect(self.screen, self.EntityColors[name], pos)
                text = f"{percent}%" if self.ParametersManager.is_nb_in_percent else f"x{quantity}"
                self.TextManager.display_message(self.screen, 0.02, 0.1 + 0.03 * (i + 1),
                    f"- {name.capitalize()} ({text})", None, "left")

            # Display simulation timer (up middle)
            time_past = self.timer_simulation.get_elapsed_time(self.current_time)
            self.TextManager.display_message(self.screen, 0.5, 0.05, f"{time_past}s", None)

            # Display commands for simulation (middle right)
            Commands = ["H : Hide UI", "R : Restart", "Space : Pause",
                "S : Save menu", "P : Parameters", "Q : Return to menu", "Echap : Quit"]

            for i, command in enumerate(Commands):
                self.TextManager.display_message(self.screen, 0.98, 0.35 + 0.05 * i, command, None, "right")

            # Display entity informations (bottom left corner)
            self.TextManager.display_message(self.screen, 0.02, 0.85, f"Entity data : ", None, "left")
            self.TextManager.display_message(self.screen, 0.02, 0.88, f"- size : {Entity(0, None).size}", None, "left")
            self.TextManager.display_message(self.screen, 0.02, 0.91, f"- speed : {Entity(0, None).speed}", None, "left")
            if self.EntityManager.is_smart_entity:
                self.TextManager.display_message(self.screen, 0.02, 0.94, f"- smart : "
                    f"{'On' if self.EntityManager.is_smart_entity else 'Off'}", None, "left")

            # Display turn (bottom middle)
            if self.ParametersManager.is_display_turn:
                self.TextManager.display_message(self.screen, 0.5, 0.98, f"Turn n°{self.timer_turn.nb_loop}", None)
        else:
            command = "H : Show UI"
            self.TextManager.display_message(self.screen, 0.98, 0.4, command, None, "right")

    def display_pause(self):                                                    # Pause menu
        surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        surface.fill((255, 255, 255, 128))                                      # Make it a transparent
        self.screen.blit(surface, (0, 0))

        self.TextManager.display_message(self.screen, 0.5, 0.25, f"Pause", "big")

        trio = (self.screen, self.mouse, self.left_click)
        condition = not (self.parametering or self.save_menuing or self.helping or
            self.asking_restart or self.asking_goback or self.asking_saving)
        hover_color = (222, 222, 222)

        if self.TextManager.display_button(*trio, f"Resume", (0.41, 0.44, 0.18, 0.1),
                bg_color_hover=hover_color, no_bg=True) and condition:
            self.resume_simulation()

        if self.TextManager.display_button(*trio, f"Options", (0.41, 0.55, 0.18, 0.1),
                bg_color_hover=hover_color, no_bg=True) and condition:
            self.open_parameters()

        if self.TextManager.display_button(*trio, f"Menu", (0.41, 0.66, 0.18, 0.1),
                bg_color_hover=hover_color, no_bg=True) and condition:
            if self.DataManager.is_sim_saved:
                self.asking_goback = True
            else:
                self.asking_saving = True
            self.left_click = False

    def pause_simulation(self):
        self.pausing = True
        self.timer_one_sec.pause(self.current_time)
        self.timer_simulation.pause(self.current_time)

    def resume_simulation(self):
        self.pausing = False
        self.timer_one_sec.unpause(self.current_time)
        self.timer_simulation.unpause(self.current_time)

    def open_saves(self):
        self.save_menuing = True
        if self.simulating:
            self.pause_simulation()                                         # Pause simulation when open save screen

    def close_saves(self):
        self.save_menuing = False
        if self.simulating and not self.pausing:
            self.resume_simulation()

    def open_help(self):
        self.helping = True
        if self.simulating:
            self.pause_simulation()                                         # Pause simulation when open help screen

    def close_help(self):
        self.helping = False
        if self.simulating and not self.pausing:
            self.resume_simulation()

    def open_parameters(self):
        self.parametering = True
        if self.simulating:
            self.pause_simulation()                                         # Pause simulation when open parameters

    def close_parameters(self):
        self.parametering = False
        if self.simulating and not self.pausing:
            self.resume_simulation()

    def display_icons(self):                                                    # To access some screens
        condition = not (self.save_menuing or self.helping or self.parametering)

        coords = (int(self.icon_size * 0.5), int(self.icon_size * 0.5))         # Top left
        self.screen.blit(self.icon_save, coords)
        pos = (*coords, self.icon_size, self.icon_size)
        if self.get_click_on_position(pos) and condition:                       # If click on icon
            self.open_saves()
            self.left_click = False

        coords = (self.screen_size[0] - int(self.icon_size * 3.5), int(self.icon_size * 0.5))
        self.screen.blit(self.icon_help, coords)
        pos = (*coords, self.icon_size, self.icon_size)
        if self.get_click_on_position(pos) and condition:                       # If click on icon
            self.open_help()
            self.left_click = False

        coords = (self.screen_size[0] - int(self.icon_size * 1.5), int(self.icon_size * 0.5))   # Top right
        self.screen.blit(self.icon_parameter, coords)
        pos = (*coords, self.icon_size, self.icon_size)
        if self.get_click_on_position(pos) and condition:                       # If click on icon
            self.open_parameters()
            self.left_click = False

        if self.is_saving:
            image = self.LoadingIcon[self.current_frame]
            self.screen.blit(image, (self.screen_size[0] - self.icon_size * 3,
                                     self.screen_size[1] - self.icon_size * 3.5))
        else:
            self.current_frame = 0

    def display_mutated_entities(self):                                         # Display all mutated entities for one turn
        if len(self.Mutated_Entities) > 0:                                      # If at least one entity have mutated
            for entity in self.Mutated_Entities:
                if entity.timer_mutation.get_paused():
                    entity.timer_mutation.start(self.current_time)
                is_loop = entity.timer_mutation.check_loop_end(self.current_time)

                if is_loop == 1:                                                # Remove entity when timer has loop
                    entity.timer_mutation.start(self.current_time)              # Reset timer
                    entity.timer_mutation.pause(self.current_time)
                    self.Mutated_Entities.remove(entity)
                else:                                                           # If timer started
                    percent_x = entity.coords[0] / self.screen_size[0]
                    percent_y = entity.coords[1] / self.screen_size[1]

                    self.TextManager.set_font_color("blue")
                    self.TextManager.display_message(self.screen, percent_x, percent_y, f"Mutated ({entity.id})")
                    self.TextManager.set_font_color()

    def display_parameters_screen(self):                                        # Display all parameter screens
        pos = self.TextManager.display_box(self.screen)
        if self.get_not_click_on_position(pos):
            self.close_parameters()

        self.TextManager.display_message(self.screen, 0.5, 0.18, f"Parameters", "big")

        self.display_parameters_tabs_list()

        current = self.ParametersManager.current_tab
        if current == self.ParametersManager.Tabs[0]:
            self.display_tab_main_screen()
        elif current == self.ParametersManager.Tabs[1]:
            self.display_tab_sim_screen()
        elif current == self.ParametersManager.Tabs[2]:
            self.display_tab_entities_screen()
        elif current == self.ParametersManager.Tabs[3]:
            self.display_tab_sounds_screen()

        self.TextManager.display_description(self.screen, self.mouse)           # Display at the end to be display above all

    def display_parameters_tabs_list(self):
        rect = (0.15, 0.22, 0.7, 0.05)
        nb = len(self.ParametersManager.Tabs)
        length = rect[2] / nb                                                   # Tab width
        width = 5

        pos = (self.screen_size[0] * rect[0], self.screen_size[1] * rect[1],
        self.screen_size[0] * rect[2], self.screen_size[1] * rect[3])
        pygame.draw.rect(self.screen, self.borders_color, pos, width)           # Big rectangle

        for i, tab in enumerate(self.ParametersManager.Tabs):
            x = (rect[0] + length * i) + length / 2
            y = rect[1] + rect[3] / 2
            self.TextManager.display_message(self.screen, x, y, tab, "middle")  # Tab name

            if i > 0:                                                           # Vertical line
                point1 = (self.screen_size[0] * (rect[0] + length * i), self.screen_size[1] * rect[1])
                point2 = (point1[0], point1[1] + self.screen_size[1] * rect[3] - width)
                pygame.draw.line(self.screen, self.borders_color, point1, point2, width)

        for i, tab in enumerate(self.ParametersManager.Tabs):                   # Display above all tabs
            x = (rect[0] + length * i)
            pos = (self.screen_size[0] * x, self.screen_size[1] * rect[1],
            self.screen_size[0] * length + 1, self.screen_size[1] * rect[3])
            if self.get_click_on_position(pos):                                 # Select another tab
                self.ParametersManager.current_tab = tab

            if self.ParametersManager.current_tab == tab:                       # Highlight current tab
                pygame.draw.rect(self.screen, self.selected_color, pos, width)

    def display_tab_main_screen(self):                                          # Display main screen
        trio = (self.screen, self.mouse, self.left_click)

        # First column
        x1 = 0.15

        self.is_fullscreen, as_change = self.TextManager.display_parameter(*trio,
            x1, 0.3, self.is_fullscreen, "Fullscreen : ")
        if as_change:
            self.change_fullscreen()

        rect = [x1, 0.35, 0.025, 0.04]
        func1 = self.reduce_gamma
        func2 = self.increase_gamma
        nb = self.gamma
        nb_max = 100
        self.TextManager.use_unactive_color()
        result = self.display_gradient_line(rect, func1, func2, f"Gamma : {nb}", nb, nb_max)
        self.TextManager.set_font_color()
        if result:
            self.gamma = result

        # Second column
        x2 = 0.5

        self.TextManager.display_message(self.screen, 0.5, 0.5, "Work in progress...", "giant")

    # [later] Make all program sizes dynamic and change them
    def change_fullscreen(self):
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_size = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode((self.full_size[0] // 2, self.full_size[1] // 2))
            self.screen_size = self.screen.get_size()

    def display_tab_sim_screen(self):                                           # Display simulation screen
        trio = (self.screen, self.mouse, self.left_click)

        # First column
        x1 = 0.15

        if self.ParametersManager.is_ui_hide:
            self.TextManager.use_unactive_color()
        self.ParametersManager.is_display_turn, _ = self.TextManager.display_parameter(*trio,
            x1, 0.3, self.ParametersManager.is_display_turn, "Display number of turns : ")

        if self.ParametersManager.is_display_turn:                              # Select pause for each turn
            if self.ParametersManager.is_ui_hide:
                self.TextManager.use_unactive_color()
            rect = [x1, 0.35, 0.025, 0.04]
            func1 = self.timer_turn.reduce_duration
            func2 = self.timer_turn.increase_duration
            nb = self.timer_turn.duration
            s = "s" if nb > 1 else ""
            text = f"Turn pause : {nb} sec{s}"
            nb_max = self.timer_turn.max_duration
            result = self.display_gradient_line(rect, func1, func2, text, nb, nb_max)
            if result:
                self.timer_turn.set_duration(result)

        descr = ("When on, forbid entities to exit screen.\n"
                 "Incompatible with 'Screen is toroidal'")
        self.ParametersManager.is_map_borders, as_change = self.TextManager.display_parameter(*trio,
            x1, 0.44, self.ParametersManager.is_map_borders, "Entities stay on screen : ", descr)
        if as_change and self.ParametersManager.is_map_borders:
            self.ParametersManager.is_infinity_map = False

        descr = ("When on, entities that exit screen end up on the other side of the screen.\n"
                 "Incompatible with 'Entities stay on screen'")
        self.ParametersManager.is_infinity_map, as_change = self.TextManager.display_parameter(*trio,
            x1, 0.51, self.ParametersManager.is_infinity_map, "Screen is toroidal : ", descr)
        if as_change and self.ParametersManager.is_infinity_map:
            self.ParametersManager.is_map_borders = False

        if self.ParametersManager.is_ui_hide:
            self.TextManager.use_unactive_color()
        descr = "When on, display quantity of entity in percent amount"
        self.ParametersManager.is_nb_in_percent, _ = self.TextManager.display_parameter(*trio,
            x1, 0.58, self.ParametersManager.is_nb_in_percent, "Quantity is in percent : ", descr)

        # Second column
        x2 = 0.5

        if self.ParametersManager.is_ui_hide:
            self.TextManager.use_unactive_color()
        descr = "When on, display ui in front of entities. When off, display it behind"
        self.ParametersManager.is_ui_on_front, _ = self.TextManager.display_parameter(*trio,
            x2, 0.3, self.ParametersManager.is_ui_on_front, "UI is on front : ", descr)

        descr = "When on, do not display ui"
        self.ParametersManager.is_ui_hide, _ = self.TextManager.display_parameter(*trio,
            x2, 0.37, self.ParametersManager.is_ui_hide, "UI is hide : ")

        descr = "When on, simulation will automatically end if only one type of entity remains"
        self.ParametersManager.is_auto_end, _ = self.TextManager.display_parameter(*trio,
            x2, 0.44, self.ParametersManager.is_auto_end, "Auto end : ", descr)

        descr = "When on, sim will automatically loop on save screen"
        self.DataManager.is_auto_play, _ = self.TextManager.display_parameter(*trio,
            x2, 0.51, self.DataManager.is_auto_play, "Auto play : ", descr)

        descr = "When on, program will automatically save before going back to menu"
        self.DataManager.is_auto_save, _ = self.TextManager.display_parameter(*trio,
            x2, 0.58, self.DataManager.is_auto_save, "Auto save : ", descr)

    def display_tab_entities_screen(self):                                      # Display entities screen
        trio = (self.screen, self.mouse, self.left_click)

        # First column
        x1 = 0.15

        if self.EntityManager.nb_entities <= 0:
            self.TextManager.use_unactive_color()
        descr = "When on, will generate the same amount of entities for each types before simulation starts"
        self.EntityManager.balanced, _ = self.TextManager.display_parameter(*trio,
            x1, 0.3, self.EntityManager.balanced, "Balanced : ", descr)

        rect = [x1, 0.35, 0.025, 0.04]
        func1 = self.EntityManager.reduce_nb_entities
        func2 = self.EntityManager.increase_nb_entities
        nb = self.EntityManager.nb_entities
        nb_max = self.EntityManager.nb_max
        result = self.display_gradient_line(rect, func1, func2, f"Quantity : {nb}", nb, nb_max)
        if result:
            self.EntityManager.set_nb_entities(result)

        if self.EntityManager.nb_entities <= 0:
            self.TextManager.use_unactive_color()
        descr = "When on, entities will flee their predator when there is no target left"
        self.EntityManager.is_smart_entity, as_change = self.TextManager.display_parameter(*trio,
            x1, 0.45, self.EntityManager.is_smart_entity, "Entities are smart : ", descr)
        if as_change:
            if self.EntityManager.is_smart_entity:
                self.EntityManager.make_entities_smart()
            else:
                self.EntityManager.make_entities_dumb()

        if self.EntityManager.nb_entities <= 0:
            self.TextManager.use_unactive_color()
        radius = round(self.EntityManager.entity_range * (1.05 if self.EntityManager.is_smart_entity else 1), 2)
        descr = f"When on, entity can only detect peers within a given radius ({radius}px)"
        self.EntityManager.is_entity_range, _ = self.TextManager.display_parameter(*trio,
            x1, 0.51, self.EntityManager.is_entity_range, "Entity have range : ", descr)

        if self.EntityManager.nb_entities <= 0:
            self.TextManager.use_unactive_color()
        rect = [x1, 0.58, 0.025, 0.04]
        func1 = self.EntityManager.reduce_speed
        func2 = self.EntityManager.increase_speed
        nb = self.EntityManager.entity_speed
        nb_max = self.EntityManager.max_entity_speed
        result = self.display_gradient_line(rect, func1, func2, f"Speed : {nb}", nb, nb_max)
        if result:
            self.EntityManager.entity_speed = result

        if self.EntityManager.nb_entities <= 0 or not self.EntityManager.is_entity_range:
            self.TextManager.use_unactive_color()
        rect = [x1, 0.68, 0.025, 0.04]
        func1 = self.EntityManager.reduce_range
        func2 = self.EntityManager.increase_range
        nb = self.EntityManager.entity_range
        nb_max = self.EntityManager.max_entity_range
        result = self.display_gradient_line(rect, func1, func2, f"Range : {nb}", nb, nb_max)
        if result:
            self.EntityManager.entity_range = result

        if self.EntityManager.nb_entities <= 0:
            self.TextManager.use_unactive_color()
        rect = [x1, 0.78, 0.025, 0.04]
        func1 = self.EntityManager.reduce_size
        func2 = self.EntityManager.increase_size
        nb = self.EntityManager.entity_size
        nb_max = self.EntityManager.max_entity_size
        result = self.display_gradient_line(rect, func1, func2, f"Size : {nb}", nb, nb_max)
        if result:
            self.EntityManager.entity_size = result

        # Second column
        x2 = 0.5

        if len(self.EntityManager.Entities) <= 0:
            self.TextManager.use_unactive_color()
        descr = "When on, make selected entity type go to mouse coordinates"
        self.EntityManager.is_follow_mouse, _ = self.TextManager.display_parameter(*trio,
            x2, 0.3, self.EntityManager.is_follow_mouse, "Entities follow mouse : ", descr)
        if self.EntityManager.is_follow_mouse:                                  # Select following entity
            self.TextManager.display_message(self.screen, x2, 0.35, f"Entity to follow : "
                                                                    f"{self.EntityManager.entity_to_follow_mouse}", "middle", "left")
            entity = self.display_entities_button(self.screen_size[0] * x2, self.screen_size[1] * 0.4,
                current_entity_name=self.EntityManager.entity_to_follow_mouse)
            if entity is not None:
                self.EntityManager.entity_to_follow_mouse = entity

        descr = "When on, make spawn the selected entity on mouse coordinates"
        self.EntityManager.is_spawn_with_click, _ = self.TextManager.display_parameter(*trio,
            x2, 0.51, self.EntityManager.is_spawn_with_click, "Spawn entity on click : ", descr)
        if self.EntityManager.is_spawn_with_click:                              # Select entity to spawn
            text = f"Entity to spawn : {self.EntityManager.entity_to_spawn}"
            self.TextManager.display_message(self.screen, x2, 0.56, text, "middle", "left")
            entity = self.display_entities_button(self.screen_size[0] * x2, self.screen_size[1] * 0.61,
                current_entity_name=self.EntityManager.entity_to_spawn)
            if entity is not None:
                self.EntityManager.entity_to_spawn = entity

        if self.EntityManager.nb_entities <= 0:
            self.TextManager.use_unactive_color()
        descr = "When on, entity can randomly change their speed, range, size, smartness or type"
        self.EntityManager.is_mutating, _ = self.TextManager.display_parameter(*trio,
            x2, 0.71, self.EntityManager.is_mutating, "Entity can mutate : ", descr)

        if self.EntityManager.is_mutating:
            if self.EntityManager.nb_entities <= 0:
                self.TextManager.use_unactive_color()
            rect = [x2, 0.78, 0.025, 0.04]
            func1 = self.EntityManager.reduce_mutate_chance
            func2 = self.EntityManager.increase_mutate_chance
            nb = self.EntityManager.mutate_chance
            nb_max = 100
            result = self.display_gradient_line(rect, func1, func2, f"Mutation chance : {nb}%", nb, nb_max)
            if result:
                self.EntityManager.mutate_chance = result

    def display_tab_sounds_screen(self):                                        # Display sounds screen
        trio = (self.screen, self.mouse, self.left_click)

        # First column
        x1 = 0.15

        self.TextManager.set_font_color(self.bg_color)
        sound = self.EntityManager.SoundManager.sound_name
        message = f"Playing '{sound.replace('.mp3', '')}'" if sound else "No sound if playing"
        self.TextManager.display_message(self.screen, x1, 0.3, message, position="left")
        self.TextManager.set_font_color()

        rect = [x1, 0.35, 0.025, 0.04]
        func1 = self.EntityManager.SoundManager.reduce_volume
        func2 = self.EntityManager.SoundManager.increase_volume
        nb = self.EntityManager.SoundManager.sound_volume
        result = self.display_gradient_line(rect, func1, func2, f"Sounds : {int(nb * 100)}%", nb, 1)
        if result:
            self.EntityManager.SoundManager.set_volume(result)

        descr = "Click to mute playing sounds, in case of a sound problem"
        if self.TextManager.display_button(*trio, "Mute all sounds", (x1, 0.44, 0.15, 0.05),
                has_border=True, bg_color_hover=self.bg_hover_color, description=descr):
            self.EntityManager.SoundManager.stop_all_sounds()

        # Second column
        x2 = 0.5

        self.TextManager.set_font_color(self.bg_color)
        music = self.EntityManager.SoundManager.music_name
        message = f"Playing '{music.replace('.mp3', '')}'" if music else "No music"
        self.TextManager.display_message(self.screen, x2, 0.3, message, position="left")
        self.TextManager.set_font_color()

        rect = [x2, 0.35, 0.025, 0.04]
        func1 = self.EntityManager.SoundManager.reduce_music_volume
        func2 = self.EntityManager.SoundManager.increase_music_volume
        nb = self.EntityManager.SoundManager.music_volume
        result = self.display_gradient_line(rect, func1, func2, f"Music : {int(nb * 100)}%", nb, 1)
        if result:
            self.EntityManager.SoundManager.set_music_volume(result)

        if self.EntityManager.SoundManager.is_loop:
            self.TextManager.use_unactive_color()
        if self.TextManager.display_button(*trio, "Next music",
                (x2, 0.44, 0.15, 0.05), has_border=True, bg_color_hover=self.bg_hover_color):
            self.EntityManager.SoundManager.play_music()
        self.TextManager.set_font_color()

        descr = "When on, play current music endlessly"
        self.EntityManager.SoundManager.is_loop, _ = self.TextManager.display_parameter(*trio,
            x2, 0.51, self.EntityManager.SoundManager.is_loop, "Endless music : ", descr)

    def display_gradient_line(self, rect, func1, func2, title="Quantity", nb=50, nb_max=100, nb_min=0):
        trio = (self.screen, self.mouse, self.left_click)
        x1 = rect[0]

        self.TextManager.display_message(self.screen, rect[0], rect[1], title, "middle", "left")
        self.TextManager.set_font_color()
        rect[0] += 0.2
        if self.TextManager.display_button(*trio, "-", rect, "lightgrey", True) and nb > nb_min:
            func1()
        rect[0] += 0.05
        if self.TextManager.display_button(*trio, "+", rect, "lightgrey", True) and nb < nb_max:
            func2()

        rect[1] += 0.05
        new_nb = None
        pos = [self.screen_size[0] * x1, self.screen_size[1] * rect[1], self.screen_size[0] * 0.28, 10]
        pygame.draw.rect(self.screen, self.bg_color, pos, border_radius=int(pos[3] * 0.5))
        if self.get_click_on_position(pos):
            length = max(nb_min, abs(self.mouse[0] + 3 - pos[0]))               # '+3' to adjust final position
            new_nb = (length / pos[2]) * nb_max
            new_nb = int(new_nb) if nb_max > 1 else round(new_nb, 2)

        pos[2] = (nb / nb_max) * pos[2]                                         # Current percent
        pygame.draw.rect(self.screen, self.borders_color, pos, border_radius=int(pos[3] * 0.5))

        return new_nb

    def increase_gamma(self):                                                   # Increase and check gamma value
        self.gamma += 1
        self.gamma = min(self.gamma, 100)

    def reduce_gamma(self):                                                     # Reduce and check gamma value
        self.gamma -= 1
        self.gamma = max(self.gamma, 0)

    # Buttons with image of each entity
    def display_entities_button(self, x, y, image_size=50, gap=10, current_entity_name=None):
        width = 3                                                               # Border width
        Each = [Entity(0, name) for name in self.EntityManager.EntityNames]
        for i, entity in enumerate(Each):
            image = pygame.transform.scale(entity.image, (image_size, image_size))
            coords = (x + (image_size + gap) * i, y)
            pos = (coords[0] - width, coords[1] - width,
            image_size + width * 2, image_size + width * 2)
            border_color = self.selected_color if current_entity_name and \
                current_entity_name == entity.name else self.TextManager.borders_color
            pygame.draw.rect(self.screen, border_color, pos, width, width)
            self.screen.blit(image, coords)
            if self.get_click_on_position(pos):
                return entity.name
        return None

    def next_help_screen(self):
        self.current_help_screen = (self.current_help_screen + 1) % self.max_help_screen

    def previous_help_screen(self):
        self.current_help_screen = (self.current_help_screen - 1) % self.max_help_screen

    # ! Use function to draw text in a rectangle instead (in TextManager) : texts with borders
    def display_help_screen(self):
        pos = self.TextManager.display_box(self.screen)
        if self.get_not_click_on_position(pos):
            self.close_help()

        self.TextManager.display_message(self.screen, 0.5, 0.18, f"Help notes", "big")

        width = 2                                                               # Display horizontal line based on page
        length = int(self.screen_size[0] * 0.7 / self.max_help_screen)
        pos = (int(self.screen_size[0] * 0.15 + length * self.current_help_screen),
            int(self.screen_size[1] * 0.21), length, width * 2)
        pygame.draw.rect(self.screen, self.TextManager.bg_color, pos, width, width)

        title = self.HelpTabs[self.current_help_screen]                         # Display title
        self.TextManager.display_message(self.screen, 0.5, 0.25, title, "middle")

        Texts = self.HelpTexts[self.current_help_screen]                        # Display texts
        lenght = 0.35 if len(Texts) > 1 else 0.7
        for i, text in enumerate(Texts):                                        # ! Use percent_size
            self.TextManager.display_message(self.screen, 0.15 + 0.35 * i, 0.3,
                text, "small", "left", [lenght, 0.5])

        image_name = "game rules.png" if self.current_help_screen == 1 else \
            "sheldon rules.png" if self.current_help_screen == 2 else None      # Display image if has one
        if image_name:
            rules = pygame.image.load(Path(self.path_image) / image_name).convert_alpha()
            rules = self.DataManager.resize_image(self.screen_size, rules, 0.28)
            self.screen.blit(rules, (self.screen_size[0] * 0.58, self.screen_size[1] * 0.15))

        page = f"{self.current_help_screen + 1}/{self.max_help_screen}"         # Show current page
        self.TextManager.display_message(self.screen, 0.85, 0.85, page, "middle")

    def collect_datas(self):
        if self.timer_one_sec.check_loop_end(self.current_time) > 0:
            EntityQuantity = self.EntityManager.get_number_entities()
            for name in self.EntityNames:
                value = EntityQuantity[name] if name in EntityQuantity.keys() else 0
                self.DataManager.EntityQuantity[name].append(value)
            if len(self.EntityManager.Entities) > 0:
                self.DataManager.Speeds.append(statistics.mean([e.speed * self.fps for e in self.EntityManager.Entities]))
                self.DataManager.Ranges.append(statistics.mean([e.range for e in self.EntityManager.Entities]))
                self.DataManager.Sizes.append(statistics.mean([e.size for e in self.EntityManager.Entities]))
            self.DataManager.take_screenshot(self.screen)

    # ... Creating function
    def display_data_screen(self):                                              # Save menu
        pos = self.TextManager.display_box(self.screen)
        if self.get_not_click_on_position(pos):
            self.close_saves()

        self.TextManager.display_message(self.screen, 0.5, 0.18, f"Saves", "big")

        self.display_saves_tabs_list()                                          # Display tabs

        current = self.DataManager.current_tab
        if current == 0:
            self.display_tab_screenshots_screen()
        elif current == 1:
            self.display_tab_graphics_screen()
        elif current == 2:
            self.display_tab_saves_screen()

    def display_saves_tabs_list(self):
        rect = (0.15, 0.22, 0.7, 0.05)
        length = rect[2] / len(self.DataManager.Tabs)                           # Tab width
        width = 5

        pos = (self.screen_size[0] * rect[0], self.screen_size[1] * rect[1],
        self.screen_size[0] * rect[2], self.screen_size[1] * rect[3])
        pygame.draw.rect(self.screen, self.borders_color, pos, width)           # Big rectangle

        for i, tab in enumerate(self.DataManager.Tabs):
            x = (rect[0] + length * i) + length / 2
            y = rect[1] + rect[3] / 2
            self.TextManager.display_message(self.screen, x, y, tab, "middle")  # Tab name

            if i > 0:                                                           # Vertical line
                point1 = (self.screen_size[0] * (rect[0] + length * i), self.screen_size[1] * rect[1])
                point2 = (point1[0], point1[1] + self.screen_size[1] * rect[3] - width)
                pygame.draw.line(self.screen, self.borders_color, point1, point2, width)

        for j, tab in enumerate(self.DataManager.Tabs):                         # Display above all tabs
            x = (rect[0] + length * j)
            pos = (self.screen_size[0] * x, self.screen_size[1] * rect[1],
            self.screen_size[0] * length + 1, self.screen_size[1] * rect[3])
            if self.get_click_on_position(pos):                                 # Select another tab
                self.DataManager.current_tab = j

            if self.DataManager.current_tab == j:                               # Highlight current tab
                pygame.draw.rect(self.screen, self.selected_color, pos, width)

    def display_tab_screenshots_screen(self):                                   # Tab of screenshots of a simulation
        trio = (self.screen, self.mouse, self.left_click)
        Datas = self.DataManager

        descr = "When on, auto play simulation turn by turn"
        self.DataManager.is_auto_play, as_change = self.TextManager.display_parameter(*trio,
            0.15, 0.15, self.DataManager.is_auto_play, "Auto-play : ", descr)
        if as_change:                                                           # Start or stop timer
            if self.DataManager.is_auto_play:
                self.DataManager.timer.start(self.current_time)
            else:
                self.DataManager.timer.reset(self.current_time)
                self.DataManager.timer.pause(self.current_time)

        if len(Datas.Screenshots[0]) > 0:
            message = (f"sim {Datas.current_sim + 1} / {len(Datas.Screenshots)} - "
                       f"turn {Datas.current_turn + 1} / {Datas.get_nb_turns()}")
            self.TextManager.display_message(self.screen, 0.5, 0.3, message)

            screenshot = Datas.Screenshots[Datas.current_sim][Datas.current_turn]
            screenshot = Datas.resize_image(self.screen_size, screenshot, height=0.45)
            x = self.screen_size[0] * 0.5 - screenshot.get_width() * 0.5
            self.screen.blit(screenshot, (x, self.screen_size[1] * 0.32))

            self.DataManager.check_display_next_turn(self.current_time)
        else:
            self.TextManager.display_message(self.screen, 0.5, 0.5, "No simulation launch today", "big")

        # Buttons
        if self.DataManager.nb_sim <= 1:
            self.TextManager.use_unactive_color()
            hover_color = None
        else:
            hover_color = self.bg_hover_color

        pos = [0.15, 0.8, 0.12, 0.05]
        if self.TextManager.display_button(*trio, "Previous sim", pos, bg_color_hover=hover_color):
            if self.DataManager.nb_sim > 1:
                self.DataManager.previous_sim()
        pos[0] += 0.15
        if self.TextManager.display_button(*trio, "Next sim", pos, bg_color_hover=hover_color):
            if self.DataManager.nb_sim > 1:
                self.DataManager.next_sim()

        if self.DataManager.nb_sim <= 1:
            self.TextManager.set_font_color()

        if self.DataManager.get_nb_turns() <= 1:
            self.TextManager.use_unactive_color()
            hover_color = None
        else:
            hover_color = self.bg_hover_color

        pos[0] += 0.15
        if self.TextManager.display_button(*trio, "Previous turn", pos, bg_color_hover=hover_color):
            if not self.DataManager.is_auto_play:
                self.DataManager.previous_turn()
        pos[0] += 0.15
        if self.TextManager.display_button(*trio, "Next turn", pos, bg_color_hover=hover_color):
            if not self.DataManager.is_auto_play:
                self.DataManager.next_turn()

        if self.DataManager.get_nb_turns() <= 1:
            self.TextManager.set_font_color()

        if self.DataManager.nb_sim <= 0:
            self.TextManager.use_unactive_color()
            hover_color = None
        else:
            hover_color = self.bg_hover_color

        pos[0] += 0.15
        nb = f" ({self.DataManager.nb_sim})" if self.DataManager.nb_sim > 0 else ""
        if self.TextManager.display_button(*trio, f"Save all{nb}", pos, bg_color_hover=hover_color):
            if self.DataManager.nb_sim > 0:
                self.DataManager.save_all()

        if self.DataManager.nb_sim <= 0:
            self.TextManager.set_font_color()

    def display_tab_graphics_screen(self):                                      # Tab of graphics
        trio = (self.screen, self.mouse, self.left_click)

        if self.DataManager.nb_sim > 0:
            if self.DataManager.current_graphic is not None:
                x = self.screen_size[0] * 0.5 - self.DataManager.current_pygame_image.get_width() * 0.5
                coords = (x, self.screen_size[1] * 0.28)
                self.screen.blit(self.DataManager.current_pygame_image, coords)
            else:
                self.TextManager.use_unactive_color()
                self.TextManager.display_message(self.screen, 0.5, 0.5, "No graphic selected")
                self.TextManager.set_font_color()

            for i, graphic in enumerate(self.DataManager.Graphics):
                coords = (self.screen_size[0] * 0.8, self.screen_size[1] * 0.3 +
                                                     (graphic.icon_size + 10) * i)
                pos = (*coords, graphic.icon_size, graphic.icon_size)

                if self.get_mouse_hover_position(pos):                          # Add bg color
                    gap = 3
                    button_pos = (pos[0] - gap, pos[1] - gap, pos[2] + gap * 2, pos[3] + gap * 2)
                    pygame.draw.rect(self.screen, self.bg_color, button_pos, border_radius=gap)

                self.screen.blit(graphic.image, coords)

                if self.get_mouse_hover_position(pos):                          # Display graphic name
                    pos_mouse = (self.mouse[0] / self.screen_size[0],
                    (self.mouse[1] - 5) / self.screen_size[1])
                    self.TextManager.display_message(self.screen, *pos_mouse, graphic.name, "small")

                if self.get_click_on_position(pos):                             # Show graphic
                    self.left_click = False
                    if self.DataManager.current_graphic == i:
                        self.DataManager.current_graphic = None
                        self.DataManager.current_pygame_image = None
                    else:
                        self.DataManager.update_graphic(self.screen_size, graphic, 0.6)

            if self.DataManager.current_graphic == 1:                           # Display options
                icon_size = Graphic(None, None).icon_size * 0.5
                for i, (option, color) in enumerate(self.DataManager.Options.items()):
                    option_pos = (self.screen_size[0] * 0.7, int(self.screen_size[1] * 0.35 +
                                                                 (icon_size + 5) * i), icon_size, icon_size)
                    pygame.draw.rect(self.screen, color, option_pos, border_radius=int(icon_size * 0.1))

                    if self.get_mouse_hover_position(option_pos):
                        pos_mouse = (self.mouse[0] / self.screen_size[0],
                        (self.mouse[1] - 5) / self.screen_size[1])
                        self.TextManager.display_message(self.screen, *pos_mouse, option.capitalize(), "small")

                    if self.get_click_on_position(option_pos):
                        self.DataManager.current_option = option
                        self.DataManager.update_graphic(self.screen_size)

            message = f"sim {self.DataManager.current_sim + 1} / {len(self.DataManager.Screenshots)}"
            self.TextManager.display_message(self.screen, 0.21, 0.68, message, "middle")
        else:
            self.TextManager.display_message(self.screen, 0.5, 0.5, "No simulation launch today", "big")

        # Buttons
        if self.DataManager.nb_sim <= 1:
            self.TextManager.use_unactive_color()
            hover_color = None
        else:
            hover_color = self.bg_hover_color

        if self.TextManager.display_button(*trio, "Previous sim", (0.15, 0.8, 0.12, 0.05), bg_color_hover=hover_color):
            if self.DataManager.nb_sim > 1:
                self.DataManager.previous_sim()
                if self.DataManager.current_graphic is not None:
                    self.DataManager.update_graphic(self.screen_size)
        if self.TextManager.display_button(*trio, "Next sim", (0.15, 0.72, 0.12, 0.05), bg_color_hover=hover_color):
            if self.DataManager.nb_sim > 1:
                self.DataManager.next_sim()
                if self.DataManager.current_graphic is not None:
                    self.DataManager.update_graphic(self.screen_size)

        if self.DataManager.nb_sim <= 1:
            self.TextManager.set_font_color()

    def display_tab_saves_screen(self):                                         # Tab for saved simulations
        trio = (self.screen, self.mouse, self.left_click)

        if len(self.DataManager.Saves) > 0:
            # ! Display all saves (can click to load it → go to screenshots_screen)
            # ! Add date, nb turn and 'delete' button on each save
            pass
        else:
            self.TextManager.display_message(self.screen, 0.5, 0.5, "No simulation saved yet", "big")

        # Buttons (work without Saves)
        if self.DataManager.nb_sim <= 0:
            self.TextManager.use_unactive_color()
            hover_color = None
        else:
            hover_color = self.bg_hover_color

        pos = [0.15, 0.8, 0.12, 0.05]
        gap = 0.05
        nb = f" ({self.DataManager.nb_sim})" if self.DataManager.nb_sim > 0 else ""
        if self.TextManager.display_button(*trio, f"Save all{nb}", pos, bg_color_hover=hover_color):
            if self.DataManager.nb_sim > 0:
                self.DataManager.save_all()

        pos[0] += 0.15
        pos[2] += gap
        s = "s" if self.DataManager.nb_sim > 1 else ""
        if self.TextManager.display_button(*trio, f"Save current sim{s}", pos, bg_color_hover=hover_color):
            if self.DataManager.nb_sim > 0:
                self.DataManager.save_current_sim()

        pos[0] += 0.35 - gap * 2
        if self.TextManager.display_button(*trio, "Delete today saves", pos, bg_color_hover=hover_color):
            if self.DataManager.nb_sim > 0:
                self.DataManager.delete_today_saves()

        if self.DataManager.nb_sim <= 0:
            self.TextManager.set_font_color()

        nb_save = len(self.DataManager.Saves)
        if nb_save <= 0:
            self.TextManager.use_unactive_color()
            hover_color = None
        else:
            hover_color = self.bg_hover_color

        pos[0] += 0.2
        pos[2] -= gap
        nb = f" ({nb_save})" if nb_save > 0 else ""
        if self.TextManager.display_button(*trio, f"Delete all{nb}", pos, bg_color_hover=hover_color):
            if nb_save > 0:
                self.DataManager.delete_all_saves()

        if nb_save <= 0:
            self.TextManager.set_font_color()

    def display_alert_messages(self):                                           # Screens to alert user about something
        trio = (self.screen, self.mouse, self.left_click)

        if self.asking_restart:
            q = "Are you sure you want to restart the ongoing simulation ?"
            result = self.TextManager.display_ask_box(*trio, 0.35, 0.35,
                "Restart simulation", q, "Yes restart", "Cancel")
            if result is None:
                pass
            elif result:
                self.asking_restart = False
                self.start_simulation()
            else:
                self.asking_restart = False
            self.left_click = False

        if self.asking_goback:
            q = "Are you sure you want to go back to menu ?"
            result = self.TextManager.display_ask_box(*trio, 0.35, 0.35,
                "Go back to menu", q, "Yes", "Cancel")
            if result is None:
                pass
            elif result:
                self.asking_goback = False
                self.go_to_menu()
            else:
                self.asking_goback = False
            self.left_click = False

        if self.asking_saving:
            q = "Go back to menu without saving ? Your progression will be lost."
            result = self.TextManager.display_ask_box(*trio, 0.35, 0.35,
                "Go back to menu", q, "Yes", "Cancel")
            if result is None:
                pass
            elif result:
                self.asking_saving = False
                self.go_to_menu()
            else:
                self.asking_saving = False
            self.left_click = False

    def display_loading_icon(self):                                             # Loading screen (bottom right)
        pass

    def check_end_simulation(self):                                             # Also display end message
        if self.simulating:
            Entities = self.EntityManager.get_number_entities()

            if len(Entities.items()) == 1:                                      # If only one type of entity remain
                message = f"The entities '{list(Entities.keys())[0].capitalize()}' have dominated other entities !"
                self.TextManager.display_message(self.screen, 0.5, 0.2, message, "middle", "center")

                if self.ParametersManager.is_auto_end:
                    message = f"Click to close the simulation"
                    self.TextManager.display_message(self.screen, 0.5, 0.3, message, "small", "center")

                    if self.left_click and not self.pausing:
                        self.go_to_menu()

    def go_to_menu(self):                                                       # Go back to menu
        self.simulating = False
        self.pausing = False

        self.DataManager.take_screenshot(self.screen)                           # Last screenshot just in case
        self.DataManager.update_simulation(self.DataManager.nb_sim,
            self.timer_simulation.get_elapsed_time(self.current_time),
            self.EntityManager.is_smart_entity, self.EntityManager.is_entity_range,
            self.ParametersManager.is_map_borders, self.ParametersManager.is_infinity_map)
        self.DataManager.reset()
        if self.DataManager.is_auto_save:
            self.DataManager.save_all()

        self.EntityManager.empty_entities()

    def start_simulation(self):                                                 # Start simulation
        self.simulating =       True
        self.parametering =     False
        self.save_menuing =     False
        self.helping =          False
        self.pausing =          False
        self.asking_restart =   False
        self.asking_goback =    False

        self.EntityManager.create_entities()
        self.DataManager.add_simulation(0, self.EntityManager.is_smart_entity, self.EntityManager.is_entity_range,
            self.ParametersManager.is_map_borders, self.ParametersManager.is_infinity_map)
        self.Mutated_Entities = []

        self.timer_one_sec.start(self.current_time)
        self.timer_simulation.start(self.current_time)
        if self.timer_turn.duration > 0:
            self.timer_turn.start(self.current_time)

    def close_game(self):                                                       # Exit program
        pygame.time.delay(200)
        self.running = False
        pygame.quit()
        quit()


if __name__ == "__main__":
    game = RPSSimulator()
