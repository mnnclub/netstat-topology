# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['netstat_dev_v0.0.4.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='netstat_dev_v0.0.4',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['png/DALLE_hhji_20240408_Create_a_detailed_illustration_of_a_fully_connected.webp'],
)
app = BUNDLE(
    exe,
    name='netstat_dev_v0.0.4.app',
    icon='./png/DALLE_hhji_20240408_Create_a_detailed_illustration_of_a_fully_connected.webp',
    bundle_identifier=None,
)
