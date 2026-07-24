#!/usr/bin/env python3
"""
Rclone Mailbox Drive Monitor - KDE Qt Version with proper tooltip support
"""

import sys
import threading
import subprocess
import time
from datetime import datetime

# Try to import Qt
try:
    from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    print("PyQt6 not found. Install with: sudo pacman -S python-pyqt6")
    sys.exit(1)

class RcloneMonitor(QObject):
    status_changed = pyqtSignal(str, str)  # status, message
    
    def __init__(self):
        super().__init__()
        self.service_name = "mailbox_drive.service"
        self.status = "idle"
        self.last_message = "Starting..."
        self.is_running = True
        self.prev_log_output = ""
        
    def get_log(self):
        """Get recent logs from journalctl"""
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
        """Background thread to monitor the service"""
        while self.is_running:
            try:
                # First check if service is running
                try:
                    result = subprocess.run(
                        ["systemctl", "--user", "is-active", self.service_name],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    is_active = result.returncode == 0
                except:
                    is_active = True
                
                if not is_active:
                    # Service is stopped/inactive
                    self.status = "error"
                    self.last_message = "Service stopped"
                    print(f"[MONITOR] Status: ERROR (service stopped)")
                    self.status_changed.emit(self.status, self.last_message)
                    time.sleep(2)
                    continue
                
                logs = self.get_log()
                
                # Check if logs changed (new activity)
                if logs != self.prev_log_output:
                    self.prev_log_output = logs
                    logs_lower = logs.lower()
                    
                    # Check for errors in logs
                    if "error" in logs_lower or "failed" in logs_lower or "exception" in logs_lower:
                        self.status = "error"
                        print(f"[MONITOR] Status: ERROR")
                    # Check for file operations
                    elif "create" in logs_lower or "modify" in logs_lower or "delete" in logs_lower or "transfer" in logs_lower:
                        self.status = "syncing"
                        print(f"[MONITOR] Status: SYNCING")
                        # After 3 seconds, go back to idle
                        time.sleep(3)
                        if self.is_running:
                            self.status = "idle"
                            print(f"[MONITOR] Status: IDLE (after sync)")
                    else:
                        self.status = "idle"
                        print(f"[MONITOR] Status: IDLE")
                    
                    # Extract message and filter out Modtime warning
                    lines = logs.split('\n')
                    message = ""
                    
                    # Find first non-Modtime line
                    for line in reversed(lines):
                        if line.strip() and "modtime" not in line.lower():
                            message = line[:100]
                            break
                    
                    if not message:
                        message = "No activity"
                    
                    self.last_message = message
                    print(f"[MONITOR] Message: {self.last_message}")
                    
                    # Emit signal to update UI
                    self.status_changed.emit(self.status, self.last_message)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"[MONITOR] Error: {e}")
                time.sleep(2)

class IconGenerator:
    """Generate status icons"""
    
    animation_frame = 0
    
    @staticmethod
    def create_icon(status, animation_frame=0):
        """Create a colored icon based on status"""
        import math
        
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Status colors
        colors = {
            "idle": QColor(76, 175, 80),        # Green
            "syncing": QColor(255, 193, 7),    # Yellow (base)
            "error": QColor(244, 67, 54),      # Red
        }
        
        color = colors.get(status, QColor(100, 100, 100))
        
        # Add pulsing effect for syncing - yellow to blue
        if status == "syncing":
            # Pulse between yellow and blue
            pulse = (1 + math.sin(animation_frame * 0.5)) / 2
            
            # Yellow: (255, 193, 7)
            # Blue: (33, 150, 243)
            color = QColor(
                int(255 + (33 - 255) * pulse),      # R: 255 -> 33
                int(193 + (150 - 193) * pulse),     # G: 193 -> 150
                int(7 + (243 - 7) * pulse)          # B: 7 -> 243
            )
        
        # Draw circle
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, size - 8, size - 8)
        painter.end()
        
        return pixmap

class TrayIconApp:
    def __init__(self, monitor):
        self.monitor = monitor
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.animation_frame = 0
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(QIcon(IconGenerator.create_icon("idle", 0)))
        
        # Create menu
        self.create_menu()
        
        # Connect signals
        self.monitor.status_changed.connect(self.on_status_changed)
        
        # Timer for tooltip updates
        self.tooltip_timer = QTimer()
        self.tooltip_timer.timeout.connect(self.update_tooltip)
        self.tooltip_timer.start(500)
        
        # Timer for animation updates (icon pulsing)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_icon)
        self.animation_timer.start(100)  # Update every 100ms for smooth animation
        
        # Show tray icon
        self.tray_icon.show()
        self.tray_icon.setToolTip("🟢 Mailbox - Idle")
        
        print("[UI] Tray icon created")
    
    def animate_icon(self):
        """Animate icon during syncing"""
        self.animation_frame += 1
        icon = IconGenerator.create_icon(self.monitor.status, self.animation_frame)
        self.tray_icon.setIcon(QIcon(icon))
    
    def create_menu(self):
        """Create tray icon context menu"""
        menu = QMenu()
        
        # Status display
        self.status_action = menu.addAction("Status: IDLE")
        self.status_action.setEnabled(False)
        
        self.message_action = menu.addAction("📝 No activity")
        self.message_action.setEnabled(False)
        
        menu.addSeparator()
        
        # Open OX Drive
        ox_action = menu.addAction("📁 Open OX Drive")
        ox_action.triggered.connect(self.open_ox_drive)
        
        # View Logs
        logs_action = menu.addAction("📋 View Logs")
        logs_action.triggered.connect(self.open_logs)
        
        # Restart
        restart_action = menu.addAction("🔄 Restart Service")
        restart_action.triggered.connect(self.restart_service)
        
        # Help
        help_action = menu.addAction("❓ Help")
        help_action.triggered.connect(self.show_help)
        
        menu.addSeparator()
        
        # Quit
        quit_action = menu.addAction("❌ Quit")
        quit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
    
    def on_status_changed(self, status, message):
        """Handle status change"""
        print(f"[UI] Updating status: {status}")
        
        # Reset animation frame on status change
        self.animation_frame = 0
        
        # Update icon with animation frame
        icon = IconGenerator.create_icon(status, self.animation_frame)
        self.tray_icon.setIcon(QIcon(icon))
        
        # Update menu
        self.status_action.setText(f"Status: {status.upper()}")
        self.message_action.setText(f"📝 {message}")
        
        # Update tooltip
        titles = {
            "idle": "🟢 Mailbox - Idle",
            "syncing": "🟡 Mailbox - Syncing",
            "error": "🔴 Mailbox - Error",
        }
        self.tray_icon.setToolTip(titles.get(status, "Mailbox Monitor"))
    
    def update_tooltip(self):
        """Periodically update the tooltip to show current status"""
        titles = {
            "idle": f"🟢 Mailbox - Idle\n{self.monitor.last_message}",
            "syncing": f"🟡 Mailbox - Syncing\n{self.monitor.last_message}",
            "error": f"🔴 Mailbox - Error\n{self.monitor.last_message}",
        }
        self.tray_icon.setToolTip(titles.get(self.monitor.status, "Mailbox Monitor"))
    
    def open_ox_drive(self):
        """Open OX Drive folder"""
        ox_path = "/home/username/Data/OX Drive/"
        try:
            subprocess.Popen(["dolphin", ox_path])
        except:
            try:
                subprocess.Popen(["nautilus", ox_path])
            except:
                pass
    
    def open_logs(self):
        """Open logs in terminal"""
        try:
            subprocess.Popen(["konsole", "-e", "journalctl", "--user", "-u", self.monitor.service_name, "-f"])
        except:
            try:
                subprocess.Popen(["xterm", "-e", "journalctl", "--user", "-u", self.monitor.service_name, "-f"])
            except:
                pass
    
    def restart_service(self):
        """Restart the service"""
        try:
            subprocess.run(["systemctl", "--user", "restart", self.monitor.service_name])
            self.monitor.status = "syncing"
            self.on_status_changed("syncing", "Service restarting...")
        except Exception as e:
            self.on_status_changed("error", str(e)[:50])
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║     RCLONE MAILBOX MONITOR - HELP & REMOVAL INSTRUCTIONS       ║
╚════════════════════════════════════════════════════════════════╝

STATUS COLORS:
  🟢 Green  = Idle (no activity)
  🟡 Yellow = Syncing (files transferring)
  🔴 Red    = Error

MENU OPTIONS:
  📁 Open OX Drive = Open sync folder
  📋 View Logs     = See live service activity
  🔄 Restart       = Restart the mailbox_drive service
  ❓ Help          = This message
  ❌ Quit          = Stop the monitor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TO REMOVE (Uninstall):

  rm ~/.config/autostart/rclone-mailbox-monitor.desktop
  rm ~/.local/bin/rclone_tray_monitor.py

Then log out and back in.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press Ctrl+C to close this window.
"""
        try:
            subprocess.Popen(["konsole", "-e", "bash", "-c", f"echo '{help_text}'; read"])
        except:
            try:
                subprocess.Popen(["xterm", "-e", "bash", "-c", f"echo '{help_text}'; read"])
            except:
                print(help_text)
    
    def quit_app(self):
        """Quit the application"""
        print("[QUIT] Stopping...")
        self.monitor.is_running = False
        self.app.quit()
    
    def run(self):
        """Run the application"""
        print("[START] Running Qt application")
        self.app.exec()

def main():
    print("[INIT] Starting Rclone Mailbox Monitor (Qt/KDE version)")
    
    monitor = RcloneMonitor()
    
    # Start monitor thread
    monitor_thread = threading.Thread(target=monitor.monitor_service, daemon=True)
    monitor_thread.start()
    print("[INIT] Monitor thread started")
    
    # Create and run UI
    app = TrayIconApp(monitor)
    app.run()

if __name__ == "__main__":
    main()
