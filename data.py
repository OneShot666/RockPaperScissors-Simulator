# from math import *
# from random import *
# from time import *
from webcolors import name_to_rgb
from pathlib import Path


class Database:                                                                 # Shared items everywhere in the program
    def __init__(self):
        # File data
        self.PATH =             Path.cwd()                                      # Current programm path
        self.PATH_DATA =        Path(self.PATH) / "data"                        # Datas path
        self.PATH_TEXT =        Path(self.PATH_DATA) / "texts"                  # Texts path
        self.PATH_FONT =        Path(self.PATH) / "fonts"                       # Fonts path
        self.PATH_IMAGE =       Path(self.PATH) / "images"                      # Images path
        self.PATH_GRAPHIC =     Path(self.PATH_IMAGE) / "graphics"              # Images of graphics path
        self.PATH_LOG =         Path(self.PATH) / "logs"                        # Logs path
        self.PATH_MUSIC =       Path(self.PATH) / "musics"                      # Musics path
        self.PATH_SAVE =        Path(self.PATH) / "saves"                       # Saves path
        self.PATH_SCREENSHOT =  Path(self.PATH) / "screenshots"                 # Screenshots path
        self.PATH_SOUND =       Path(self.PATH) / "sounds"                      # Sounds path
        # Color data
        self.COLORNAMES =   ["red", "orange", "wheat", "gold", "yellow",
            "green", "cyan", "blue", "purple", "deeppink",
            "brown", "lightgrey", "grey", "white", "black"]     # Name of colors available (unused)
        self.COLORS = {color: name_to_rgb(color) for color in self.COLORNAMES}  # RGB version of colors (used instead)
        self.BG_HOVER_COLOR =   self.COLORS["white"]                            # For screens
        self.BG_COLOR =         self.COLORS["lightgrey"]
        self.BORDER_COLOR =     self.COLORS["grey"]
        self.FONT_COLOR =       self.COLORS["black"]
        self.SELECTED_COLOR =   self.COLORS["gold"]
        # Font data
        self.FONTSIZES =    {"small": 25, "middle": 40, "big": 60, "giant": 80}
        # Entity data
        # ! Add dynamically found files and names
        self.ENTITYCOLORS = {"rock": self.COLORS["grey"], "paper": self.COLORS["wheat"],
            "scissors": self.COLORS["red"]}                     # Colors associates with entities
        # Option data
        self.OPTIONCOLORS = {"speed": self.COLORS["yellow"], "range": self.COLORS["wheat"],
            "size": self.COLORS["cyan"]}
        # Help screen data
        self.HELPTABS = []
        self.HELPTEXTS = []

    # [later] Makes Sheldon's rules text when they're added
    def create_texts(self):                                                     # Launch later to avoid FileNotFoundError
        Files = [_ for _ in Path(self.PATH_TEXT).iterdir() if _.suffix == ".txt"]
        for file in Files:
            with open(file, "r") as content:
                text = content.read().split("---")
                self.HELPTABS.append(text[0])
                self.HELPTEXTS.append(text[1:])
