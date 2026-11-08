# Clone simples de Minecraft criado em Python usando Panda3D, inspirado nas primeiras versões do jogo original

# Simple Minecraft clone created in Python using Panda3D inspired by the early versions of the original game

from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from direct.gui.DirectGui import *
import random
import math


class VoxelGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.WORLD_WIDTH = 512
        self.WORLD_DEPTH = 512
        self.WORLD_HEIGHT = 64
        self.CHUNK_SIZE = 16
        self.RENDER_DISTANCE = 6

        self.player_pos = LVector3f(256, 256, 45)
        self.player_h = 0.0
        self.player_p = 0.0
        self.move_speed = 5.0
        self.mouse_sensitivity = 1.8
        self.gravity = -30.0
        self.jump_velocity = 8.5
        self.vertical_velocity = 0.0
        self.player_height = 1.8
        self.is_on_ground = False
        self.camera_margin = 0.5

        self.keys = {'w': False, 's': False, 'a': False, 'd': False,
                     'space': False, 'shift': False}

        self.chunks = {}
        self.world_data = {}
        self.tree_cells = set()
        self.cactus_cells = set()
        self.noise_seed = random.randint(0, 10000)
        self.sensitivity_level = 2
        self.sensitivity_values = {1: 0.9, 2: 1.8, 3: 2.7}

        self.tree_cell_size = 10
        self.cactus_cell_size = 8

        self.game_started = False
        self.game_paused = False
        self.loading_frame = None

        # ── Language system ──────────────────────────────────────────────────
        self.lang = 'pt'

        self.translations = {
            'pt': {
                # Main menu
                'play':           'Jogar',
                'how_to_play':    'Como Jogar',
                'quit':           'Fechar',
                # Controls screen
                'controls_title': 'COMO JOGAR',
                'controls_body': (
                    "COMO JOGAR\n\nWASD - Andar\nMouse - Olhar\nEspaço - Saltar\n"
                    "Shift - Descer\nESC - Menu de pausa\n\n1-9 / Scroll - Selecionar item\n"
                    "Clique Esquerdo - Atacar/Minerar\nClique Direito - Colocar bloco\n\n"
                    "Ferramentas:\n1. Espada (arma)\n2. Picareta (pedra)\n3. Machado (madeira)\n"
                    "4. Pá (terra/areia/grama)\n\nBlocos quebrados vão para a hotbar!\n"
                    "Use clique direito para colocar blocos."
                ),
                'back':           'Voltar',
                # Pause menu
                'pause_title':    'PAUSA',
                'continue':       'Continuar',
                'main_menu':      'Menu Principal',
                'close_game':     'Fechar Jogo',
                'sensitivity':    'Sensibilidade',
                # Death screen
                'you_died':       'Você Morreu',
                'restart':        'Recomeçar',
                'close':          'Fechar',
                # Loading
                'loading':        'Gerando mundo...',
                # Block names
                'block_grass':    'Grama',
                'block_dirt':     'Terra',
                'block_stone':    'Pedra',
                'block_sand':     'Areia',
                'block_wood':     'Madeira',
                'block_leaves':   'Folhas',
                'block_cactus':   'Cacto',
                'block_water':    'Água',
                # Console messages
                'collected':      'Coletado',
                'total':          'Total',
                'new_item':       'Novo item',
                'hotbar_full':    'Hotbar cheia! Não foi possível adicionar',
                'block_placed':   'Bloco {} colocado em ({}, {}, {})',
            },
            'en': {
                # Main menu
                'play':           'Play',
                'how_to_play':    'How to Play',
                'quit':           'Quit',
                # Controls screen
                'controls_title': 'HOW TO PLAY',
                'controls_body': (
                    "HOW TO PLAY\n\nWASD - Move\nMouse - Look\nSpace - Jump\n"
                    "Shift - Descend\nESC - Pause menu\n\n1-9 / Scroll - Select item\n"
                    "Left Click - Attack/Mine\nRight Click - Place block\n\n"
                    "Tools:\n1. Sword (weapon)\n2. Pickaxe (stone)\n3. Axe (wood)\n"
                    "4. Shovel (dirt/sand/grass)\n\nMined blocks go to the hotbar!\n"
                    "Right click to place blocks."
                ),
                'back':           'Back',
                # Pause menu
                'pause_title':    'PAUSED',
                'continue':       'Continue',
                'main_menu':      'Main Menu',
                'close_game':     'Close Game',
                'sensitivity':    'Sensitivity',
                # Death screen
                'you_died':       'You Died',
                'restart':        'Restart',
                'close':          'Close',
                # Loading
                'loading':        'Generating world...',
                # Block names
                'block_grass':    'Grass',
                'block_dirt':     'Dirt',
                'block_stone':    'Stone',
                'block_sand':     'Sand',
                'block_wood':     'Wood',
                'block_leaves':   'Leaves',
                'block_cactus':   'Cactus',
                'block_water':    'Water',
                # Console messages
                'collected':      'Collected',
                'total':          'Total',
                'new_item':       'New item',
                'hotbar_full':    'Hotbar full! Could not add',
                'block_placed':   '{} block placed at ({}, {}, {})',
            },
        }

        # Block key → translation key mapping
        self._block_name_key = {
            'grass': 'block_grass', 'dirt': 'block_dirt', 'stone': 'block_stone',
            'sand': 'block_sand',   'wood': 'block_wood', 'leaves': 'block_leaves',
            'cactus': 'block_cactus', 'water': 'block_water',
        }
        # ─────────────────────────────────────────────────────────────────────

        self.hotbar_slots = 9
        self.selected_slot = 0
        self.hotbar_items = {
            0: {'type': 'espada', 'count': 1}, 1: {'type': 'picareta', 'count': 1},
            2: {'type': 'machado', 'count': 1}, 3: {'type': 'pa', 'count': 1},
            4: None, 5: None, 6: None, 7: None, 8: None
        }
        self.hotbar_frames = []
        self.hotbar_labels = []
        self.hotbar_icons = []
        self.hand_display = None

        self.max_health = 10
        self.health = 10
        self.invincibility_timer = 0.0
        self.INVINCIBILITY_DURATION = 0.5
        self.regen_cooldown = 0.0
        self.regen_tick = 0.0
        self.health_hearts = []
        self.health_bar_frame = None

        self.max_oxygen = 10
        self.oxygen = 10
        self.oxygen_tick = 0.0
        self.oxygen_drain_tick = 0.0
        self.oxygen_damage_tick = 0.0
        self.cactus_damage_tick = 0.0
        self.oxygen_bubbles = []
        self.oxygen_bar_frame = None

        self.zombies = []
        self.underwater_overlay = None
        self.swing_timer = 0.0
        self.player_knockback_vel = LVector3f(0, 0, 0)
        self.spawned_zombie_chunks = set()

        self.setup_main_menu()

    # ── Translation helper ───────────────────────────────────────────────────
    def t(self, key):
        return self.translations[self.lang].get(key, key)

    def get_block_name(self, block_type):
        name_key = self._block_name_key.get(block_type)
        if name_key:
            return self.t(name_key)
        return block_type.capitalize()

    def change_language(self, lang):
        self.lang = lang
        # Rebuild the main menu to reflect new language
        for w in [self.menu_frame, self.title, self.btn_play, self.btn_howto, self.btn_quit]:
            w.destroy()
        if hasattr(self, 'lang_btn_pt'):
            self.lang_btn_pt.destroy()
            self.lang_btn_en.destroy()
        self.setup_main_menu()
    # ─────────────────────────────────────────────────────────────────────────

    def setup_underwater_overlay(self):
        self.underwater_overlay = DirectFrame(
            frameColor=(0.0, 0.05, 0.2, 0.5),
            frameSize=(-2, 2, -2, 2),
            parent=self.aspect2d,
        )
        self.underwater_overlay.hide()

    def _make_colored_cube(self, r, g, b):
        arr = GeomVertexArrayFormat()
        arr.addColumn(InternalName.make('vertex'), 3, Geom.NTFloat32, Geom.CPoint)
        arr.addColumn(InternalName.make('color'),  4, Geom.NTFloat32, Geom.CColor)
        fmt = GeomVertexFormat()
        fmt.addArray(arr)
        fmt = GeomVertexFormat.registerFormat(fmt)
        vdata = GeomVertexData('cube', fmt, Geom.UHStatic)
        vw = GeomVertexWriter(vdata, 'vertex')
        cw = GeomVertexWriter(vdata, 'color')
        tris = GeomTriangles(Geom.UHStatic)
        vc = 0
        def quad(v0, v1, v2, v3):
            nonlocal vc
            for v in (v0, v1, v2):
                vw.addData3(*v); cw.addData4(r, g, b, 1)
            tris.addVertices(vc, vc+1, vc+2); vc += 3
            for v in (v0, v2, v3):
                vw.addData3(*v); cw.addData4(r, g, b, 1)
            tris.addVertices(vc, vc+1, vc+2); vc += 3
        quad((0,0,1),(1,0,1),(1,1,1),(0,1,1))
        quad((1,0,0),(0,0,0),(0,1,0),(1,1,0))
        quad((0,1,0),(0,1,1),(1,1,1),(1,1,0))
        quad((1,0,0),(1,0,1),(0,0,1),(0,0,0))
        quad((1,0,0),(1,1,0),(1,1,1),(1,0,1))
        quad((0,1,0),(0,0,0),(0,0,1),(0,1,1))
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode('cube')
        node.addGeom(geom)
        return node

    def spawn_zombie(self, x, y):
        surface_z = self.get_terrain_height(x, y)
        if self.world_data.get((x, y, surface_z)) == 'water':
            return

        zombie_np = self.render.attachNewNode('zombie')
        zombie_np.setPos(x + 0.5, y + 0.5, surface_z + 1)
        zombie_np.setTwoSided(True)

        HEAD_G  = (0.1, 0.4, 0.1)
        TORSO_G = (0.4, 0.7, 0.9)
        LEG_G   = (0.1, 0.1, 0.5)

        legs = zombie_np.attachNewNode(self._make_colored_cube(*LEG_G))
        legs.setScale(0.5, 0.5, 1.0)
        legs.setPos(-0.25, -0.25, 0.0)

        torso = zombie_np.attachNewNode(self._make_colored_cube(*TORSO_G))
        torso.setScale(0.5, 0.5, 1.0)
        torso.setPos(-0.25, -0.25, 1.0)

        arm_l = zombie_np.attachNewNode(self._make_colored_cube(*HEAD_G))
        arm_l.setScale(0.25, 0.25, 0.75)
        arm_l.setPos(-0.5, -0.25, 1.25)

        arm_r = zombie_np.attachNewNode(self._make_colored_cube(*HEAD_G))
        arm_r.setScale(0.25, 0.25, 0.75)
        arm_r.setPos(0.25, -0.25, 1.25)

        head = zombie_np.attachNewNode(self._make_colored_cube(*HEAD_G))
        head.setScale(0.5)
        head.setPos(-0.25, -0.25, 2.0)

        angle = random.uniform(0, 2 * math.pi)
        wander_dir = [math.cos(angle), math.sin(angle)]

        self.zombies.append({
            'pos': LVector3f(x + 0.5, y + 0.5, surface_z + 1),
            'health': 10.0,
            'node': zombie_np,
            'wander_dir': wander_dir,
            'wander_timer': 0.0,
            'hit_flash': 0.0,
            'knockback_vel': LVector3f(0, 0, 0),
        })

    def spawn_zombies_for_chunk(self, cx, cy):
        if (cx, cy) in self.spawned_zombie_chunks:
            return
        self.spawned_zombie_chunks.add((cx, cy))
        count = 1 if random.random() < 0.08 else 0
        sx, sy = cx * self.CHUNK_SIZE, cy * self.CHUNK_SIZE
        for _ in range(count):
            ox = sx + random.randint(1, self.CHUNK_SIZE - 2)
            oy = sy + random.randint(1, self.CHUNK_SIZE - 2)
            ox = max(5, min(self.WORLD_WIDTH - 5, ox))
            oy = max(5, min(self.WORLD_DEPTH - 5, oy))
            self.spawn_zombie(ox, oy)

    def update_zombies(self, dt, px, py, pz):
        zombie_speed = self.move_speed * 0.5
        for zombie in list(self.zombies):
            if zombie['health'] <= 0:
                zombie['node'].removeNode()
                self.zombies.remove(zombie)
                continue

            if zombie['hit_flash'] > 0:
                zombie['hit_flash'] = max(0.0, zombie['hit_flash'] - dt)
                color = (1, 0.1, 0.1, 1) if zombie['hit_flash'] > 0 else None
                if color:
                    zombie['node'].setColorScale(*color)
                else:
                    zombie['node'].clearColorScale()

            zx, zy = zombie['pos'].x, zombie['pos'].y
            dx_to_p = px - zx
            dy_to_p = py - zy
            dist = math.sqrt(dx_to_p**2 + dy_to_p**2)

            kb = zombie['knockback_vel']
            if kb.length() > 0.01:
                zx += kb.x * dt
                zy += kb.y * dt
                zombie['knockback_vel'] *= max(0.0, 1.0 - dt * 8)
            elif dist < 12.0 and dist > 0.1:
                zx += (dx_to_p / dist) * zombie_speed * dt
                zy += (dy_to_p / dist) * zombie_speed * dt
            else:
                zombie['wander_timer'] -= dt
                if zombie['wander_timer'] <= 0:
                    angle = random.uniform(0, 2 * math.pi)
                    zombie['wander_dir'] = [math.cos(angle), math.sin(angle)]
                    zombie['wander_timer'] = random.uniform(2.0, 5.0)
                zx += zombie['wander_dir'][0] * zombie_speed * dt
                zy += zombie['wander_dir'][1] * zombie_speed * dt

            zx = max(1, min(self.WORLD_WIDTH - 1, zx))
            zy = max(1, min(self.WORLD_DEPTH - 1, zy))
            surface_z = self.get_terrain_height(int(zx), int(zy))
            zombie['pos'].x = zx
            zombie['pos'].y = zy
            zombie['pos'].z = surface_z + 1
            zombie['node'].setPos(zx, zy, surface_z + 1)

            if dist < 12.0 and dist > 0.1:
                face_angle = math.degrees(math.atan2(-(dx_to_p), dy_to_p))
            else:
                fd = zombie['wander_dir']
                face_angle = math.degrees(math.atan2(-fd[0], fd[1]))
            zombie['node'].setH(face_angle)

            if dist < 1.5:
                kb_dir = LVector3f(px - zx, py - zy, 0)
                if kb_dir.length() > 0.01:
                    kb_dir.normalize()
                self.take_damage(2, knockback_dir=kb_dir)

    def attack_zombie(self):
        cam_pos = self.camera.getPos()
        forward = self.camera.getQuat().getForward()
        best = None
        best_dist = 7.0
        for zombie in self.zombies:
            zx, zy = zombie['pos'].x, zombie['pos'].y
            zz_base = zombie['pos'].z
            for zz in (zz_base + 0.5, zz_base + 1.0, zz_base + 1.5, zz_base + 2.2):
                to_z = LVector3f(zx - cam_pos.x, zy - cam_pos.y, zz - cam_pos.z)
                dist = to_z.length()
                if dist < 0.01 or dist > best_dist:
                    continue
                dot = forward.dot(to_z / dist)
                if dot > 0.7:
                    best = zombie
                    best_dist = dist
        if best is None:
            return False
        best['health'] -= 2.5
        best['hit_flash'] = 0.2
        best['node'].setColorScale(1, 0.1, 0.1, 1)
        kb_dir = LVector3f(forward.x, forward.y, 0)
        if kb_dir.length() > 0.01:
            kb_dir.normalize()
        best['knockback_vel'] = kb_dir * 15.0
        if best['health'] <= 0:
            best['node'].removeNode()
            self.zombies.remove(best)
        return True

    def setup_main_menu(self):
        self.menu_frame = DirectFrame(frameColor=(0.25, 0.15, 0.1, 1),
                                      frameSize=(-2, 2, -2, 2), pos=(0, 0, 0))
        self.title = DirectLabel(text="MCPY", text_scale=0.4,
                                 text_fg=(0.8, 0.8, 0.8, 1), frameColor=(0, 0, 0, 0),
                                 pos=(0, 0, 0.6))
        self.title.setTransparency(TransparencyAttrib.M_alpha)
        self.title['text_shadow'] = (0, 0, 0, 1)
        self.title['text_shadowOffset'] = (0.05, 0.05)
        btn_cfg = dict(text_fg=(0, 0, 0, 1), frameColor=(0.7, 0.7, 0.7, 1), pressEffect=1)
        self.btn_play  = DirectButton(text=self.t('play'),        scale=0.15, pos=(0, 0,  0.1),
                                      command=self.start_game, **btn_cfg)
        self.btn_howto = DirectButton(text=self.t('how_to_play'), scale=0.15, pos=(0, 0, -0.15),
                                      command=self.show_controls, **btn_cfg)
        self.btn_quit  = DirectButton(text=self.t('quit'),        scale=0.15, pos=(0, 0, -0.4),
                                      command=self.quit_game, **btn_cfg)
        self.setBackgroundColor(0.25, 0.15, 0.1, 1)

        # ── Language buttons (bottom-right) ──────────────────────────────────
        lang_btn_cfg = dict(text_fg=(0, 0, 0, 1), pressEffect=1)

        pt_color = (0.9, 0.75, 0.2, 1) if self.lang == 'pt' else (0.6, 0.6, 0.6, 1)
        en_color = (0.9, 0.75, 0.2, 1) if self.lang == 'en' else (0.6, 0.6, 0.6, 1)

        self.lang_btn_pt = DirectButton(
            text='PT', scale=0.09, pos=(1.6, 0, -0.88),
            command=self.change_language, extraArgs=['pt'],
            frameColor=pt_color, **lang_btn_cfg)

        self.lang_btn_en = DirectButton(
            text='EN', scale=0.09, pos=(1.75, 0, -0.88),
            command=self.change_language, extraArgs=['en'],
            frameColor=en_color, **lang_btn_cfg)
        # ─────────────────────────────────────────────────────────────────────

    def show_controls(self):
        self.hide_main_menu()
        self.controls_frame = DirectFrame(frameColor=(0.25, 0.15, 0.1, 1),
                                          frameSize=(-2, 2, -2, 2), pos=(0, 0, 0))
        DirectLabel(text=self.t('controls_body'), parent=self.controls_frame, text_scale=0.07,
                    text_fg=(0.8, 0.8, 0.8, 1), frameColor=(0, 0, 0, 0),
                    pos=(0, 0, 0.85), text_align=TextNode.ACenter)
        DirectButton(text=self.t('back'), parent=self.controls_frame, scale=0.15,
                     pos=(0, 0, -0.85), command=self.back_to_menu,
                     text_fg=(0, 0, 0, 1), frameColor=(0.7, 0.7, 0.7, 1), pressEffect=1)

    def back_to_menu(self):
        if hasattr(self, 'controls_frame'):
            self.controls_frame.destroy()
        self.show_main_menu()

    def hide_main_menu(self):
        for w in [self.menu_frame, self.title, self.btn_play, self.btn_howto, self.btn_quit,
                  self.lang_btn_pt, self.lang_btn_en]:
            w.hide()

    def show_main_menu(self):
        for w in [self.menu_frame, self.title, self.btn_play, self.btn_howto, self.btn_quit,
                  self.lang_btn_pt, self.lang_btn_en]:
            w.show()

    def setup_pause_menu(self):
        self.pause_frame = DirectFrame(frameColor=(0.2, 0.2, 0.2, 0.7),
                                       frameSize=(-2, 2, -2, 2), pos=(0, 0, 0))
        lbl = DirectLabel(text=self.t('pause_title'), parent=self.pause_frame, text_scale=0.2,
                          text_fg=(0.8, 0.8, 0.8, 1), frameColor=(0, 0, 0, 0), pos=(0, 0, 0.5))
        lbl['text_shadow'] = (0, 0, 0, 1)
        lbl['text_shadowOffset'] = (0.05, 0.05)
        btn_cfg = dict(text_fg=(0, 0, 0, 1), frameColor=(0.7, 0.7, 0.7, 1), pressEffect=1)
        DirectButton(text=self.t('continue'),   parent=self.pause_frame, scale=0.15,
                     pos=(0, 0,  0.1), command=self.resume_game, **btn_cfg)
        DirectButton(text=self.t('main_menu'),  parent=self.pause_frame, scale=0.15,
                     pos=(0, 0, -0.15), command=self.return_to_main_menu, **btn_cfg)
        DirectButton(text=self.t('close_game'), parent=self.pause_frame, scale=0.15,
                     pos=(0, 0, -0.4), command=self.quit_game, **btn_cfg)

        # --- Sensitivity control (bottom-left) ---
        sens_x = -1.75
        sens_y = -0.85

        DirectLabel(text=self.t('sensitivity'), parent=self.pause_frame,
                    text_scale=0.06, text_fg=(0.8, 0.8, 0.8, 1),
                    frameColor=(0, 0, 0, 0), pos=(sens_x + 0.13, 0, sens_y + 0.12))

        DirectButton(text="▲", parent=self.pause_frame, scale=0.07,
                     pos=(sens_x + 0.13, 0, sens_y + 0.04),
                     command=self.increase_sensitivity,
                     text_fg=(1, 1, 1, 1), frameColor=(0.4, 0.4, 0.4, 0.9), pressEffect=1)

        self.sensitivity_label = DirectLabel(
                    text=str(self.sensitivity_level), parent=self.pause_frame,
                    text_scale=0.09, text_fg=(1, 1, 0.3, 1),
                    frameColor=(0, 0, 0, 0), pos=(sens_x + 0.13, 0, sens_y - 0.05))

        DirectButton(text="▼", parent=self.pause_frame, scale=0.07,
                     pos=(sens_x + 0.13, 0, sens_y - 0.14),
                     command=self.decrease_sensitivity,
                     text_fg=(1, 1, 1, 1), frameColor=(0.4, 0.4, 0.4, 0.9), pressEffect=1)

        self.pause_frame.hide()

    def increase_sensitivity(self):
        if self.sensitivity_level < 3:
            self.sensitivity_level += 1
            self.mouse_sensitivity = self.sensitivity_values[self.sensitivity_level]
            self.sensitivity_label['text'] = str(self.sensitivity_level)

    def decrease_sensitivity(self):
        if self.sensitivity_level > 1:
            self.sensitivity_level -= 1
            self.mouse_sensitivity = self.sensitivity_values[self.sensitivity_level]
            self.sensitivity_label['text'] = str(self.sensitivity_level)

    def setup_health_bar(self):
        hotbar_start_x = -((self.hotbar_slots * 0.13) / 2) + (0.13 / 2)
        spacing = 0.065
        y_pos = -0.72

        self.health_bar_frame = DirectFrame(frameColor=(0, 0, 0, 0),
                                            frameSize=(0, self.max_health * spacing, -0.04, 0.04),
                                            pos=(hotbar_start_x - spacing / 2, 0, y_pos),
                                            parent=self.aspect2d)
        self.health_hearts = []
        for i in range(self.max_health):
            heart = DirectFrame(parent=self.health_bar_frame,
                                frameColor=(0.85, 0.1, 0.1, 1),
                                frameSize=(-0.024, 0.024, -0.024, 0.024),
                                pos=(i * spacing, 0, 0))
            self.health_hearts.append(heart)
        self.update_health_bar()

    def update_health_bar(self):
        for i, heart in enumerate(self.health_hearts):
            if i < self.health:
                heart['frameColor'] = (0.85, 0.1, 0.1, 1)
            else:
                heart['frameColor'] = (0.25, 0.05, 0.05, 0.6)

    def setup_oxygen_bar(self):
        hotbar_start_x = -((self.hotbar_slots * 0.13) / 2) + (0.13 / 2)
        spacing = 0.065
        y_pos = -0.655

        self.oxygen_bar_frame = DirectFrame(frameColor=(0, 0, 0, 0),
                                            frameSize=(0, self.max_oxygen * spacing, -0.04, 0.04),
                                            pos=(hotbar_start_x - spacing / 2, 0, y_pos),
                                            parent=self.aspect2d)
        self.oxygen_bubbles = []
        for i in range(self.max_oxygen):
            bubble = DirectFrame(parent=self.oxygen_bar_frame,
                                 frameColor=(1, 1, 1, 1),
                                 frameSize=(-0.024, 0.024, -0.024, 0.024),
                                 pos=(i * spacing, 0, 0))
            self.oxygen_bubbles.append(bubble)
        self.oxygen_bar_frame.hide()

    def update_oxygen_bar(self):
        for i, bubble in enumerate(self.oxygen_bubbles):
            if i < self.oxygen:
                bubble['frameColor'] = (1, 1, 1, 1)
            else:
                bubble['frameColor'] = (0.3, 0.3, 0.3, 0.5)

    def take_damage(self, amount=1, knockback_dir=None):
        if self.invincibility_timer > 0:
            return
        self.health = max(0, self.health - amount)
        self.invincibility_timer = self.INVINCIBILITY_DURATION
        self.regen_cooldown = 10.0
        self.regen_tick = 0.0
        self.update_health_bar()
        if knockback_dir is not None:
            self.player_knockback_vel = LVector3f(knockback_dir.x, knockback_dir.y, 0) * 18.0
        if self.health <= 0:
            self.show_death_screen()

    def show_death_screen(self):
        self.game_paused = True
        self._set_window_cursor(False)
        self.death_frame = DirectFrame(frameColor=(0.5, 0.0, 0.0, 0.92),
                                       frameSize=(-2, 2, -2, 2), pos=(0, 0, 0))
        lbl = DirectLabel(text=self.t('you_died'), parent=self.death_frame,
                          text_scale=0.3, text_fg=(1, 1, 1, 1),
                          frameColor=(0, 0, 0, 0), pos=(0, 0, 0.4))
        lbl['text_shadow'] = (0.2, 0, 0, 1)
        lbl['text_shadowOffset'] = (0.06, 0.06)
        btn_cfg = dict(text_fg=(0, 0, 0, 1), frameColor=(0.85, 0.85, 0.85, 1), pressEffect=1)
        DirectButton(text=self.t('restart'),   parent=self.death_frame, scale=0.15,
                     pos=(0, 0,  0.0), command=self.restart_game, **btn_cfg)
        DirectButton(text=self.t('main_menu'), parent=self.death_frame, scale=0.15,
                     pos=(0, 0, -0.22), command=self.death_return_to_menu, **btn_cfg)
        DirectButton(text=self.t('close'),     parent=self.death_frame, scale=0.15,
                     pos=(0, 0, -0.44), command=self.quit_game, **btn_cfg)

    def restart_game(self):
        self.death_frame.destroy()
        self.return_to_main_menu()
        self.start_game()

    def death_return_to_menu(self):
        self.death_frame.destroy()
        self.return_to_main_menu()

    def setup_hotbar(self):
        slot_size = 0.12
        spacing = 0.13
        start_x = -((self.hotbar_slots * spacing) / 2) + (spacing / 2)
        y_pos = -0.85
        for i in range(self.hotbar_slots):
            x_pos = start_x + (i * spacing)
            frame = DirectFrame(frameColor=(0.3, 0.3, 0.3, 0.8),
                                frameSize=(-slot_size/2, slot_size/2, -slot_size/2, slot_size/2),
                                pos=(x_pos, 0, y_pos), parent=self.aspect2d)
            DirectLabel(text=str(i + 1), text_scale=0.035, text_fg=(0.9, 0.9, 0.9, 1),
                        frameColor=(0, 0, 0, 0),
                        pos=(-slot_size/2 + 0.012, 0, slot_size/2 - 0.018),
                        text_align=TextNode.ALeft, parent=frame)
            count_label = DirectLabel(text="", text_scale=0.03, text_fg=(1, 1, 1, 1),
                                      frameColor=(0, 0, 0, 0),
                                      pos=(slot_size/2 - 0.005, 0, -slot_size/2 + 0.005),
                                      text_align=TextNode.ARight, parent=frame)
            self.hotbar_labels.append(count_label)
            self.hotbar_frames.append(frame)
            self.hotbar_icons.append(None)
        self.update_hotbar_display()
        self.update_hotbar_selection()

    def _make_block_icon(self, block_type, parent):
        top_colors = {
            'grass':  (0.2,  0.8,  0.2), 'dirt':   (0.6,  0.4,  0.2),
            'stone':  (0.5,  0.5,  0.5), 'sand':   (0.9,  0.85, 0.4),
            'wood':   (0.4,  0.25, 0.1), 'leaves': (0.15, 0.55, 0.15),
            'cactus': (0.1,  0.35, 0.1), 'water':  (0.05, 0.15, 0.5),
        }
        r, g, b = top_colors.get(block_type, (0.5, 0.5, 0.5))
        half = 0.028
        return DirectFrame(parent=parent, frameColor=(r, g, b, 1),
                           frameSize=(-half, half, -half, half), pos=(0, 0, 0))

    def _make_tool_icon(self, tool_type, parent):
        W  = (1.000, 1.000, 1.000, 1)
        CL = (0.800, 0.800, 0.800, 1)
        CE = (0.533, 0.533, 0.533, 1)
        M  = (0.545, 0.271, 0.075, 1)
        MD = (0.361, 0.180, 0.000, 1)

        grids = {
            'espada': [
                [None, None, None,  CL,  CL, None, None, None],
                [None, None, None,  W,   CE, None, None, None],
                [None, None, None,  W,   CE, None, None, None],
                [None, None, None,  W,   CE, None, None, None],
                [None, None, None,  W,   CE, None, None, None],
                [None, None, None,  W,   CE, None, None, None],
                [None, None, None,  W,   CE, None, None, None],
                [None,  CE,  CE,  CE,  CE,  CE,  CE, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  MD,  MD, None, None, None],
            ],
            'picareta': [
                [ CL,  W,   W,   W,   W,   W,   W,   CL],
                [ CE,  CE, None,  CE,  CE, None,  CE,  CE],
                [None,  CE, None,  M,   M,  None,  CE, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  MD,  MD, None, None, None],
            ],
            'machado': [
                [None,  CL,  W,   W,   CE,  M,   M,  None],
                [ CL,   W,   W,   W,   CE,  M,   M,  None],
                [ CL,   W,   W,   W,   CE,  M,   M,  None],
                [None,  CL,  W,   W,   CE,  M,   M,  None],
                [None, None, None, None, None,  M,   M,  None],
                [None, None, None, None, None,  M,   M,  None],
                [None, None, None, None, None,  M,   M,  None],
                [None, None, None, None, None,  MD,  MD, None],
            ],
            'pa': [
                [None, None,  CL,  CL,  CL,  CE, None, None],
                [None, None,  W,   W,   W,   CE, None, None],
                [None, None,  W,   W,   W,   CE, None, None],
                [None, None, None,  CE,  CE, None, None, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  M,   M,  None, None, None],
                [None, None, None,  MD,  MD, None, None, None],
            ],
        }

        grid = grids.get(tool_type)
        if grid is None:
            return

        COLS  = 8
        ROWS  = len(grid)
        pixel = 0.008
        half_x = COLS * pixel / 2
        half_z = ROWS * pixel / 2

        for row, line in enumerate(grid):
            for col, color in enumerate(line):
                if color is None:
                    continue
                x = -half_x + col * pixel + pixel / 2
                z =  half_z - row * pixel - pixel / 2
                p = pixel / 2
                DirectFrame(parent=parent, frameColor=color,
                            frameSize=(-p, p, -p, p), pos=(x, 0, z))

    def update_hotbar_display(self):
        for i in range(self.hotbar_slots):
            if self.hotbar_icons[i] is not None:
                self.hotbar_icons[i].removeNode()
                self.hotbar_icons[i] = None
            item_data = self.hotbar_items.get(i)
            frame = self.hotbar_frames[i]
            if item_data:
                item_type = item_data['type']
                icon_root = DirectFrame(parent=frame, frameColor=(0, 0, 0, 0),
                                        frameSize=(-0.04, 0.04, -0.04, 0.04),
                                        pos=(0, 0, -0.005))
                if self.is_tool(item_type):
                    self._make_tool_icon(item_type, icon_root)
                    self.hotbar_labels[i]['text'] = ""
                else:
                    self._make_block_icon(item_type, icon_root)
                    count = item_data.get('count', 1)
                    self.hotbar_labels[i]['text'] = str(count) if count > 1 else ""
                self.hotbar_icons[i] = icon_root
            else:
                self.hotbar_labels[i]['text'] = ""
        self.update_hand_display(swinging=self.swing_timer > 0)

    def update_hotbar_selection(self):
        for i, frame in enumerate(self.hotbar_frames):
            frame['frameColor'] = (0.8, 0.8, 0.3, 0.9) if i == self.selected_slot else (0.3, 0.3, 0.3, 0.8)
        self.update_hand_display()

    def update_hand_display(self, swinging=False):
        if self.hand_display is not None:
            self.hand_display.destroy()
            self.hand_display = None

        if not self.hotbar_frames:
            return

        item_data = self.hotbar_items.get(self.selected_slot)
        if not item_data:
            return

        item_type = item_data['type']
        SCALE = 8.0

        container = DirectFrame(parent=self.aspect2d,
                                frameColor=(0, 0, 0, 0),
                                frameSize=(-0.04 * SCALE, 0.04 * SCALE,
                                           -0.04 * SCALE, 0.04 * SCALE),
                                pos=(1.55, 0, -0.62))

        icon_root = DirectFrame(parent=container, frameColor=(0, 0, 0, 0),
                                frameSize=(-0.04, 0.04, -0.04, 0.04),
                                pos=(0, 0, 0))
        icon_root.setScale(SCALE)

        if swinging:
            icon_root.setR(-75)

        if self.is_tool(item_type):
            self._make_tool_icon(item_type, icon_root)
        else:
            self._make_block_icon(item_type, icon_root)

        self.hand_display = container

    def select_hotbar_slot(self, slot):
        if 0 <= slot < self.hotbar_slots:
            self.selected_slot = slot
            self.update_hotbar_selection()

    def scroll_hotbar(self, direction):
        if self.game_paused:
            return
        self.selected_slot = (self.selected_slot + direction) % self.hotbar_slots
        self.update_hotbar_selection()

    def get_selected_item(self):
        item_data = self.hotbar_items.get(self.selected_slot)
        return item_data['type'] if item_data else None

    def is_tool(self, item_type):
        return item_type in ('espada', 'picareta', 'machado', 'pa')

    def add_item_to_hotbar(self, block_type):
        for i in range(self.hotbar_slots):
            item_data = self.hotbar_items.get(i)
            if item_data and item_data['type'] == block_type:
                item_data['count'] += 1
                self.update_hotbar_display()
                print(f"{self.t('collected')}: {self.get_block_name(block_type)} ({self.t('total')}: {item_data['count']})")
                return
        for i in range(self.hotbar_slots):
            if self.hotbar_items.get(i) is None:
                self.hotbar_items[i] = {'type': block_type, 'count': 1}
                self.update_hotbar_display()
                print(f"{self.t('collected')}: {self.get_block_name(block_type)} ({self.t('new_item')})")
                return
        print(f"{self.t('hotbar_full')} {self.get_block_name(block_type)}")

    def remove_item_from_hotbar(self, slot):
        item_data = self.hotbar_items.get(slot)
        if not item_data or self.is_tool(item_data['type']):
            return False
        item_data['count'] -= 1
        if item_data['count'] <= 0:
            self.hotbar_items[slot] = None
        self.update_hotbar_display()
        return True

    def raycast_block_with_face(self):
        cam_pos = self.camera.getPos()
        forward = self.camera.getQuat().getForward()
        max_distance = 8.0
        step = 0.05
        prev_pos = None
        for dist in range(int(max_distance / step)):
            check_pos = cam_pos + forward * (dist * step)
            x, y, z = int(check_pos.x), int(check_pos.y), int(check_pos.z)
            if (x, y, z) in self.world_data:
                if prev_pos is None:
                    return (x, y, z), None
                px, py, pz = prev_pos
                return (x, y, z), (px - x, py - y, pz - z)
            prev_pos = (x, y, z)
        return None, None

    def can_break_block(self, block_type, tool):
        if self.is_liquid(block_type):
            return False
        tool_map = {
            'pa': ('grass', 'dirt', 'sand'),
            'machado': ('wood', 'leaves'),
            'picareta': ('stone',),
        }
        return block_type in tool_map.get(tool, ())

    def break_block(self):
        if self.game_paused:
            return
        self.swing_timer = 0.15
        self.update_hand_display(swinging=True)
        selected_tool = self.get_selected_item()
        if selected_tool == 'espada':
            if self.attack_zombie():
                return
        block_pos, _ = self.raycast_block_with_face()
        if not block_pos:
            return
        x, y, z = block_pos
        block_type = self.world_data.get(block_pos)
        if not block_type:
            return
        selected_tool = self.get_selected_item()
        if selected_tool and self.can_break_block(block_type, selected_tool):
            self.add_item_to_hotbar(block_type)
            del self.world_data[block_pos]
            cx, cy = x // self.CHUNK_SIZE, y // self.CHUNK_SIZE
            if (cx, cy) in self.chunks:
                self.chunks[(cx, cy)].removeNode()
                del self.chunks[(cx, cy)]
            self.create_chunk_mesh(cx, cy)

    def place_block(self):
        if self.game_paused:
            return
        item_data = self.hotbar_items.get(self.selected_slot)
        if not item_data:
            return
        block_type = item_data['type']
        if self.is_tool(block_type):
            return
        block_pos, face = self.raycast_block_with_face()
        if not block_pos or not face:
            return
        x, y, z = block_pos
        new_x, new_y, new_z = x + face[0], y + face[1], z + face[2]
        if not (0 <= new_x < self.WORLD_WIDTH and 0 <= new_y < self.WORLD_DEPTH and 0 <= new_z < self.WORLD_HEIGHT):
            return
        if (new_x, new_y, new_z) in self.world_data:
            return
        pxi, pyi = int(self.player_pos.x), int(self.player_pos.y)
        pzf, pzh = int(self.player_pos.z - self.player_height), int(self.player_pos.z)
        if new_x == pxi and new_y == pyi and pzf <= new_z <= pzh:
            return
        self.world_data[(new_x, new_y, new_z)] = block_type
        if self.remove_item_from_hotbar(self.selected_slot):
            cx, cy = new_x // self.CHUNK_SIZE, new_y // self.CHUNK_SIZE
            if (cx, cy) in self.chunks:
                self.chunks[(cx, cy)].removeNode()
                del self.chunks[(cx, cy)]
            self.create_chunk_mesh(cx, cy)
            print(self.t('block_placed').format(
                self.get_block_name(block_type), new_x, new_y, new_z))

    def toggle_pause(self):
        if not self.game_started:
            return
        self.game_paused = not self.game_paused
        props = WindowProperties()
        if self.game_paused:
            self.pause_frame.show()
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)
        else:
            self.pause_frame.hide()
            props.setCursorHidden(True)
            props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)

    def resume_game(self):
        self.toggle_pause()

    def _set_window_cursor(self, hidden):
        try:
            props = WindowProperties()
            props.setCursorHidden(hidden)
            props.setMouseMode(WindowProperties.M_relative if hidden else WindowProperties.M_absolute)
            self.win.requestProperties(props)
        except Exception:
            pass

    def return_to_main_menu(self):
        for chunk_np in self.chunks.values():
            chunk_np.removeNode()
        self.chunks.clear()
        self.world_data.clear()
        self.tree_cells.clear()
        self.cactus_cells.clear()
        self.pause_frame.hide()
        if self.health_bar_frame is not None:
            self.health_bar_frame.destroy()
            self.health_bar_frame = None
            self.health_hearts = []
        if self.oxygen_bar_frame is not None:
            self.oxygen_bar_frame.destroy()
            self.oxygen_bar_frame = None
            self.oxygen_bubbles = []
        if self.underwater_overlay is not None:
            self.underwater_overlay.destroy()
            self.underwater_overlay = None
        for zombie in self.zombies:
            zombie['node'].removeNode()
        self.zombies.clear()
        self.spawned_zombie_chunks.clear()
        if self.hand_display is not None:
            self.hand_display.destroy()
            self.hand_display = None
        for frame in self.hotbar_frames:
            frame.destroy()
        self.hotbar_frames.clear()
        self.hotbar_labels.clear()
        self.hotbar_icons.clear()
        self.game_started = False
        self.game_paused = False
        self.health = self.max_health
        self.invincibility_timer = 0.0
        self.regen_cooldown = 0.0
        self.regen_tick = 0.0
        self.oxygen = self.max_oxygen
        self.oxygen_tick = 0.0
        self.oxygen_drain_tick = 0.0
        self.oxygen_damage_tick = 0.0
        self.cactus_damage_tick = 0.0
        self.hotbar_items = {
            0: {'type': 'espada', 'count': 1}, 1: {'type': 'picareta', 'count': 1},
            2: {'type': 'machado', 'count': 1}, 3: {'type': 'pa', 'count': 1},
            4: None, 5: None, 6: None, 7: None, 8: None
        }
        self.taskMgr.remove("update")
        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(0, 0, 0)
        self.setup_main_menu()
        self.setBackgroundColor(0.25, 0.15, 0.1, 1)
        self._set_window_cursor(False)

    def quit_game(self):
        import sys
        sys.exit()

    def show_loading_screen(self):
        self.loading_frame = DirectFrame(frameColor=(0.25, 0.15, 0.1, 1),
                                         frameSize=(-2, 2, -2, 2), pos=(0, 0, 0))
        self.loading_label = DirectLabel(text=self.t('loading'), parent=self.loading_frame,
                                         text_scale=0.15, text_fg=(0.8, 0.8, 0.8, 1),
                                         frameColor=(0, 0, 0, 0), pos=(0, 0, 0))
        self.loading_frame.show()
        self.graphicsEngine.renderFrame()
        self.graphicsEngine.renderFrame()

    def hide_loading_screen(self):
        if self.loading_frame:
            self.loading_frame.destroy()
            self.loading_frame = None

    def start_game(self):
        if self.game_started:
            return
        self.hide_main_menu()
        self.menu_frame.destroy()
        self.title.destroy()
        self.btn_play.destroy()
        self.btn_howto.destroy()
        self.btn_quit.destroy()
        self.lang_btn_pt.destroy()
        self.lang_btn_en.destroy()
        self.show_loading_screen()
        self.setup_camera()
        self.setup_lighting()
        self.setup_controls()
        self.setup_crosshair()
        self.setup_pause_menu()
        self.setup_hotbar()
        self.setup_health_bar()
        self.setup_oxygen_bar()
        self.setup_underwater_overlay()
        self.preload_all_chunks()
        self.hide_loading_screen()
        cx = int(self.player_pos.x) // self.CHUNK_SIZE
        cy = int(self.player_pos.y) // self.CHUNK_SIZE
        self.last_chunk_pos = (cx, cy)
        self.taskMgr.add(self.update, "update")
        self.setFrameRateMeter(True)
        self.invincibility_timer = 5.0
        self.regen_cooldown = 10.0
        self.regen_tick = 0.0
        self.game_started = True

    def setup_camera(self):
        self.disableMouse()
        self.camera.setPos(self.player_pos)
        self.camera.setHpr(0, 0, 0)
        lens = self.cam.node().getLens()
        lens.setFov(80)
        lens.setNear(0.01)
        lens.setFar(2000)
        self._set_window_cursor(True)

    def setup_lighting(self):
        ambient = AmbientLight("ambient")
        ambient.setColor((0.7, 0.7, 0.7, 1))
        self.render.setLight(self.render.attachNewNode(ambient))
        sun = DirectionalLight("sun")
        sun.setColor((0.9, 0.9, 0.85, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -45, 0)
        self.render.setLight(sun_np)
        fog = Fog("fog")
        fog.setColor(0.53, 0.81, 0.92)
        fog.setLinearRange(0, self.RENDER_DISTANCE * self.CHUNK_SIZE + 20)
        self.render.setFog(fog)
        self.setBackgroundColor(0.53, 0.81, 0.92, 1)

    def setup_controls(self):
        for key in ('w', 's', 'a', 'd', 'space', 'shift'):
            self.accept(key, self.set_key, [key, True])
            self.accept(f'{key}-up', self.set_key, [key, False])
        for i in range(1, 10):
            self.accept(str(i), self.select_hotbar_slot, [i - 1])
        self.accept('mouse1', self.break_block)
        self.accept('mouse3', self.place_block)
        self.accept('escape', self.toggle_pause)
        self.accept('wheel_up', self.scroll_hotbar, [-1])
        self.accept('wheel_down', self.scroll_hotbar, [1])

    def set_key(self, key, value):
        if not self.game_paused:
            self.keys[key] = value

    def setup_crosshair(self):
        lines = LineSegs()
        lines.setThickness(2.0)
        lines.setColor(1, 1, 1, 1)
        size = 0.02
        lines.moveTo(-size, 0, 0); lines.drawTo(size, 0, 0)
        lines.moveTo(0, 0, -size); lines.drawTo(0, 0, size)
        crosshair_np = self.aspect2d.attachNewNode(lines.create())
        crosshair_np.setBin('fixed', 0)
        crosshair_np.setDepthTest(False)
        crosshair_np.setDepthWrite(False)

    def noise2d(self, x, y):
        x += self.noise_seed
        y += self.noise_seed * 1.5
        ix, iy = int(x), int(y)
        fx = x - ix
        fy = y - iy
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        def h(a, b):
            n = a + b * 57
            n = (n << 13) ^ n
            return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0
        return (h(ix, iy) * (1-fx) + h(ix+1, iy) * fx) * (1-fy) + \
               (h(ix, iy+1) * (1-fx) + h(ix+1, iy+1) * fx) * fy

    def get_terrain_height(self, x, y):
        h = 18
        h += self.noise2d(x * 0.02, y * 0.02) * 6
        h += self.noise2d(x * 0.05, y * 0.05) * 3
        return max(3, min(int(h), self.WORLD_HEIGHT - 10))

    def get_tree_cell(self, x, y):
        return (x // self.tree_cell_size, y // self.tree_cell_size)

    def get_cactus_cell(self, x, y):
        return (x // self.cactus_cell_size, y // self.cactus_cell_size)

    def get_tree_height(self, x, y):
        v = self.noise2d(x * 0.5 + 1000, y * 0.5 + 1000)
        return 5 if v < 0.33 else (12 if v < 0.66 else 18)

    def get_cactus_height(self, x, y):
        return 2 if self.noise2d(x * 0.7 + 3000, y * 0.7 + 3000) < 0.5 else 3

    def generate_lake_for_chunk(self, cx, cy):
        import random as _rng
        CHUNK = self.CHUNK_SIZE
        seed = (self.noise_seed * 2654435761 + cx * 73856093 + cy * 19349663) & 0xFFFFFFFF
        rng = _rng.Random(seed)
        if rng.randint(0, 11) != 0:
            return
        mx = cx * CHUNK + CHUNK // 2
        my = cy * CHUNK + CHUNK // 2
        if self.noise2d(mx * 0.008, my * 0.008) > 0.4:
            return

        ox = cx * CHUNK + rng.randint(2, CHUNK - 3)
        oy = cy * CHUNK + rng.randint(2, CHUNK - 3)
        surface_z = self.get_terrain_height(ox, oy)
        raio_H = rng.randint(4, 16)
        raio_V = rng.randint(4, 12)
        SOLIDOS = {'grass', 'dirt', 'stone', 'sand'}

        candidatos = {}
        for dx in range(-raio_H, raio_H + 1):
            for dy in range(-raio_H, raio_H + 1):
                for dz in range(-raio_V, 1):
                    dist = (dx / raio_H) ** 2 + (dy / raio_H) ** 2 + (dz / raio_V) ** 2
                    if dist > 1.0:
                        continue
                    bx = ox + dx
                    by = oy + dy
                    bz = surface_z + dz
                    if not (0 < bx < self.WORLD_WIDTH - 1 and
                            0 < by < self.WORLD_DEPTH - 1 and
                            0 < bz < self.WORLD_HEIGHT - 1):
                        continue
                    if self.world_data.get((bx, by, bz)) not in SOLIDOS:
                        continue
                    candidatos[(bx, by, bz)] = 'air' if dz == 0 else 'water'

        if not candidatos or not any(v == 'water' for v in candidatos.values()):
            return

        for (bx, by, bz), tipo in candidatos.items():
            if tipo == 'air':
                if candidatos.get((bx, by, bz - 1)) == 'water':
                    self.world_data.pop((bx, by, bz), None)
            else:
                self.world_data[(bx, by, bz)] = 'water'

    def place_tree(self, x, y, surface_z):
        tree_height = self.get_tree_height(x, y)
        self.tree_cells.add(self.get_tree_cell(x, y))
        for z in range(surface_z + 1, surface_z + tree_height + 1):
            if z < self.WORLD_HEIGHT:
                self.world_data[(x, y, z)] = 'wood'
        leaf_start = surface_z + tree_height - 2
        leaf_end = surface_z + tree_height + 2

        def add_leaves(lz, radius, max_dist=None):
            for lx in range(-radius, radius + 1):
                for ly in range(-radius, radius + 1):
                    if max_dist is None or math.sqrt(lx*lx + ly*ly) <= max_dist:
                        pos = (x + lx, y + ly, lz)
                        if pos not in self.world_data and pos[2] < self.WORLD_HEIGHT:
                            self.world_data[pos] = 'leaves'

        if tree_height <= 5:
            for lz in range(leaf_start, leaf_end):
                for lx in range(-1, 2):
                    for ly in range(-1, 2):
                        if abs(lx) + abs(ly) <= 1 or lz == surface_z + tree_height + 1:
                            pos = (x + lx, y + ly, lz)
                            if pos not in self.world_data and pos[2] < self.WORLD_HEIGHT:
                                self.world_data[pos] = 'leaves'
        elif tree_height <= 12:
            for lz in range(leaf_start - 1, leaf_end):
                radius = 2 if lz < surface_z + tree_height else 1
                add_leaves(lz, radius, radius + 0.5)
        else:
            for lz in range(leaf_start - 2, leaf_end + 1):
                radius = 2 if lz >= surface_z + tree_height else (3 if lz >= surface_z + tree_height - 3 else 2)
                add_leaves(lz, radius, radius + 0.3)

    def place_cactus(self, x, y, surface_z):
        self.cactus_cells.add(self.get_cactus_cell(x, y))
        for z in range(surface_z + 1, surface_z + self.get_cactus_height(x, y) + 1):
            if z < self.WORLD_HEIGHT:
                self.world_data[(x, y, z)] = 'cactus'

    def _is_desert(self, x, y):
        height = self.get_terrain_height(x, y)
        return self.noise2d(x * 0.008, y * 0.008) > 0.4 and height < 22

    def generate_chunk(self, cx, cy):
        if (cx, cy) in self.chunks:
            return
        sx, sy = cx * self.CHUNK_SIZE, cy * self.CHUNK_SIZE
        for lx in range(self.CHUNK_SIZE):
            for ly in range(self.CHUNK_SIZE):
                x, y = sx + lx, sy + ly
                if x >= self.WORLD_WIDTH or y >= self.WORLD_DEPTH:
                    continue
                height = self.get_terrain_height(x, y)
                is_desert = self._is_desert(x, y)
                for z in range(height + 1):
                    if is_desert:
                        block = 'sand'
                    elif z == height:
                        block = 'grass'
                    elif z >= height - 3:
                        block = 'dirt'
                    else:
                        block = 'stone'
                    self.world_data[(x, y, z)] = block

    def generate_vegetation(self, cx, cy):
        sx, sy = cx * self.CHUNK_SIZE, cy * self.CHUNK_SIZE
        for lx in range(self.CHUNK_SIZE):
            for ly in range(self.CHUNK_SIZE):
                x, y = sx + lx, sy + ly
                if x >= self.WORLD_WIDTH or y >= self.WORLD_DEPTH:
                    continue
                height = self.get_terrain_height(x, y)
                surface_block = self.world_data.get((x, y, height))
                is_desert = self._is_desert(x, y)
                if surface_block == 'grass':
                    if x <= 5 or x >= self.WORLD_WIDTH - 5 or y <= 5 or y >= self.WORLD_DEPTH - 5:
                        continue
                    if self.get_tree_cell(x, y) in self.tree_cells:
                        continue
                    if self.noise2d(x * 0.15 + 500, y * 0.15 + 500) > 0.6:
                        self.place_tree(x, y, height)
                elif surface_block == 'sand' and is_desert:
                    if x <= 2 or x >= self.WORLD_WIDTH - 2 or y <= 2 or y >= self.WORLD_DEPTH - 2:
                        continue
                    if self.get_cactus_cell(x, y) in self.cactus_cells:
                        continue
                    if self.noise2d(x * 0.2 + 2500, y * 0.2 + 2500) > 0.7:
                        self.place_cactus(x, y, height)

    def create_chunk_mesh(self, cx, cy):
        if (cx, cy) in self.chunks:
            return
        sx, sy = cx * self.CHUNK_SIZE, cy * self.CHUNK_SIZE
        colors = {
            'grass': (0.2, 0.8, 0.2, 1.0), 'dirt': (0.6, 0.4, 0.2, 1.0),
            'stone': (0.5, 0.5, 0.5, 1.0), 'sand': (0.9, 0.85, 0.4, 1.0),
            'wood':  (0.4, 0.25, 0.1, 1.0), 'leaves': (0.15, 0.55, 0.15, 1.0),
            'cactus': (0.1, 0.35, 0.1, 1.0), 'water': (0.05, 0.15, 0.5, 1.0),
        }
        arr = GeomVertexArrayFormat()
        arr.addColumn(InternalName.make('vertex'), 3, Geom.NTFloat32, Geom.CPoint)
        arr.addColumn(InternalName.make('color'), 4, Geom.NTFloat32, Geom.CColor)
        fmt = GeomVertexFormat()
        fmt.addArray(arr)
        fmt = GeomVertexFormat.registerFormat(fmt)
        vdata = GeomVertexData('chunk', fmt, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        tris = GeomTriangles(Geom.UHStatic)
        vc = 0

        def quad(v0, v1, v2, v3, col):
            nonlocal vc
            r, g, b, a = col
            for v in (v0, v1, v2):
                vertex.addData3(*v); color.addData4(r, g, b, a)
            tris.addVertices(vc, vc+1, vc+2); vc += 3
            for v in (v0, v2, v3):
                vertex.addData3(*v); color.addData4(r, g, b, a)
            tris.addVertices(vc, vc+1, vc+2); vc += 3

        for lx in range(self.CHUNK_SIZE):
            for ly in range(self.CHUNK_SIZE):
                x, y = sx + lx, sy + ly
                if x >= self.WORLD_WIDTH or y >= self.WORLD_DEPTH:
                    continue
                for z in range(self.WORLD_HEIGHT):
                    if (x, y, z) not in self.world_data:
                        continue
                    bt = self.world_data[(x, y, z)]
                    is_wat = (bt == 'water')
                    adj = lambda nx, ny, nz: self.world_data.get((nx, ny, nz))
                    vis = (lambda nb: nb is None) if is_wat else (lambda nb: nb is None or nb == 'water')
                    col = colors.get(bt, colors['stone'])
                    if vis(adj(x, y, z+1)):
                        quad((x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1), col)
                    if z > 0 and vis(adj(x, y, z-1)):
                        quad((x+1,y,z),(x,y,z),(x,y+1,z),(x+1,y+1,z), col)
                    if vis(adj(x, y+1, z)):
                        quad((x,y+1,z),(x,y+1,z+1),(x+1,y+1,z+1),(x+1,y+1,z), col)
                    if vis(adj(x, y-1, z)):
                        quad((x+1,y,z),(x+1,y,z+1),(x,y,z+1),(x,y,z), col)
                    if vis(adj(x+1, y, z)):
                        quad((x+1,y,z),(x+1,y+1,z),(x+1,y+1,z+1),(x+1,y,z+1), col)
                    if vis(adj(x-1, y, z)):
                        quad((x,y+1,z),(x,y,z),(x,y,z+1),(x,y+1,z+1), col)

        if vc == 0:
            return
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode(f'chunk_{cx}_{cy}')
        node.addGeom(geom)
        np = self.render.attachNewNode(node)
        np.setTwoSided(True)
        np.node().setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))
        np.setTransparency(TransparencyAttrib.M_alpha)
        self.chunks[(cx, cy)] = np

    def preload_all_chunks(self):
        total_x = self.WORLD_WIDTH // self.CHUNK_SIZE
        total_y = self.WORLD_DEPTH // self.CHUNK_SIZE
        for cx in range(total_x):
            for cy in range(total_y):
                self.generate_chunk(cx, cy)
        for cx in range(total_x):
            for cy in range(total_y):
                self.generate_lake_for_chunk(cx, cy)
        for (x, y, z), bt in list(self.world_data.items()):
            if bt == 'dirt' and (x, y, z+1) not in self.world_data and not self._is_desert(x, y):
                self.world_data[(x, y, z)] = 'grass'
        for cx in range(total_x):
            for cy in range(total_y):
                self.generate_vegetation(cx, cy)
        px, py = int(self.player_pos.x), int(self.player_pos.y)
        ccx, ccy = px // self.CHUNK_SIZE, py // self.CHUNK_SIZE
        for dx in range(-self.RENDER_DISTANCE, self.RENDER_DISTANCE + 1):
            for dy in range(-self.RENDER_DISTANCE, self.RENDER_DISTANCE + 1):
                if dx*dx + dy*dy > self.RENDER_DISTANCE**2:
                    continue
                cx, cy = ccx + dx, ccy + dy
                if 0 <= cx < total_x and 0 <= cy < total_y:
                    self.create_chunk_mesh(cx, cy)
                    self.spawned_zombie_chunks.add((cx, cy))

    def generate_world_around_player(self):
        px, py = int(self.player_pos.x), int(self.player_pos.y)
        ccx, ccy = px // self.CHUNK_SIZE, py // self.CHUNK_SIZE
        total_x = self.WORLD_WIDTH // self.CHUNK_SIZE
        total_y = self.WORLD_DEPTH // self.CHUNK_SIZE
        for dx in range(-self.RENDER_DISTANCE, self.RENDER_DISTANCE + 1):
            for dy in range(-self.RENDER_DISTANCE, self.RENDER_DISTANCE + 1):
                if dx*dx + dy*dy > self.RENDER_DISTANCE**2:
                    continue
                cx, cy = ccx + dx, ccy + dy
                if 0 <= cx < total_x and 0 <= cy < total_y:
                    self.create_chunk_mesh(cx, cy)
                    self.spawn_zombies_for_chunk(cx, cy)

    def unload_distant_chunks(self):
        px, py = int(self.player_pos.x), int(self.player_pos.y)
        ccx, ccy = px // self.CHUNK_SIZE, py // self.CHUNK_SIZE
        to_remove = [(cx, cy) for (cx, cy) in self.chunks
                     if (cx-ccx)**2 + (cy-ccy)**2 > (self.RENDER_DISTANCE + 1)**2]
        for k in to_remove:
            self.chunks[k].removeNode()
            del self.chunks[k]

    def update_chunks(self):
        px, py = int(self.player_pos.x), int(self.player_pos.y)
        cx, cy = px // self.CHUNK_SIZE, py // self.CHUNK_SIZE
        if (cx, cy) != self.last_chunk_pos:
            self.last_chunk_pos = (cx, cy)
            self.generate_world_around_player()
            self.unload_distant_chunks()

    def is_liquid(self, block_type):
        return block_type == 'water'

    def is_block_solid(self, x, y, z):
        bt = self.world_data.get((int(x), int(y), int(z)))
        return bt is not None and not self.is_liquid(bt)

    def get_camera_safe_position(self, cam_x, cam_y, cam_z):
        margin = self.camera_margin
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    bx, by, bz = int(cam_x)+dx, int(cam_y)+dy, int(cam_z)+dz
                    if (bx, by, bz) in self.world_data:
                        dir_x = cam_x - (bx + 0.5)
                        dir_y = cam_y - (by + 0.5)
                        dir_z = cam_z - (bz + 0.5)
                        ax, ay, az = abs(dir_x), abs(dir_y), abs(dir_z)
                        if ax >= ay and ax >= az:
                            cam_x = bx + 1.0 + margin if dir_x > 0 else bx - margin
                        elif ay >= ax and ay >= az:
                            cam_y = by + 1.0 + margin if dir_y > 0 else by - margin
                        else:
                            cam_z = bz + 1.0 + margin if dir_z > 0 else bz - margin
        return cam_x, cam_y, cam_z

    def update(self, task):
        if self.game_paused:
            return Task.cont
        dt = min(globalClock.getDt(), 0.1)

        if self.mouseWatcherNode and self.mouseWatcherNode.hasMouse():
            m = self.mouseWatcherNode.getMouse()
            self.player_h -= m.x * self.mouse_sensitivity * 100
            self.player_p = max(-89, min(89, self.player_p + m.y * self.mouse_sensitivity * 100))
            try:
                props = self.win.getProperties()
                self.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2)
            except Exception:
                pass

        self.camera.setHpr(self.player_h, self.player_p, 0)
        rad = math.radians(self.player_h)
        fx, fy = -math.sin(rad), math.cos(rad)
        rx, ry =  math.cos(rad), math.sin(rad)

        dx = dy = 0.0
        if self.keys['w']: dx += fx; dy += fy
        if self.keys['s']: dx -= fx; dy -= fy
        if self.keys['d']: dx += rx; dy += ry
        if self.keys['a']: dx -= rx; dy -= ry

        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = (dx / length) * self.move_speed * dt
            dy = (dy / length) * self.move_speed * dt

        px, py, pz = self.player_pos.x, self.player_pos.y, self.player_pos.z
        feet_z = pz - self.player_height
        new_x, new_y = px + dx, py + dy

        kb = self.player_knockback_vel
        if kb.length() > 0.01:
            new_x += kb.x * dt
            new_y += kb.y * dt
            self.player_knockback_vel *= max(0.0, 1.0 - dt * 8)
        else:
            self.player_knockback_vel = LVector3f(0, 0, 0)

        collision_x = collision_y = False
        for offset in (0.2, 0.6, 1.0, 1.4):
            check_z = int(feet_z + offset)
            if self.is_block_solid(new_x, py, check_z): collision_x = True
            if self.is_block_solid(px, new_y, check_z): collision_y = True

        if not collision_x: self.player_pos.x = new_x
        if not collision_y: self.player_pos.y = new_y
        self.player_pos.x = max(1, min(self.WORLD_WIDTH - 1, self.player_pos.x))
        self.player_pos.y = max(1, min(self.WORLD_DEPTH - 1, self.player_pos.y))

        px, py, pz = self.player_pos.x, self.player_pos.y, self.player_pos.z
        feet_z = pz - self.player_height

        def in_liquid(x, y, z):
            return self.world_data.get((int(x), int(y), int(z))) == 'water'

        submerged = in_liquid(px, py, int(feet_z)) or in_liquid(px, py, int(pz))

        ground_below = 0
        for z in range(int(feet_z), -1, -1):
            if self.is_block_solid(px, py, z):
                ground_below = z + 1
                break

        self.is_on_ground = abs(feet_z - ground_below) < 0.05

        if submerged:
            if self.keys['space']:
                water_surface = int(pz)
                for z in range(int(pz) + 1, self.WORLD_HEIGHT):
                    if self.world_data.get((int(px), int(py), z)) != 'water':
                        water_surface = z
                        break
                target_z = water_surface + self.player_height * 0.5
                self.vertical_velocity = self.jump_velocity * 0.6 if pz < target_z else 0
            else:
                self.vertical_velocity += self.gravity * 0.15 * dt
                self.vertical_velocity = max(-3.0, min(self.vertical_velocity, 3.0))
        else:
            if self.keys['space'] and self.is_on_ground:
                self.vertical_velocity = self.jump_velocity
                self.is_on_ground = False
            if self.keys['shift']:
                self.vertical_velocity = -self.jump_velocity
            if not self.is_on_ground:
                self.vertical_velocity = max(-50, self.vertical_velocity + self.gravity * dt)
            else:
                self.vertical_velocity = 0

        new_z = pz + self.vertical_velocity * dt
        new_feet_z = new_z - self.player_height
        new_ground = 0
        for z in range(int(new_feet_z), -1, -1):
            if self.is_block_solid(px, py, z):
                new_ground = z + 1
                break
        if new_feet_z < new_ground:
            fall_damage = max(0, int((-self.vertical_velocity - 15) / 5))
            new_z = new_ground + self.player_height
            self.vertical_velocity = 0
            self.is_on_ground = True
            if fall_damage > 0:
                self.take_damage(fall_damage)

        if self.invincibility_timer > 0:
            self.invincibility_timer = max(0.0, self.invincibility_timer - dt)

        if self.swing_timer > 0:
            self.swing_timer = max(0.0, self.swing_timer - dt)
            if self.swing_timer == 0.0:
                self.update_hand_display(swinging=False)

        touching_cactus = any(
            self.world_data.get((int(px) + dx, int(py) + dy, int(feet_z) + dz)) == 'cactus'
            for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (0, 1)
        )
        if touching_cactus:
            self.cactus_damage_tick += dt
            if self.cactus_damage_tick >= 1.0:
                self.cactus_damage_tick -= 1.0
                self.take_damage(1)
        else:
            self.cactus_damage_tick = 0.0

        if submerged:
            self.underwater_overlay.show()
            self.oxygen_bar_frame.show()
            self.oxygen_drain_tick += dt
            if self.oxygen_drain_tick >= 1.0:
                self.oxygen_drain_tick -= 1.0
                if self.oxygen > 0:
                    self.oxygen -= 1
                    self.update_oxygen_bar()
                else:
                    self.oxygen_damage_tick += 1.0
            if self.oxygen == 0:
                self.oxygen_damage_tick += dt
                if self.oxygen_damage_tick >= 1.0:
                    self.oxygen_damage_tick -= 1.0
                    self.take_damage(1)
        else:
            if self.oxygen < self.max_oxygen:
                self.oxygen_tick += dt
                if self.oxygen_tick >= 0.5:
                    self.oxygen_tick -= 0.5
                    self.oxygen = min(self.max_oxygen, self.oxygen + 1)
                    self.update_oxygen_bar()
            if self.oxygen == self.max_oxygen:
                self.oxygen_bar_frame.hide()
            self.oxygen_drain_tick = 0.0
            self.oxygen_damage_tick = 0.0
            self.underwater_overlay.hide()

        if self.health < self.max_health:
            if self.regen_cooldown > 0:
                self.regen_cooldown = max(0.0, self.regen_cooldown - dt)
            else:
                self.regen_tick += dt
                if self.regen_tick >= 1.0:
                    self.regen_tick -= 1.0
                    self.health = min(self.max_health, self.health + 1)
                    self.update_health_bar()

        self.player_pos.z = max(self.player_height, min(new_z, self.WORLD_HEIGHT + 10))
        safe_x, safe_y, safe_z = self.get_camera_safe_position(
            self.player_pos.x, self.player_pos.y, self.player_pos.z)
        self.camera.setPos(safe_x, safe_y, safe_z)
        self.update_zombies(dt, px, py, pz)
        self.update_chunks()
        return Task.cont


if __name__ == "__main__":
    game = VoxelGame()
    game.run()
