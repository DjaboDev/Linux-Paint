#!/bin/sh
set -eu
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
app_dir="$HOME/.local/share/LinuxPaint-binary"
mkdir -p "$app_dir" "$HOME/.local/bin" "$HOME/.local/share/applications" "$HOME/.local/share/icons/hicolor/256x256/apps"
if [ "$source_dir" != "$app_dir" ]; then cp -a "$source_dir/." "$app_dir/"; fi
cat > "$HOME/.local/bin/linux-paint" <<EOF
#!/bin/sh
exec "$app_dir/LinuxPaint" "\$@"
EOF
chmod +x "$HOME/.local/bin/linux-paint" "$app_dir/LinuxPaint"
cat > "$HOME/.local/share/applications/io.github.DjaboDev.LinuxPaint.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Linux Paint
Comment=Editor de imagens com ribbon e remoção local de fundo
Exec="$HOME/.local/bin/linux-paint" %f
Icon=io.github.DjaboDev.LinuxPaint
Terminal=false
Categories=Graphics;2DGraphics;RasterGraphics;
MimeType=image/png;image/jpeg;image/bmp;image/gif;image/webp;image/tiff;
StartupWMClass=LinuxPaint
StartupNotify=true
EOF
cp "$app_dir/linux-paint.png" "$HOME/.local/share/icons/hicolor/256x256/apps/io.github.DjaboDev.LinuxPaint.png"
if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$HOME/.local/share/applications"; fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor"; fi
printf 'Linux Paint instalado. Abra pelo menu de aplicativos.\n'
