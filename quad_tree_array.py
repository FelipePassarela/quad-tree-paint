class Node:
    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.w, self.h = width, height
        self.children_idx = [None]
        self.is_leaf = True
        self.px, self.py = None, None


class QuadTree:
    def __init__(self, x, y, width, height):
        self.nodes = [Node(x, y, width, height)]
    
    def insert(self, px, py):
        current_idx = 0  # Root

        while True:
            node = self.nodes[current_idx]

            if not node.is_leaf:
                quadrant_idx = self._find_quadrant(px, py, node)
                current_idx = node.children_idx[quadrant_idx]
                continue

            is_empty = (node.px == None)
            if is_empty:
                node.px = px
                node.py = py
                break
            else:
                # Avoid deep recursion by checking if the particle is already in the node
                dist_sqr = (node.px - px) ** 2 + (node.py - py) ** 2
                if dist_sqr < 1e-6:
                    break

                self._subdivide(node)

                # Insert old particle in properly quadrant
                old_px, old_py = node.px, node.py
                node.px, node.py = None, None

                quadrant_idx = self._find_quadrant(old_px, old_py, node)
                child_idx = node.children_idx[quadrant_idx]
                child = self.nodes[child_idx]
                child.px, child.py = old_px, old_py

    def _find_quadrant(self, px, py, node):
        mid_x = node.x + node.w // 2
        mid_y = node.y + node.h // 2

        if px < mid_x:
            target_idx = 0 if py < mid_y else 2
        else:
            target_idx = 1 if py < mid_y else 3
        return target_idx

    def _subdivide(self, node):
        node.children_idx = list(range(len(self.nodes), len(self.nodes) + 4))
        node.is_leaf = False

        x, y = node.x, node.y
        half_w = node.w // 2
        half_h = node.h // 2

        self.nodes += [
            Node(x, y, half_w, half_h),                    # NE
            Node(x + half_w, y, half_w, half_h),           # NW
            Node(x, y + half_h, half_w, half_h),           # SE
            Node(x + half_w, y + half_h, half_w, half_h),  # SW
        ]

