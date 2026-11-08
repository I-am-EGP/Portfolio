from ursina import *
import math
import random
from audio import audio


ENEMY_TYPES = {
    "imp": {
        "health": 20, "damage": 5, "speed": 4.5,
        "scale": (1, 1, 1),
        "attack_range": 1.5, "attack_cooldown": 1.0,
    },
    "demon": {
        "health": 50, "damage": 15, "speed": 2.5,
        "scale": (1.5, 3, 1.5),
        "attack_range": 1.8, "attack_cooldown": 1.2,
    },
}


ENEMY_PART_COLORS = {
    "imp": {
        "head":  color.rgb32(230, 90, 90),
        "torso": color.rgb32(230, 90, 90),
        "arm":   color.rgb32(230, 90, 90),
        "leg":   color.rgb32(230, 90, 90),
    },
    "demon": {
        "head":  color.rgb32(140, 140, 140),
        "torso": color.rgb32(120, 20, 20),
        "arm":   color.rgb32(120, 20, 20),
        "leg":   color.rgb32(60, 35, 20),
    },
}


ENEMY_PARTS_LAYOUT = [
    ("head",  (0.0,  0.35, 0.0), (0.60, 0.25, 0.60)),
    ("torso", (0.0,  0.05, 0.0), (0.70, 0.40, 0.50)),
    ("arm",   (-0.40, 0.05, 0.0), (0.15, 0.40, 0.15)),
    ("arm",   (0.40,  0.05, 0.0), (0.15, 0.40, 0.15)),
    ("leg",   (-0.20, -0.35, 0.0), (0.25, 0.30, 0.35)),
    ("leg",   (0.20,  -0.35, 0.0), (0.25, 0.30, 0.35)),
]


class Enemy(Entity):
    def __init__(self, position=(0, 0, 0), player=None, enemy_type="imp"):
        cfg = ENEMY_TYPES[enemy_type]
        size = cfg["scale"]

        super().__init__(
            position=(position[0], size[1] / 2, position[2]),
            model="cube",
            color=color.rgba(0, 0, 0, 0),
            scale=size,
            collider="box",
        )

        self.player = player
        self.enemy_type = enemy_type
        self.max_health = cfg["health"]
        self.health = cfg["health"]
        self.damage = cfg["damage"]
        self.speed = cfg["speed"]
        self.attack_range = cfg["attack_range"]
        self.attack_cooldown_time = cfg["attack_cooldown"]
        self.attack_cooldown = 0.0

        self.hit_flash_timer = 0.0
        self.is_dead = False
        self._walls = None

        # Faz o campo de força do player nos tratar como obstáculo
        self.pushes_player = True

        self.view_distance = 15
        self.wander_dir = Vec3(0, 0, 0)
        self.wander_timer = 0.0

        self.parts = []
        self._build_body()

    def _build_body(self):
        colors = ENEMY_PART_COLORS[self.enemy_type]
        for name, pos, scale_ in ENEMY_PARTS_LAYOUT:
            c = colors[name]
            e = Entity(
                parent=self,
                model="cube",
                color=c,
                position=pos,
                scale=scale_,
            )
            self.parts.append((e, c))

    def _flash(self, c):
        for e, _ in self.parts:
            e.color = c

    def _restore_colors(self):
        for e, base in self.parts:
            e.color = base

    def update(self):
        if self.is_dead or self.player is None:
            return
        if self.player.health <= 0:
            return

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= time.dt
            if self.hit_flash_timer <= 0:
                self._restore_colors()

        d = distance(self, self.player)

        if self._can_see_player():
            self._look_flat_at(self.player.position)
            if d > self.attack_range * 0.9:
                self._move_with_separation()
        else:
            self._wander()

        self.attack_cooldown -= time.dt
        if d < self.attack_range and self.attack_cooldown <= 0:
            self.player.take_damage(self.damage)
            self.attack_cooldown = self.attack_cooldown_time

    def _look_flat_at(self, target):
        dx = target.x - self.x
        dz = target.z - self.z
        if abs(dx) + abs(dz) > 0.001:
            self.rotation_y = math.degrees(math.atan2(dx, dz))

    def _can_see_player(self):
        d = distance(self, self.player)
        if d > self.view_distance:
            return False

        origin = Vec3(self.x, 0.9, self.z)
        target = Vec3(self.player.x, 0.9, self.player.z)
        direction = target - origin
        if direction.length() < 0.01:
            return True
        direction = direction.normalized()

        ignore = [self]
        for e in scene.entities:
            if isinstance(e, Enemy) and e is not self:
                ignore.append(e)

        hit = raycast(origin, direction,
                      distance=self.view_distance, ignore=ignore)
        if not hit.hit:
            return False
        return hit.entity is self.player

    def _ensure_walls(self):
        if self._walls is not None:
            return
        walls = []
        for e in scene.entities:
            if e is self:
                continue
            if isinstance(e, Enemy):
                continue
            if getattr(e, "item_type", None) is not None:
                continue
            if hasattr(e, "health"):
                continue
            if getattr(e, "collider", None) is None:
                continue
            walls.append(e)
        self._walls = walls

    def _aabb_clear(self, new_pos):
        self._ensure_walls()

        hx = self.scale_x * 0.5
        hy = self.scale_y * 0.5
        hz = self.scale_z * 0.5

        n_min_x = new_pos.x - hx
        n_max_x = new_pos.x + hx
        n_min_y = new_pos.y - hy
        n_max_y = new_pos.y + hy
        n_min_z = new_pos.z - hz
        n_max_z = new_pos.z + hz

        for w in self._walls:
            wx = getattr(w, "scale_x", 0) * 0.5
            wy = getattr(w, "scale_y", 0) * 0.5
            wz = getattr(w, "scale_z", 0) * 0.5

            if (n_min_x < w.x + wx and n_max_x > w.x - wx and
                    n_min_y < w.y + wy and n_max_y > w.y - wy and
                    n_min_z < w.z + wz and n_max_z > w.z - wz):
                return False
        return True

    def _overlaps_player(self, new_pos):
        """True se o AABB do inimigo em new_pos sobrepõe o do player (só X/Z)."""
        if self.player is None:
            return False
        hx = self.scale_x * 0.5
        hz = self.scale_z * 0.5

        e_min_x = new_pos.x - hx
        e_max_x = new_pos.x + hx
        e_min_z = new_pos.z - hz
        e_max_z = new_pos.z + hz

        p_hx = 0.4 * 0.5
        p_hz = 0.4 * 0.5
        p_min_x = self.player.x - p_hx
        p_max_x = self.player.x + p_hx
        p_min_z = self.player.z - p_hz
        p_max_z = self.player.z + p_hz

        return (e_min_x < p_max_x and e_max_x > p_min_x and
                e_min_z < p_max_z and e_max_z > p_min_z)

    def _try_move(self, direction, step):
        new_pos = self.position + direction * step
        if not self._aabb_clear(new_pos):
            new_pos = None
        elif self._overlaps_player(new_pos):
            new_pos = None

        if new_pos is not None:
            self.position = new_pos
            return True

        perp_a = Vec3(-direction.z, 0, direction.x)
        perp_b = Vec3(direction.z, 0, -direction.x)

        new_a = self.position + perp_a * step
        if self._aabb_clear(new_a) and not self._overlaps_player(new_a):
            self.position = new_a
            return True

        new_b = self.position + perp_b * step
        if self._aabb_clear(new_b) and not self._overlaps_player(new_b):
            self.position = new_b
            return True

        return False

    def _move_with_separation(self):
        step = self.speed * time.dt

        for other in scene.entities:
            if other is self:
                continue
            if not isinstance(other, Enemy) or other.is_dead:
                continue
            if distance(self, other) < 1.4:
                away = self.position - other.position
                away.y = 0
                if away.length() > 0.01:
                    self._try_move(away.normalized(), step)
                return

        direction = self.player.position - self.position
        direction.y = 0
        if direction.length() < 0.01:
            return
        self._try_move(direction.normalized(), step)

    def _wander(self):
        self.wander_timer -= time.dt
        if self.wander_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            self.wander_dir = Vec3(math.sin(angle), 0, math.cos(angle))
            self.wander_timer = random.uniform(1.0, 2.5)

        step = self.speed * 0.5 * time.dt
        if not self._try_move(self.wander_dir, step):
            self.wander_timer = 0.0

    def take_damage(self, amount):
        if self.is_dead:
            return
        self.health -= amount
        self._flash(color.white)
        self.hit_flash_timer = 0.1

        if self.health <= 0:
            self.is_dead = True
            if self.player:
                self.player.score += 50
            audio.play("death")
            destroy(self)
        else:
            audio.play("hit")