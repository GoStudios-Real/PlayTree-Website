# PLAYTREE Android TV App

This is a minimal Android TV web-wrapper app that displays the PLAYTREE TV page (`tv.html`) full-screen on an Android TV / Google TV Streamer.

## Build options

### Option A — Build with Android Studio (recommended)
1. Open Android Studio.
2. File > Open > select this `android_tv` folder.
3. Let Gradle sync.
4. Build > Generate Signed Bundle / APK > APK.
5. Copy `app/build/outputs/apk/debug/app-debug.apk` to `playtree/bin/PLAYTREE-TV.apk`.
6. Run `install_on_tv.bat`.

### Option B — Build with command-line Gradle
```bash
cd android_tv
gradle assembleDebug
```
Output: `app/build/outputs/apk/debug/app-debug.apk`

## Install via ADB
1. Run `adb_tv_connect.bat` first (connects to your TV at 192.168.0.78).
2. Run `install_on_tv.bat`.

## Requirements
- Android SDK (API 24+)
- Java 17+
- `adb.exe` (platform-tools) in PATH

## Notes
- The app loads `https://playtree.game/tv.html` by default.
- If the website is not live yet, change the URL in `app/src/main/java/com/gostudios/playtree/MainActivity.java` to a locally hosted URL or a GitHub Pages URL.
- For local testing, you can point it at `http://<YOUR_PC_IP>:8000/tv.html` (start a local server with `python -m http.server` in the `website` folder).