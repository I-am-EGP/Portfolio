from ursina import *
import math
from audio import audio


BOSS_COLOR = color.rgb32(20, 80, 20)
BOSS_WIDTH = 3
BOSS_HEIGHT = 6
BOSS_DEPTH = 3
BOSS_MAX_HEALTH = 2000
BOSS_MELEE_DAMAGE = 35
BOSS_MELEE_RANGE = 2.5
BOSS_MELEE_COOLDOWN = 1.5
BOSS_FIREBALL_DAMAGE = 40
BOSS_FIREBALL_COOLDOWN = 5.0
BOSS_SPEED = 1.2
FIREBALL_SPEED = 70.0


BOSS_PART_COLORS = {
    "head":  BOSS_COLOR,
    "torso": BOSS_COLOR,
    "arm":   BOSS_COLOR,
    "leg":   BOSS_COLOR,
}


BOSS_PARTS_LAYOUT = [
    ("head",  (0.0,  0.35, 0.0), (0.60, 0.25, 0.60)),
    ("torso", (0.0,  0.05, 0.0), (0.70, 0.40, 0.50)),
    ("arm",   (-0.40, 0.05, 0.0), (0.15, 0.40, 0.15)),
    ("arm",   (0.40,  0.05, 0.0), (0.15, 0.40, 0.15)),
    ("leg",   (-0.20, -0.35, 0.0), (0.25, 0.30, 0.35)),
    ("leg",   (0.20,  -0.35, 0.0), (0.25, 0.30, 0.35)),
]


class Boss(Entity):
    def __init__(self, position=(0, 0), player=None, game=None):
        size = (BOSS_WIDTH, BOSS_HEIGHT, BOSS_DEPTH)
        super().__init__(
            position=(position[0], size[1] / 2, position[1]),
            model="cube",
            color=color.rgba(0, 0, 0, 0),
            scale=size,
            collider="box",
        )

        self.player = player
        self.game = game
        self.pushes_player = True

        self.max_health = BOSS_MAX_HEALTH
        self.health = BOSS_MAX_HEALTH
        self.melee_damage = BOSS_MELEE_DAMAGE
        self.melee_range = BOSS_MELEE_RANGE
        self.melee_cooldown_time = BOSS_MELEE_COOLDOWN
        self.melee_cooldown = 0.0

        self.fireball_damage = BOSS_FIREBALL_DAMAGE
        self.fireball_cooldown_time = BOSS_FIREBALL_COOLDOWN
        self.fireball_cooldown = BOSS_FIREBALL_COOLDOWN

        self.speed = BOSS_SPEED
        self.is_dead = False

        self.hit_flash_timer = 0.0
        self._walls = None

        self.half_health_triggered = False

        self.parts = []
        self._build_body()

    def _build_body(self):
        for name, pos, scale_ in BOSS_PARTS_LAYOUT:
            c = BOSS_PART_COLORS[name]
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

        if (not self.half_health_triggered and
                self.health <= self.max_health * 0.5):
            self.half_health_triggered = True
            if self.game:
                self.game.respawn_all_demons()

        dx = self.player.x - self.x
        dz = self.player.z - self.z
        d_flat = math.sqrt(dx * dx + dz * dz)

        self.melee_cooldown -= time.dt
        if d_flat < self.melee_range and self.melee_cooldown <= 0:
            self.player.take_damage(self.melee_damage)
            self.melee_cooldown = self.melee_cooldown_time

        self.fireball_cooldown -= time.dt
        if self.fireball_cooldown <= 0:
            self._fire_fireball()
            self.fireball_cooldown = self.fireball_cooldown_time

        self._look_flat_at(self.player.position)
        if d_flat > self.melee_range * 0.8:
            self._move_toward_player()

    def _look_flat_at(self, target):
        dx = target.x - self.x
        dz = target.z - self.z
        if abs(dx) + abs(dz) > 0.001:
            self.rotation_y = math.degrees(math.atan2(dx, dz))

    def _fire_fireball(self):
        if self.player is None:
            return
        origin = Vec3(self.x, self.y + 1.5, self.z)
        target = Vec3(self.player.x, self.player.y + 1.0, self.player.z)
        direction = target - origin
        if direction.length() < 0.01:
            return
        Fireball(
            position=origin,
            direction=direction.normalized(),
            damage=self.fireball_damage,
            player=self.player,
            game=self.game,
        )
        audio.play("shoot")

    def _ensure_walls(self):
        if self._walls is not None:
            return
        self._walls = [e for e in scene.entities
                       if getattr(e, "is_wall", False)]

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
        if self.player is None:
            return False
        hx = self.scale_x * 0.5
        hz = self.scale_z * 0.5

        b_min_x = new_pos.x - hx
        b_max_x = new_pos.x + hx
        b_min_z = new_pos.z - hz
        b_max_z = new_pos.z + hz

        p_hx = 0.4 * 0.5
        p_hz = 0.4 * 0.5
        p_min_x = self.player.x - p_hx
        p_max_x = self.player.x + p_hx
        p_min_z = self.player.z - p_hz
        p_max_z = self.player.z + p_hz

        return (b_min_x < p_max_x and b_max_x > p_min_x and
                b_min_z < p_max_z and b_max_z > p_min_z)

    def _try_move(self, new_pos):
        if not self._aabb_clear(new_pos):
            return False
        if self._overlaps_player(new_pos):
            return False
        self.position = new_pos
        return True

    def _move_toward_player(self):
        direction = self.player.position - self.position
        direction.y = 0
        if direction.length() < 0.01:
            return
        direction = direction.normalized()

        step = self.speed * time.dt

        if self._try_move(self.position + direction * step):
            return

        perp_a = Vec3(-direction.z, 0, direction.x)
        perp_b = Vec3(direction.z, 0, -direction.x)

        if self._try_move(self.position + perp_a * step):
            return
        self._try_move(self.position + perp_b * step)

    def take_damage(self, amount):
        if self.is_dead:
            return
        self.health -= amount
        self._flash(color.white)
        self.hit_flash_timer = 0.1

        if self.health <= 0:
            self.is_dead = True
            if self.player:
                self.player.score += 500
            if self.game:
                self.game.kill_all_enemies()
            audio.play("death")
            destroy(self)
        else:
            audio.play("hit")


class Fireball(Entity):
    SPEED = FIREBALL_SPEED
    LIFETIME = 5.0

    def __init__(self, position, direction, damage, player, game=None):
        super().__init__(
            model="cube",
            color=color.orange,
            position=position,
            scale=0.6,
        )
        self.direction = direction.normalized()
        self.damage = damage
        self.player = player
        self.game = game
        self.lifetime = self.LIFETIME
        self.dead = False

    def update(self):
        if self.dead:
            return

        self.lifetime -= time.dt
        if self.lifetime <= 0:
            self._destroy()
            return

        step = self.SPEED * time.dt
        self.position += self.direction * step

        dx = self.x - self.player.x
        dy = self.y - (self.player.y + 1.0)
        dz = self.z - self.player.z
        if dx * dx + dy * dy + dz * dz < 0.9 * 0.9:
            self.player.take_damage(self.damage)
            self._destroy()
            return

        fh = self.scale_x * 0.5
        for w in scene.entities:
            if not getattr(w, "is_wall", False):
                continue
            wx = w.scale_x * 0.5
            wy = w.scale_y * 0.5
            wz = w.scale_z * 0.5
            if (abs(self.x - w.x) < fh + wx and
                    abs(self.y - w.y) < fh + wy and
                    abs(self.z - w.z) < fh + wz):
                self._destroy()
                return

    def _destroy(self):
        if self.dead:
            return
        self.dead = True
        destroy(self)