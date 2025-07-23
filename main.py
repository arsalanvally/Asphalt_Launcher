import os
import sys
import shutil
import subprocess
import psutil
import json
import uuid
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QFileDialog, QTextEdit, QDialog, QProgressBar, QDialogButtonBox
)
from PySide6.QtGui import QPixmap, QIcon, QPainter
from PySide6.QtCore import Qt

import minecraft_launcher_lib


class BackgroundWidget(QWidget):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(self.rect(), self.pixmap)


def get_appdata_path():
    return os.path.join(os.getenv("APPDATA"), "AsphaltLauncher")


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def get_minecraft_dir():
    return os.path.expandvars(r"%APPDATA%\.minecraft")


CONFIG_FILE = os.path.join(get_appdata_path(), "launcher.json")


def load_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"username": "", "jvm_args": ["-Xms2G", "-Xmx4G"], "java_path": None}


def save_config(username, jvm_args, java_path):
    os.makedirs(get_appdata_path(), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username, "jvm_args": jvm_args, "java_path": java_path}, f, indent=2)


LAST_PLAYED_FILE = os.path.join(get_appdata_path(), "last_played.json")


def load_last_played():
    if os.path.isfile(LAST_PLAYED_FILE):
        try:
            with open(LAST_PLAYED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_last_played(version_id):
    lp = load_last_played()
    lp[version_id] = datetime.now().timestamp()
    with open(LAST_PLAYED_FILE, "w", encoding="utf-8") as f:
        json.dump(lp, f, indent=2)


def _scan_local_versions():
    local = {}
    versions_dir = os.path.join(get_minecraft_dir(), "versions")
    if os.path.isdir(versions_dir):
        for name in os.listdir(versions_dir):
            folder = os.path.join(versions_dir, name)
            if os.path.isdir(folder):
                local[name] = os.path.getmtime(folder)
    return local


def get_available_versions():
    remote = minecraft_launcher_lib.utils.get_version_list()
    type_labels = {
        "release": "Release",
        "snapshot": "Snapshot",
        "old_beta": "Beta",
        "old_alpha": "Alpha"
    }

    last_played = load_last_played()
    all_ids = set()
    items = []

    for v in remote:
        vid = v["id"]
        if vid in all_ids:
            continue
        all_ids.add(vid)
        label = f"{type_labels.get(v['type'], v['type'])} - {vid}"
        if vid in _scan_local_versions():
            label = f"🔧 {label}"
        items.append((label, vid))

    for vid in _scan_local_versions():
        if vid in all_ids:
            continue
        all_ids.add(vid)
        items.append((f"🔧 {vid}", vid))

    last_vid = max(last_played, key=last_played.get, default=None)
    if last_vid:
        idx = next((i for i, (_, vid) in enumerate(items) if vid == last_vid), None)
        if idx is not None:
            items.insert(0, items.pop(idx))

    return items


def launch_minecraft(username, version, java_executable=None, jvm_args=None):
    offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_OID, username))
    options = {
        "username": username,
        "uuid": offline_uuid,
        "token": "0" * 32
    }
    if java_executable:
        options["executablePath"] = java_executable
    if jvm_args:
        options["jvmArguments"] = jvm_args

    mc_dir = get_minecraft_dir()
    minecraft_launcher_lib.install.install_minecraft_version(version, mc_dir, callback=None)
    command = minecraft_launcher_lib.command.get_minecraft_command(version, mc_dir, options)

    proc = subprocess.Popen(
        command,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        cwd=os.path.expandvars(r"%APPDATA%\.minecraft")
        )
    save_last_played(version)
    proc.wait()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] != os.getpid():
                if "asphalt-launcher" in ' '.join(proc.info['cmdline']).lower():
                    proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


class JvmArgsDialog(QDialog):
    def __init__(self, parent=None, current=None):
        super().__init__(parent)
        self.setWindowTitle("Custom JVM Arguments")
        self.setFixedSize(500, 300)
        layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setPlainText("\n".join(current or []))
        layout.addWidget(self.text)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def args(self):
        txt = self.text.toPlainText().strip()
        return txt.splitlines() if txt else []


class JavaPickerDialog(QDialog):
    def __init__(self, parent=None, current=""):
        super().__init__(parent)
        self.setWindowTitle("Select Java Executable")
        self.setFixedSize(400, 100)
        layout = QVBoxLayout(self)

        self.path = QLineEdit(current or "")
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.path)
        row.addWidget(browse)
        layout.addLayout(row)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _browse(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Java executable", "",
            "Executables (*.exe)" if os.name == 'nt' else "")
        if file:
            self.path.setText(file)

    def java_path(self):
        return self.path.text().strip() or None


class AsphaltLauncher(QWidget):
    def __init__(self):
        super().__init__()

        self.appdata_dir = get_appdata_path()
        self.assets_dir = os.path.join(self.appdata_dir, "assets")
        self.icon_path = os.path.join(self.assets_dir, "logo.ico")
        self.ensure_assets_exist()

        self.cfg = load_config()
        self.java_executable = self.cfg.get("java_path")
        self.jvm_arguments = self.cfg.get("jvm_args", ["-Xms2G", "-Xmx4G"])

        self.setWindowTitle("Asphalt Launcher")
        self.setFixedSize(880, 520)
        self.setWindowIcon(QIcon(self.icon_path))

        bg_path = os.path.join(self.assets_dir, "background.webp")
        if os.path.isfile(bg_path):
            bg_pixmap = QPixmap(bg_path)
            bg = BackgroundWidget(bg_pixmap, self)
            bg.setGeometry(self.rect())
            bg.lower()
        else:
            self.setStyleSheet("background-color: #2c2c2c; color: white; font-family: 'Segoe UI';")

        main_layout = QHBoxLayout(self)

        ui_layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        top_bar.addWidget(username_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your Minecraft username")
        self.username_input.setFixedWidth(300)
        self.username_input.setText(self.cfg.get("username", ""))
        top_bar.addWidget(self.username_input)
        top_bar.addStretch()
        ui_layout.addLayout(top_bar)

        opts_layout = QHBoxLayout()

        self.btn_jvm = QPushButton("Custom JVM Args")
        self.btn_jvm.clicked.connect(self.edit_jvm_args)

        self.btn_java = QPushButton("Select JRE")
        self.btn_java.clicked.connect(self.select_java)

        self.btn_mc_folder = QPushButton(".minecraft")
        self.btn_mc_folder.clicked.connect(lambda: self.open_folder(get_minecraft_dir()))

        self.btn_launcher_folder = QPushButton("Launcher Dir")
        self.btn_launcher_folder.clicked.connect(lambda: self.open_folder(self.appdata_dir))

        for btn in (self.btn_jvm, self.btn_java, self.btn_mc_folder, self.btn_launcher_folder):
            btn.setStyleSheet("background-color: #888888; padding: 10px; font-size: 12px;")
            opts_layout.addWidget(btn)

        ui_layout.addLayout(opts_layout)

        bottom_bar = QHBoxLayout()
        self.version_dropdown = QComboBox()
        self.version_map = {}
        versions = get_available_versions()
        most_recent_index = 0
        for idx, (label, version_id) in enumerate(versions):
            self.version_dropdown.addItem(label)
            self.version_map[label] = version_id
            if label.startswith("🔧") and most_recent_index == 0:
                most_recent_index = idx
        self.version_dropdown.setCurrentIndex(most_recent_index)
        last = load_last_played()
        if last:
            last_vid = max(last, key=last.get)
            idx = next((i for i, (_, vid) in enumerate(versions) if vid == last_vid), 0)
            self.version_dropdown.setCurrentIndex(idx)
        self.version_dropdown.setFixedWidth(250)

        self.start_btn = QPushButton("START")
        self.start_btn.setFixedWidth(160)
        self.start_btn.setStyleSheet(
            "background-color: #6ab04c; font-size: 16px; padding: 10px; font-weight: bold;")
        self.start_btn.clicked.connect(self.launch_game)

        bottom_bar.addWidget(self.version_dropdown)
        bottom_bar.addWidget(self.start_btn)
        bottom_bar.addStretch()
        ui_layout.addLayout(bottom_bar)

        footer = QLabel("A Launcher for Minecraft - Asphalt Launcher :)")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        ui_layout.addWidget(footer)

        main_layout.addLayout(ui_layout)

    def edit_jvm_args(self):
        dlg = JvmArgsDialog(self, self.jvm_arguments)
        if dlg.exec():
            self.jvm_arguments = dlg.args()
            save_config(self.username_input.text(), self.jvm_arguments, self.java_executable)

    def select_java(self):
        dlg = JavaPickerDialog(self, self.java_executable or "")
        if dlg.exec():
            self.java_executable = dlg.java_path()
            save_config(self.username_input.text(), self.jvm_arguments, self.java_executable)

    def open_folder(self, path):
        if os.path.isdir(path):
            os.startfile(path)

    def launch_game(self):
        username = self.username_input.text().strip()
        selected_label = self.version_dropdown.currentText()
        version_id = self.version_map.get(selected_label)

        if not username:
            dlg = QDialog(self)
            dlg.setWindowTitle("Attention")
            dlg.setFixedSize(300, 80)
            dlg.setModal(True)

            lay = QVBoxLayout(dlg)
            lay.addWidget(
                QLabel("Username is required to launch Minecraft"),
                alignment=Qt.AlignCenter
            )
            ok = QPushButton("OK")
            ok.clicked.connect(dlg.accept)
            lay.addWidget(ok, alignment=Qt.AlignCenter)

            dlg.exec()
            return

        save_config(username, self.jvm_arguments, self.java_executable)
        mc_dir = get_minecraft_dir()

        version_dir = os.path.join(mc_dir, "versions", version_id)
        json_file = os.path.join(version_dir, f"{version_id}.json")
        jar_file = os.path.join(version_dir, f"{version_id}.jar")
        already_installed = os.path.isfile(json_file) and os.path.isfile(jar_file)

        if not already_installed:
            progress = QDialog(self)
            progress.setWindowTitle("Downloading…")
            progress.setFixedSize(300, 80)
            progress.setModal(True)
            layout = QVBoxLayout(progress)
            bar = QProgressBar()
            label = QLabel("Preparing…")
            layout.addWidget(label)
            layout.addWidget(bar)
            progress.show()
            QApplication.processEvents()

            callback = {
                "setStatus": lambda txt: label.setText(txt),
                "setMax": lambda m: bar.setMaximum(m),
                "setProgress": lambda v: (bar.setValue(v), QApplication.processEvents())
            }
            try:
                minecraft_launcher_lib.install.install_minecraft_version(
                    version_id, mc_dir, callback=callback
                )
            except Exception as e:
                progress.close()
                print(f"Download failed: {e}")
                return
            progress.close()

        self.hide()
        try:
            launch_minecraft(username, version_id,
                             java_executable=self.java_executable,
                             jvm_args=self.jvm_arguments)
        except Exception as e:
            print(f"Launch failed: {e}")
        finally:
            self.show()

    def ensure_assets_exist(self):
        os.makedirs(self.assets_dir, exist_ok=True)
        for asset in ("logo.ico", "background.webp"):
            dst = os.path.join(self.assets_dir, asset)
            if not os.path.exists(dst):
                src = resource_path(f"assets/{asset}")
                if os.path.exists(src):
                    shutil.copy(src, dst)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = AsphaltLauncher()
    launcher.show()
    sys.exit(app.exec())