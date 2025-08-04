from pathlib import Path
from typing import Optional
from webcolors import name_to_rgb, IntegerRGB
import pygame


class TextManager:
    def __init__(self, screen_size, db):
        # Variables
        self.screen_size: list[int, int] = screen_size
        # Colors data
        self.Colors =           db.COLORS
        self.bg_color =         db.BG_COLOR
        self.borders_color =    db.BORDER_COLOR
        self.font_color =       db.FONT_COLOR
        # Font data
        self.Fonts: list[pygame.Font] = db.FONTS
        self.main_font: pygame.Font = None                                      # Mostly used font in entire program
        # Text data
        self.scroll_offset = 0
        self.scroll_speed = 20
        self.description: str = None
        # Based function
        self.set_font_size()

    def set_font_size(self, new_size=1):                                        # Change size of the main font
        new_size = max(min(new_size, len(self.Fonts) - 1), -len(self.Fonts))    # Between [-n, n-1]
        self.main_font = self.Fonts[new_size]

    def set_borders_color(self, new_color_name="grey"):                         # Change color of the borders
        if new_color_name in self.Colors.keys():
            self.borders_color = self.Colors[new_color_name]

    def set_font_color(self, new_color_name="black"):                           # Change color of the font
        if type(new_color_name) is str and new_color_name in self.Colors.keys():
            self.font_color = self.Colors[new_color_name]
        elif type(new_color_name) is IntegerRGB and new_color_name in self.Colors.values():
            self.font_color = new_color_name

    @staticmethod
    def get_mouse_hover_position(pos: list[int], mouse: tuple[int, int]):
        return pos[0] <= mouse[0] <= pos[0] + pos[2] and pos[1] <= mouse[1] <= pos[1] + pos[3]

    def get_click_on_position(self, pos, mouse, left_click):
        return self.get_mouse_hover_position(pos, mouse) and left_click

    def get_not_click_on_position(self, pos, mouse, left_click):
        return not self.get_mouse_hover_position(pos, mouse) and left_click

    def use_unactive_color(self, unactive=None):
        unactive = self.borders_color if unactive is None else unactive
        self.set_font_color(unactive)

    def display_message(self, screen: pygame.Surface, percent_x=0.5, percent_y=0.5,
            message="", font_size=1, align="center", percent_size: Optional[list[float]] = None,
            get_pos_only=False):                                                # Display message on screen
        self.set_font_size(font_size)

        if percent_size is None:                                                # If no size limit for message
            text = self.main_font.render(str(message), True, self.font_color)
            coords = [int(self.screen_size[0] * percent_x), int(self.screen_size[1] * percent_y)]
            size = text.get_size()

            if align == "up":                                                   # Text in up-left corner by default
                coords[1] += 0
            elif align == "down":
                coords[1] -= int(size[1])
            elif align == "left":
                coords[0] += 0
            elif align == "right":
                coords[0] -= int(size[0])
            else:
                coords[0] = int(coords[0] - size[0] * 0.5)
                coords[1] = int(coords[1] - size[1] * 0.5)

            if not get_pos_only:                                                # Arg to don't display text
                screen.blit(text, coords)

            return [coords[0], coords[1], size[0], size[1]]                     # Return pos of button
        else:
            pos = [int(self.screen_size[0] * percent_x), int(self.screen_size[1] * percent_y),
                int(self.screen_size[0] * percent_size[0]), int(self.screen_size[1] * percent_size[1])]
            if not get_pos_only:
                self.display_large_text(screen, pos, message)

            return pos

    # [later] Upgrade function with test.py
    def display_large_text(self, screen: pygame.Surface, area: list[int], text: str):   # Display a large text in a given area
        x, y, w, h = area
        x += 5                                                                  # Add a little gap
        y += 5
        space_width, line_height = self.main_font.size("Tg")                    # 'Tg': To get max height of font
        Paragraphs = text.split("\n")

        y_offset = y
        for paragraph in Paragraphs:
            Words = paragraph.split(" ")
            line = ""

            for word in Words:
                test_line = (line + " " + word).strip()
                test_width, _ = self.main_font.size(test_line)

                if test_width <= w:
                    line = test_line
                else:
                    line_surface = self.main_font.render(line, True, self.font_color)
                    screen.blit(line_surface, (x, y_offset))
                    y_offset += line_height
                    line = word

            if line:                                                            # Draw remaining line
                line_surface = self.main_font.render(line, True, self.font_color)
                screen.blit(line_surface, (x, y_offset))
                y_offset += line_height

            y_offset += 5

            if y_offset > y + h:                                                # Stop if above height
                break                                                           # ! Should use scrollable text function

    # ! Move second part of display_message() (with percent_size) in here
    # ! Move to this function if text is too long or is this function instead ?
    def display_scrollable_text(self, screen: pygame.Surface, pos: list[int], text: str, event: pygame.Event):
        """Display a scrollable text (with mouse)"""
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

    def display_bg_name(self, screen: pygame.Surface, name: str):               # Display name of the game in the bg
        self.set_font_color(self.borders_color)
        self.display_message(screen, message=name, font_size=3)
        self.set_font_color()                                                   # Default color
        self.set_font_size()                                                    # Default size

    def display_screen(self, screen: pygame.Surface, pos: list[int], bg_color=None,
            border_width: int = None, border_radius: int = None):
        if bg_color is None:
            bg_color = self.Colors["white"]
        if border_radius is None:
            border_radius = int(pos[3] * 0.5)
        pygame.draw.rect(screen, bg_color, pos, border_radius=border_radius)
        if border_width:
            pygame.draw.rect(screen, self.borders_color, pos, border_width, border_radius)

    def display_parameter(self, screen: pygame.Surface, mouse: list[int], click,
            percent_x=0.5, percent_y=0.5, param=False, message="Parameter : ", description: str = None):
        self.set_font_size(1)

        pos = self.display_message(screen, percent_x, percent_y, message, align="left")

        self.set_font_color("white")                                            # Diff font color to make it readable

        border = 5
        b_p = (border / self.screen_size[0], border / self.screen_size[1])      # b_p : Border percent
        active = 'On' if param else 'Off'
        color = "green" if param else "red"
        width = self.main_font.size(active)[0]
        pos_b = (self.screen_size[0] * percent_x + pos[2], self.screen_size[1] * percent_y - border,
        width + border * 2, pos[3] + border * 2)                       # Position of button

        self.display_screen(screen, pos_b, color, border_radius=10)
        self.display_message(screen, pos_b[0] / self.screen_size[0] + b_p[0],
            pos_b[1] / self.screen_size[1] + b_p[1], active, align='left')

        self.set_font_color()                                                   # Go back to default color

        pos_click = (pos[0], pos[1] - border, pos[2] + pos_b[2], pos[3] + border * 2)
        if self.get_mouse_hover_position(pos_click, mouse) and description is not None:
            self.description = description

        if self.get_click_on_position(pos_click, mouse, click):
            return not param, True
        return param, False

    def display_description(self, screen: pygame.Surface, mouse: list[int]):    # Text to display is mouse overlay
        if self.description:
            gap = 5
            coords = ((mouse[0] + 12) / self.screen_size[0], mouse[1] / self.screen_size[1])
            pos_m = self.display_message(screen, *coords, self.description, 0,
                'left', get_pos_only=True)                                      # Called it before to get position
            pos_m = (pos_m[0] - gap, pos_m[1] - gap, pos_m[2] + gap * 2, pos_m[3] + gap * 2)

            percent_size = None
            if self.screen_size[0] <= pos_m[0] + pos_m[2]:                      # If text too longs
                percent_size = [(self.screen_size[0] - pos_m[0] - gap * 2) / self.screen_size[0],
                    (pos_m[3] * 2) / self.screen_size[1]]
                pos_m = self.display_message(screen, *coords, self.description, 0,
                    'left', percent_size, True)                                 # Recalculate bg size

            self.display_screen(screen, pos_m, None, 2, 5)
            self.display_message(screen, *coords, self.description, 0, 'left', percent_size)

            self.set_font_size()
            self.description = None                                             # Reset description

    def display_box(self, screen: pygame.Surface, x_percent=0.8, y_percent=0.8,
            bg_color=None, border_width=10, border_radius=20):
        if bg_color is None:
            bg_color = self.Colors["white"]
        pos = (self.screen_size[0] * (1 - x_percent) / 2, self.screen_size[1] * (1 - y_percent) / 2,
        self.screen_size[0] * x_percent, self.screen_size[1] * y_percent)
        pygame.draw.rect(screen, bg_color, pos, border_radius=border_radius)
        pygame.draw.rect(screen, self.borders_color, pos, border_width, border_radius)
        return pos

    # Return a boolean when click on one of the 2 buttons : True is the first option, False the second one
    def display_ask_box(self, screen, mouse, click, x_percent=0.35, y_percent=0.35,
            title="Question ?", text='Text', button1="Yes", button2="No"):
        pos = self.display_box(screen, x_percent, y_percent)
        pos_percent = [x / self.screen_size[i % 2] for i, x in enumerate(pos)]
        self.display_message(screen, pos_percent[0] + pos_percent[2] * 0.5,
            pos_percent[1] + self.Fonts[2].get_height() / self.screen_size[1], title, 2)
        if text is not None:
            text_pos = (pos_percent[0] + pos_percent[2] * 0.1, pos_percent[1] + pos_percent[3] * 0.3,
            pos_percent[2] * 0.8, pos_percent[3] * 0.4)
            self.display_message(screen, text_pos[0], text_pos[1], text,
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
            bg_color=None, has_border=False, bg_color_hover=None, no_bg=False, description: str = None):
        pos = (self.screen_size[0] * pos_percent[0], self.screen_size[1] * pos_percent[1],
        self.screen_size[0] * pos_percent[2], self.screen_size[1] * pos_percent[3])
        radius = int(pos[3] * 0.1)

        if bg_color_hover and self.get_mouse_hover_position(pos, mouse):
            bg_color = bg_color_hover
        elif no_bg:
            bg_color = None
        elif bg_color is None:
            bg_color = self.bg_color
        if type(bg_color) is str:
            bg_color = self.Colors[bg_color]
        if bg_color is not None:
            pygame.draw.rect(screen, bg_color, pos, border_radius=radius)

        if self.get_mouse_hover_position(pos, mouse) and description is not None:
            self.description = description

        if has_border:
            pygame.draw.rect(screen, self.borders_color, pos, int(pos[2] * 0.025), radius)
        self.display_message(screen, pos_percent[0] + pos_percent[2] * 0.5,
            pos_percent[1] + pos_percent[3] * 0.5, name)
        return self.get_click_on_position(pos, mouse, click)
