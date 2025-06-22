import pygame

from quad_tree_array import QuadTree

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualizador de QuadTree")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

def draw_quadtree(surface, qt):
    for i in range(len(qt.x)):
        x, y = qt.x[i], qt.y[i]
        w, h = qt.w[i], qt.h[i]
        pygame.draw.rect(surface, GRAY, (x, y, w, h), 1)


def draw_particles(surface, qt):
    for i in range(len(qt.px)):
        px, py = qt.px[i], qt.py[i]
        is_leaf = qt.is_leaf[i]
        if is_leaf and px is not None:
            pygame.draw.circle(surface, RED, (px, py), 3)


def main():
    run = True
    clock = pygame.time.Clock()

    qtree = QuadTree(0, 0, WIDTH, HEIGHT)

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONUP:
                px, py = event.pos
                qtree.insert(px, py)
            if event.type  == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    qtree = QuadTree(0, 0, WIDTH, HEIGHT)

        WIN.fill(WHITE)
        draw_quadtree(WIN, qtree)
        draw_particles(WIN, qtree)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
