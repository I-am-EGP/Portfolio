import asyncio
import platform
import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroides")

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)
GREY   = (180, 180, 180)
DARK   = (30,  30,  30)
YELLOW = (255, 220, 50)

lang = "PT"  # "PT" | "EN"

STRINGS = {
    "PT": {
        "title":          "ASTEROIDES",
        "play":           "Jogar",
        "tutorial":       "Tutorial",
        "close":          "Fechar",
        "back":           "← Voltar",
        "main_menu":      "Menu Principal",
        "restart":        "Recomeçar",
        "score":          "Pontuação: {}",
        "you_died":       "VOCÊ MORREU",
        "final_score":    "Pontuação final: {}",
        "tut_title":      "TUTORIAL",
        "tut_controls":   "CONTROLES",
        "tut_score":      "PONTUAÇÃO",
        "tut_survival":   "SOBREVIVÊNCIA",
        "tut_lines": [
            [
                "Girar à esquerda   →   Seta Esquerda  /  A",
                "Girar à direita    →   Seta Direita   /  D",
                "Acelerar           →   Seta Cima      /  W",
                "Frear / recuar     →   S",
                "Atirar             →   Espaço  (máx. 5 balas)",
            ],
            [
                "Destruir um asteroide  →  +10 pontos",
                "Asteroides grandes se quebram em 2 menores",
                "Não há limite de pontuação",
            ],
            [
                "Evite colisões com asteroides — game over imediato",
                "A nave e os asteroides atravessam as bordas da tela",
                "Novos asteroides surgem continuamente",
            ],
        ],
    },
    "EN": {
        "title":          "ASTEROIDS",
        "play":           "Play",
        "tutorial":       "Tutorial",
        "close":          "Close",
        "back":           "← Back",
        "main_menu":      "Main Menu",
        "restart":        "Play Again",
        "score":          "Score: {}",
        "you_died":       "YOU DIED",
        "final_score":    "Final score: {}",
        "tut_title":      "TUTORIAL",
        "tut_controls":   "CONTROLS",
        "tut_score":      "SCORING",
        "tut_survival":   "SURVIVAL",
        "tut_lines": [
            [
                "Rotate left    →   Left Arrow  /  A",
                "Rotate right   →   Right Arrow /  D",
                "Thrust         →   Up Arrow    /  W",
                "Brake / reverse →  S",
                "Fire           →   Space  (max. 5 bullets)",
            ],
            [
                "Destroy an asteroid  →  +10 points",
                "Large asteroids split into 2 smaller ones",
                "There is no points limit",
            ],
            [
                "Avoid collisions with asteroids — instant game over",
                "The ship and asteroids wrap around screen edges",
                "New asteroids spawn continuously",
            ],
        ],
    },
}

def t(key):
    return STRINGS[lang][key]


game_state = "menu"

player_pos = [WIDTH // 2, HEIGHT // 2]
player_angle = 0
player_speed = 0
player_max_speed = 5
player_acceleration = 0.1
player_rotation_speed = 5
player_size = 20

bullets = []
bullet_speed = 7
bullet_lifetime = 60

asteroids = []
asteroid_sizes  = [30, 20, 10]
asteroid_speeds = [2,  3,  4]
asteroid_spawn_rate  = 60
asteroid_spawn_timer = 0

score = 0
FPS   = 60
clock = pygame.time.Clock()



def draw_button(text, rect, mouse_pos, font,
                color_normal=(60, 60, 60),
                color_hover=(100, 100, 100),
                border=WHITE):
    hovered = rect.collidepoint(mouse_pos)
    colour  = color_hover if hovered else color_normal
    pygame.draw.rect(screen, colour, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=8)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))
    return hovered


def draw_lang_buttons(mouse_pos, font):
    """Desenha os botões PT / EN no canto inferior direito.
    Devolve (rect_pt, rect_en) para detecção de clique."""
    bw, bh = 42, 30
    margin  = 10
    rect_en = pygame.Rect(WIDTH - margin - bw,           HEIGHT - margin - bh, bw, bh)
    rect_pt = pygame.Rect(WIDTH - margin - bw * 2 - 6,   HEIGHT - margin - bh, bw, bh)

    for code, rect in (("PT", rect_pt), ("EN", rect_en)):
        selected = (lang == code)
        bg  = (60, 60, 120) if selected else (40, 40, 40)
        bdr = YELLOW if selected else GREY
        pygame.draw.rect(screen, bg,  rect, border_radius=5)
        pygame.draw.rect(screen, bdr, rect, 2, border_radius=5)
        lbl = font.render(code, True, YELLOW if selected else GREY)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    return rect_pt, rect_en


def handle_lang_click(mouse_pos, rect_pt, rect_en):
    global lang
    if rect_pt.collidepoint(mouse_pos):
        lang = "PT"
    elif rect_en.collidepoint(mouse_pos):
        lang = "EN"



async def menu_loop():
    global game_state

    font_title  = pygame.font.SysFont(None, 90)
    font_button = pygame.font.SysFont(None, 46)
    font_lang   = pygame.font.SysFont(None, 28)

    btn_w, btn_h = 260, 55
    btn_x = WIDTH // 2 - btn_w // 2
    btn_play     = pygame.Rect(btn_x, 240, btn_w, btn_h)
    btn_tutorial = pygame.Rect(btn_x, 320, btn_w, btn_h)
    btn_quit     = pygame.Rect(btn_x, 400, btn_w, btn_h)

    deco = [{"pos": [random.randint(0, WIDTH), random.randint(0, HEIGHT)],
             "vel": [random.uniform(-1, 1), random.uniform(-1, 1)],
             "size": random.choice(asteroid_sizes)} for _ in range(8)]

    _rpt = _ren = pygame.Rect(0, 0, 1, 1)

    while game_state == "menu":
        mouse = pygame.mouse.get_pos()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_lang_click(mouse, _rpt, _ren)
                if btn_play.collidepoint(mouse):
                    game_state = "game"
                elif btn_tutorial.collidepoint(mouse):
                    game_state = "tutorial"
                elif btn_quit.collidepoint(mouse):
                    pygame.quit()
                    return

        for a in deco:
            a["pos"][0] = (a["pos"][0] + a["vel"][0]) % WIDTH
            a["pos"][1] = (a["pos"][1] + a["vel"][1]) % HEIGHT

        screen.fill(BLACK)
        for a in deco:
            pygame.draw.circle(screen, DARK,
                               (int(a["pos"][0]), int(a["pos"][1])), a["size"], 1)

        title = font_title.render(t("title"), True, YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 140)))

        draw_button(t("play"),     btn_play,     mouse, font_button)
        draw_button(t("tutorial"), btn_tutorial, mouse, font_button)
        draw_button(t("close"),    btn_quit,     mouse, font_button,
                    color_normal=(90, 30, 30), color_hover=(130, 50, 50))

        _rpt, _ren = draw_lang_buttons(mouse, font_lang)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)



async def tutorial_loop():
    global game_state

    font_title  = pygame.font.SysFont(None, 60)
    font_text   = pygame.font.SysFont(None, 32)
    font_small  = pygame.font.SysFont(None, 28)
    font_button = pygame.font.SysFont(None, 40)
    font_lang   = pygame.font.SysFont(None, 28)

    btn_back = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 70, 200, 45)

    _rpt = _ren = pygame.Rect(0, 0, 1, 1)

    while game_state == "tutorial":
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_lang_click(mouse, _rpt, _ren)
                if btn_back.collidepoint(mouse):
                    game_state = "menu"

        section_headings = [t("tut_controls"), t("tut_score"), t("tut_survival")]
        lines_data       = t("tut_lines")

        screen.fill(BLACK)

        title = font_title.render(t("tut_title"), True, YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 45)))
        pygame.draw.line(screen, GREY, (60, 75), (WIDTH - 60, 75), 1)

        y = 100
        for heading, lines in zip(section_headings, lines_data):
            h = font_text.render(heading, True, WHITE)
            screen.blit(h, (80, y))
            y += 34
            for line in lines:
                l = font_small.render(line, True, GREY)
                screen.blit(l, (100, y))
                y += 26
            y += 14

        draw_button(t("back"), btn_back, mouse, font_button,
                    color_normal=(40, 40, 80), color_hover=(70, 70, 130))

        _rpt, _ren = draw_lang_buttons(mouse, font_lang)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)



def setup():
    global asteroids, bullets, player_pos, player_angle, player_speed, score, asteroid_spawn_timer
    asteroids = []
    bullets   = []
    player_pos   = [WIDTH // 2, HEIGHT // 2]
    player_angle = 0
    player_speed = 0
    score        = 0
    asteroid_spawn_timer = 0
    spawn_asteroid()

def draw_triangle(pos, angle, size, color):
    x, y = pos
    rad    = math.radians(angle)
    point1 = (x + math.cos(rad)       * size, y - math.sin(rad)       * size)
    point2 = (x + math.cos(rad + 2.5) * size, y - math.sin(rad + 2.5) * size)
    point3 = (x + math.cos(rad - 2.5) * size, y - math.sin(rad - 2.5) * size)
    pygame.draw.polygon(screen, color, [point1, point2, point3])

def spawn_asteroid():
    size = random.choice(asteroid_sizes)
    edge = random.randint(0, 3)
    spd  = asteroid_speeds[asteroid_sizes.index(size)]
    if edge == 0:
        pos = [random.randint(0, WIDTH), 0]
        vel = [random.uniform(-2, 2), random.uniform(1, spd)]
    elif edge == 1:
        pos = [WIDTH, random.randint(0, HEIGHT)]
        vel = [random.uniform(-spd, -1), random.uniform(-2, 2)]
    elif edge == 2:
        pos = [random.randint(0, WIDTH), HEIGHT]
        vel = [random.uniform(-2, 2), random.uniform(-spd, -1)]
    else:
        pos = [0, random.randint(0, HEIGHT)]
        vel = [random.uniform(1, spd), random.uniform(-2, 2)]
    asteroids.append({"pos": pos, "vel": vel, "size": size})

def check_collision(pos1, size1, pos2, size2):
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return math.sqrt(dx**2 + dy**2) < (size1 + size2)

async def update_loop():
    global player_pos, player_angle, player_speed, bullets, asteroids
    global score, asteroid_spawn_timer, game_state

    font_lang = pygame.font.SysFont(None, 28)
    _rpt = _ren = pygame.Rect(0, 0, 1, 1)

    running = True
    while running and game_state == "game":
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_lang_click(mouse, _rpt, _ren)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_angle += player_rotation_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_angle -= player_rotation_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_speed = min(player_speed + player_acceleration, player_max_speed)
        if keys[pygame.K_s]:
            player_speed = max(player_speed - player_acceleration, -player_max_speed)
        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                rad        = math.radians(player_angle)
                bullet_pos = [player_pos[0] + math.cos(rad) * player_size,
                              player_pos[1] - math.sin(rad) * player_size]
                bullet_vel = [math.cos(rad) * bullet_speed, -math.sin(rad) * bullet_speed]
                bullets.append({"pos": bullet_pos, "vel": bullet_vel, "lifetime": bullet_lifetime})

        rad = math.radians(player_angle)
        player_pos[0] += math.cos(rad) * player_speed
        player_pos[1] -= math.sin(rad) * player_speed
        player_speed   *= 0.99
        player_pos[0]   = player_pos[0] % WIDTH
        player_pos[1]   = player_pos[1] % HEIGHT

        bullets = [{"pos": [b["pos"][0] + b["vel"][0], b["pos"][1] + b["vel"][1]],
                    "vel": b["vel"], "lifetime": b["lifetime"] - 1} for b in bullets]
        bullets = [b for b in bullets if b["lifetime"] > 0
                   and 0 <= b["pos"][0] <= WIDTH and 0 <= b["pos"][1] <= HEIGHT]

        for asteroid in asteroids:
            asteroid["pos"][0] = (asteroid["pos"][0] + asteroid["vel"][0]) % WIDTH
            asteroid["pos"][1] = (asteroid["pos"][1] + asteroid["vel"][1]) % HEIGHT

        asteroid_spawn_timer += 1
        if asteroid_spawn_timer >= asteroid_spawn_rate:
            spawn_asteroid()
            asteroid_spawn_timer = 0

        new_asteroids = []
        for asteroid in asteroids[:]:
            if check_collision(player_pos, player_size, asteroid["pos"], asteroid["size"]):
                running = False
                break
            for bullet in bullets[:]:
                if check_collision(bullet["pos"], 2, asteroid["pos"], asteroid["size"]):
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    score += 10
                    if asteroid["size"] > asteroid_sizes[-1]:
                        new_size = asteroid_sizes[asteroid_sizes.index(asteroid["size"]) + 1]
                        spd      = asteroid_speeds[asteroid_sizes.index(new_size)]
                        for _ in range(2):
                            new_asteroids.append({
                                "pos": asteroid["pos"].copy(),
                                "vel": [random.uniform(-spd, spd), random.uniform(-spd, spd)],
                                "size": new_size
                            })
                    break
        asteroids.extend(new_asteroids)

        screen.fill(BLACK)
        draw_triangle(player_pos, player_angle, player_size, WHITE)
        for bullet in bullets:
            pygame.draw.circle(screen, WHITE,
                               (int(bullet["pos"][0]), int(bullet["pos"][1])), 2)
        for asteroid in asteroids:
            pygame.draw.circle(screen, WHITE,
                               (int(asteroid["pos"][0]), int(asteroid["pos"][1])),
                               asteroid["size"], 1)
        font_hud = pygame.font.SysFont(None, 36)
        screen.blit(font_hud.render(t("score").format(score), True, WHITE), (10, 10))

        _rpt, _ren = draw_lang_buttons(mouse, font_lang)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    game_state = "gameover"



async def gameover_loop():
    global game_state

    font_title  = pygame.font.SysFont(None, 90)
    font_score  = pygame.font.SysFont(None, 42)
    font_button = pygame.font.SysFont(None, 46)
    font_lang   = pygame.font.SysFont(None, 28)

    btn_w, btn_h = 280, 55
    btn_x = WIDTH // 2 - btn_w // 2
    btn_restart = pygame.Rect(btn_x, 310, btn_w, btn_h)
    btn_menu    = pygame.Rect(btn_x, 385, btn_w, btn_h)
    btn_quit    = pygame.Rect(btn_x, 460, btn_w, btn_h)

    final_score = score
    _rpt = _ren = pygame.Rect(0, 0, 1, 1)

    while game_state == "gameover":
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_lang_click(mouse, _rpt, _ren)
                if btn_restart.collidepoint(mouse):
                    game_state = "game"
                elif btn_menu.collidepoint(mouse):
                    game_state = "menu"
                elif btn_quit.collidepoint(mouse):
                    pygame.quit()
                    return

        screen.fill(BLACK)

        title = font_title.render(t("you_died"), True, RED)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 180)))

        score_text = font_score.render(t("final_score").format(final_score), True, GREY)
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 255)))

        draw_button(t("restart"),   btn_restart, mouse, font_button,
                    color_normal=(40, 80, 40), color_hover=(60, 120, 60))
        draw_button(t("main_menu"), btn_menu,    mouse, font_button)
        draw_button(t("close"),     btn_quit,    mouse, font_button,
                    color_normal=(90, 30, 30), color_hover=(130, 50, 50))

        _rpt, _ren = draw_lang_buttons(mouse, font_lang)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)



async def main():
    global game_state
    while True:
        if game_state == "menu":
            await menu_loop()
        elif game_state == "tutorial":
            await tutorial_loop()
        elif game_state == "game":
            setup()
            await update_loop()
        elif game_state == "gameover":
            await gameover_loop()
        else:
            break


if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())