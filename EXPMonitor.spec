# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import (
    collect_all,
    collect_data_files,
    copy_metadata,
)


extra_datas = [('exp_monitor.py', '.')]
extra_binaries = []
extra_hiddenimports = [
    'win32gui', 'win32con', 'win32ui', 'win32api', 'pywintypes',
    'mss', 'mss.windows', 'pyqtgraph', 'numpy', 'cv2',
]

for package_name in (
    'paddleocr',
    'paddle',
    'skimage',
    'pyclipper',
    'lmdb',
    'rapidfuzz',
    'albumentations',
    'albucore',
):
    datas, binaries, hiddenimports = collect_all(package_name, include_py_files=True)
    extra_datas += datas
    extra_binaries += binaries
    extra_hiddenimports += hiddenimports

extra_datas += collect_data_files('Cython', include_py_files=False)

for package_name in (
    'paddleocr',
    'paddlepaddle',
    'scikit-image',
    'pyclipper',
    'lmdb',
    'rapidfuzz',
    'albumentations',
    'albucore',
):
    extra_datas += copy_metadata(package_name)


a = Analysis(
    ['exp_monitor_qt.py'],
    pathex=[],
    binaries=extra_binaries,
    datas=extra_datas,
    hiddenimports=extra_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'torchvision', 'matplotlib', 'tkinter', 'apted'],
    noarchive=False,
    module_collection_mode={
        'paddleocr': 'py',
        'paddleocr.ppocr': 'py',
        'paddleocr.ppstructure': 'py',
        'paddleocr.tools': 'py',
    },
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
