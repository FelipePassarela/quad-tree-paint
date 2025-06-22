import numpy as np
import pygame

from quad_tree_array import QuadTree

WHITE = (245, 233, 223)
BLACK = (107, 85, 66)
GRAY = (207, 188, 180)
RED = (245, 67, 40)
BLUE = (99, 105, 205)
FONT_SIZE = 20

def draw_quadtree(surface, qt):
    for i in range(len(qt)):
        x, y = int(qt.x[i]), int(qt.y[i])
        w, h = int(qt.w[i]), int(qt.h[i])
        pygame.draw.rect(surface, GRAY, (x, y, w, h), 1)

    if np.isnan(qt.cm_x[0]):
        return
    root_cm = int(qt.cm_x[0]), int(qt.cm_y[0])
    pygame.draw.line(surface, BLUE, (root_cm[0] - 4, root_cm[1]), (root_cm[0] + 4, root_cm[1]), 2)
    pygame.draw.line(surface, BLUE, (root_cm[0], root_cm[1] - 4), (root_cm[0], root_cm[1] + 4), 2)


def draw_particles(surface, qt):
    for i in range(len(qt)):
        px, py = qt.px[i], qt.py[i]
        is_leaf = qt.is_leaf[i]
        if is_leaf and not np.isnan(px):
            pygame.draw.circle(surface, RED, (int(px), int(py)), 3)


def draw_fps(surface, fps):
    font = pygame.font.SysFont("Arial", FONT_SIZE)
    fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
    surface.blit(fps_text, (10, 10))


def draw_counters(surface, particles_count, qt):
    font = pygame.font.SysFont("Arial", FONT_SIZE)
    count_text = font.render(f"Particles: {particles_count}", True, BLACK)
    qt_size_text = font.render(f"Quadrants: {len(qt)}", True, BLACK)
    surface.blit(count_text, (10, 40))
    surface.blit(qt_size_text, (10, 70))


def main():
    WIDTH, HEIGHT = 800, 600
    SURFACE = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visualizador de QuadTree")
    pygame.font.init()
    
    running = True
    clock = pygame.time.Clock()

    qtree = QuadTree(0, 0, WIDTH, HEIGHT)
    particles_count = 0

    while running:
        clock.tick(120)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type  == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    qtree.clear()
                    particles_count = 0
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            px, py = pygame.mouse.get_pos()
            particles_count += qtree.insert(px, py, 1.0)

        SURFACE.fill(WHITE)
        draw_quadtree(SURFACE, qtree)
        draw_particles(SURFACE, qtree)
        draw_fps(SURFACE, clock.get_fps())
        draw_counters(SURFACE, particles_count, qtree)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
