# Um clone simples de Doom Classico feito em Python com Panda3D e Ursina
# A simple Classic Doom clone made in Python with Panda3D and Ursina

from ursina import *
from game import DoomGame
from menu import MainMenu, PauseMenu, GameOverMenu
from audio import audio

app = Ursina()

# ShowBase do Panda3D já existe -> podemos gerar/carregar os sons.
audio.init()

ADVANCEABLE = (
    "assets/maps/level1.txt",
    "assets/maps/level2.txt",
)

NEXT_LEVEL = {
    "assets/maps/level1.txt": "assets/maps/level2.txt",
    "assets/maps/level2.txt": "assets/maps/level3.txt",
}

state = {
    "menu": None,
    "pause": None,
    "gameover": None,
    "playing": False,
}


def show_game_over(victory):
    if state["gameover"] is not None:
        return
    on_advance = None
    if victory and game.level_file in ADVANCEABLE:
        on_advance = advance_level
    state["gameover"] = GameOverMenu(
        victory=victory,
        on_restart=restart_game,
        on_main_menu=return_to_menu,
        on_quit=application.quit,
        on_advance=on_advance,
    )
    application.paused = True
    mouse.locked = False
    mouse.visible = True


def advance_level():
    if state["gameover"] is None:
        return

    current = game.level_file
    destroy(state["gameover"])
    state["gameover"] = None

    next_level = NEXT_LEVEL.get(current)
    if next_level is None:
        return

    game.load_level(next_level, keep_score=True)
    application.paused = False
    mouse.locked = True
    mouse.visible = False
    state["playing"] = True


game = DoomGame(on_game_over=show_game_over)


def start_game():
    if state["menu"]:
        destroy(state["menu"])
        state["menu"] = None
    game.ui.set_visible(True)
    game.weapon.set_visible(True)
    application.paused = False
    mouse.locked = True
    mouse.visible = False
    state["playing"] = True


def pause_game():
    if state["pause"] is not None:
        return
    application.paused = True
    game.ui.set_visible(False)
    game.weapon.set_visible(False)
    state["pause"] = PauseMenu(
        on_resume=resume_game,
        on_main_menu=return_to_menu,
        on_quit=application.quit,
    )
    mouse.locked = False
    mouse.visible = True


def resume_game():
    if state["pause"]:
        destroy(state["pause"])
        state["pause"] = None
    game.ui.set_visible(True)
    game.weapon.set_visible(True)
    application.paused = False
    mouse.locked = True
    mouse.visible = False


def restart_game():
    if state["gameover"]:
        destroy(state["gameover"])
        state["gameover"] = None
    game.reset()
    game.ui.set_visible(True)
    game.weapon.set_visible(True)
    application.paused = False
    mouse.locked = True
    mouse.visible = False
    state["playing"] = True


def return_to_menu():
    if state["pause"]:
        destroy(state["pause"])
        state["pause"] = None
    if state["gameover"]:
        destroy(state["gameover"])
        state["gameover"] = None

    game.reset()
    game.ui.set_visible(False)
    game.weapon.set_visible(False)

    state["menu"] = MainMenu(on_start=start_game, on_quit=application.quit)
    application.paused = True
    mouse.locked = False
    mouse.visible = True
    state["playing"] = False


def input(key):
    if key == "escape":
        if state["menu"] is not None:
            return
        if state["gameover"] is not None:
            return
        if not state["playing"]:
            return
        if state["pause"] is None:
            pause_game()
        else:
            resume_game()


game.ui.set_visible(False)
game.weapon.set_visible(False)
state["menu"] = MainMenu(on_start=start_game, on_quit=application.quit)
application.paused = True

app.run()