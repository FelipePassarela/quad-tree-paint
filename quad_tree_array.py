import numpy as np


class QuadTree:
    def __init__(self, x, y, width, height, initial_capacity=4096):
        self.capacity = initial_capacity

        self.x = np.zeros(self.capacity, dtype=np.float32)
        self.y = np.zeros(self.capacity, dtype=np.float32)
        self.w = np.zeros(self.capacity, dtype=np.float32)
        self.h = np.zeros(self.capacity, dtype=np.float32)

        self.px = np.full(self.capacity, np.nan, dtype=np.float32)
        self.py = np.full(self.capacity, np.nan, dtype=np.float32)
        self.eps = 1e-2 * np.sqrt(width**2 + height**2)  # Epsilon for avoiding deep recursion

        self.is_leaf = np.zeros(self.capacity, dtype=bool)
        self.children_idx = -np.ones((self.capacity, 4), dtype=np.int32)

        # Initialize the root node
        self.count = 1
        self.x[0] = x
        self.y[0] = y
        self.w[0] = width
        self.h[0] = height
        self.is_leaf[0] = True
    
    def insert(self, px, py):
        current_idx = 0  # Root

        while True:
            if not self.is_leaf[current_idx]:
                quadrant_idx = self._find_quadrant(px, py, current_idx)
                current_idx = self.children_idx[current_idx, quadrant_idx]
                continue

            is_empty = np.isnan(self.px[current_idx])
            if is_empty:
                self.px[current_idx] = px
                self.py[current_idx] = py
                break
            
            # Avoid deep recursion by checking if the particle is close enough
            dist_sqr = (self.px[current_idx] - px) ** 2 + (self.py[current_idx] - py) ** 2
            if dist_sqr < self.eps:
                break

            self._subdivide(current_idx)

            # Insert old particle in properly quadrant
            old_px, old_py = self.px[current_idx], self.py[current_idx]
            self.px[current_idx], self.py[current_idx] = np.nan, np.nan

            quadrant_idx = self._find_quadrant(old_px, old_py, current_idx)
            child_idx = self.children_idx[current_idx, quadrant_idx]
            self.px[child_idx] = old_px
            self.py[child_idx] = old_py

            # The loop continues to find the correct quadrant for the new particle.
            # current_idx does not change, so the next iteration will start from the current node,
            # which is now no longer a leaf.

    def _find_quadrant(self, px, py, node_idx):
        mid_x = self.x[node_idx] + self.w[node_idx] / 2
        mid_y = self.y[node_idx] + self.h[node_idx] / 2

        if px < mid_x:
            target_idx = 0 if py < mid_y else 2
        else:
            target_idx = 1 if py < mid_y else 3
        return target_idx

    def _subdivide(self, node_idx):
        if self.count + 4 > self.capacity:
            self._resize()

        self.children_idx[node_idx] = list(range(self.count, self.count + 4))
        self.is_leaf[node_idx] = False

        x, y = self.x[node_idx], self.y[node_idx]
        half_w = self.w[node_idx] / 2
        half_h = self.h[node_idx] / 2

        # Append new nodes for the four quadrants
        new_indices = slice(self.count, self.count + 4)
        self.x[new_indices] = [x, x + half_w, x, x + half_w]
        self.y[new_indices] = [y, y, y + half_h, y + half_h]
        self.w[new_indices] = half_w
        self.h[new_indices] = half_h
        self.px[new_indices] = np.nan
        self.py[new_indices] = np.nan
        self.is_leaf[new_indices] = True
        self.children_idx[new_indices] = -1

        self.count += 4

    def _resize(self):
        new_capacity = self.capacity * 2
        
        self.x.resize(new_capacity, refcheck=False)
        self.y.resize(new_capacity, refcheck=False)
        self.w.resize(new_capacity, refcheck=False)
        self.h.resize(new_capacity, refcheck=False)
        
        self.px.resize(new_capacity, refcheck=False)
        self.py.resize(new_capacity, refcheck=False)
        self.px[self.capacity:] = np.nan
        self.py[self.capacity:] = np.nan

        self.is_leaf.resize(new_capacity, refcheck=False)
        self.is_leaf[self.capacity:] = False

        self.children_idx.resize((new_capacity, 4), refcheck=False)
        self.children_idx[self.capacity:] = -1

        self.capacity = new_capacity
        print(f"QuadTree resized to {self.capacity} nodes.")  # DEBUG

    def clear(self):
        self.count = 1
        self.is_leaf[0] = True
        self.children_idx[0] = -1
        self.px[0] = np.nan
        self.py[0] = np.nan

    def __len__(self):
        return self.count
    

