from matplotlib.colors import to_rgb
from webcolors import name_to_rgb
from pathlib import Path
import pygame
import os


class Database:                                                                 # Shared items everywhere in the program
    def __init__(self):
        # Screen data
        self.SCREEN =       pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.FULL_SIZE =    (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.SCREEN_SIZE =  self.SCREEN.get_size()                              # Full screen by default
        # Format data
        self.DATE_FORMAT =      "%d-%m-%Y"                                      # Today's date: dd-mm-yyyy
        self.SAVE_FORMAT =      ".json"                                         # Format for save files
        self.IMAGE_FORMAT =     ".png"                                          # Format for most image files
        self.SCREEN_FORMAT =    ".gif"                                          # Format for screenshot files
        self.MUSIC_FORMAT =     ".mp3"                                          # Format for music files
        self.HELP_FORMAT =      ".txt"                                          # Format for help text files
        self.LOG_FORMAT =       ".md"                                           # Format for log files
        # File data
        self.FILES = ("data", "data/texts", "images", "images/entity",
            "images/graphics", "logs", "musics", "saves", "sounds")    # All files to create at first launch
        self.PATH =             Path.cwd()                                      # Current programm path
        self.PATH_DATA =        Path(self.PATH) / "data"                        # Datas path
        self.PATH_TEXT =        Path(self.PATH_DATA) / "texts"                  # Texts path
        self.PATH_IMAGE =       Path(self.PATH) / "images"                      # Images path
        self.PATH_ICON_ENTITY = Path(self.PATH_IMAGE) / "entity"                # Icons of entities path
        self.PATH_ICON_GRAPHIC = Path(self.PATH_IMAGE) / "graphics"             # Icons of graphics path
        self.PATH_LOG =         Path(self.PATH) / "logs"                        # Logs path (for saves)
        self.PATH_MUSIC =       Path(self.PATH) / "musics"                      # Musics path
        self.PATH_SAVE =        Path(self.PATH) / "saves"                       # Saves path (for saves)
        self.PATH_SOUND =       Path(self.PATH) / "sounds"                      # Sounds path
        # Color data
        self.COLORNAMES =   ("red", "orange", "wheat", "gold", "yellow", "lime",
            "green", "cyan", "deepskyblue", "blue", "purple", "deeppink",
            "brown", "sandybrown", "lightgrey", "grey", "white", "black")       # Name of colors available (unused)
        self.COLORS = {color: name_to_rgb(color) for color in self.COLORNAMES}  # RGB version of colors (used instead)
        self.FLOAT_COLORS = {color: to_rgb(color) for color in self.COLORNAMES} # Float version of RGB (for graphics)
        self.BG_HOVER_COLOR =   self.COLORS["white"]                            # For screens
        self.BG_COLOR =         self.COLORS["lightgrey"]
        self.BORDER_COLOR =     self.COLORS["grey"]
        self.FONT_COLOR =       self.COLORS["black"]
        self.SELECTED_COLOR =   self.COLORS["gold"]
        # Font data
        FontSizes = (25, 40, 60, 80)
        self.FONTS = [pygame.font.SysFont(None, size) for size in FontSizes]
        # Entity data
        self.BASENAMES = ["paper", "rock", "scissors"]
        self.ENTITYNAMES = [_.replace(self.IMAGE_FORMAT, "") for _ in os.listdir(self.PATH_ICON_ENTITY)]
        Colors = ["lime", "wheat", "grey", "red", "deepskyblue"]                # Colors of entities
        self.BASECOLORS = {name: self.COLORS[color] for name, color in zip(self.BASENAMES, Colors[1:-1])}
        self.ENTITYCOLORS = {name: self.COLORS[color]
            for name, color in zip(self.ENTITYNAMES, Colors)}                   # Colors associates with entities
        self.ENTITYIMAGES = {name: pygame.image.load(f"{self.PATH_ICON_ENTITY}/{name}{self.IMAGE_FORMAT}").convert_alpha()
            for name in self.ENTITYNAMES}
        self.FOODCHAIN = {"lizard": ["spock", "paper"], "paper": ["rock", "spock"], "rock": ["scissors", "lizard"],
            "scissors": ["paper", "lizard"], "spock": ["scissors", "rock"]}     # Which entity beats which ones
        # Option data
        OptionColors = {"speed": "yellow", "range": "sandybrown", "size": "cyan"}
        self.OPTIONCOLORS = {name: self.COLORS[color] for name, color in OptionColors.items()}  # Colors associates with options
        # Graphics data
        self.GRAPHICS_NAMES = ("Number of entity every second", "Average options evolution",
            "Pinnacle for each entity", "Maximum for each option", "Dominance of entities")
        self.GRAPHICS_TYPES = [_ for _ in Path(self.PATH_ICON_GRAPHIC).iterdir()
            if _.suffix == self.IMAGE_FORMAT]
        self.GRAPHICS_ENTITY_COLORS = {name: self.FLOAT_COLORS[color]
            for name, color in zip(self.ENTITYNAMES, Colors)}
        self.GRAPHICS_OPTION_COLORS = {name: self.FLOAT_COLORS[color]
            for name, color in OptionColors.items()}                            # Colors associates with graphics
        # Help screen data
        self.HELPTABS =   []
        self.HELPTEXTS =  []
        self.HELPIMAGES = (None, "game rules.png", "sheldon rules.png", None, None)
        # Credits data
        self.CREDITS = []

    # [later] Write Sheldon's rules text when they're added
    def load_help_texts(self):                                                  # Launch later to avoid FileNotFoundError
        Files = [_ for _ in Path(self.PATH_TEXT).iterdir() if _.suffix == self.HELP_FORMAT]
        for file in Files:
            with open(file, "r") as content:
                Texts = content.read().split("---")
                self.HELPTABS.append(Texts[0])
                Texts.pop(0)                                                    # Remove title
                self.HELPTEXTS.append(Texts)

    def load_credits(self):                                                     # Create a list of surface to display
        filename = Path(self.PATH_DATA) / "credits.txt"
        with open(filename, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                line = line.rstrip("\n")
                if line.startswith("## "):
                    text = line[3:]
                    font = self.FONTS[2]
                elif line.startswith("# "):
                    text = line[2:]
                    font = self.FONTS[3]
                elif line.startswith("~ "):
                    text = line[2:]
                    font = self.FONTS[0]
                else:
                    text = line
                    font = self.FONTS[1]
                surf = font.render(text, True, self.FONT_COLOR).convert_alpha()
                self.CREDITS.append(surf)
