import numpy as np


class QuadTree:
    def __init__(self, x, y, width, height, initial_capacity=4096):
        self.capacity = initial_capacity

        self.x = np.empty(self.capacity, dtype=np.float32)
        self.y = np.empty(self.capacity, dtype=np.float32)
        self.w = np.empty(self.capacity, dtype=np.float32)
        self.h = np.empty(self.capacity, dtype=np.float32)

        self.px = np.empty(self.capacity, dtype=np.float32)
        self.py = np.empty(self.capacity, dtype=np.float32)
        self.cm_x = np.empty(self.capacity, dtype=np.float32)
        self.cm_y = np.empty(self.capacity, dtype=np.float32)
        self.masses = np.empty(self.capacity, dtype=np.float32)

        self.is_leaf = np.empty(self.capacity, dtype=bool)
        self.children_idx = np.empty((self.capacity, 4), dtype=np.int32)
        self.parent_idx = np.empty(self.capacity, dtype=np.int32)

        # Initialize all arrays with invalid values
        self.invalid_values = {
            "x": np.float32(np.nan),
            "y": np.float32(np.nan),
            "w": np.float32(np.nan),
            "h": np.float32(np.nan),
            "px": np.float32(np.nan),
            "py": np.float32(np.nan),
            "cm_x": np.float32(np.nan),
            "cm_y": np.float32(np.nan),
            "masses": np.float32(0.0),
            "is_leaf": np.bool_(False),
            "children_idx": np.int32(-1),
            "parent_idx": np.int32(-1),
        }

        for attr, value in self.invalid_values.items():
            array = getattr(self, attr)
            if not array.dtype == np.dtype(value):
                raise ValueError(f"Initialization error: dtype mismatch for attribute '{attr}'. Expected {value.dtype}, got {array.dtype}.")
            array.fill(value)

        # Initialize the root node
        self.count = 1
        self.x[0] = x
        self.y[0] = y
        self.w[0] = width
        self.h[0] = height
        self.is_leaf[0] = True

        self.eps = 1e-2 * np.sqrt(width**2 + height**2)  # Epsilon for avoiding deep recursion
    
    def insert(self, px, py, mass):
        insert_success = False
        current_idx = 0  # Root

        while True:
            if not self.is_leaf[current_idx]:
                quadrant_idx = self._find_quadrant(px, py, current_idx)
                current_idx = self.children_idx[current_idx, quadrant_idx]
                continue

            is_empty = np.isnan(self.px[current_idx])
            if is_empty:
                self._insert_particle(px, py, mass, current_idx)
                insert_success = True
                break
            
            # Avoid deep recursion by checking if the particle is close enough
            dist_sqr = (self.px[current_idx] - px) ** 2 + (self.py[current_idx] - py) ** 2
            if dist_sqr < self.eps:
                insert_success = False
                break

            self._subdivide(current_idx)

            # The loop continues to find the correct quadrant for the new particle.
            # current_idx does not change, so the next iteration will start from the current node,
            # which is now no longer a leaf.

        if insert_success:
            self._update_cm(current_idx)
        return insert_success
    
    def compute_forces(self, px, py, mass, g=1.0, theta=0.5):
        fx, fy = 0.0, 0.0
        stack = [0]

        while stack:
            node_idx = stack.pop()

            if np.isnan(self.cm_x[node_idx]) or self.masses[node_idx] == 0.0:
                continue
            if self.is_leaf[node_idx] and px == self.px[node_idx] and py == self.py[node_idx]:
                # Skip the particle itself
                continue

            dx = self.cm_x[node_idx] - px
            dy = self.cm_y[node_idx] - py
            dist_sq = dx * dx + dy * dy + 1e-1
            dist = np.sqrt(dist_sq)
            s = self.w[node_idx]

            if self.is_leaf[node_idx] or (s / dist) < theta:
                force_mag = g * mass * self.masses[node_idx] / (dist_sq * dist)
                fx += force_mag * dx
                fy += force_mag * dy
            else:
                stack.extend(child_idx for child_idx in self.children_idx[node_idx] if child_idx != -1)

        return np.array([fx, fy], dtype=np.float32)

    def _insert_particle(self, px, py, mass, node_idx):
        self.px[node_idx] = px
        self.py[node_idx] = py
        self.cm_x[node_idx] = px
        self.cm_y[node_idx] = py
        self.masses[node_idx] = mass

    def _update_cm(self, leaf_idx):
        current = leaf_idx
        while True:
            parent = self.parent_idx[current]
            if parent == -1:
                break

            total_mass = 0.0
            weighted_x = 0.0
            weighted_y = 0.0

            for child_idx in self.children_idx[parent]:
                if child_idx == -1 or np.isnan(self.cm_x[child_idx]):
                    continue
                total_mass += self.masses[child_idx]
                weighted_x += self.cm_x[child_idx] * self.masses[child_idx]
                weighted_y += self.cm_y[child_idx] * self.masses[child_idx]

            if total_mass > 0.0:  # Preserve default values if no mass is present
                self.cm_x[parent] = weighted_x / total_mass
                self.cm_y[parent] = weighted_y / total_mass
                self.masses[parent] = total_mass

            current = parent

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

        self.children_idx[node_idx] = np.arange(self.count, self.count + 4, dtype=np.int32)
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
        self.is_leaf[new_indices] = True
        self.parent_idx[new_indices] = node_idx

        # Insert old particle in properly child
        old_px = self.px[node_idx]
        old_py = self.py[node_idx]
        old_mass = self.masses[node_idx]
        self._insert_particle(self.invalid_values["px"], 
                              self.invalid_values["py"], 
                              self.invalid_values["masses"], 
                              node_idx)
        
        quadrant_idx = self._find_quadrant(old_px, old_py, node_idx)
        child_idx = self.children_idx[node_idx, quadrant_idx]
        self._insert_particle(old_px, old_py, old_mass, child_idx)
        
        self.count += 4

    def _resize(self):
        new_capacity = self.capacity * 2

        for attr, value in self.invalid_values.items():
            array = getattr(self, attr)
            new_shape = (new_capacity,) + array.shape[1:] if array.ndim > 1 else (new_capacity,)
            array.resize(new_shape, refcheck=False)
            array[self.capacity:] = value

        self.capacity = new_capacity
        print(f"QuadTree resized to {self.capacity} nodes.")  # DEBUG

    def clear(self):
        root_x, root_y = self.x[0], self.y[0]
        root_w, root_h = self.w[0], self.h[0]

        for attr, value in self.invalid_values.items():
            array = getattr(self, attr)
            array.fill(value)

        # Reset the root node
        self.count = 1
        self.x[0] = root_x
        self.y[0] = root_y
        self.w[0] = root_w
        self.h[0] = root_h
        self.is_leaf[0] = True
        
    def __len__(self):
        return self.count
    

