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

        stack = [(current_idx, px, py)]
        while len(stack) > 0:
            current_idx, px, py = stack.pop()

            is_empty = (self.nodes[current_idx].px == None)
            if is_empty:
                self.nodes[current_idx].px = px
                self.nodes[current_idx].py = py

            if not self.nodes[current_idx].is_leaf:
                target_idx = self._find_quadrant(px, py, current_idx)
                child_idx = self.nodes[current_idx].children_idx[target_idx]
                stack.append((child_idx, px, py))

            if self.nodes[current_idx].is_leaf and not is_empty:
                self._subdivide(current_idx)

                # Insert self particle in properly quadrant
                self_px = self.nodes[current_idx].px
                self_py = self.nodes[current_idx].py

                target_idx = self._find_quadrant(self_px, self_py, current_idx)
                child_idx = self.nodes[current_idx].children_idx[target_idx]
                stack .append((child_idx, self_px, self_py))

                # Insert new particle in properly quadrant
                target_idx = self._find_quadrant(px, py, current_idx)
                child_idx = self.nodes[current_idx].children_idx[target_idx]
                stack.append((child_idx, px, py))

    def _find_quadrant(self, px, py, node_idx):
        mid_x = self.nodes[node_idx].x + self.nodes[node_idx].w // 2
        mid_y = self.nodes[node_idx].y + self.nodes[node_idx].h // 2

        if px < mid_x:
            target_idx = 0 if py < mid_y else 2
        else:
            target_idx = 1 if py < mid_y else 3
        return target_idx

    def _subdivide(self, node_idx):
        self.nodes[node_idx].children_idx = list(range(len(self.nodes), len(self.nodes) + 4))
        self.nodes[node_idx].is_leaf = False

        x, y = self.nodes[node_idx].x, self.nodes[node_idx].y
        half_w = self.nodes[node_idx].w // 2
        half_h = self.nodes[node_idx].h // 2

        self.nodes += [
            Node(x, y, half_w, half_h),                    # NE
            Node(x + half_w, y, half_w, half_h),           # NW
            Node(x, y + half_h, half_w, half_h),           # SE
            Node(x + half_w, y + half_h, half_w, half_h),  # SW
        ]

