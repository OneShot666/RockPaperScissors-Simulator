from math import inf, sqrt
from random import *
from time import time, sleep
from entity import Entity
from textmanager import TextManager
from collections import defaultdict
from pathlib import Path
import pygame
import os


def test1(*args):
    # Initialisation
    pygame.init()
    screen_size = (800, 600)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Scrollable Text Test")

    text_manager = TextManager(screen_size)

    pos = (50, 50, 700, 500)  # x, y, width, height for the text box
    text = "\n".join([f"Line {i + 1}" for i in range(50)])  # Example text with 50 lines

    # Boucle principale
    running = True
    while running:
        screen.fill("lightgrey")
        event = None

        # Draw the border of the text box
        pygame.draw.rect(screen, "grey", pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Display the scrollable text
        text_manager.display_scrollable_text(screen, pos, text, event)

        pygame.display.flip()

    pygame.quit()


def test2(*args):
    percent = 0
    for i in range(10000):
        percent = randint(50000, 100000) // (i + 1)
    print(percent)


def time_function(func, *args):                                                 # Mesure du temps d'exécution
    start_time = time()
    func(*args)
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Temps d'exécution de {func.__name__}: {elapsed_time:.10f} secondes")
    return elapsed_time


def test():
    time_test1 = time_function(test1)
    # time_test2 = time_function(test2)


if __name__ == "__main__":
    test()
