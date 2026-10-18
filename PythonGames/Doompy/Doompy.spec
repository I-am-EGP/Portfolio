# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Coleta os dados e submódulos do Panda3D e da Ursina automaticamente.
# Isso resolve a maioria dos erros de "módulo não encontrado" e "arquivo não encontrado".
panda3d_datas = collect_data_files('panda3d')
panda3d_hiddenimports = collect_submodules('panda3d')
ursina_datas = collect_data_files('ursina')
ursina_hiddenimports = collect_submodules('ursina')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # Copia a pasta 'assets' inteira para dentro do exe
        *panda3d_datas,
        *ursina_datas,
    ],
    hiddenimports=[
        *panda3d_hiddenimports,
        *ursina_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Doompy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Mude para True se quiser ver logs de erro no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
