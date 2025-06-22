# from math import *
# from random import *
# from time import *
from pathlib import Path
from matplotlib.backends.backend_agg import FigureCanvasAgg as Figure
from data import Database
import matplotlib.pyplot as plt
import numpy as np
import pygame


class Graphic:
    def __init__(self, name, type_value, with_options=False):
        # Attributes
        self.is_options = with_options
        self.name = name
        db = Database()
        # Path data
        self.path_graphic = db.PATH_GRAPHIC
        # Graphics data
        self.type = type_value
        self.GraphicTypes = [_ for _ in Path(self.path_graphic).iterdir() if _.suffix == ".png"]
        self.LineStyles = ["-", "--", ":", "-,"]                                # All graphic line styles
        self.style = self.LineStyles[0]                                         # Current line style
        self.color = "blue"                                                     # Default color for graphics
        # Menu data
        self.icon_size = 70
        self.image = self.get_image()
        # Entities data
        self.EntityNames = list(db.ENTITYCOLORS.keys())
        self.EntityColors = db.ENTITYCOLORS
        # Options data
        self.Options = db.OPTIONCOLORS

    def get_image(self):                                                        # Load and resize graphic image
        if self.type:
            image = pygame.image.load(Path(self.path_graphic) / self.type).convert_alpha()
            image = pygame.transform.scale(image, (self.icon_size, self.icon_size))
            return image
        return None

    @staticmethod
    def get_pygame_image(figure):
        canvas = Figure(figure)
        canvas.draw()
        data = canvas.tostring_rgb()
        size = canvas.get_width_height()

        pygame_image = pygame.image.fromstring(data, size, "RGB")               # Convert matplotlib image to pygame
        return pygame_image

    def show_graphic(self, EntityQuantity, Speeds, Ranges, Sizes, Option):      # Display associate graphic
        figure = None
        if self.type == self.GraphicTypes[0]:                                   # bar chart
            if self.is_options:
                figure = self.graphic_max_options(Speeds, Ranges, Sizes)
            else:
                figure = self.graphic_max_quantity(EntityQuantity)
        elif self.type == self.GraphicTypes[1]:                                 # histogram
            figure = self.graphic_histogram()
        elif self.type == self.GraphicTypes[2]:                                 # line plot
            if self.is_options:
                figure = self.graphic_average_option(Option)
            else:
                figure = self.graphic_nb_entity(EntityQuantity)
        elif self.type == self.GraphicTypes[3]:                                 # pie chart
            figure = self.graphic_dominant_entity(EntityQuantity)
        elif self.type == self.GraphicTypes[4]:                                 # scatter plot
            figure = self.graphic_scatter_plot()

        if figure:
            image = self.get_pygame_image(figure)
            return image, figure
        return None, None

    def graphic_nb_entity(self, EntityQuantity):                                # line plot graphic
        fig, ax = plt.subplots()

        if len(EntityQuantity.keys()) > 0:
            nb = len(list(EntityQuantity.values())[0])
            x = np.linspace(1, nb, nb)                                          # (min, max, nb points)
            for name, Values in EntityQuantity.items():
                ax.plot(x, Values, label=name, linestyle=self.style, color=self.EntityColors[name])

        ax.set_xlabel("Time")                                                  # Name axes
        ax.set_ylabel("Quantity of entities")
        ax.set_title(self.name)                                                # Largest population an entity has reached
        ax.legend()
        ax.grid(True)                                                          # Display grid

        return fig

    def graphic_average_option(self, Option):                                   # Show average option evolution (every second)
        fig, ax = plt.subplots()

        name, Values = list(Option.items())[0]
        nb = len(Values)
        x = np.linspace(1, nb, nb)                                              # (min, max, nb points)
        ax.plot(x, Values, label=name, linestyle=self.style, color=self.Options[name])

        ax.set_xlabel("Turns")                                                  # Name axes
        ax.set_ylabel("Quantity")
        ax.set_title(self.name)
        ax.legend()
        ax.grid(True)                                                           # Display grid

        return fig

    def graphic_max_quantity(self, EntityQuantity):                             # bar chart graphic
        fig, ax = plt.subplots()

        if all(len(value) > 0 for value in EntityQuantity.values()):
            Names = EntityQuantity.keys()
            Values = [max(value) for value in EntityQuantity.values()]
            Colors = [self.EntityColors[name] for name in Names]

            ax.bar(Names, Values, color=Colors)
            for i, v in enumerate(Values):
                ax.text(i, v + 0.5, str(v), ha='center', fontsize=12, fontweight='bold')

        ax.set_xlabel("Entities' types")                                        # Name axes
        ax.set_ylabel("Quantity")
        ax.set_title(self.name)

        return fig

    def graphic_max_options(self, Speeds, Ranges, Sizes):                       # Show max value of all options during sim
        fig, ax = plt.subplots()

        if len(Speeds) > 0 and len(Ranges) > 0 and len(Sizes) > 0:
            Values = [max(Speeds), max(Ranges), max(Sizes)]
            ax.bar(self.Options.keys(), Values, color=self.Options.values())
            for i, v in enumerate(Values):
                ax.text(i, v + 0.5, str(v), ha='center', fontsize=12, fontweight='bold')

        ax.set_xlabel("Options")                                                # Name axes
        ax.set_ylabel("Quantity")
        ax.set_title(self.name)                                                 # Largest value an option has reached

        return fig

    def graphic_dominant_entity(self, EntityQuantity):                          # pie chart graphic
        fig, ax = plt.subplots()

        if all(len(value) > 0 for value in EntityQuantity.values()):
            Names = EntityQuantity.keys()
            Values = [max(value) for value in EntityQuantity.values()]
            Colors = [self.EntityColors[name] for name in Names]

            ax.pie(Values, labels=Names, colors=Colors, autopct='%1.1f%%')
        else:
            ax.pie([100], labels=["--empty--"], colors=["lightgrey"])           # to display something

        ax.set_title(self.name)                                                 # Largest population an entity has reached
        ax.legend()

        return fig

    # ! No purpose found for scatter (cloud) yet
    @staticmethod
    def graphic_scatter_plot():                                                 # scatter plot graphic
        fig, ax = plt.subplots()
        x = np.random.rand(50)
        y = np.random.rand(50)

        ax.scatter(x, y, color='red', marker='o')

        ax.set_xlabel("X")                                                      # Name axes
        ax.set_ylabel("Y")
        ax.set_title(self.name)
        ax.legend()
        ax.grid(True)                                                           # Display grid

        return fig

    # ! No purpose found for histogram yet
    @staticmethod
    def graphic_histogram():                                                    # histogram graphic
        fig, ax = plt.subplots()
        data = np.random.randint(1, 100, 100)

        ax.hist(data, bins=len(data), color='gray', edgecolor='black')          # bins: nb columns

        ax.set_xlabel("Value")                                                  # Name axes
        ax.set_ylabel("Frequency")
        ax.set_title(self.name)
        ax.legend()
        ax.grid(True)                                                           # Display grid

        return fig
