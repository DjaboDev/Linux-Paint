"""Run with Python 3.11 on the target operating system and architecture."""
import argparse
import hashlib
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parent


def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arch', choices=['x86_64', 'arm64', 'universal2'])
    args = parser.parse_args()
    system = platform.system()
    if system not in {'Darwin', 'Windows', 'Linux'}:
        parser.error('Supported build systems: macOS, Windows, Linux')
    arch = {'AMD64': 'x86_64', 'aarch64': 'arm64'}.get(platform.machine(), platform.machine())
    target = args.arch or arch
    if system != 'Darwin' and target != arch:
        parser.error('Build natively on the target architecture; cross-compilation is not supported')
    import PySide6
    import PyInstaller
    cmd = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
           '--name', 'LinuxPaint', '--paths', str(ROOT),
           '--add-data', str(ROOT / 'classic_paint' / 'assets') + ':classic_paint/assets',
           '--distpath', str(ROOT / 'dist'), '--workpath', str(ROOT / 'build')]
    if system == 'Darwin':
        cmd += ['--windowed', '--onedir', '--target-arch', target,
                '--osx-bundle-identifier', 'io.github.DjaboDev.LinuxPaint']
    else:
        cmd += ['--onefile']
        if system == 'Windows':
            cmd += ['--windowed']
    # PyInstaller's PySide6 hooks collect Qt libraries and required plugins.
    run(*cmd, ROOT / 'paint.py')
    releases = ROOT / 'release'
    releases.mkdir(exist_ok=True)
    label = f'LinuxPaint-{system.lower()}-{target}'
    if system == 'Darwin':
        stage = ROOT / 'build' / 'dmg-stage'
        if stage.exists():
            shutil.rmtree(stage)
        stage.mkdir(parents=True)
        shutil.copytree(ROOT / 'dist' / 'LinuxPaint.app', stage / 'LinuxPaint.app', symlinks=True)
        (stage / 'Applications').symlink_to('/Applications')
        artifact = releases / f'{label}.dmg'
        artifact.unlink(missing_ok=True)
        run('hdiutil', 'create', '-volname', 'Linux Paint', '-srcfolder', stage,
            '-ov', '-format', 'UDZO', artifact)
    elif system == 'Windows':
        artifact = releases / f'{label}.exe'
        shutil.copy2(ROOT / 'dist' / 'LinuxPaint.exe', artifact)
    else:
        artifact = releases / f'{label}.tar.gz'
        with tarfile.open(artifact, 'w:gz') as archive:
            archive.add(ROOT / 'dist' / 'LinuxPaint', arcname='LinuxPaint')
            archive.add(ROOT / 'classic_paint' / 'assets' / 'linux-paint.png', arcname='linux-paint.png')
            archive.add(ROOT / 'linux' / 'io.github.DjaboDev.LinuxPaint.desktop', arcname='io.github.DjaboDev.LinuxPaint.desktop')
    digest = hashlib.file_digest(artifact.open('rb'), 'sha256').hexdigest()
    artifact.with_name(artifact.name + '.sha256').write_text(f'{digest}  {artifact.name}\n')
    print(artifact)


if __name__ == '__main__':
    main()
