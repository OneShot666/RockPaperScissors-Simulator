# from math import *
# from random import *
# from time import *
# import pygame


class ParameterScreen:                                                          # To manage parameters
    def __init__(self):
        # Tabs data
        self.Tabs = ["Main", "Simulation", "Entities", "Sounds"]
        self.current_tab = self.Tabs[1]
        # Parameters data
        self.is_display_turn =  False
        self.is_map_borders =   False                                           # Allow entities to exit the screen
        self.is_infinity_map =  False                                           # Make screen toroidal
        self.is_nb_in_percent = False                                           # Display nb of entities in percent
        self.is_ui_on_front =   False                                           # Display UI on front of entities
        self.is_ui_hide =       False                                           # If UI is displayed
        self.is_auto_end =      False                                           # End sim if only one type of entity remain

    def get_current_tab_index(self):
        return self.Tabs.index(self.current_tab)

    def previous_tab(self):
        i = self.get_current_tab_index()
        i -= 1
        if i < 0:
            i = len(self.Tabs) - 1
        self.current_tab = self.Tabs[i]

    def next_tab(self):
        i = self.get_current_tab_index()
        i += 1
        if i > len(self.Tabs) - 1:
            i = 0
        self.current_tab = self.Tabs[i]
