# Linux Paint 0.4.1 — modern dialogs and safer background removal

Linux-only update to the 0.4.0 baseline. Available packages: **tar.gz, AppImage, Flatpak, deb and rpm**, with SHA256 checksums.

- Replaced traditional message boxes with readable modal alerts, internal headings, safe cancellation and clearly distinguished save/discard actions.
- Unified action-dialog headers for background removal, color editing, resizing and keyboard shortcuts; removed legacy colored button icons.
- Larger horizontal minus/plus numeric controls retain keyboard editing and respect their limits in both themes.
- Original-image comparison is read-only. Starting detection returns to the result preview, preventing edits from being hidden behind the original image.
- Magic selection supports feathering and expansion/contraction without creating permanent erase markings.
- Border detection samples the dominant border color instead of erasing every object touching the image boundary.
- Corrected one-pixel correction brushes, true 100% preview after layout changes, excessive checkerboard drawing at high zoom and completed worker cleanup.
- Release automation safely recognizes an already published version instead of failing on duplicate creation.

41 regression tests cover drawing, persistence, localization, dialogs and cutout behavior, including original comparison before/after detection, magic selection, manual corrections, refinement, undo/reset, transparency, zoom, failures and cancellation. The cached local ONNX model was additionally exercised on a real app-icon image with an opaque background. These checks do not guarantee a perfect cutout for every photograph; review the preview and use keep/remove corrections as needed.
