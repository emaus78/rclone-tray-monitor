#!/usr/bin/env python3
"""
Rclone Mailbox Drive Monitor - Qt6 System Tray Application
"""

import sys
import os
import signal
import configparser
import threading
import subprocess
import time

try:
    from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
except ImportError:
    print("PyQt6 not found. Please install python-pyqt6.")
    sys.exit(1)

# Default Config Setup
CONFIG_DIR = os.path.expanduser("~/.config/rclone-tray-monitor")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.ini")

def load_config():
    config = configparser.ConfigParser()
    default_config = {
        "service_name": "mailbox_drive.service",
        "sync_path": os.path.expanduser("~")
    }
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)
        return {
            "service_name": config.get("Settings", "service_name", fallback=default_config["service_name"]),
            "sync_path": config.get("Settings", "sync_path", fallback=default_config["sync_path"])
        }
    return default_config

class RcloneMonitor(QObject):
    status_changed = pyqtSignal(str, str)
    
    def __init__(self, service_name):
        super().__init__()
        self.service_name = service_name
        self.status = "idle"
        self.last_message = "Starting..."
        self.is_running = True
        self.prev_log_output = ""
        
    def get_log(self):
        try:
            result = subprocess.run(
                ["journalctl", "--user", "-u", self.service_name, "-n", "5", "--no-pager", "-q"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def monitor_service(self):
        while self.is_running:
            try:
                result = subprocess.run(
                    ["systemctl", "--user", "is-active", self.service_name],
                    capture_output=True, text=True, timeout=5
                )
                is_active = (result.returncode == 0)
                
                if not is_active:
                    if self.status != "error":
                        self.status = "error"
                        self.last_message = "Service stopped"
                        self.status_changed.emit(self.status, self.last_message)
                    time.sleep(2)
                    continue
                
                logs = self.get_log()
                
                if logs != self.prev_log_output:
                    self.prev_log_output = logs
                    logs_lower = logs.lower()
                    
                    if any(err in logs_lower for err in ["error", "failed", "exception"]):
                        self.status = "error"
                    elif any(kw in logs_lower for kw in ["create", "modify", "delete", "transfer"]):
                        self.status = "syncing"
                        lines = logs.split('\n')
                        message = next((line[:100] for line in reversed(lines) if line.strip() and "modtime" not in line.lower()), "Syncing...")
                        self.last_message = message
                        self.status_changed.emit(self.status, self.last_message)
                        
                        time.sleep(3)
                        if self.is_running:
                            self.status = "idle"
                    else:
                        self.status = "idle"
                    
                    lines = logs.split('\n')
                    message = next((line[:100] for line in reversed(lines) if line.strip() and "modtime" not in line.lower()), "No activity")
                    self.last_message = message
                    self.status_changed.emit(self.status, self.last_message)
                
                time.sleep(1)
            except Exception as e:
                time.sleep(2)

class IconGenerator:
    @staticmethod
    def create_icon(status, animation_frame=0):
        import math
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        colors = {
            "idle": QColor(76, 175, 80),
            "syncing": QColor(255, 193, 7),
            "error": QColor(244, 67, 54),
        }
        color = colors.get(status, QColor(100, 100, 100))
        
        if status == "syncing":
            pulse = (1 + math.sin(animation_frame * 0.5)) / 2
            color = QColor(
                int(255 + (33 - 255) * pulse),
                int(193 + (150 - 193) * pulse),
                int(7 + (243 - 7) * pulse)
            )
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, size - 8, size - 8)
        painter.end()
        return pixmap

class TrayIconApp:
    def __init__(self, monitor, sync_path):
        self.monitor = monitor
        self.sync_path = sync_path
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.animation_frame = 0
        
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(QIcon(IconGenerator.create_icon("idle", 0)))
        
        self.create_menu()
        self.monitor.status_changed.connect(self.on_status_changed)
        
        self.tooltip_timer = QTimer()
        self.tooltip_timer.timeout.connect(self.update_tooltip)
        self.tooltip_timer.start(1000)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_icon)
        
        self.tray_icon.show()
        self.update_tooltip()
    
    def animate_icon(self):
        if self.monitor.status == "syncing":
            self.animation_frame += 1
            self.tray_icon.setIcon(QIcon(IconGenerator.create_icon(self.monitor.status, self.animation_frame)))
        else:
            self.animation_timer.stop()
    
    def create_menu(self):
        menu = QMenu()
        self.status_action = menu.addAction("Status: IDLE")
        self.status_action.setEnabled(False)
        self.message_action = menu.addAction("📝 No activity")
        self.message_action.setEnabled(False)
        menu.addSeparator()
        
        menu.addAction("📁 Open Folder", self.open_folder)
        menu.addAction("📋 View Logs", self.open_logs)
        menu.addAction("⏸️ Stop Service", self.stop_service)
        menu.addAction("▶️ Start Service", self.start_service)
        menu.addSeparator()
        menu.addAction("❌ Quit", self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
    
    def on_status_changed(self, status, message):
        self.animation_frame = 0
        if status == "syncing":
            if not self.animation_timer.isActive():
                self.animation_timer.start(100)
        else:
            if self.animation_timer.isActive():
                self.animation_timer.stop()
            self.tray_icon.setIcon(QIcon(IconGenerator.create_icon(status, 0)))
        
        self.status_action.setText(f"Status: {status.upper()}")
        self.message_action.setText(f"📝 {message}")
        self.update_tooltip()

    def update_tooltip(self):
        titles = {
            "idle": f"🟢 Mailbox - Idle\n{self.monitor.last_message}",
            "syncing": f"🟡 Mailbox - Syncing\n{self.monitor.last_message}",
            "error": f"🔴 Mailbox - Error\n{self.monitor.last_message}",
        }
        self.tray_icon.setToolTip(titles.get(self.monitor.status, "Mailbox Monitor"))
    
    def open_folder(self):
        path = self.sync_path if os.path.exists(self.sync_path) else os.path.expanduser("~")
        subprocess.Popen(["xdg-open", path])
    
    def open_logs(self):
        terminals = [["konsole", "-e"], ["gnome-terminal", "--"], ["xfce4-terminal", "-e"], ["xterm", "-e"]]
        cmd = ["journalctl", "--user", "-u", self.monitor.service_name, "-f"]
        for term in terminals:
            try:
                subprocess.Popen(term + cmd)
                return
            except FileNotFoundError:
                continue

    def stop_service(self):
        subprocess.run(["systemctl", "--user", "stop", self.monitor.service_name])
    
    def start_service(self):
        subprocess.run(["systemctl", "--user", "start", self.monitor.service_name])
    
    def quit_app(self):
        self.monitor.is_running = False
        self.app.quit()
    
    def run(self):
        self.app.exec()

def main():
    cfg = load_config()
    
    monitor = RcloneMonitor(cfg["service_name"])
    monitor_thread = threading.Thread(target=monitor.monitor_service, daemon=True)
    monitor_thread.start()
    
    app = TrayIconApp(monitor, cfg["sync_path"])
    
    # Catch SIGINT (Ctrl+C) and SIGTERM cleanly
    signal.signal(signal.SIGINT, lambda *args: app.quit_app())
    signal.signal(signal.SIGTERM, lambda *args: app.quit_app())
    
    app.run()

if __name__ == "__main__":
    main()
