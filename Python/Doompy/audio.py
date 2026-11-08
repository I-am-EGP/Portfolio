import wave
import struct
import math
import random
import os
import sys
import builtins


# ---------------------------------------------------------------------------
# Geração procedural dos WAVs
# ---------------------------------------------------------------------------

def _write_wav(path, samples, rate=44100):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    data = bytearray()
    for s in samples:
        v = int(round(s * 32767.0))
        if v > 32767:
            v = 32767
        elif v < -32768:
            v = -32768
        data += struct.pack('<h', v)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(data))


def _tone(freq_fn, dur, env_fn=None, wave_type='sine', rate=44100, noise=0.0):
    n = int(rate * dur)
    samples = []
    phase = 0.0
    inv_rate = 1.0 / rate
    two_pi = 2.0 * math.pi
    for i in range(n):
        t = i * inv_rate
        f = freq_fn(t)
        phase += two_pi * f * inv_rate
        if wave_type == 'sine':
            val = math.sin(phase)
        elif wave_type == 'square':
            val = 1.0 if math.sin(phase) >= 0 else -1.0
        elif wave_type == 'saw':
            val = 2.0 * ((phase / two_pi) % 1.0) - 1.0
        else:
            val = math.sin(phase)
        if noise > 0:
            val = val * (1 - noise) + random.uniform(-1, 1) * noise
        if env_fn is not None:
            val *= env_fn(t)
        samples.append(val)
    return samples


def _env_exp(decay):
    return lambda t: math.exp(-t * decay)


def _gen_shoot():
    return _tone(lambda t: 90, 0.25, env_fn=_env_exp(9), wave_type='sine', noise=0.6)


def _gen_hit():
    return _tone(lambda t: 220, 0.08, env_fn=_env_exp(20), wave_type='square')


def _gen_death():
    return _tone(lambda t: 300 - 240 * (t / 0.4), 0.4, env_fn=_env_exp(4), wave_type='saw')


def _gen_hurt():
    return _tone(lambda t: 180 - 100 * (t / 0.2), 0.2, env_fn=_env_exp(6), wave_type='square')


def _gen_victory():
    notes = [523, 659, 784, 1047]
    seg = 0.15

    def f(t):
        idx = int(t / seg)
        if idx >= len(notes):
            idx = len(notes) - 1
        return notes[idx]

    return _tone(f, 0.6, env_fn=_env_exp(2.5), wave_type='sine')


def _gen_gameover():
    return _tone(lambda t: 400 - 350 * (t / 0.6), 0.6, env_fn=_env_exp(2.5), wave_type='saw')


def _sounds_dir():
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "assets", "sounds")


# ---------------------------------------------------------------------------
# Checagens do Panda3D
# ---------------------------------------------------------------------------

def _panda_base():
    return getattr(builtins, "base", None)


def _panda_loader_ready():
    b = _panda_base()
    return b is not None and getattr(b, "loader", None) is not None


def _panda_has_sfx_manager():
    b = _panda_base()
    if b is None:
        return False
    try:
        return bool(b.sfxManagerList)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# AudioManager
# ---------------------------------------------------------------------------

class AudioManager:
    GENERATORS = {
        "shoot": _gen_shoot,
        "hit": _gen_hit,
        "death": _gen_death,
        "hurt": _gen_hurt,
        "victory": _gen_victory,
        "gameover": _gen_gameover,
    }

    def __init__(self):
        self.sounds = {}          # name -> AudioSound do Panda3D
        self.sfx_volume = 0.7
        self._loaded = False
        self._failed = False

    # ------------------------------------------------------------------
    def init(self):
        """Deve ser chamado APÓS 'app = Ursina()'."""
        if self._loaded or self._failed:
            return
        if not _panda_loader_ready():
            return  # ainda sem ShowBase; play() tentará de novo depois

        if not _panda_has_sfx_manager():
            self._report_no_audio_backend()
            self._failed = True
            return

        sounds_dir = _sounds_dir()
        try:
            os.makedirs(sounds_dir, exist_ok=True)
        except Exception as e:
            print(f"[audio] erro criando '{sounds_dir}': {e}")
            self._failed = True
            return

        base = _panda_base()
        loaded = 0

        for name, gen in self.GENERATORS.items():
            path = os.path.join(sounds_dir, f"{name}.wav")

            if not self._file_is_valid_wav(path):
                try:
                    _write_wav(path, gen())
                except Exception as e:
                    print(f"[audio] falha gerando '{name}': {e}")
                    continue

            clip = self._load_clip(base, path)
            if clip is None:
                continue

            try:
                clip.setVolume(self.sfx_volume)
            except Exception:
                pass
            try:
                clip.setLoop(False)
            except Exception:
                pass

            self.sounds[name] = clip
            loaded += 1

        if loaded == 0:
            print("[audio] Nenhum som carregado — áudio indisponível.")
            self._failed = True
            return

        self._loaded = True
        print(f"[audio] {loaded}/{len(self.GENERATORS)} sons carregados: "
              f"{sorted(self.sounds.keys())}")

    # ------------------------------------------------------------------
    @staticmethod
    def _file_is_valid_wav(path):
        if not os.path.exists(path):
            return False
        try:
            if os.path.getsize(path) <= 44:
                return False
            with wave.open(path, 'rb') as w:
                if w.getnchannels() != 1:
                    return False
                if w.getsampwidth() != 2:
                    return False
                if w.getnframes() <= 0:
                    return False
            return True
        except Exception:
            return False

    @staticmethod
    def _load_clip(base, path):
        # 1) caminho direto
        try:
            clip = base.loader.loadSfx(path)
            if clip is not None:
                return clip
        except Exception as e:
            print(f"[audio] loadSfx('{path}') erro: {e}")

        # 2) via Filename (algumas builds exigem)
        try:
            from panda3d.core import Filename
            fn = Filename.fromOsSpecific(os.path.abspath(path))
            clip = base.loader.loadSfx(fn)
            if clip is not None:
                return clip
        except Exception as e:
            print(f"[audio] loadSfx(Filename) erro em '{path}': {e}")

        # 3) via Audio() do Ursina (última tentativa)
        try:
            from ursina import Audio
            a = Audio(path, loop=False, autoplay=False)
            clip = getattr(a, "clip", None)
            if clip is not None:
                return clip
        except Exception as e:
            print(f"[audio] Audio('{path}') erro: {e}")

        print(f"[audio] não foi possível carregar '{os.path.basename(path)}'")
        return None

    # ------------------------------------------------------------------
    def play(self, name):
        if not self._loaded and not self._failed:
            self.init()
        clip = self.sounds.get(name)
        if clip is None:
            return
        try:
            clip.play()
        except Exception as e:
            print(f"[audio] play('{name}') falhou: {e}")

    def set_volume(self, v):
        self.sfx_volume = v
        for clip in self.sounds.values():
            try:
                clip.setVolume(v)
            except Exception:
                pass

    # ------------------------------------------------------------------
    @staticmethod
    def _report_no_audio_backend():
        print()
        print("=" * 64)
        print(" [audio] Panda3D NÃO tem nenhum backend de áudio ativo.")
        print("         (base.sfxManagerList está vazio)")
        print()
        print(" No Arch Linux / KDE Plasma:")
        print("     sudo pacman -S openal")
        print()
        print(" Se usa PipeWire, garanta também:")
        print("     sudo pacman -S pipewire-pulse pipewire-alsa")
        print()
        print(" Verifique se a lib está visível:")
        print("     ldconfig -p | grep -i openal")
        print()
        print(" Teste rápido (lista deve ser não vazia):")
        print("     python -c \"from ursina import *; Ursina(); "
              "from builtins import base; print(base.sfxManagerList)\"")
        print("=" * 64)
        print()


audio = AudioManager()