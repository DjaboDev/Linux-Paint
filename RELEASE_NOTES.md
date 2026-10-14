# Linux Paint 0.4.0 — new Linux-only baseline

This release restarts the version series at 0.4.0 and incorporates all improvements from the previous releases. Distribution and support now target Linux x86_64 exclusively.

Available packages: **tar.gz, AppImage, Flatpak, deb and rpm**, with SHA256 checksums. Flatpak uses the Freedesktop 25.08 runtime and is distributed as a bundle from this repository, not as a Flathub listing.

- Pencil width now follows the selected value, from 1 to 200 pixels, independently of the previously selected brush.
- Edge hardness works for pencil strokes (including a 1-pixel tip), airbrush intensity, lines and geometric shapes. Soft shape previews preserve the existing canvas and remain undoable.
- Right-click shape drawing correctly swaps outline and fill colors.
- Width shortcuts [ and ] update the ribbon controls; Ctrl + and Ctrl - remain zoom shortcuts.
- Modern font previews, symbolic text-background options and message icons, themed combo boxes, fields, menus and scrollbars.
- Automatic English/Portuguese system-language interface, with English fallback for other locales. README fully translated into English.
- Window size and maximized state restored after interface setup, and the last successfully opened folder remembered, with home-directory fallback.
- Previous features retained: custom app icon and desktop identity, unified header, compact ribbon, consistent light/dark modes, native file chooser, readable controls, resize feedback and local background removal with magic selection, AI, GrabCut and manual corrections.

29 regression tests cover drawing, width, hardness, all shapes, canvas boundaries, language/menu behavior, persistence, transparency, cancellation and undo/redo. Each package is checked by launching its executable payload; Flatpak is additionally launched inside its sandbox.
