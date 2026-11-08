from ursina import *
import random
import os
import sys


ENEMY_FOOTPRINT = {
    "imp": 0,
    "demon": 1,
    "boss": 1,
}


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MapLoader:
    def load_map(self, map_file, wall_height=4):
        map_file = resource_path(map_file)
        if not os.path.exists(map_file):
            print(f"[MapLoader] arquivo não encontrado: {map_file}")
            return [], None, []

        with open(map_file, "r") as f:
            map_data = [list(line) for line in f.read().splitlines()]

        if not map_data:
            print("[MapLoader] arquivo vazio")
            return [], None, []

        height = len(map_data)
        width = max(len(line) for line in map_data)

        for line in map_data:
            while len(line) < width:
                line.append(" ")

        entities = []
        player_start = None
        enemy_types = []

        entities.append(Entity(
            model="cube", color=color.gray,
            position=(width / 2, -0.05, height / 2),
            scale=(width + 4, 0.1, height + 4),
            collider="box",
        ))

        entities.append(Entity(
            model="cube", color=color.rgb32(30, 30, 35),
            position=(width / 2, wall_height, height / 2),
            scale=(width + 4, 0.2, height + 4),
            collider=None,
        ))

        wall_colors = {
            "1": color.rgb32(80, 80, 85),
            "2": color.rgb32(60, 60, 65),
        }
        consumed = [[False] * width for _ in range(height)]

        for y in range(height):
            for x in range(width):
                c = map_data[y][x]

                if c in ("P", "p"):
                    player_start = Vec3(x, 1, y)
                    consumed[y][x] = True

                elif c == "H":
                    entities.append(Entity(
                        model="cube", color=color.green,
                        position=(x, 0.5, y), scale=0.5,
                        item_type="health", amount=25,
                    ))
                    consumed[y][x] = True

                elif c == "A":
                    entities.append(Entity(
                        model="cube", color=color.cyan,
                        position=(x, 0.5, y), scale=0.5,
                        item_type="ammo", amount=30,
                    ))
                    consumed[y][x] = True

                elif c == "i":
                    enemy_types.append("imp")
                    consumed[y][x] = True

                elif c == "d":
                    enemy_types.append("demon")
                    consumed[y][x] = True

                elif c == "b":
                    enemy_types.append("boss")
                    consumed[y][x] = True

                elif c in wall_colors and not consumed[y][x]:
                    w = 0
                    while (x + w < width and
                           map_data[y][x + w] == c and
                           not consumed[y][x + w]):
                        w += 1

                    h = 1
                    while y + h < height:
                        ok = True
                        for dx in range(w):
                            if (x + dx >= width or
                                    map_data[y + h][x + dx] != c or
                                    consumed[y + h][x + dx]):
                                ok = False
                                break
                        if not ok:
                            break
                        h += 1

                    for dy in range(h):
                        for dx in range(w):
                            consumed[y + dy][x + dx] = True

                    cx = x + (w - 1) / 2
                    cz = y + (h - 1) / 2
                    entities.append(Entity(
                        model="cube",
                        color=wall_colors[c],
                        position=(cx, wall_height / 2, cz),
                        scale=(w, wall_height, h),
                        collider="box",
                        is_wall=True,
                    ))

        free_cells = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if map_data[y][x] == "." and not consumed[y][x]
        ]

        if player_start is not None:
            px, pz = player_start.x, player_start.z
            free_cells = [
                (x, y) for (x, y) in free_cells
                if (x - px) ** 2 + (y - pz) ** 2 >= 36
            ]

        random.shuffle(free_cells)
        free_set = set(free_cells)

        enemy_spawns = []
        for etype in enemy_types:
            r = ENEMY_FOOTPRINT.get(etype, 0)
            chosen_idx = None

            for i, (x, y) in enumerate(free_cells):
                ok = True
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if (x + dx, y + dy) not in free_set:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    chosen_idx = i
                    break

            if chosen_idx is None:
                continue

            x, y = free_cells.pop(chosen_idx)
            free_set.discard((x, y))

            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if (dx, dy) == (0, 0):
                        continue
                    nb = (x + dx, y + dy)
                    if nb in free_set:
                        free_set.discard(nb)
                        try:
                            free_cells.remove(nb)
                        except ValueError:
                            pass

            enemy_spawns.append((x, y, etype))

        return entities, player_start, enemy_spawns