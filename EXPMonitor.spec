# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['exp_monitor_qt.py'],
    pathex=[],
    binaries=[],
    datas=[('exp_monitor.py', '.'), ('exp_template_ocr.py', '.'), ('templates', 'templates')],
    hiddenimports=['win32gui', 'win32con', 'win32ui', 'win32api', 'pywintypes', 'mss', 'mss.windows', 'pyqtgraph', 'numpy', 'cv2', 'pytesseract'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['easyocr', 'torch', 'torchvision', 'matplotlib', 'tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EXPMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EXPMonitor',
)
