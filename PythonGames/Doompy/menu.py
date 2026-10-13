from ursina import *


LANGUAGE = "pt"


TRANSLATIONS = {
    "pt": {
        "subtitle": "Um clone de Doom em Python",
        "play": "JOGAR",
        "how_to_play": "COMO JOGAR",
        "quit": "SAIR",
        "back": "VOLTAR",
        "paused": "PAUSADO",
        "continue": "CONTINUAR",
        "main_menu": "MENU PRINCIPAL",
        "victory": "VITORIA!",
        "game_over": "GAME OVER",
        "restart": "RECOMECAR",
        "advance": "AVANCAR",
        "health_label": "VIDA",
        "ammo_label": "MUNICAO",
        "score_label": "SCORE",
        "instructions": (
            "CONTROLES\n"
            "  Mover...........WASD\n"
            "  Olhar...........Mouse\n"
            "  Atirar..........Clique esquerdo\n"
            "  Trocar de arma..1 / 2 / 3\n"
            "  Pausar..........ESC\n"
            "\n"
            "INIMIGOS\n"
            "  Imp.............rapido, 20 HP\n"
            "  Demon...........lento, 50 HP\n"
            "\n"
            "ARMAS\n"
            "  Pistol..........10 dano, semi-auto\n"
            "  Shotgun.........12 dano x6 pellets\n"
            "  Chaingun........6 dano, automatica\n"
            "\n"
            "ITENS\n"
            "  Verde..............+25 vida\n"
            "  Ciano..............+30 municao"
        ),
    },
    "en": {
        "subtitle": "A Doom clone in Python",
        "play": "PLAY",
        "how_to_play": "HOW TO PLAY",
        "quit": "QUIT",
        "back": "BACK",
        "paused": "PAUSED",
        "continue": "CONTINUE",
        "main_menu": "MAIN MENU",
        "victory": "VICTORY!",
        "game_over": "GAME OVER",
        "restart": "RESTART",
        "advance": "ADVANCE",
        "health_label": "HEALTH",
        "ammo_label": "AMMO",
        "score_label": "SCORE",
        "instructions": (
            "CONTROLS\n"
            "  Move............WASD\n"
            "  Look............Mouse\n"
            "  Shoot...........Left click\n"
            "  Switch weapon...1 / 2 / 3\n"
            "  Pause...........ESC\n"
            "\n"
            "ENEMIES\n"
            "  Imp.............fast, 20 HP\n"
            "  Demon...........slow, 50 HP\n"
            "\n"
            "WEAPONS\n"
            "  Pistol..........10 damage, semi-auto\n"
            "  Shotgun.........12 damage x6 pellets\n"
            "  Chaingun........6 damage, automatic\n"
            "\n"
            "ITEMS\n"
            "  Green..............+25 health\n"
            "  Cyan...............+30 ammo"
        ),
    },
}


def t(key):
    return TRANSLATIONS[LANGUAGE][key]


class InstructionsPanel(Entity):
    def __init__(self, on_back):
        super().__init__(parent=camera.ui)
        self.on_back = on_back

        Entity(parent=self, model="quad",
               color=color.rgba(0, 0, 0, 255),
               scale=(2.5, 1.5), z=1)

        Text(parent=self, text=t("how_to_play"), origin=(0, 0), y=0.44,
             scale=4, color=color.red)

        Text(parent=self, text=t("instructions"), origin=(0, 0.5), y=0.30,
             scale=1.2, color=color.white)

        Button(parent=self, text=t("back"), y=-0.44, scale=(0.35, 0.08),
               color=color.dark_gray, highlight_color=color.red,
               on_click=self._back)

    def _back(self):
        self.on_back()
        destroy(self)


class MainMenu(Entity):
    def __init__(self, on_start, on_quit):
        super().__init__(parent=camera.ui)
        self.on_start = on_start
        self.on_quit = on_quit

        Entity(parent=self, model="quad",
               color=color.rgba(0, 0, 0, 255),
               scale=(2.5, 1.5), z=1)

        Text(parent=self, text="DOOMPY", origin=(0, 0), y=0.28,
             scale=10, color=color.red)
        self.subtitle = Text(parent=self, text="", origin=(0, 0), y=0.16,
                             scale=1.5, color=color.gray)

        self.btn_play = Button(parent=self, text="", y=0.02, scale=(0.4, 0.1),
                               color=color.dark_gray, highlight_color=color.red,
                               on_click=self.on_start)
        self.btn_how = Button(parent=self, text="", y=-0.11, scale=(0.4, 0.1),
                              color=color.dark_gray, highlight_color=color.red,
                              on_click=self._show_instructions)
        self.btn_quit = Button(parent=self, text="", y=-0.24, scale=(0.4, 0.1),
                               color=color.dark_gray, highlight_color=color.red,
                               on_click=self.on_quit)

        self.btn_lang = Button(parent=self, text="", position=(0.65, -0.42),
                               scale=(0.15, 0.07),
                               color=color.dark_gray, highlight_color=color.yellow,
                               on_click=self._toggle_language)

        self._apply_language()

        mouse.locked = False
        mouse.visible = True

    def _apply_language(self):
        self.subtitle.text = t("subtitle")
        self.btn_play.text = t("play")
        self.btn_how.text = t("how_to_play")
        self.btn_quit.text = t("quit")
        self.btn_lang.text = "ENG" if LANGUAGE == "pt" else "PT"

    def _toggle_language(self):
        global LANGUAGE
        LANGUAGE = "en" if LANGUAGE == "pt" else "pt"
        self._apply_language()

    def _show_instructions(self):
        self.enabled = False
        InstructionsPanel(on_back=self._hide_instructions)

    def _hide_instructions(self):
        self.enabled = True


class PauseMenu(Entity):
    def __init__(self, on_resume, on_main_menu, on_quit):
        super().__init__(parent=camera.ui)
        self.on_resume = on_resume
        self.on_main_menu = on_main_menu
        self.on_quit = on_quit

        Entity(parent=self, model="quad",
               color=color.rgba(0, 0, 0, 255),
               scale=(2.5, 1.5), z=1)

        Text(parent=self, text=t("paused"), origin=(0, 0), y=0.28,
             scale=6, color=color.white)

        Button(parent=self, text=t("continue"), y=0.08, scale=(0.4, 0.1),
               color=color.dark_gray, highlight_color=color.green,
               on_click=self.on_resume)
        Button(parent=self, text=t("main_menu"), y=-0.05, scale=(0.4, 0.1),
               color=color.dark_gray, highlight_color=color.orange,
               on_click=self.on_main_menu)
        Button(parent=self, text=t("quit"), y=-0.18, scale=(0.4, 0.1),
               color=color.dark_gray, highlight_color=color.red,
               on_click=self.on_quit)

        mouse.locked = False
        mouse.visible = True


class GameOverMenu(Entity):
    def __init__(self, victory, on_restart, on_main_menu, on_quit, on_advance=None):
        super().__init__(parent=camera.ui)

        Entity(parent=self, model="quad",
               color=color.rgba(0, 0, 0, 255),
               scale=(2.5, 1.5), z=1)

        title = t("victory") if victory else t("game_over")
        title_color = color.green if victory else color.red

        Text(parent=self, text=title, origin=(0, 0), y=0.42,
             scale=7, color=title_color)

        if on_advance is not None:
            Button(parent=self, text=t("advance"), y=0.15, scale=(0.4, 0.1),
                   color=color.dark_gray, highlight_color=color.green,
                   on_click=on_advance)

        Button(parent=self, text=t("restart"), y=0.03, scale=(0.4, 0.1),
               color=color.dark_gray, highlight_color=color.green,
               on_click=on_restart)
        Button(parent=self, text=t("main_menu"), y=-0.09, scale=(0.4, 0.1),
               color=color.dark_gray, highlight_color=color.orange,
               on_click=on_main_menu)
        Button(parent=self, text=t("quit"), y=-0.21, scale=(0.4, 0.1),
               color=color.dark_gray, highlight_color=color.red,
               on_click=on_quit)

        mouse.locked = False
        mouse.visible = True