# Asphalt Launcher
**A Launcher for Minecraft :)**
**An open-source, lightweight, and minimal Minecraft launcher made using Python**

![](./assets/logo.png)

> **This launcher is intended for educational and experimental use only.**
> Please support Mojang by [purchasing Minecraft from the official website](https://www.minecraft.net/). Piracy is not encouraged or supported.

[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

## Features

- Offline Minecraft launch with custom username
- Custom JVM arguments for advanced configuration
- Select and manage multiple Minecraft versions
- Choose your preferred Java executable manually
- Auto-installs missing Minecraft version files

## Screenshot

![](/assets/screenshot.png)

## Installation

```bash
pip install -r requirements.txt
```
Double-click **run.bat**

## Build as EXE (Windows)

```bash
python -m PyInstaller build.spec --clean --noconfirm
```
The executable will be generated in the **dist/** folder.

## Contributing

Feel free to fork the repository, though pull requests are not accepted.

## License

MIT License
