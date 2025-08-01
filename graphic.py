# from math import *
# from random import *
# from time import *
from io import BytesIO
from pathlib import Path
from data import Database
from matplotlib.backends.backend_agg import FigureCanvasAgg as Figure
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pygame


# ! Modify class to always have options (one list with all and one to get current options to show in graphic)
class Graphic:
    icon_size: int = 70                                                         # To be directly accessible by save menu

    def __init__(self, name, type_value, entity_type=False):
        matplotlib.use("Agg")                                                   # Use non-interactive back-end
        db = Database()
        # Attributes
        self.is_entity = entity_type                                            # If graphic display entity data or not
        self.name = name
        # Path data
        self.path_graphic = db.PATH_ICON_GRAPHIC
        # Graphics data
        self.type = type_value
        self.GraphicTypes = db.GRAPHICS_TYPES
        self.linestyle = "-"                                                    # Continuous line
        # Icon data
        self.icon_size = 70
        self.icon = self.get_icon()
        self.image = None                                                       # Pygame image to display
        self.figure = None                                                      # Figure graphic to save
        self.image_format = db.IMAGE_FORMAT
        # Entities data
        self.EntityNames =  db.ENTITYNAMES
        self.EntityColors = db.GRAPHICS_ENTITY_COLORS
        # Options data
        self.OptionNames = list(db.OPTIONCOLORS.keys())
        self.OptionColors = db.GRAPHICS_OPTION_COLORS
        self.Options = self.EntityNames if self.is_entity else self.OptionNames

    def get_icon(self):                                                        # Load and resize graphic image
        if self.type:
            icon = pygame.image.load(Path(self.path_graphic) / self.type).convert_alpha()
            icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
            return icon
        return None

    @staticmethod
    def get_figure_to_pygame_image(figure):                                     # Convert matplotlib image to pygame
        buf = BytesIO()
        figure.savefig(buf, format="png")                                       # Save in a buffer
        buf.seek(0)
        surface = pygame.image.load(buf, "temp.png")
        buf.close()                                                             # Free memory from buffer
        return surface

    @staticmethod
    def get_percentage_data(Values):
        if max(Values) == min(Values):
            return [50.0] * len(Values)
        return [(x - min(Values)) / (max(Values) - min(Values)) * 100 for x in Values]

    def get_image(self, EntityQuantity, Options=None):   # Display associate graphic
        EntityQuantity = {name: Values for name, Values in EntityQuantity.items() if name in self.Options} \
            if self.is_entity else EntityQuantity if EntityQuantity else {}
        Options = {name: Values for name, Values in Options.items() if name in self.Options} \
            if not self.is_entity else Options if Options else {}
        figure = None
        if self.type == self.GraphicTypes[0]:                                   # bar chart
            if self.is_entity:
                figure = self.graphic_max_quantity(EntityQuantity)
            else:
                figure = self.graphic_max_options(Options)
        elif self.type == self.GraphicTypes[1]:                                 # histogram
            figure = self.graphic_histogram()
        elif self.type == self.GraphicTypes[2]:                                 # line plot
            if self.is_entity:
                figure = self.graphic_nb_entity(EntityQuantity)
            else:
                figure = self.graphic_average_option(Options)
        elif self.type == self.GraphicTypes[3]:                                 # pie chart
            figure = self.graphic_dominant_entity(EntityQuantity)
        elif self.type == self.GraphicTypes[4]:                                 # scatter plot
            figure = self.graphic_scatter_plot()

        if figure:
            plt.close()                                                         # Close open graphic
            image = self.get_figure_to_pygame_image(figure)
            return image, figure
        return None, None

    def update_image(self, EntityQuantity, Speeds, Ranges, Sizes):
        Options = {"speed": Speeds, "range": Ranges, "size": Sizes}
        self.image, self.figure = self.get_image(EntityQuantity, Options)

    def save_image(self, name):
        name = name.with_suffix(self.image_format) if name.suffix != self.image_format else name
        self.figure.savefig(name)

    def graphic_nb_entity(self, EntityQuantity):                                # line plot graphic
        fig, ax = plt.subplots()                                                # Types : figure.Figure, axes.Axes

        if len(EntityQuantity.keys()) > 0:
            nb = len(list(EntityQuantity.values())[0])
            x = np.linspace(1, nb, nb)                                          # (min, max, nb points)
            for name, Values in EntityQuantity.items():
                ax.plot(x, Values, label=name, linestyle=self.linestyle,
                    color=self.EntityColors[name])

        ax.set_xlabel("Time")                                                  # Name axes
        ax.set_ylabel("Quantity of entities")
        ax.set_title(self.name)                                                # Largest population an entity has reached
        ax.legend()
        ax.grid(True)                                                          # Display grid

        return fig

    def graphic_average_option(self, Options):                                  # Show average option evolution (every second)
        fig, ax = plt.subplots()

        for name, Values in Options.items():
            nb = len(Values)
            x = np.linspace(1, nb, nb)                                          # (min, max, nb points)
            Percents = self.get_percentage_data(Values) if len(Values) > 0 else []
            ax.plot(x, Percents, label=name, linestyle=self.linestyle,
                color=self.OptionColors[name])

        ax.set_xlabel("Turns")                                                  # Name axes
        ax.set_ylabel("Percentage (%)")
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

    def graphic_max_options(self, Options):                                     # Show max value of all options during sim
        fig, ax = plt.subplots()

        if all(len(value) > 0 for value in Options.values()):
            Values = [max(Values) for Values in Options.values()]
            ax.bar(Options.keys(), Values, color=[self.OptionColors.get(v) for v in Options])
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
