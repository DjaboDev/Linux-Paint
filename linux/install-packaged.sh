#!/bin/sh
set -eu
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
prefix="${LINUXPAINT_PREFIX:-$HOME/.local}"
app_dir="$prefix/share/LinuxPaint-binary"
mkdir -p "$app_dir" "$prefix/bin" "$prefix/share/applications" "$prefix/share/icons/hicolor/256x256/apps"
if [ "$source_dir" != "$app_dir" ]; then cp -a "$source_dir/." "$app_dir/"; fi
cat > "$prefix/bin/linux-paint" <<EOF
#!/bin/sh
exec "$app_dir/LinuxPaint" "\$@"
EOF
chmod +x "$prefix/bin/linux-paint" "$app_dir/LinuxPaint"
cat > "$prefix/bin/classic-paint" <<EOF
#!/bin/sh
exec "$prefix/bin/linux-paint" "\$@"
EOF
chmod +x "$prefix/bin/classic-paint"
cat > "$prefix/share/applications/io.github.DjaboDev.LinuxPaint.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Linux Paint
Comment=Editor de imagens com ribbon e remoção local de fundo
Exec="$prefix/bin/linux-paint" %f
Icon=io.github.DjaboDev.LinuxPaint
Terminal=false
Categories=Graphics;2DGraphics;RasterGraphics;
MimeType=image/png;image/jpeg;image/bmp;image/gif;image/webp;image/tiff;
StartupWMClass=LinuxPaint
StartupNotify=true
EOF
cp "$app_dir/linux-paint.png" "$prefix/share/icons/hicolor/256x256/apps/io.github.DjaboDev.LinuxPaint.png"
if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$prefix/share/applications"; fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -f -t "$prefix/share/icons/hicolor"; fi
printf 'Linux Paint instalado. Abra pelo menu de aplicativos.\n'
