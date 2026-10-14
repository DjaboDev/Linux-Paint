![Linux Paint](screenshots/screenshot_1.png)

# Linux Paint

A feature-rich, native Python/PySide6 clone of Microsoft Paint with the modern ribbon interface for Linux, with full support for transparent PNGs and extensive usability enhancements.

> **Note & Credits:** This project is a fork of [Classic Paint](https://github.com/blankresearch/ClassicPaint) created by [Youssef](https://yousbot.com) ([blankresearch](https://github.com/blankresearch)). All credit for the foundational interface, tool implementations, and original reverse-engineering belongs to the original author.

---

## What's New in Linux Paint (Fork Improvements)

This fork introduces extensive bug fixes, quality-of-life enhancements, and native transparent PNG support:

### 🐧 GNOME & Linux Desktop Modernization
- **Unified GNOME HeaderBar (CSD):** Client-Side Decorations (CSD) with modern window controls (Minimize, Maximize/Restore, Close), document title with dirty state indicator (`*`), hamburger menu (≡), and quick action buttons (Save, Undo, Redo).
- **Adaptive Window Corners:** Follows GNOME's rounded window corners (12px radius) when floating/restored, switching to square edges (0px) seamlessly when maximized.
- **Native Dark Mode as Default:** Elegant modern dark theme matching GNOME Adwaita Dark styling, with a one-click toggle to traditional Light Mode in the menu and "Exibir" tab.
- **Active Brush Visual Indicator:** The "Pincéis" button in the Ribbon now dynamically displays the active brush icon (Round, Square, or Airbrush) with checkmarks inside the dropdown.
- **Granular Stroke Size Control:** Size menu now includes both standard presets and a precision slider + spinbox (1 to 200 pixels) for fine tool control.
- **Edge Hardness & Transition (Antialiasing) Slider:** Adjust edge softness/transition from 0% (smooth anti-aliased blend) to 100% (crisp, pixel-exact cut) for Pencil, Eraser, and Brushes.
- **Eraser Shape Selection:** Choose between Circular (Round) and Square eraser shapes directly in the Size dropdown menu.
- **Expanded Format Compatibility (WebP):** Native support for reading and saving WebP images with alpha transparency, alongside PNG, JPEG, BMP, and TIFF.

### 🎨 Transparency & PNG Overhaul
- **Real-time Checkerboard Canvas:** Transparent areas are visually rendered with a classic alpha checkerboard grid underneath the image.
- **New Transparent Canvas:** Create new transparent documents using `File -> New (Transparent)` or `Ctrl+Shift+N`.
- **Erase to Transparent:** Right-click with the Eraser tool now erases pixels directly to transparent instead of only using the secondary color.
- **Transparent Palette Swatch:** Slot 20 in the quick color palette is set to transparent with a checkerboard indicator.
- **Full Alpha Channel Support:** The Color Dialog now includes full alpha channel controls (`ShowAlphaChannel`).
- **Clear to Transparent:** Clear the canvas or current selection directly to transparent using `Ctrl+Alt+Delete` or via the Image menu.
- **Transparency-Preserving Selections:** Moving or cutting selections preserves transparent backgrounds instead of flattening them to white.

### ⚡ Bug Fixes & Usability
- **Immediate Undo/Redo for Selections:** Fixed an issue where `Ctrl+Z` would not undo a moved selection until clicking outside the selection boundary.
- **Ctrl + Mouse Wheel Zoom:** Zoom in and out smoothly centered directly on the cursor position (`25%` to `800%`).
- **Magnifier Tool Centering:** Clicking with the Magnifier tool now automatically centers the clicked point inside the viewport.
- **Drag-and-Drop:** Drag and drop image files (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.webp`, `.tiff`, `.gif`) directly into the window from your file manager.
- **Recent Pictures:** Integrated "Recent pictures" menu in the File menu, remembering your recent files across sessions.
- **Window State Persistence:** Automatically saves and restores window dimensions and position between launches.
- **Cleaner Status Bar & Rulers:** Coordinates in the status bar and ruler guideline indicators reset cleanly when the mouse leaves the canvas.
- **Keyboard Shortcuts on Canvas:** Direct and reliable handling of `Ctrl+C` (Copy), `Ctrl+X` (Cut), `Ctrl+V` (Paste), and `Ctrl+A` (Select All) even when canvas has focus.
- **Quick Stroke Size Adjustment:** Use `Ctrl + +` / `Ctrl + =` and `Ctrl + -` to quickly increase or decrease the brush, pencil, and eraser size.
- **High-Resolution Icons:** Includes vector SVG and 256x256 icons for Linux desktop integration.

---

## Features

- Modern Ribbon toolbar inspired by Windows 7 Paint with unified GNOME HeaderBar.
- Pencil, brushes (Round, Square, Airbrush), eraser (Round, Square), flood fill, color picker, text, and shapes.
- Rectangular and free-form selection, moving, cropping, resizing, and rotation.
- Clipboard support, full undo/redo history, and rich keyboard shortcuts.
- Image loading, saving (PNG, JPEG, BMP, TIFF, WebP), and printing.

---

## Installation & Running

### Requirements
- Python 3.10+ (tested on Python 3.11 and 3.12)
- PySide6

### Running from source

Clone this repository and create a virtual environment:

```bash
git clone https://github.com/DjaboDev/Linux-Paint.git
cd Linux-Paint
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python paint.py
```

Open an image directly from terminal:

```bash
python paint.py /path/to/image.png
```

---

## Desktop Integration on Linux

To integrate Linux Paint with your desktop application menu:

1. Copy the icons to your user icons directory:
```bash
mkdir -p ~/.local/share/icons/hicolor/scalable/apps ~/.local/share/icons/hicolor/256x256/apps
cp classic-paint.svg ~/.local/share/icons/hicolor/scalable/apps/classic-paint.svg
cp classic-paint-256.png ~/.local/share/icons/hicolor/256x256/apps/classic-paint.png
```

2. Create a desktop launcher at `~/.local/share/applications/classic-paint.desktop`.

---

## Attribution & License

- **Original Project:** Forked from [blankresearch/ClassicPaint](https://github.com/blankresearch/ClassicPaint) by [Youssef](https://yousbot.com).
- **Code License:** Python code is licensed under the MIT License.
- **Artwork License:** Microsoft Paint and its original artwork belong to Microsoft Corporation. Artwork embedded in the original project is separately licensed and unaffiliated with Microsoft.