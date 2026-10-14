"""Build native Linux, macOS or Windows artifacts and verify the packaged runtime."""
import argparse
import hashlib
import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile
from PIL import Image
from classic_paint import __version__

ROOT=Path(__file__).resolve().parent

def run(*args,env=None):
    subprocess.run([str(arg) for arg in args],cwd=ROOT,check=True,env=env)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--arch',choices=['x86_64','arm64'])
    args=parser.parse_args();system=platform.system()
    if system not in ('Linux','Darwin','Windows'):parser.error('Build on Linux, macOS or Windows.')
    native={'AMD64':'x86_64','aarch64':'arm64'}.get(platform.machine(),platform.machine())
    target=args.arch or native
    if target!=native:parser.error('Build on the target architecture; cross-compilation is not supported.')
    staging=ROOT/'build';staging.mkdir(exist_ok=True)
    image=Image.open(ROOT/'classic_paint'/'assets'/'linux-paint.png').convert('RGBA')
    icon=staging/('linux-paint.icns' if system=='Darwin' else 'linux-paint.ico')
    if system=='Darwin':image.resize((1024,1024),Image.Resampling.LANCZOS).save(icon)
    else:image.resize((256,256),Image.Resampling.LANCZOS).save(icon,sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
    cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--name','LinuxPaint',
         '--paths',str(ROOT),'--add-data',str(ROOT/'classic_paint'/'assets')+os.pathsep+'classic_paint/assets',
         '--collect-data','onnxruntime','--add-data',str(ROOT/'THIRD_PARTY_NOTICES.md')+os.pathsep+'.',
         '--add-data',str(ROOT/'LICENSE')+os.pathsep+'.','--distpath',str(ROOT/'dist'),'--workpath',str(staging)]
    if system=='Darwin':cmd+=['--windowed','--onedir','--target-arch',target,'--osx-bundle-identifier','io.github.DjaboDev.LinuxPaint','--icon',str(icon)]
    elif system=='Windows':cmd+=['--onefile','--windowed','--icon',str(icon)]
    else:cmd+=['--onedir']
    run(*cmd,ROOT/'paint.py')
    binary=ROOT/'dist'/('LinuxPaint.exe' if system=='Windows' else 'LinuxPaint.app/Contents/MacOS/LinuxPaint' if system=='Darwin' else 'LinuxPaint/LinuxPaint')
    env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen'
    # Exit status is authoritative even for a Windows GUI executable with no console.
    run(binary,'--self-test',env=env)
    releases=ROOT/'release';releases.mkdir(exist_ok=True)
    label=f'LinuxPaint-{__version__}-{system.lower()}-{target}'
    if system=='Darwin':
        stage=staging/'dmg-stage'
        if stage.exists():shutil.rmtree(stage)
        stage.mkdir();shutil.copytree(ROOT/'dist'/'LinuxPaint.app',stage/'LinuxPaint.app',symlinks=True)
        (stage/'Applications').symlink_to('/Applications')
        artifact=releases/(label+'.dmg');artifact.unlink(missing_ok=True)
        run('hdiutil','create','-volname','Linux Paint','-srcfolder',stage,'-ov','-format','UDZO',artifact)
    elif system=='Windows':
        artifact=releases/(label+'.exe');shutil.copy2(binary,artifact)
    else:
        folder=ROOT/'dist'/'LinuxPaint'
        shutil.copy2(ROOT/'classic_paint'/'assets'/'linux-paint.png',folder/'linux-paint.png')
        shutil.copy2(ROOT/'linux'/'install-packaged.sh',folder/'install.sh');(folder/'install.sh').chmod(0o755)
        shutil.copy2(ROOT/'linux'/'io.github.DjaboDev.LinuxPaint.desktop',folder/'io.github.DjaboDev.LinuxPaint.desktop')
        shutil.copy2(ROOT/'README.md',folder/'README.md');shutil.copy2(ROOT/'THIRD_PARTY_NOTICES.md',folder/'THIRD_PARTY_NOTICES.md')
        artifact=releases/(label+'.tar.gz')
        with tarfile.open(artifact,'w:gz') as archive:archive.add(folder,arcname='LinuxPaint')
    with artifact.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    artifact.with_name(artifact.name+'.sha256').write_text(f'{digest}  {artifact.name}\n')
    print(artifact)

if __name__=='__main__':main()
