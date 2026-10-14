"""Package the verified PyInstaller onedir build as a type-2 AppImage."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request

TOOLS = {
    'appimagetool': ('https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage',
                    '95cbe7cce9717fce90c484e34052ee7c7f1d7635b33c12525b4776826a7d29b6'),
    'runtime': ('https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-x86_64',
                '156f4bdbde9c52d01814600013e0a273f0118dc2de98975f3c8c63427ec79074'),
}

def verified_tool(name,folder):
    url,expected=TOOLS[name];path=folder/name
    if path.exists():
        with path.open('rb') as stream:
            if hashlib.file_digest(stream,'sha256').hexdigest()==expected:return path
    request=urllib.request.Request(url,headers={'User-Agent':'LinuxPaint-build'})
    temp=path.with_suffix('.download')
    try:
        with urllib.request.urlopen(request,timeout=120) as response,temp.open('wb') as stream:shutil.copyfileobj(response,stream)
        with temp.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=expected:raise RuntimeError(f'{name}: download checksum mismatch; update the pinned official asset after review.')
        temp.replace(path);path.chmod(0o755)
    finally:temp.unlink(missing_ok=True)
    return path

def make_appimage(root,folder,releases,label):
    work=root/'build'/'appimage';work.mkdir(parents=True,exist_ok=True)
    appdir=work/'LinuxPaint.AppDir'
    if appdir.exists():shutil.rmtree(appdir)
    shutil.copytree(folder,appdir/'usr'/'bin',symlinks=True)
    desktop=(root/'linux'/'io.github.DjaboDev.LinuxPaint.desktop').read_text().replace('Exec=linux-paint %f','Exec=LinuxPaint %f')
    (appdir/'io.github.DjaboDev.LinuxPaint.desktop').write_text(desktop)
    shutil.copy2(folder/'linux-paint.png',appdir/'io.github.DjaboDev.LinuxPaint.png')
    (appdir/'.DirIcon').symlink_to('io.github.DjaboDev.LinuxPaint.png')
    launcher=appdir/'AppRun'
    launcher.write_text('#!/bin/sh\nset -eu\napp_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec "$app_dir/usr/bin/LinuxPaint" "$@"\n')
    launcher.chmod(0o755)
    tool=verified_tool('appimagetool',work);runtime=verified_tool('runtime',work)
    destination=releases/(label+'.AppImage')
    env=os.environ.copy();env['ARCH']='x86_64';env['APPIMAGE_EXTRACT_AND_RUN']='1'
    subprocess.run([str(tool),'--runtime-file',str(runtime),'--no-appstream',str(appdir),str(destination)],cwd=work,env=env,check=True)
    destination.chmod(0o755)
    env['QT_QPA_PLATFORM']='offscreen'
    subprocess.run([str(destination),'--self-test'],cwd=work,env=env,check=True)
    with destination.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    destination.with_name(destination.name+'.sha256').write_text(f'{digest}  {destination.name}\n')
    return destination
