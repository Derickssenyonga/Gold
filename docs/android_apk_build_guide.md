# Android APK Build Guide for Gold Scalper

## Overview

The Gold Scalper Kivy app can be packaged as an Android APK in three ways:

1. **Cloud-based builder** (recommended for Windows users)
2. **WSL (Windows Subsystem for Linux) setup** (intermediate)
3. **Full Android Studio environment** (advanced)

---

## Option 1: Cloud-Based APK Builder (Recommended)

Use **Buildozer Cloud** or **GitHub Actions** to build your APK without installing Android tools locally.

### Using GitHub Actions

1. Create a GitHub repository with your project
2. Add `.github/workflows/build-apk.yml`:

```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build APK
        uses: arturadib/Kivy-Android-APK-Build@master
        with:
          directory: android_app
      - name: Upload APK
        uses: actions/upload-artifact@v2
        with:
          name: gold-scalper.apk
          path: android_app/bin/goldscalper*.apk
```

3. Push to GitHub and download the APK from the Actions artifacts

### Alternative: Buildozer Cloud

Visit: https://buildozer.cloud/

1. Upload your project
2. Select "Android Debug"
3. Download the resulting APK

---

## Option 2: Windows WSL Setup (Intermediate)

### Prerequisites

- Windows 10/11 with WSL2 enabled
- Ubuntu 20.04+ in WSL

### Steps

1. **Enable WSL2**:

```powershell
wsl --install
```

2. **In WSL Ubuntu terminal**:

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev openjdk-11-jdk
pip3 install buildozer cython
```

3. **Install Android SDK/NDK**:

```bash
# Download Android SDK
wget https://dl.google.com/android/repository/commandlinetools-linux-*.zip
unzip commandlinetools-linux-*.zip
mkdir -p ~/Android/sdk/cmdline-tools
mv cmdline-tools ~/Android/sdk/cmdline-tools/latest

# Set environment
export ANDROID_HOME=$HOME/Android/sdk
export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$PATH

# Install SDK components
sdkmanager --install "build-tools;34.0.0" "platforms;android-34" "ndk;26.1.10909125"
```

4. **Build the APK**:

```bash
cd ~/gold_mt5_scalper/android_app
buildozer android debug
```

5. **Find your APK**:

```bash
ls -la bin/
# Output: goldscalper-1.0-debug.apk
```

---

## Option 3: Full Android Studio Setup (Windows)

### Prerequisites

- Android Studio (https://developer.android.com/studio)
- JDK 11+
- Python 3.11+

### Steps

1. **Install Android Studio**
   - Download from https://developer.android.com/studio
   - During setup, install:
     - Android SDK Platform 34
     - Android NDK 26.1
     - Build Tools 34.0.0

2. **Set environment variables** (PowerShell as Admin):

```powershell
[Environment]::SetEnvironmentVariable("ANDROID_HOME", "$env:LOCALAPPDATA\Android\Sdk", "User")
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", "$env:LOCALAPPDATA\Android\Sdk", "User")
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Android\Android Studio\jbr", "User")
```

3. **Install Python dependencies**:

```bash
pip install buildozer cython
```

4. **Build from Windows Command Prompt**:

```cmd
cd C:\Users\deric\gold_mt5_scalper\android_app
buildozer android debug
```

---

## Post-Build: Installing on Android Device

### Requirements

- Android 5.1+ device
- USB debugging enabled
- ADB installed (via Android SDK)

### Steps

1. **Connect your device** via USB

2. **Install the APK**:

```bash
adb install -r bin/goldscalper-1.0-debug.apk
```

Or manually:
- Transfer `goldscalper-1.0-debug.apk` to your phone
- Open file manager
- Tap the APK file
- Select "Install"

3. **Launch the app**:
- Find "GoldScalper" on your home screen
- Tap to open

---

## Troubleshooting

### Build fails with "Java not found"

**Windows:**
```powershell
# Verify Java installation
java -version
# If missing, install from: https://www.oracle.com/java/technologies/downloads/
```

**WSL:**
```bash
sudo apt-get install openjdk-11-jdk
```

### Build fails with "Android SDK not found"

- Verify `ANDROID_HOME` environment variable is set
- Ensure SDK components are installed via `sdkmanager`
- Run `buildozer android debug --debug` for more details

### APK installation fails on device

- Enable "Install from unknown sources" in Settings → Security
- Ensure device API level matches `android.minapi` in buildozer.spec
- Try `adb uninstall org.example.goldscalper` first

---

## Next Steps

Once the APK is installed on your Android device:

1. Configure the dashboard server address in the app settings
2. Enable Wi-Fi on both PC and phone
3. Launch the app and point it to your bot's dashboard:
   - Dashboard URL: `http://<your-pc-ip>:5000/mobile`
   - Admin Panel: `http://<your-pc-ip>:5050/`

4. Run the full stack on your PC:
   ```bash
   python run_full_stack.py
   ```

5. Open the Android app to monitor your gold scalper bot in real-time

---

## Release Build (Production)

For distributing on Google Play:

1. Generate a signing key:

```bash
keytool -genkey -v -keystore my-release-key.keystore -keyalg RSA -keysize 2048 -validity 10000 -alias key0
```

2. Update `buildozer.spec`:

```ini
[app]
android.release_artifact = apk
android.keystore = 1
android.keystore_path = /path/to/my-release-key.keystore
android.keystore_alias = key0
```

3. Build:

```bash
buildozer android release
```

4. Upload to Google Play Console

---

## References

- Kivy: https://kivy.org/
- Buildozer: https://buildozer.readthedocs.io/
- Android Developer Docs: https://developer.android.com/docs
