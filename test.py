from math import *
from random import *
from time import time, sleep
from entity import Entity
import pygame


# Draw a long text in a box (then add scrolling function in test2.py)
def draw_text_in_box(screen, box_rect, text, font, text_color, box_color):
    pygame.draw.rect(screen, box_color, box_rect)

    max_width = box_rect.width * 0.9
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)  # Ajouter la ligne complète
            current_line = word  # Commencer une nouvelle ligne

    if current_line:                                                            # Add last line
        lines.append(current_line)

    # Dessiner chaque ligne de texte, centrée dans la boîte
    # 'Tg' : in order to mesure full height of font with uppercase and low char like 'g' or 'y'
    total_text_height = len(lines) * font.size("Tg")[1]                         # Hauteur totale du texte
    start_y = box_rect.top + (box_rect.height - total_text_height) // 2         # Point de départ vertical

    for i, line in enumerate(lines):
        line_surface = font.render(line, True, text_color)
        line_width, line_height = line_surface.get_size()
        x = box_rect.left + (box_rect.width - line_width) // 2                  # Centrer horizontalement
        y = start_y + i * line_height                                           # Ajuster verticalement
        screen.blit(line_surface, (x, y))


def test(*args):
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    font = pygame.font.Font(None, 36)  # Police par défaut avec taille 36
    text = "Ceci est un texte très long qui doit être divisé en plusieurs lignes si nécessaire."
    running = True

    while running:
        screen.fill((30, 30, 30))  # Fond gris foncé

        box = pygame.Rect(150, 100, 300, 200)                                   # Définir une boîte
        draw_text_in_box(screen, box, text, font, (255, 255, 255), (50, 50, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    test()
