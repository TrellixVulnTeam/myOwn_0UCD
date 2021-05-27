# -*- mode: python -*-

from kivy_deps import sdl2, glew
import sys

app_name = 'client_app'
# sys.path += [""]

# block_cipher = pyi_crypto.PyiBlockCipher(key='1234567890')
block_cipher = None

a = Analysis(['main.py'],
  pathex=['C:\\projects\\myOwn\\client_app'],
  binaries=None,
  datas=None,

  hiddenimports=[],

  hookspath=[],
  runtime_hooks=[],
  excludes=[],
  win_no_prefer_redirects=False,
  win_private_assemblies=False,
  cipher=block_cipher)

# exclusion list
from os.path import join
from fnmatch import fnmatch
exclusion_patterns = (
  join("kivy_install", "data", "images", "testpattern.png"),
  join("kivy_install", "data", "images", "image-loading.gif"),
  join("kivy_install", "data", "keyboards*"),
  join("kivy_install", "data", "settings_kivy.json"),
  join("kivy_install", "data", "logo*"),
  join("kivy_install", "data", "fonts", "DejaVuSans*"),
  join("kivy_install", "modules*"),
  join("Include*"),
  join("sdl2-config"),

  # Filter app directory
  join(".idea*"),
)

def can_exclude(fn):
    for pat in exclusion_patterns:
        if fnmatch(fn, pat):
            return True

a.datas = [x for x in a.datas if not can_exclude(x[0])]
a.binaries = [x for x in a.binaries if not can_exclude(x[0])]
# Filter app directory
appfolder = [x for x in Tree('C:\\projects\\myOwn\\client_app', excludes=['*.py','*.pyc']) if not can_exclude(x[0])]  

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
  a.scripts,
  appfolder,
  a.binaries,
  a.zipfiles,
  a.datas,
  *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins )],
  name='client_app',
  debug=False,
  strip=False,
  upx=True,
  console=False)