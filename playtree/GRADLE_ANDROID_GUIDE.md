# Gradle-Based Android Build (Alternative to Buildozer)

This project uses pygame-ce. For a Gradle-based Android build, you need python-for-android (p4a) with a Gradle wrapper.

## Prerequisites
- Android Studio (latest)
- Android SDK (API 31+)
- Android NDK (25b)
- Java 17+
- Python 3.11+

## Steps

### 1. Install python-for-android
```bash
pip install python-for-android
```

### 2. Create the project
```bash
p4a create --dist_name playtree --bootstrap sdl2 --requirements python3,pygame-ce --arch arm64-v8a --copy-libs
```

### 3. Configure build.gradle
In the generated `build/` directory, update `build.gradle`:
- Set `applicationId "org.gostudios.playtree"`
- Set `minSdkVersion 24`, `targetSdkVersion 33`
- Add permissions: INTERNET, WRITE_EXTERNAL_STORAGE

### 4. Build APK
```bash
p4a apk --private . --package org.gostudios.playtree --name PLAYTREE --version 1.0.1 --bootstrap sdl2 --requirements python3,pygame-ce --arch arm64-v8a
```

### 5. Or use Gradle directly
```bash
cd p4a-build
./gradlew assembleDebug
```

## Notes
- Buildozer (in `buildozer.spec`) is the recommended and tested path for this project.
- Gradle-based builds require manual configuration of SDL2, Python, and pygame-ce native libraries.
- For most users, `buildozer android debug` is simpler and more reliable.