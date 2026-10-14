"""Build Linux installers from the same tested standalone executable."""
import hashlib
from pathlib import Path
import os
import shutil
import subprocess
import tarfile
from classic_paint import __version__

APP_ID='io.github.DjaboDev.LinuxPaint'

def run(*args,env=None):
    subprocess.run([str(a) for a in args],check=True,env=env)

def checksum(path):
    with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    path.with_name(path.name+'.sha256').write_text(f'{digest}  {path.name}\n')

def tree(root,folder):
    stage=root/'build'/'linux-installers'
    if stage.exists():shutil.rmtree(stage)
    stage.mkdir(parents=True)
    shutil.copytree(folder,stage/'opt'/'linux-paint',symlinks=True)
    executable=stage/'usr'/'bin'/'linux-paint';executable.parent.mkdir(parents=True)
    executable.write_text('#!/bin/sh\nexec /opt/linux-paint/LinuxPaint "$@"\n');executable.chmod(0o755)
    desktop=stage/'usr'/'share'/'applications'/f'{APP_ID}.desktop';desktop.parent.mkdir(parents=True)
    shutil.copy2(root/'linux'/f'{APP_ID}.desktop',desktop)
    icon=stage/'usr'/'share'/'icons'/'hicolor'/'256x256'/'apps'/f'{APP_ID}.png';icon.parent.mkdir(parents=True)
    shutil.copy2(folder/'linux-paint.png',icon)
    meta=stage/'usr'/'share'/'metainfo';meta.mkdir(parents=True)
    shutil.copy2(root/'linux'/f'{APP_ID}.metainfo.xml',meta/f'{APP_ID}.metainfo.xml')
    docs=stage/'usr'/'share'/'doc'/'linux-paint';docs.mkdir(parents=True)
    shutil.copy2(root/'LICENSE',docs/'copyright')
    shutil.copy2(root/'THIRD_PARTY_NOTICES.md',docs/'THIRD_PARTY_NOTICES.md')
    return stage

def native_packages(root,folder,releases,label):
    stage=tree(root,folder);control=stage/'DEBIAN';control.mkdir()
    (control/'control').write_text(f"""Package: linux-paint
Version: {__version__}
Section: graphics
Priority: optional
Architecture: amd64
Maintainer: DjaboDev <djabo@users.noreply.github.com>
Installed-Size: {sum(p.stat().st_size for p in stage.rglob('*') if p.is_file())//1024}
Depends: libc6 (>= 2.35), libgl1, libegl1, libxkbcommon0, libxcb-cursor0, libdbus-1-3, libfontconfig1
Description: Editor de imagens com ribbon e remocao local de fundo
 Linux Paint inclui lapis, pinceis, formas, selecao e recorte inteligente.
""")
    deb=releases/(label+'.deb');run('dpkg-deb','--build','--root-owner-group',stage,deb)
    shutil.rmtree(control)
    top=root/'build'/'rpm'
    if top.exists():shutil.rmtree(top)
    for name in ('BUILD','BUILDROOT','RPMS','SOURCES','SPECS','SRPMS'):(top/name).mkdir(parents=True)
    with tarfile.open(top/'SOURCES'/'payload.tar.gz','w:gz') as archive:archive.add(stage,arcname='payload')
    spec=top/'SPECS'/'linux-paint.spec'
    spec.write_text(f"""%global __strip /bin/true
%global debug_package %{{nil}}
Name: linux-paint
Version: {__version__}
Release: 1
Summary: Image editor with ribbon and local background removal
License: MIT
URL: https://github.com/DjaboDev/Linux-Paint
Source0: payload.tar.gz
BuildArch: x86_64
AutoReqProv: no
Requires: glibc >= 2.35, libGL.so.1()(64bit), libEGL.so.1()(64bit), libxkbcommon.so.0()(64bit), libxcb-cursor.so.0()(64bit), libdbus-1.so.3()(64bit), libfontconfig.so.1()(64bit)
%description
Linux Paint includes drawing tools, shapes, selection and local AI cutout.
%prep
%setup -q -n payload
%build
%install
mkdir -p %{{buildroot}}
cp -a . %{{buildroot}}/
%files
/opt/linux-paint
/usr/bin/linux-paint
/usr/share/applications/{APP_ID}.desktop
/usr/share/icons/hicolor/256x256/apps/{APP_ID}.png
/usr/share/doc/linux-paint
/usr/share/metainfo/{APP_ID}.metainfo.xml
""")
    run('rpmbuild','-bb','--define',f'_topdir {top}',spec)
    rpm=releases/(label+'.rpm');shutil.copy2(next((top/'RPMS').rglob('*.rpm')),rpm)
    env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen'
    for package in (deb,rpm):
        dest=root/'build'/('verify-'+package.suffix[1:])
        if dest.exists():shutil.rmtree(dest)
        dest.mkdir()
        if package.suffix=='.deb':run('dpkg-deb','-x',package,dest)
        else:
            with subprocess.Popen(['rpm2cpio',str(package)],stdout=subprocess.PIPE) as archive:
                subprocess.run(['cpio','-idmu','--quiet'],stdin=archive.stdout,cwd=dest,check=True)
                archive.stdout.close()
                if archive.wait():raise RuntimeError('RPM extraction failed')
        run(dest/'opt'/'linux-paint'/'LinuxPaint','--self-test',env=env)
        checksum(package)
    return deb,rpm

def flatpak_package(root,folder,releases,label):
    work=root/'build'/'flatpak';work.mkdir(parents=True,exist_ok=True)
    stage=work/'app'
    if stage.exists():shutil.rmtree(stage)
    run('flatpak','build-init',stage,APP_ID,'org.freedesktop.Sdk','org.freedesktop.Platform','25.08')
    files=stage/'files'
    shutil.copytree(folder,files/'lib'/'LinuxPaint',symlinks=True)
    launcher=files/'bin'/'linux-paint';launcher.parent.mkdir(parents=True)
    launcher.write_text('#!/bin/sh\nexec /app/lib/LinuxPaint/LinuxPaint "$@"\n');launcher.chmod(0o755)
    desktop=files/'share'/'applications'/f'{APP_ID}.desktop';desktop.parent.mkdir(parents=True)
    shutil.copy2(root/'linux'/f'{APP_ID}.desktop',desktop)
    icon=files/'share'/'icons'/'hicolor'/'256x256'/'apps'/f'{APP_ID}.png';icon.parent.mkdir(parents=True)
    shutil.copy2(folder/'linux-paint.png',icon)
    meta=files/'share'/'metainfo';meta.mkdir(parents=True)
    shutil.copy2(root/'linux'/f'{APP_ID}.metainfo.xml',meta/f'{APP_ID}.metainfo.xml')
    run('flatpak','build-finish',stage,'--command=linux-paint','--share=ipc','--share=network','--socket=wayland','--socket=fallback-x11','--device=dri','--filesystem=home')
    repo=work/'repo';run('flatpak','build-export',repo,stage,'stable')
    package=releases/(label+'.flatpak')
    run('flatpak','build-bundle',repo,package,APP_ID,'stable','--runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo')
    run('flatpak','--user','install','--noninteractive','-y',package)
    run('dbus-run-session','--','flatpak','run','--env=QT_QPA_PLATFORM=offscreen',APP_ID,'--self-test')
    checksum(package)
    return package

if __name__=='__main__':
    root=Path(__file__).resolve().parent;folder=root/'dist'/'LinuxPaint';releases=root/'release'
    label=f'LinuxPaint-{__version__}-linux-x86_64'
    print(*native_packages(root,folder,releases,label),sep='\n')
    print(flatpak_package(root,folder,releases,label))
