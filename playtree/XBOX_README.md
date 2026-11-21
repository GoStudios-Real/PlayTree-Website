# PLAYTREE on Xbox

This project is a Python/pygame-ce game. There is **no one-click Xbox build** from this source, but there are two realistic paths.

## Option A — Microsoft Store (PC/Xbox desktop listing, recommended first)

1. Build the Windows EXE:
   ```bat
   cd playtree
   build_playtree.bat
   ```
2. Package as MSIX using Microsoft MSIX Packaging Tool or `makeappx`/`signtool`:
   - Install MSIX Packaging Tool from Microsoft Store.
   - Create a new package, select `dist\PLAYTREE.exe` as entry point.
   - Package identity should match Partner Center (e.g. `GoStudios.PLAYTREE`).
   - Output: `PLAYTREE.msix`.
3. Create a Microsoft Partner Center app, reserve name `PLAYTREE`, upload MSIX, complete store listing/age rating.
4. For Xbox console availability, enable Xbox device families in Partner Center and test with Xbox Dev Mode. A desktop MSIX may run on Xbox in some scenarios, but full console certification usually requires UWP/native compliance.

## Option B — Xbox Dev Mode (testing)

1. Enable Developer Mode on your Xbox (Xbox Dev Mode app).
2. Build/package as UWP-compatible. Pygame-ce does not ship an official Xbox UWP target; you will likely need a wrapper (e.g. UWP WebView host, or port to a supported engine/framework).
3. Deploy via Device Portal.

## What is already prepared

- Full Xbox controller input/prompts exist in game code (`src/ui.py`, `src/game.py`, `src/tv_support.py`).
- Windows EXE build script: `build_playtree.bat`.
- Android APK build spec: `buildozer.spec`.

## Recommended practical path

Publish Windows EXE + Microsoft Store PC package first, then evaluate an engine port or UWP wrapper for native Xbox console certification.