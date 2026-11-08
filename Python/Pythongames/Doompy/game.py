from ursina import *
from player import Player
from enemy import Enemy
from boss import Boss
from weapon import Weapon
from ui import UI
from map_loader import MapLoader


LEVEL_WALL_HEIGHTS = {
    "assets/maps/level1.txt": 4,
    "assets/maps/level2.txt": 4,
    "assets/maps/level3.txt": 8,
}


class DoomGame(Entity):
    def __init__(self, on_game_over=None):
        super().__init__()

        window.title = "Doom Python"
        Sky(color=color.rgb32(70, 100, 150))

        self.loader = MapLoader()
        self.player = None
        self.ui = None
        self.weapon = None
        self.map_entities = []
        self.enemies = []
        self.enemy_spawns = []
        self.game_over = False
        self.on_game_over = on_game_over
        self.spawn_pos = Vec3(0, 2, 0)
        self.level_file = "assets/maps/level1.txt"

        self._build_world()

    def _build_world(self):
        wall_height = LEVEL_WALL_HEIGHTS.get(self.level_file, 4)
        entities, start_pos, enemy_spawns = self.loader.load_map(
            self.level_file, wall_height=wall_height)
        self.map_entities = entities
        self.enemy_spawns = enemy_spawns

        if start_pos:
            self.spawn_pos = start_pos + Vec3(0, 1, 0)

        if self.player is None:
            self.player = Player(position=self.spawn_pos)
            self.ui = UI(self.player)
            self.weapon = Weapon(self.player)
        else:
            self.player.position = self.spawn_pos
            self.player.health = self.player.max_health
            self.player.ammo = self.player.max_ammo
            self.player.score = 0

        self._spawn_enemies()

    def _spawn_enemies(self):
        self.enemies = []
        for (x, z, t) in self.enemy_spawns:
            if t == "boss":
                e = Boss(position=(x, z), player=self.player, game=self)
            else:
                e = Enemy(position=(x, 0, z), player=self.player, enemy_type=t)
            self.enemies.append(e)

    def respawn_all_demons(self):
        for (x, z, t) in self.enemy_spawns:
            if t != "demon":
                continue
            e = Enemy(position=(x, 0, z), player=self.player, enemy_type="demon")
            self.enemies.append(e)

    def kill_all_enemies(self):
        for e in list(self.enemies):
            if getattr(e, "is_dead", False):
                continue
            e.is_dead = True
            destroy(e)

    def load_level(self, path, keep_score=False):
        for e in self.enemies:
            destroy(e)
        self.enemies = []
        for e in self.map_entities:
            destroy(e)
        self.map_entities = []

        self.game_over = False
        self.level_file = path

        saved_score = self.player.score if (keep_score and self.player) else 0

        self._build_world()

        if keep_score and self.player:
            self.player.score = saved_score

        self.ui.set_visible(True)
        self.weapon.set_visible(True)

    def reset(self):
        self.load_level("assets/maps/level1.txt", keep_score=False)

    def update(self):
        if self.game_over:
            return

        self.enemies = [e for e in self.enemies if not e.is_dead]

        self._check_pickups()

        if self.player.health <= 0:
            self._trigger_game_over(victory=False)
        elif len(self.enemies) == 0:
            self._trigger_game_over(victory=True)

    def _check_pickups(self):
        PICKUP_RADIUS = 0.8
        r2 = PICKUP_RADIUS * PICKUP_RADIUS

        for e in list(self.map_entities):
            if not hasattr(e, "item_type"):
                continue

            dx = self.player.x - e.x
            dz = self.player.z - e.z
            if dx * dx + dz * dz > r2:
                continue

            if e.item_type == "health":
                if self.player.health >= self.player.max_health:
                    continue
                self.player.heal(e.amount)
            elif e.item_type == "ammo":
                if self.player.ammo >= self.player.max_ammo:
                    continue
                self.player.add_ammo(e.amount)

            self.map_entities.remove(e)
            destroy(e)

    def _trigger_game_over(self, victory):
        self.game_over = True
        self.ui.set_visible(False)
        self.weapon.set_visible(False)
        if self.on_game_over:
            self.on_game_over(victory)