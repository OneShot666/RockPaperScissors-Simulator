import pygame

pygame.init()

# Paramètres de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Position de départ de la ligne
start_x = 200
start_y = HEIGHT // 2
line_length = 100  # Longueur initiale

running = True
while running:
    screen.fill((255, 255, 255))  # Fond blanc

    # Récupération des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, _ = pygame.mouse.get_pos()  # Récupération de la position X de la souris
            line_length = max(10, abs(mx - start_x))  # Mise à jour de la variable de longueur

    # Calcul de l'extrémité de la ligne en fonction de la variable
    end_x = start_x + line_length
    end_pos = (end_x, start_y)

    # Dessiner la ligne
    pygame.draw.line(screen, (0, 0, 0), (start_x, start_y), end_pos, 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
