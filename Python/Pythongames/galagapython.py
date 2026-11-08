# Clone simples de Galaga feito em Python como projeto paralelo

# Simple Galaga clone made in Python as a side project

import pygame
import random
import asyncio
import platform

pygame.init()

LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Galaga Python")

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARELO = (255, 220, 0)
CINZA = (180, 180, 180)
CINZA_ESCURO = (60, 60, 60)
AZUL = (80, 140, 255)
LARANJA = (255, 160, 0)

FPS = 60
VELOCIDADE_JOGADOR = 5
VELOCIDADE_INIMIGO = 2
VELOCIDADE_TIRO = 7

ESTADO_MENU = "menu"
ESTADO_JOGO = "jogo"
ESTADO_TUTORIAL = "tutorial"
ESTADO_PAUSA = "pausa"

estado_atual = ESTADO_MENU
idioma = "PT"  

fonte_titulo = pygame.font.SysFont('arial', 52, bold=True)
fonte_botao  = pygame.font.SysFont('arial', 28)
fonte_texto  = pygame.font.SysFont('arial', 20)
fonte_pontuacao = pygame.font.SysFont('arial', 24)
fonte_lang   = pygame.font.SysFont('arial', 18, bold=True)

TEXTOS = {
    "PT": {
        "titulo":        "Galaga Python",
        "subtitulo":     "— Destrua os inimigos e sobreviva! —",
        "jogar":         "Jogar",
        "tutorial":      "Tutorial",
        "fechar":        "Fechar",
        "voltar":        "← Voltar",
        "tut_titulo":    "Tutorial",
        "sec_controlos": "CONTROLOS",
        "ctrl_mover":    "← → ou A / D   Mover a nave para a esquerda/direita",
        "ctrl_atirar":   "Espaço          Disparar (máximo 3 tiros simultâneos)",
        "ctrl_reiniciar":"R               Reiniciar após vencer",
        "ctrl_pausa":    "ESC             Pausar / retomar o jogo",
        "sec_pontuacao": "PONTUAÇÃO",
        "pont_1":        "Cada inimigo destruído vale  +10 pontos",
        "pont_2":        "Destrua todos os 30 inimigos para vencer",
        "sec_sobrev":    "SOBREVIVÊNCIA",
        "sobrev_1":      "Evite que os inimigos toquem na sua nave",
        "sobrev_2":      "Se um inimigo colidir consigo, o jogo reinicia",
        "sobrev_3":      "Os inimigos descem cada vez que atingem a borda",
        "pontuacao":     "Pontuação",
        "vitoria":       "Você venceu! Pressione R para reiniciar.",
        "pausa_titulo":  "PAUSADO",
        "continuar":     "Continuar",
        "reiniciar":     "Reiniciar",
        "menu_principal":"Menu Principal",
    },
    "EN": {
        "titulo":        "Galaga Python",
        "subtitulo":     "— Destroy the enemies and survive! —",
        "jogar":         "Play",
        "tutorial":      "Tutorial",
        "fechar":        "Quit",
        "voltar":        "← Back",
        "tut_titulo":    "Tutorial",
        "sec_controlos": "CONTROLS",
        "ctrl_mover":    "← → or A / D   Move the ship left/right",
        "ctrl_atirar":   "Space           Shoot (max 3 simultaneous shots)",
        "ctrl_reiniciar":"R               Restart after winning",
        "ctrl_pausa":    "ESC             Pause / resume the game",
        "sec_pontuacao": "SCORING",
        "pont_1":        "Each enemy destroyed is worth  +10 points",
        "pont_2":        "Destroy all 30 enemies to win",
        "sec_sobrev":    "SURVIVAL",
        "sobrev_1":      "Prevent enemies from touching your ship",
        "sobrev_2":      "If an enemy collides with you, the game resets",
        "sobrev_3":      "Enemies move down each time they hit a wall",
        "pontuacao":     "Score",
        "vitoria":       "You won! Press R to restart.",
        "pausa_titulo":  "PAUSED",
        "continuar":     "Continue",
        "reiniciar":     "Restart",
        "menu_principal":"Main Menu",
    },
}

def t(chave):
    return TEXTOS[idioma][chave]


class Botao:
    def __init__(self, x, y, largura, altura, texto, cor=CINZA_ESCURO, cor_hover=AZUL):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor = cor
        self.cor_hover = cor_hover

    def desenhar(self, superficie):
        mouse = pygame.mouse.get_pos()
        cor_atual = self.cor_hover if self.rect.collidepoint(mouse) else self.cor
        pygame.draw.rect(superficie, cor_atual, self.rect, border_radius=10)
        pygame.draw.rect(superficie, BRANCO, self.rect, 2, border_radius=10)
        texto_surf = fonte_botao.render(self.texto, True, BRANCO)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        superficie.blit(texto_surf, texto_rect)

    def clicado(self, pos):
        return self.rect.collidepoint(pos)


class BotaoLang:
    """Botão pequeno de idioma com destaque no activo."""
    def __init__(self, x, y, codigo):
        self.rect = pygame.Rect(x, y, 46, 28)
        self.codigo = codigo

    def desenhar(self, superficie):
        ativo = (self.codigo == idioma)
        cor_fundo = LARANJA if ativo else CINZA_ESCURO
        mouse = pygame.mouse.get_pos()
        if not ativo and self.rect.collidepoint(mouse):
            cor_fundo = AZUL
        pygame.draw.rect(superficie, cor_fundo, self.rect, border_radius=6)
        pygame.draw.rect(superficie, BRANCO, self.rect, 1, border_radius=6)
        surf = fonte_lang.render(self.codigo, True, BRANCO)
        superficie.blit(surf, surf.get_rect(center=self.rect.center))

    def clicado(self, pos):
        return self.rect.collidepoint(pos)


class Jogador:
    def __init__(self):
        self.largura = 40
        self.altura = 40
        self.x = LARGURA // 2 - self.largura // 2
        self.y = ALTURA - 60
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)

    def mover(self, direcao):
        self.x += direcao * VELOCIDADE_JOGADOR
        if self.x < 0:
            self.x = 0
        elif self.x > LARGURA - self.largura:
            self.x = LARGURA - self.largura
        self.rect.topleft = (self.x, self.y)

    def desenhar(self):
        pygame.draw.rect(tela, VERDE, self.rect)

class Inimigo:
    def __init__(self, x, y):
        self.largura = 30
        self.altura = 30
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)
        self.direcao = 1

    def mover(self):
        self.x += VELOCIDADE_INIMIGO * self.direcao
        self.rect.topleft = (self.x, self.y)

    def desenhar(self):
        pygame.draw.rect(tela, VERMELHO, self.rect)

class Tiro:
    def __init__(self, x, y):
        self.largura = 5
        self.altura = 10
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)

    def mover(self):
        self.y -= VELOCIDADE_TIRO
        self.rect.topleft = (self.x, self.y)

    def desenhar(self):
        pygame.draw.rect(tela, BRANCO, self.rect)


jogador = None
inimigos = []
tiros = []
pontuacao = 0

def setup():
    global jogador, inimigos, tiros, pontuacao
    jogador = Jogador()
    inimigos = [Inimigo(x * 60 + 50, y * 60 + 50) for y in range(3) for x in range(10)]
    tiros = []
    pontuacao = 0


BT_JOGAR    = Botao(LARGURA // 2 - 120, 230, 240, 55, "")
BT_TUTORIAL = Botao(LARGURA // 2 - 120, 310, 240, 55, "")
BT_FECHAR   = Botao(LARGURA // 2 - 120, 390, 240, 55, "", cor_hover=VERMELHO)
BT_VOLTAR   = Botao(LARGURA // 2 - 100, ALTURA - 70, 200, 50, "")

BT_PT = BotaoLang(LARGURA - 108, ALTURA - 38, "PT")
BT_EN = BotaoLang(LARGURA - 58,  ALTURA - 38, "EN")

BT_CONTINUAR     = Botao(LARGURA // 2 - 130, 230, 260, 55, "")
BT_REINICIAR     = Botao(LARGURA // 2 - 130, 305, 260, 55, "")
BT_MENU_PRINCIPAL = Botao(LARGURA // 2 - 130, 380, 260, 55, "", cor_hover=VERMELHO)


def desenhar_botoes_idioma():
    BT_PT.desenhar(tela)
    BT_EN.desenhar(tela)


def desenhar_menu():
    tela.fill(PRETO)

    titulo = fonte_titulo.render(t("titulo"), True, AMARELO)
    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 140)))

    sub = fonte_texto.render(t("subtitulo"), True, CINZA)
    tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 195)))

    BT_JOGAR.texto    = t("jogar")
    BT_TUTORIAL.texto = t("tutorial")
    BT_FECHAR.texto   = t("fechar")

    BT_JOGAR.desenhar(tela)
    BT_TUTORIAL.desenhar(tela)
    BT_FECHAR.desenhar(tela)

    desenhar_botoes_idioma()


def desenhar_tutorial():
    tela.fill(PRETO)

    titulo = fonte_titulo.render(t("tut_titulo"), True, AMARELO)
    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 55)))

    secoes = [
        (t("sec_controlos"), AZUL),
        (t("ctrl_mover"),    BRANCO),
        (t("ctrl_atirar"),   BRANCO),
        (t("ctrl_reiniciar"),BRANCO),
        (t("ctrl_pausa"),    BRANCO),
        (t("sec_pontuacao"), AZUL),
        (t("pont_1"),        BRANCO),
        (t("pont_2"),        BRANCO),
        (t("sec_sobrev"),    AZUL),
        (t("sobrev_1"),      BRANCO),
        (t("sobrev_2"),      BRANCO),
        (t("sobrev_3"),      BRANCO),
    ]

    y = 125
    for texto, cor in secoes:
        if cor == AZUL:
            surf = fonte_botao.render(texto, True, cor)
            y += 8
        else:
            surf = fonte_texto.render(f"  {texto}", True, cor)
        tela.blit(surf, (60, y))
        y += surf.get_height() + 6

    BT_VOLTAR.texto = t("voltar")
    BT_VOLTAR.desenhar(tela)
    desenhar_botoes_idioma()


def desenhar_pausa():
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    tela.blit(overlay, (0, 0))

    painel = pygame.Rect(LARGURA // 2 - 160, 160, 320, 300)
    pygame.draw.rect(tela, CINZA_ESCURO, painel, border_radius=14)
    pygame.draw.rect(tela, AMARELO, painel, 2, border_radius=14)

    titulo = fonte_titulo.render(t("pausa_titulo"), True, AMARELO)
    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 195)))

    BT_CONTINUAR.texto      = t("continuar")
    BT_REINICIAR.texto      = t("reiniciar")
    BT_MENU_PRINCIPAL.texto = t("menu_principal")

    BT_CONTINUAR.desenhar(tela)
    BT_REINICIAR.desenhar(tela)
    BT_MENU_PRINCIPAL.desenhar(tela)

    desenhar_botoes_idioma()


def update_loop():
    global pontuacao, estado_atual, idioma

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and estado_atual == ESTADO_JOGO:
                estado_atual = ESTADO_PAUSA
            elif event.key == pygame.K_ESCAPE and estado_atual == ESTADO_PAUSA:
                estado_atual = ESTADO_JOGO

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if BT_PT.clicado(pos):
                idioma = "PT"
            elif BT_EN.clicado(pos):
                idioma = "EN"

            elif estado_atual == ESTADO_MENU:
                if BT_JOGAR.clicado(pos):
                    setup()
                    estado_atual = ESTADO_JOGO
                elif BT_TUTORIAL.clicado(pos):
                    estado_atual = ESTADO_TUTORIAL
                elif BT_FECHAR.clicado(pos):
                    pygame.quit()
                    return False

            elif estado_atual == ESTADO_TUTORIAL:
                if BT_VOLTAR.clicado(pos):
                    estado_atual = ESTADO_MENU

            elif estado_atual == ESTADO_PAUSA:
                if BT_CONTINUAR.clicado(pos):
                    estado_atual = ESTADO_JOGO
                elif BT_REINICIAR.clicado(pos):
                    setup()
                    estado_atual = ESTADO_JOGO
                elif BT_MENU_PRINCIPAL.clicado(pos):
                    setup()
                    estado_atual = ESTADO_MENU

    if estado_atual == ESTADO_MENU:
        desenhar_menu()
        pygame.display.flip()
        return True

    if estado_atual == ESTADO_TUTORIAL:
        desenhar_tutorial()
        pygame.display.flip()
        return True

    teclas = pygame.key.get_pressed()
    if estado_atual == ESTADO_JOGO:
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            jogador.mover(-1)
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            jogador.mover(1)
        if teclas[pygame.K_SPACE]:
            if len(tiros) < 3:
                tiros.append(Tiro(jogador.x + jogador.largura // 2 - 2.5, jogador.y))

        for inimigo in inimigos:
            inimigo.mover()
            if inimigo.x <= 0 or inimigo.x >= LARGURA - inimigo.largura:
                inimigo.direcao *= -1
                inimigo.y += 20

        for tiro in tiros[:]:
            tiro.mover()
            if tiro.y < 0:
                tiros.remove(tiro)

        for tiro in tiros[:]:
            for inimigo in inimigos[:]:
                if tiro.rect.colliderect(inimigo.rect):
                    inimigos.remove(inimigo)
                    tiros.remove(tiro)
                    pontuacao += 10
                    break

        for inimigo in inimigos:
            if jogador.rect.colliderect(inimigo.rect):
                setup()
                break

    tela.fill(PRETO)
    jogador.desenhar()
    for inimigo in inimigos:
        inimigo.desenhar()
    for tiro in tiros:
        tiro.desenhar()

    texto_pontuacao = fonte_pontuacao.render(f'{t("pontuacao")}: {pontuacao}', True, BRANCO)
    tela.blit(texto_pontuacao, (10, 10))

    if not inimigos and estado_atual == ESTADO_JOGO:
        texto_vitoria = fonte_pontuacao.render(t("vitoria"), True, AMARELO)
        tela.blit(texto_vitoria, (LARGURA // 2 - 180, ALTURA // 2))
        if teclas[pygame.K_r]:
            setup()

    if estado_atual == ESTADO_PAUSA:
        desenhar_pausa()
    else:
        desenhar_botoes_idioma()

    pygame.display.flip()
    return True


async def main():
    clock = pygame.time.Clock()
    running = True
    while running:
        running = update_loop()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
