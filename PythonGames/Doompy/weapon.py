from ursina import *
import random
from audio import audio


class Weapon(Entity):
    PIXEL = 0.040

    BARREL_COLOR = color.rgb32(30, 30, 35)
    HANDLE_COLOR = color.rgb32(60, 35, 20)

    WEAPONS = {
        "pistol": {
            "damage": 10, "ammo_cost": 1, "fire_rate": 0.3,
            "range": 50, "auto": False,
            "pellets": 1, "spread": 0.0,
            "barrel": 4,  "handle": 1, "rows": 1, "thick": 1,
            "pixel_mult": 2.0,
            "handle_w": 1,
            "front_handle_gap": 0,
        },
        "shotgun": {
            "damage": 12, "ammo_cost": 2, "fire_rate": 0.8,
            "range": 30, "auto": False,
            "pellets": 6, "spread": 4.0,
            "barrel": 6,  "handle": 1, "rows": 1, "thick": 1,
            "pixel_mult": 1.8,
            "handle_w": 1,
            "front_handle_gap": 0,
        },
        "chaingun": {
            "damage": 6, "ammo_cost": 1, "fire_rate": 0.08,
            "range": 60, "auto": True,
            "pellets": 1, "spread": 1.5,
            "barrel": 16, "handle": 4, "rows": 2, "thick": 2,
            "pixel_mult": 0.6,
            "handle_w": 2,
            "front_handle_gap": 2,
        },
    }

    BASE_POS = (0.72, -0.42)
    BASE_ROT = 45
    RECOIL_OFFSET = (0.02, 0.02)

    def __init__(self, player):
        super().__init__(parent=camera.ui)
        self.player = player
        self.current_weapon = "pistol"

        self.weapon_root = Entity(
            parent=camera.ui,
            position=self.BASE_POS,
            rotation_z=self.BASE_ROT,
        )

        self.muzzle = Entity(
            parent=self.weapon_root,
            model="quad",
            color=color.yellow,
            scale=(self.PIXEL * 1.5, self.PIXEL * 1.5),
            enabled=False,
        )

        self.fire_cooldown = 0.0
        self.recoil_timer = 0.0
        self.muzzle_timer = 0.0
        self.mouse_held = False
        self._sprites = []

        self._build_weapon(self.current_weapon)

    def _build_weapon(self, name):
        for s in self._sprites:
            destroy(s)
        self._sprites = []

        cfg = self.WEAPONS[name]
        px = self.PIXEL * cfg["pixel_mult"]
        barrel = cfg["barrel"]
        handle = cfg["handle"]
        rows = cfg["rows"]
        thick = cfg["thick"]
        handle_w = cfg["handle_w"]
        front_gap = cfg["front_handle_gap"]

        barrel_h = rows * thick
        barrel_y_top = (barrel_h - 1) / 2 * px

        # ----- Cano -----
        for r in range(rows):
            for t in range(thick):
                line_index = r * thick + t
                y = barrel_y_top - line_index * px
                for i in range(barrel):
                    x = -(i + 0.5) * px
                    s = Entity(
                        parent=self.weapon_root,
                        model="quad",
                        color=self.BARREL_COLOR,
                        scale=(px, px),
                        position=(x, y),
                    )
                    self._sprites.append(s)

        # ----- Empunhaduras -----
        min_y = barrel_y_top - (barrel_h - 1) * px
        handle_start_y = min_y - px

        # Traseira: topo em handle_start_y, desce handle pixels
        for i in range(handle):
            y = handle_start_y - i * px
            for j in range(handle_w):
                x = -(j + 0.5) * px
                s = Entity(
                    parent=self.weapon_root,
                    model="quad",
                    color=self.HANDLE_COLOR,
                    scale=(px, px),
                    position=(x, y),
                )
                self._sprites.append(s)

        # Dianteira (só se front_gap > 0)
        if front_gap > 0:
            back_left_x = -handle_w * px
            front_right_x = back_left_x - front_gap * px

            for i in range(handle):
                y = handle_start_y - i * px
                for j in range(handle_w):
                    x = front_right_x - (j + 0.5) * px
                    s = Entity(
                        parent=self.weapon_root,
                        model="quad",
                        color=self.HANDLE_COLOR,
                        scale=(px, px),
                        position=(x, y),
                    )
                    self._sprites.append(s)

            # Fileira conectora EMBAIXO das duas empunhaduras
            bottom_y = handle_start_y - handle * px
            total_w = 2 * handle_w + front_gap
            for j in range(total_w):
                x = -(j + 0.5) * px
                s = Entity(
                    parent=self.weapon_root,
                    model="quad",
                    color=self.HANDLE_COLOR,
                    scale=(px, px),
                    position=(x, bottom_y),
                )
                self._sprites.append(s)

        self.muzzle.scale = (px * 1.5, px * 1.5)
        self.muzzle.position = (-barrel * px, barrel_y_top, 0)

    def set_visible(self, visible):
        self.weapon_root.enabled = visible
        if not visible:
            self.muzzle.enabled = False

    def input(self, key):
        if key == "1":
            self._switch_weapon("pistol")
        elif key == "2":
            self._switch_weapon("shotgun")
        elif key == "3":
            self._switch_weapon("chaingun")

    def update(self):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= time.dt
        if self.muzzle_timer > 0:
            self.muzzle_timer -= time.dt
            if self.muzzle_timer <= 0:
                self.muzzle.enabled = False

        if self.recoil_timer > 0:
            self.recoil_timer -= time.dt
            self.weapon_root.position = (
                self.BASE_POS[0] + self.RECOIL_OFFSET[0],
                self.BASE_POS[1] + self.RECOIL_OFFSET[1],
            )
        else:
            self.weapon_root.position = self.BASE_POS

        if mouse.left:
            cfg = self.WEAPONS[self.current_weapon]
            if cfg["auto"] or not self.mouse_held:
                self.shoot()
            self.mouse_held = True
        else:
            self.mouse_held = False

    def _switch_weapon(self, name):
        if name == self.current_weapon:
            return
        self.current_weapon = name
        self._build_weapon(name)

    def shoot(self):
        if self.fire_cooldown > 0:
            return False

        cfg = self.WEAPONS[self.current_weapon]
        if self.player.ammo < cfg["ammo_cost"]:
            return False

        self.player.ammo -= cfg["ammo_cost"]
        self.fire_cooldown = cfg["fire_rate"]
        self.recoil_timer = 0.1

        self.muzzle.enabled = True
        self.muzzle_timer = 0.05
        audio.play("shoot")

        hit_any = False
        for _ in range(cfg["pellets"]):
            direction = camera.forward + Vec3(
                random.uniform(-cfg["spread"], cfg["spread"]) * 0.01,
                random.uniform(-cfg["spread"], cfg["spread"]) * 0.01,
                random.uniform(-cfg["spread"], cfg["spread"]) * 0.01,
            )
            hit_info = raycast(origin=camera.world_position,
                               direction=direction,
                               distance=cfg["range"],
                               ignore=[self.player])
            if hit_info.hit and hasattr(hit_info.entity, "take_damage"):
                hit_info.entity.take_damage(cfg["damage"])
                hit_any = True

        return hit_any