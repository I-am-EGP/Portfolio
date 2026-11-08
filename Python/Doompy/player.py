import math
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from audio import audio


class Player(FirstPersonController):
    def __init__(self, position=(0, 2, 0)):
        super().__init__()
        self.position = position
        self.speed = 8
        self.health = 100
        self.max_health = 100
        self.ammo = 100
        self.max_ammo = 100
        self.score = 0
        self.collider = BoxCollider(self, size=(0.4, 1.9, 0.4))

    def input(self, key):
        if key == "space":
            return
        super().input(key)

    def take_damage(self, amount):
        audio.play("hurt")
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def add_ammo(self, amount):
        self.ammo = min(self.max_ammo, self.ammo + amount)

    def update(self):
        self._apply_force_field()
        super().update()

    def _get_obstacles(self):
        out = []
        for e in scene.entities:
            if getattr(e, "is_wall", False):
                out.append(e)
            elif getattr(e, "pushes_player", False):
                out.append(e)
        return out

    def _apply_force_field(self):
        FIELD = 0.5
        for w in self._get_obstacles():
            whx = getattr(w, "scale_x", 0) * 0.5
            whz = getattr(w, "scale_z", 0) * 0.5

            closest_x = max(w.x - whx, min(self.x, w.x + whx))
            closest_z = max(w.z - whz, min(self.z, w.z + whz))

            dx = self.x - closest_x
            dz = self.z - closest_z
            dist = math.sqrt(dx * dx + dz * dz)

            if dist >= FIELD:
                continue

            if dist > 0.001:
                push = (FIELD - dist) + 0.05
                self.x += (dx / dist) * push
                self.z += (dz / dist) * push
            else:
                left = self.x - (w.x - whx)
                right = (w.x + whx) - self.x
                front = self.z - (w.z - whz)
                back = (w.z + whz) - self.z

                m = min(left, right, front, back)
                if m == left:
                    self.x -= FIELD
                elif m == right:
                    self.x += FIELD
                elif m == front:
                    self.z -= FIELD
                else:
                    self.z += FIELD