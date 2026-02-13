# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("tools")

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[("config.json", ".")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AutomationHub",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

# ----- macOS build (.app) -----
if sys.platform == "darwin":

    app = BUNDLE(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        name="AutomationHub.app",
        icon=None,
        bundle_identifier=None,
    )

    coll = COLLECT(
        exe,   # ← importante: exe también acá
        app,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name="AutomationHub",
    )

# ----- Windows/Linux build -----
else:

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name="AutomationHub",
    )
