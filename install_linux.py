"""Install this checkout for the current user; preserve legacy launcher compatibility."""
import argparse
import ast
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from datetime import datetime

APP_ID = 'io.github.DjaboDev.LinuxPaint'
ROOT = Path(__file__).resolve().parent

def install():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prefix', type=Path, default=Path.home()/'.local')
    parser.add_argument('--skip-desktop-cache', action='store_true')
    args=parser.parse_args()
    prefix=args.prefix.resolve()
    dest=prefix/'share'/'LinuxPaint'
    if dest==ROOT: raise SystemExit('Choose an installation directory other than the source checkout.')
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/'classic_paint',dest/'classic_paint',dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(ROOT/'paint.py',dest/'paint.py')
    bindir=prefix/'bin';bindir.mkdir(parents=True,exist_ok=True)
    command=f'exec {shlex.quote(sys.executable)} {shlex.quote(str(dest/"paint.py"))} "$@"'
    for name in ('linux-paint','classic-paint'):
        wrapper=bindir/name
        wrapper.write_text('#!/bin/sh\n'+command+'\n');wrapper.chmod(0o755)
    applications=prefix/'share'/'applications';applications.mkdir(parents=True,exist_ok=True)
    text=(ROOT/'linux'/f'{APP_ID}.desktop').read_text()
    text=text.replace('Exec=linux-paint %f','Exec='+ '"'+str(bindir/'linux-paint')+'" %f')
    (applications/f'{APP_ID}.desktop').write_text(text)
    legacy=applications/'classic-paint.desktop'
    if legacy.exists():
        backup=dest/'launcher-backups';backup.mkdir(exist_ok=True)
        shutil.copy2(legacy,backup/(datetime.now().strftime('%Y%m%d-%H%M%S')+'-classic-paint.desktop'))
        legacy.write_text(text+'NoDisplay=true\n')
    icons=prefix/'share'/'icons'/'hicolor'/'256x256'/'apps';icons.mkdir(parents=True,exist_ok=True)
    from PySide6.QtGui import QImage
    from PySide6.QtCore import Qt
    im=QImage(str(ROOT/'classic_paint'/'assets'/'linux-paint.png'))
    if im.isNull(): raise SystemExit('Missing application icon')
    im.scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation).save(str(icons/f'{APP_ID}.png'))
    if not args.skip_desktop_cache:
        for exe,cmd in [('update-desktop-database',[str(applications)]),('gtk-update-icon-cache',['-f','-t',str(prefix/'share'/'icons'/'hicolor')])]:
            if shutil.which(exe): subprocess.run([exe]+cmd,check=False)
        # A pinned legacy launcher must point to the same desktop ID as Qt/Wayland.
        if shutil.which('gsettings'):
            result=subprocess.run(['gsettings','get','org.gnome.shell','favorite-apps'],capture_output=True,text=True)
            if result.returncode==0:
                try: favorites=ast.literal_eval(result.stdout.strip())
                except (ValueError,SyntaxError): favorites=[]
                updated=[f'{APP_ID}.desktop' if f=='classic-paint.desktop' else f for f in favorites]
                updated=list(dict.fromkeys(updated))
                if updated!=favorites:
                    subprocess.run(['gsettings','set','org.gnome.shell','favorite-apps',repr(updated)],check=True)
    print(f'Installed Linux Paint: {dest}\nLauncher: {applications/ (APP_ID+".desktop")}')

if __name__=='__main__': install()
