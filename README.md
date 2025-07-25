# Asphalt Launcher
**A Launcher for Minecraft :)**
**An open-source, lightweight, and minimal Minecraft launcher made using Python**

![](./assets/logo.png)

> **This launcher is intended for educational and experimental use only.**
> Please support Mojang by [purchasing Minecraft from the official website](https://www.minecraft.net/). Piracy is not encouraged or supported.

[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

## ✨ What’s New in This Release

| Feature | Benefit |
|---------|---------|
| **Offline Mode** | If your internet drops, the launcher instantly switches to “offline mode” and lists only the versions you already have installed—no interruptions. |
| **Smart Version List** | Your last-played version is automatically moved to the top of the drop-down for faster launches. |
| **Responsive Downloads** | A progress bar now runs in the background, keeping the UI snappy while missing files download. |
| **Cleaner UI** | All extra settings tucked behind a single ⚙️ gear—main screen stays minimal and distraction-free. |
| **Easy RAM Sliders** | Adjust min/max memory with simple sliders in Settings—no JVM flags required. |

## Core Features

- Offline Minecraft launch with custom username
- Custom JVM arguments for advanced configuration
- Select and manage multiple Minecraft versions
- Choose your preferred Java executable manually
- Auto-installs missing Minecraft version files

## Screenshot

![](/assets/screenshot1.png)
![](/assets/screenshot2.png)

## Installation

```bash
pip install -r requirements.txt
```
Double-click **run.bat**

## Build as EXE (Windows)

```bash
python -m PyInstaller build.spec --clean --noconfirm
# Output → dist/AsphaltLauncher.exe
```

## Contributing

Feel free to fork the repository, though pull requests are **not** accepted currently.

## License

MIT License
