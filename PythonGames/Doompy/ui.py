from ursina import *
import menu


class UI(Entity):
    def __init__(self, player):
        super().__init__(parent=camera.ui)
        self.player = player

        self.health_text = Text(text="", position=(-0.85, 0.47),
                                scale=1.5, color=color.red)
        self.ammo_text = Text(text="", position=(-0.85, 0.42),
                              scale=1.5, color=color.white)
        self.score_text = Text(text="", position=(0.55, 0.47),
                               scale=1.5, color=color.yellow)

        self.crosshair = Entity(parent=camera.ui)
        self.crosshair_h = Entity(parent=self.crosshair, model="quad",
                                   color=color.white, scale=(0.028, 0.006))
        self.crosshair_v = Entity(parent=self.crosshair, model="quad",
                                    color=color.white, scale=(0.006, 0.028))
        self._crosshair_color = color.white

        self.game_over_text = Text(text="", origin=(0, 0), y=0.2,
                                   scale=3, color=color.red, enabled=False)

    def set_visible(self, visible):
        self.health_text.enabled = visible
        self.ammo_text.enabled = visible
        self.score_text.enabled = visible
        self.crosshair.enabled = visible

    def hide_game_over(self):
        self.game_over_text.text = ""
        self.game_over_text.enabled = False

    def _set_crosshair_color(self, c):
        if c == self._crosshair_color:
            return
        self._crosshair_color = c
        self.crosshair_h.color = c
        self.crosshair_v.color = c

    def update(self):
        self.health_text.text = f"{menu.t('health_label')}: {int(self.player.health)}"
        self.ammo_text.text = f"{menu.t('ammo_label')}: {self.player.ammo}"
        self.score_text.text = f"{menu.t('score_label')}: {self.player.score}"

        hit = raycast(camera.world_position, camera.forward,
                      distance=50, ignore=[self.player])
        if hit.hit and hasattr(hit.entity, "take_damage"):
            self._set_crosshair_color(color.red)
        else:
            self._set_crosshair_color(color.white)

    def show_game_over(self, text="GAME OVER", color_=color.red):
        self.game_over_text.text = text
        self.game_over_text.color = color_
        self.game_over_text.enabled = True