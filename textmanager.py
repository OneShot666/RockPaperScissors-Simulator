# from math import *
# from random import *
# from time import *
from webcolors import name_to_rgb
from pathlib import Path
import pygame


class TextManager:
    def __init__(self, screen_size):
        # Variables
        self.path = str(Path(__file__).parent)                                  # Current programm path
        self.screen_size = screen_size
        # Colors data
        self.ColorNames = ["red", "orange", "wheat", "gold", "yellow", "green",
                           "cyan", "blue", "purple", "deeppink", "brown",
                           "lightgrey", "grey", "white", "black"]
        self.Colors = {color: name_to_rgb(color) for color in self.ColorNames}
        self.bg_color = self.Colors["lightgrey"]                                # For screens
        self.borders_color = self.Colors["grey"]
        self.font_color = self.Colors["black"]
        # Font data
        self.Fonts = []
        self.FontSizes = {"small": 25, "middle": 40, "big": 60, "giant": 80}
        self.font_name: str = None
        self.main_font: pygame.font.Font = None
        self.set_font_size(self.FontSizes["middle"])
        # Text data
        self.scroll_offset = 0
        self.scroll_speed = 20
        self.description = None

    def set_borders_color(self, new_color_name="grey"):                         # Change color of the borders
        if new_color_name in self.Colors.keys():
            self.borders_color = self.Colors[new_color_name]

    def set_font_color(self, new_color_name="black"):                           # Change color of the font
        if new_color_name in self.Colors.keys():
            self.font_color = self.Colors[new_color_name]

    def set_font_size(self, new_size=40):                                       # Change size of the main font
        font_path = f"{self.path}/fonts/{self.font_name}" if self.font_name else None
        self.main_font = pygame.font.Font(font_path, new_size)

    @staticmethod
    def get_mouse_hover_position(pos, mouse):
        return pos[0] <= mouse[0] <= pos[0] + pos[2] and pos[1] <= mouse[1] <= pos[1] + pos[3]

    def get_click_on_position(self, pos, mouse, left_click):
        return self.get_mouse_hover_position(pos, mouse) and left_click

    def get_not_click_on_position(self, pos, mouse, left_click):
        return not self.get_mouse_hover_position(pos, mouse) and left_click

    # ! Move second part of display_message() (with percent_size) in here
    def display_scrollable_text(self, screen, pos, text, event):                # Display a scrollable text (with mouse)
        lines = text.splitlines()
        line_height = self.main_font.get_linesize()
        surface = pygame.Surface((pos[2], len(lines) * line_height), pygame.SRCALPHA)
        viewport = pygame.Rect(*pos)                                            # Visible zone

        for i, line in enumerate(lines):                                        # Draw lines on surface
            rendered_line = self.main_font.render(str(line), True, "white")
            # rendered_line = self.main_font.render(str(line), True, self.font_color)
            surface.blit(rendered_line, (0, i * line_height))

        if event and event.type == pygame.MOUSEWHEEL:                           # If scrolling
            self.scroll_offset -= event.y * self.scroll_speed
            self.scroll_offset = max(0, min(self.scroll_offset, surface.get_height() - viewport.height))

        visible_area = surface.subsurface((0, self.scroll_offset, viewport.width, viewport.height))  # Portion visible
        screen.blit(visible_area, viewport.topleft)

    def display_large_text(self, screen, pos, text):                            # Display a large text in a given area
        Words = text.split()
        Lines = []
        current_line = ""

        for word in Words:                                                      # Get lines based on message's lenght
            test_line = current_line + (" " if current_line else "") + word
            # The '+ 5' is just to leave some margin
            if self.main_font.size(test_line)[0] <= pos[2] + 5:                 # If line is under max lenght
                current_line = test_line
            else:
                Lines.append(current_line)                                      # Add full line
                current_line = word                                             # Start a new line

        if current_line:                                                        # Add last line
            Lines.append(current_line)

        # "Tg" : in order to mesure full height of font with uppercase and low char like 'g' or 'y'
        total_text_height = len(Lines) * self.main_font.size("Tg")[1]           # Text's height
        start_y = pos[1] + (pos[3] - total_text_height) // 2

        for i, line in enumerate(Lines):                                        # Draw each line
            line_surface = self.main_font.render(line, True, self.font_color)
            line_width, line_height = line_surface.get_size()
            x = pos[0] + (pos[2] - line_width) // 2                             # Center text
            y = start_y + i * line_height
            screen.blit(line_surface, (x, y))

    def display_message(self, screen, percent_x=0.5, percent_y=0.5, message="",
    font_size=None, position=None, percent_size=None, get_pos_only=False):      # Display message on screen
        if font_size is not None:                                               # Change font size if a new one is required
            self.set_font_size(self.FontSizes[font_size])

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

            if not get_pos_only:
                screen.blit(text, coords)

            return [coords[0], coords[1], size[0], size[1]]                     # Return pos of button
        else:
            pos = [int(self.screen_size[0] * percent_x), int(self.screen_size[1] * percent_y),
                   int(self.screen_size[0] * percent_size[0]), int(self.screen_size[1] * percent_size[1])]
            if not get_pos_only:
                self.display_large_text(screen, pos, message)

            return pos

    def display_bg_name(self, screen, name):                                    # Display name of the game in the bg
        self.set_font_color("grey")
        self.display_message(screen, message=name, font_size="giant")
        self.set_font_color()                                                   # Default color
        self.set_font_size()                                                    # Default size

    def display_screen(self, screen, pos, bg_color=None, border_width=None, border_radius=None):
        if bg_color is None:
            bg_color = self.Colors["white"]
        if border_radius is None:
            border_radius = int(pos[3] * 0.5)
        pygame.draw.rect(screen, bg_color, pos, border_radius=border_radius)
        if border_width:
            pygame.draw.rect(screen, self.borders_color, pos, border_width, border_radius)

    def display_parameter(self, screen, mouse, click, percent_x=0.5, percent_y=0.5,
    param=False, message="Parameter : ", description=None):
        old_size = self.main_font.get_height()
        self.set_font_size(self.FontSizes["middle"])

        pos = self.display_message(screen, percent_x, percent_y, message, "middle", "left")

        self.set_font_color("white")

        border = 5
        b_p = (border / self.screen_size[0], border / self.screen_size[1])      # b_p : Border percent
        active = 'On' if param else 'Off'
        color = "green" if param else "red"
        width = self.main_font.size(active)[0]
        pos_b = (self.screen_size[0] * percent_x + pos[2], self.screen_size[1] * percent_y - border,
                 width + border * 2, pos[3] + border * 2)                       # Position of button

        self.display_screen(screen, pos_b, color, border_radius=10)
        self.display_message(screen, pos_b[0] / self.screen_size[0] + b_p[0],
            pos_b[1] / self.screen_size[1] + b_p[1], active, position='left')

        self.set_font_color()                                                   # Go back to default color

        pos_click = (pos[0], pos[1] - border, pos[2] + pos_b[2], pos[3] + border * 2)
        if self.get_mouse_hover_position(pos_click, mouse) and description is not None:
            self.description = description

        self.set_font_size(old_size)                                            # Go back to old font size

        if self.get_click_on_position(pos_click, mouse, click):
            return not param, True
        return param, False

    def display_description(self, screen, mouse):
        if self.description:
            self.set_font_size(25)

            gap = 5
            coords = ((mouse[0] + 12) / self.screen_size[0], mouse[1] / self.screen_size[1])
            pos_m = self.display_message(screen, *coords, self.description,
                position='left', get_pos_only=True)                             # Called it before to get position
            pos_m = (pos_m[0] - gap, pos_m[1] - gap, pos_m[2] + gap * 2, pos_m[3] + gap * 2)

            percent_size = None
            if self.screen_size[0] <= pos_m[0] + pos_m[2]:                      # If text too long
                percent_size = [(self.screen_size[0] - pos_m[0] - gap * 2) / self.screen_size[0],
                                (pos_m[3] * 2) / self.screen_size[1]]
                pos_m = self.display_message(screen, *coords, self.description,
                    position='left', percent_size=percent_size, get_pos_only=True)  # Recalculate bg size

            self.display_screen(screen, pos_m, border_width=2, border_radius=5)
            self.display_message(screen, *coords, self.description, position='left', percent_size=percent_size)

            self.set_font_size()
            self.description = None                                             # Reset description

    def display_box(self, screen, x_percent=0.8, y_percent=0.8, bg_color=None, border_width=10, border_radius=20):
        if bg_color is None:
            bg_color = self.Colors["white"]
        pos = (self.screen_size[0] * (1 - x_percent) / 2, self.screen_size[1] * (1 - y_percent) / 2,
               self.screen_size[0] * x_percent, self.screen_size[1] * y_percent)
        pygame.draw.rect(screen, bg_color, pos, border_radius=border_radius)
        pygame.draw.rect(screen, self.borders_color, pos, border_width, border_radius)
        return pos

    # Return a boolean when click on one of the 2 button : True is the first option, False the second one
    def display_ask_box(self, screen, mouse, click, x_percent=0.35, y_percent=0.35,
    title="Question ?", text='Text', button1="Yes", button2="No"):
        pos = self.display_box(screen, x_percent, y_percent)
        pos_percent = [x / self.screen_size[i % 2] for i, x in enumerate(pos)]
        size = None
        self.display_message(screen, pos_percent[0] + pos_percent[2] * 0.5,
                             pos_percent[1] + self.FontSizes["big"] / self.screen_size[1], title, "big")
        if text is not None:
            text_pos = (pos_percent[0] + pos_percent[2] * 0.1, pos_percent[1] + pos_percent[3] * 0.3,
                        pos_percent[2] * 0.8, pos_percent[3] * 0.4)
            self.display_message(screen, text_pos[0], text_pos[1], text, "middle",
                                 percent_size=(text_pos[2], text_pos[3]))
        button_pos = [pos_percent[0] + pos_percent[2] * 0.05, pos_percent[1] + pos_percent[3] * 0.7,
                      pos_percent[2] * 0.4, pos_percent[3] * 0.25]
        if self.display_button(screen, mouse, click, button1, button_pos, self.borders_color, True, self.bg_color):
            return True
        button_pos[0] += (pos_percent[2] * 0.5)                               # Second button is more to the right
        if (self.display_button(screen, mouse, click, button2, button_pos, self.borders_color, True, self.bg_color) or
                self.get_not_click_on_position(pos_percent, mouse, click)):
            return False
        return None

    def display_button(self, screen, mouse, click, name="", pos_percent=(0, 0, 0, 0),
    bg_color=None, has_border=False, bg_color_hover=None):
        pos = (self.screen_size[0] * pos_percent[0], self.screen_size[1] * pos_percent[1],
               self.screen_size[0] * pos_percent[2], self.screen_size[1] * pos_percent[3])
        radius = int(pos[3] * 0.1)
        if bg_color_hover and self.get_mouse_hover_position(pos, mouse):
            bg_color = bg_color_hover
        elif bg_color is None:
            bg_color = self.bg_color
        if type(bg_color) is str:
            bg_color = self.Colors[bg_color]
        pygame.draw.rect(screen, bg_color, pos, border_radius=radius)
        if has_border:
            pygame.draw.rect(screen, self.borders_color, pos, int(pos[2] * 0.025), radius)
        self.display_message(screen, pos_percent[0] + pos_percent[2] * 0.5,
                             pos_percent[1] + pos_percent[3] * 0.5, name, "middle")
        return self.get_click_on_position(pos, mouse, click)
