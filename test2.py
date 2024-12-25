import pygame

# Scrolling test (work fine)

pygame.init()

# Initialisation de la fenêtre
screen = pygame.display.set_mode((500, 600))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Texte long
long_text = "\n".join([f"Ligne {i+1}: Ceci est une ligne de texte." for i in range(50)])

# Création de la surface pour le texte
text_lines = long_text.splitlines()
line_height = font.get_linesize()
# Surface adaptée à la hauteur du texte
width = screen.get_width() * 0.95
text_surface = pygame.Surface((width, len(text_lines) * line_height))

# Dessin du texte sur la surface
for idx, line in enumerate(text_lines):
    rendered_line = font.render(line, True, (255, 255, 255))
    text_surface.blit(rendered_line, (0, idx * line_height))

# Zone visible (viewport)
viewport = pygame.Rect(10, 10, width, 580)

# Décalage pour le scroll
scroll_offset = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:  # Gestion de la molette de la souris
            scroll_offset -= event.y * 20  # Ajuste la vitesse du scroll
            scroll_offset = max(0, min(scroll_offset, text_surface.get_height() - viewport.height))

    # Affichage
    screen.fill((0, 0, 0))  # Fond noir
    visible_area = text_surface.subsurface((0, scroll_offset, viewport.width, viewport.height))  # Portion visible
    screen.blit(visible_area, viewport.topleft)
    pygame.draw.rect(screen, (255, 0, 0), viewport, 2)  # Optionnel : bordure pour la zone visible

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
