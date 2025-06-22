import numpy as np


class QuadTree:
    def __init__(self, x, y, width, height):
        self.x = [x]
        self.y = [y]
        self.w = [width]
        self.h = [height]
        self.px = [None]
        self.py = [None]
        self.is_leaf = [True]
        self.children_idx = [[None, None, None, None]]
        self.eps = 1e-6 * np.sqrt(width * height)
    
    def insert(self, px, py):
        current_idx = 0  # Root

        while True:
            if not self.is_leaf[current_idx]:
                quadrant_idx = self._find_quadrant(px, py, current_idx)
                current_idx = self.children_idx[current_idx][quadrant_idx]
                continue

            is_empty = (self.px[current_idx] == None)
            if is_empty:
                self.px[current_idx] = px
                self.py[current_idx] = py
                break
            else:
                # Avoid deep recursion by checking if the particle is close enough
                dist_sqr = (self.px[current_idx] - px) ** 2 + (self.py[current_idx] - py) ** 2
                if dist_sqr < self.eps:
                    break

                self._subdivide(current_idx)

                # Insert old particle in properly quadrant
                old_px, old_py = self.px[current_idx], self.py[current_idx]
                self.px[current_idx], self.py[current_idx] = None, None

                quadrant_idx = self._find_quadrant(old_px, old_py, current_idx)
                child_idx = self.children_idx[current_idx][quadrant_idx]
                self.px[child_idx] = old_px
                self.py[child_idx] = old_py

            # The loop continues to find the correct quadrant for the new particle.
            # current_idx does not change, so the next iteration will start from the current node,
            # which is now no longer a leaf.

    def _find_quadrant(self, px, py, node_idx):
        mid_x = self.x[node_idx] + self.w[node_idx] // 2
        mid_y = self.y[node_idx] + self.h[node_idx] // 2

        if px < mid_x:
            target_idx = 0 if py < mid_y else 2
        else:
            target_idx = 1 if py < mid_y else 3
        return target_idx

    def _subdivide(self, node_idx):
        self.children_idx[node_idx] = list(range(len(self.x), len(self.x) + 4))
        self.is_leaf[node_idx] = False

        x, y = self.x[node_idx], self.y[node_idx]
        half_w = self.w[node_idx] // 2
        half_h = self.h[node_idx] // 2

        self.x.extend([x, x + half_w, x, x + half_w])
        self.y.extend([y, y, y + half_h, y + half_h])
        self.w.extend([half_w, half_w, half_w, half_w])
        self.h.extend([half_h, half_h, half_h, half_h])

        self.px.extend([None] * 4)
        self.py.extend([None] * 4)
        self.is_leaf.extend([True] * 4)
        self.children_idx.extend([[None, None, None, None] for _ in range(4)])
