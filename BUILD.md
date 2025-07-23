# Asphalt Launcher — Build Guide

Welcome to the official build guide for **Asphalt Launcher**

This guide is intended for developers who want to build, test, and package the launcher into a portable `.exe`.

---

## Requirements

| Dependency               | Version    | Notes                      |
|--------------------------|------------|----------------------------|
| Python                   | 3.12+      | Required runtime environment |
| [PyInstaller](https://pyinstaller.org)         | Latest     | Used to package Python scripts into executables |
| [PySide6](https://pypi.org/project/PySide6/)  | Latest     | Qt GUI framework bindings for Python |
| [minecraft-launcher-lib](https://pypi.org/project/minecraft-launcher-lib/) | Latest     | For Minecraft launching |
| psutil                   | Latest     | System and process utility access            |

### Install All Requirements

```bash
pip install -r requirements.txt