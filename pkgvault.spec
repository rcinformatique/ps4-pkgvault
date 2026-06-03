# -*- mode: python ; coding: utf-8 -*-
# PKGVault — fichier de configuration PyInstaller
# Pour recompiler : pyinstaller pkgvault.spec

from pathlib import Path

block_cipher = None

# ------------------------------------------------------------------ #
#  Données à embarquer (fichiers non-Python)                          #
# ------------------------------------------------------------------ #

added_files = [
    # Templates Jinja2
    ("templates",           "templates"),

    # Font Awesome (CSS + webfonts)
    ("assets/fontawesome",  "assets/fontawesome"),

    # Icônes de l'application
    ("assets/icons",        "assets/icons"),
]

# ------------------------------------------------------------------ #
#  Analyse                                                             #
# ------------------------------------------------------------------ #

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebChannel",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "jinja2",
        "markupsafe",
        "PIL",
        "requests",
        "sqlite3",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "unittest",
        "pydoc",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ------------------------------------------------------------------ #
#  Archive Python                                                      #
# ------------------------------------------------------------------ #

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# ------------------------------------------------------------------ #
#  Exécutable                                                          #
# ------------------------------------------------------------------ #

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PS4PKGVault",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # ← False = pas de console noire
                            #   True  = console visible (utile pour déboguer)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # ← Remplacer par "assets/icons/app.ico" quand dispo
)

# ------------------------------------------------------------------ #
#  Dossier de distribution                                             #
# ------------------------------------------------------------------ #

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PS4PKGVault",
)
