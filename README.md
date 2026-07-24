# Rclone Tray Monitor

A lightweight system tray monitor for **rclone** services on Linux.

It watches an **rclone systemd user service**, displays its current status in the system tray with colors and animations, and provides quick access to logs, your synchronized folder, and service controls.

Originally developed for **Mailbox.org WebDAV** and **OX Drive**. It can be adapted to **any rclone service**.

## Features

- 🟢 **Green** tray icon when idle
- 🟡 **Yellow-Blue pulsing** animation while syncing (3 seconds minimum)
- 🔴 **Red** tray icon on errors or when service is stopped
- Live tooltip showing status and recent activity (Modtime warnings filtered out)
- View systemd journal logs in real-time
- Restart the rclone service from menu
- Open the synchronized folder from menu
- Lightweight, fast, and native PyQt6 application
- Works great on KDE Plasma, GNOME, and other Linux desktops

---

## Quick Start (Easiest Way)

### Automated Installation with Script

This is the easiest way - the script does everything for you!

1. **Download all files** to a folder:
   - `rclone_tray_monitor.py`
   - `install.sh`
   - `README.md`

2. **Run the installer:**
   ```bash
   bash install.sh
   ```

3. **Answer the questions** (the script will ask for):
   - Your rclone service name
   - Your sync folder path

4. **Done!** Log out and back in, or run manually:
   ```bash
   ~/.local/bin/rclone_tray_monitor.py
   ```

The script automatically:
- ✓ Installs PyQt6 if needed
- ✓ Finds your rclone services
- ✓ Configures everything
- ✓ Sets up autostart on login

**That's it! No manual editing needed.**

---

## Requirements

- **Python 3** (3.7+)
- **PyQt6** (installer will install this automatically)
- **rclone** (with configured remote)
- **systemd** (user service)
- Linux desktop with system tray support (KDE, GNOME, etc.)

---

## Manual Installation (If You Prefer)

If you don't want to use the automatic installer, you can set up manually:

### Step 1: Install Dependencies

**Arch / Manjaro:**
```bash
sudo pacman -S python-pyqt6
```

**Ubuntu / Debian:**
```bash
sudo apt install python3-pyqt6
```

**Fedora:**
```bash
sudo dnf install python3-pyqt6
```

### Step 2: Download the Script

Create a directory for the script:
```bash
mkdir -p ~/.local/bin
```

Copy `rclone_tray_monitor.py` to `~/.local/bin/`:
```bash
cp rclone_tray_monitor.py ~/.local/bin/
chmod +x ~/.local/bin/rclone_tray_monitor.py
```

### Step 3: Configure for Your Service

Edit the script to match your setup:
```bash
nano ~/.local/bin/rclone_tray_monitor.py
```

Find and modify these lines (around line 32-35):

```python
self.service_name = "mailbox_drive.service"  # Change to your service name
```

And in the `open_ox_drive()` method (around line 310), change the path:

```python
ox_path = "/home/username/Data/OX Drive/"  # Change to your sync folder path
```

**How to find your service name:**
```bash
systemctl --user list-units | grep -i rclone
# Or for your specific service:
systemctl --user list-units | grep -i your_service_name
```

### Step 4: Test It

Run the script manually to test:
```bash
~/.local/bin/rclone_tray_monitor.py
```

You should see:
- `[INIT] Starting Rclone Mailbox Monitor (Qt/KDE version)`
- `[START] Monitor thread started`
- `[UI] Tray icon created`
- A colored circle appearing in your system tray

Press `Ctrl+C` to stop it.

### Step 5: Auto-Start on Login

Create the autostart file:
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/rclone-mailbox-monitor.desktop
```

Paste this content (change `username` to your actual username):

```ini
[Desktop Entry]
Type=Application
Name=Rclone Mailbox Monitor
Comment=Monitor rclone mailbox_drive service
Exec=/home/username/.local/bin/rclone_tray_monitor.py
Icon=folder-sync
Terminal=false
Categories=Utility;System;
StartupNotify=false
X-GNOME-Autostart-enabled=true
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Log Out and Back In

The monitor will automatically start on your next login. Or restart it manually:
```bash
~/.local/bin/rclone_tray_monitor.py
```

---

## Configuration Guide

### Finding Your Service Name

```bash
# List all user services
systemctl --user list-units | grep -i service

# Or search for rclone specifically
systemctl --user list-units | grep -i rclone
```

Example output:
```
mailbox_drive.service         loaded active running   RCloud mailbox_drive
```

Use `mailbox_drive.service` (everything before the status)

### Finding Your Sync Folder

```bash
# Check your rclone config
cat ~/.config/rclone/rclone.conf

# Look for the local path in your service file
systemctl --user cat your_service_name.service
```

Or just use `ls` to browse:
```bash
ls ~/
# Find your sync folder and note the full path
```

### Complete Configuration Example

For **OX Drive on Mailbox.org**, the config would be:

```python
self.service_name = "mailbox_drive.service"
```

And in `open_ox_drive()`:
```python
ox_path = "/home/username/Data/OX Drive/"
```

---

## Usage

### System Tray Icon

The icon shows your service status:

- 🟢 **Green** = Service idle, all good
- 🟡 **Yellow-Blue pulsing** = Files syncing right now
- 🔴 **Red** = Error or service stopped

### Right-Click Menu

- **Status** - Shows current state (IDLE, SYNCING, ERROR)
- **Message** - Latest log line (helpful for debugging)
- **📁 Open OX Drive** - Opens your sync folder in file manager
- **📋 View Logs** - Opens live journalctl logs in terminal
- **🔄 Restart Service** - Restarts the rclone service
- **❓ Help** - Shows help text with removal instructions
- **❌ Quit** - Stops the monitor

### Hover Tooltip

When you hover over the icon, you'll see:
```
🟡 Mailbox - Syncing
/home/username/Data/OX Drive/some_file.txt
```

---

## Troubleshooting

### Icon doesn't appear in tray

1. Make sure PyQt6 is installed:
   ```bash
   python3 -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
   ```

2. Try running manually to see error messages:
   ```bash
   ~/.local/bin/rclone_tray_monitor.py
   ```

3. Check if your desktop supports system tray:
   ```bash
   # Should not be empty
   echo $XDG_CURRENT_DESKTOP
   ```

### Service not detected

1. Verify service exists and is running:
   ```bash
   systemctl --user status mailbox_drive.service
   ```

2. Check service name is correct in script:
   ```bash
   systemctl --user is-active mailbox_drive.service
   # Should return: active
   ```

3. View recent service logs:
   ```bash
   journalctl --user -u mailbox_drive.service -n 20
   ```

### Icon always red (says "Service stopped")

The service might be inactive. Start it:
```bash
systemctl --user start mailbox_drive.service
```

Check its status:
```bash
systemctl --user status mailbox_drive.service
```

### Modtime warnings showing in tooltip

The script already filters these out. If still seeing them, check your rclone config:
```bash
nano ~/.config/rclone/rclone.conf
```

Look for `--checksum` flag in your remote config.

---

## Uninstall

Remove everything with:

```bash
rm ~/.config/autostart/rclone-mailbox-monitor.desktop
rm ~/.local/bin/rclone_tray_monitor.py
```

Log out and back in, or restart your desktop environment.

---

## Reinstall

If you deleted it and want it back:

```bash
cp rclone_tray_monitor.py ~/.local/bin/
cp rclone-mailbox-monitor.desktop ~/.config/autostart/
chmod +x ~/.local/bin/rclone_tray_monitor.py
```

Then log out and back in.

---

## For Different Services

### Using with Nextcloud instead of Mailbox.org

1. Change service name:
   ```python
   self.service_name = "nextcloud_sync.service"
   ```

2. Change folder path:
   ```python
   ox_path = "/home/username/Nextcloud/"
   ```

3. (Optional) Change display name in Help menu

### Using with Google Drive / OneDrive

Same process - just use your actual service name and folder path.

**To find your service:**
```bash
systemctl --user list-units | grep -i sync
```

---

## How It Works

1. **Monitor Thread**: Runs in background, checks `journalctl` logs every 1-2 seconds
2. **Status Detection**: 
   - Detects file operations (CREATE, MODIFY, DELETE) = Syncing
   - Detects errors in logs = Error state
   - No activity = Idle
3. **Animation Thread**: Updates icon smoothly every 100ms
4. **UI Thread**: PyQt6 handles menu and tray icon display

Everything is non-blocking - your system stays responsive.

---

## Screenshots

### Idle (Green)
System tray shows green circle

### Syncing (Yellow-Blue Pulse)
System tray shows pulsing yellow-to-blue animation for 3 seconds minimum

### Error (Red)
System tray shows red circle when service has errors or is stopped

### Menu
Right-click shows status, folder link, log viewer, and service controls

---

## Notes

- The monitor continues running even when you close the terminal (it's in the tray)
- Clicking the tray icon won't do anything by design (right-click for menu instead)
- The 3-second minimum sync time ensures you see the animation even for quick syncs
- Modtime warnings are automatically filtered from displayed messages
- The script is safe to stop at any time with `Ctrl+C` or via the Quit menu option

---

## License

MIT - Feel free to modify and distribute

---

## Support

If you have issues:

1. Run manually and check output:
   ```bash
   ~/.local/bin/rclone_tray_monitor.py
   ```

2. Check logs:
   ```bash
   journalctl --user -u your_service_name.service -n 50 -e
   ```

3. Verify service is working:
   ```bash
   systemctl --user status your_service_name.service
   ```

Happy syncing! 🚀

### Step 1: Install Dependencies

**Arch / Manjaro:**
```bash
sudo pacman -S python-pyqt6
```

**Ubuntu / Debian:**
```bash
sudo apt install python3-pyqt6
```

**Fedora:**
```bash
sudo dnf install python3-pyqt6
```

### Step 2: Download the Script

Create a directory for the script:
```bash
mkdir -p ~/.local/bin
```

Copy `rclone_tray_monitor.py` to `~/.local/bin/`:
```bash
cp rclone_tray_monitor.py ~/.local/bin/
chmod +x ~/.local/bin/rclone_tray_monitor.py
```

### Step 3: Configure for Your Service

Edit the script to match your setup:
```bash
nano ~/.local/bin/rclone_tray_monitor.py
```

Find and modify these lines (around line 32-35):

```python
self.service_name = "mailbox_drive.service"  # Change to your service name
```

And in the `open_ox_drive()` method (around line 310), change the path:

```python
ox_path = "/home/username/Data/OX Drive/"  # Change to your sync folder path
```

**How to find your service name:**
```bash
systemctl --user list-units | grep -i rclone
# Or for your specific service:
systemctl --user list-units | grep -i your_service_name
```

### Step 4: Test It

Run the script manually to test:
```bash
~/.local/bin/rclone_tray_monitor.py
```

You should see:
- `[INIT] Starting Rclone Mailbox Monitor (Qt/KDE version)`
- `[START] Monitor thread started`
- `[UI] Tray icon created`
- A colored circle appearing in your system tray

Press `Ctrl+C` to stop it.

### Step 5: Auto-Start on Login

Create the autostart file:
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/rclone-mailbox-monitor.desktop
```

Paste this content (change `username` to your actual username):

```ini
[Desktop Entry]
Type=Application
Name=Rclone Mailbox Monitor
Comment=Monitor rclone mailbox_drive service
Exec=/home/username/.local/bin/rclone_tray_monitor.py
Icon=folder-sync
Terminal=false
Categories=Utility;System;
StartupNotify=false
X-GNOME-Autostart-enabled=true
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Log Out and Back In

The monitor will automatically start on your next login. Or restart it manually:
```bash
~/.local/bin/rclone_tray_monitor.py
```

---

## Configuration Guide

### Finding Your Service Name

```bash
# List all user services
systemctl --user list-units | grep -i service

# Or search for rclone specifically
systemctl --user list-units | grep -i rclone
```

Example output:
```
mailbox_drive.service         loaded active running   RCloud mailbox_drive
```

Use `mailbox_drive.service` (everything before the status)

### Finding Your Sync Folder

```bash
# Check your rclone config
cat ~/.config/rclone/rclone.conf

# Look for the local path in your service file
systemctl --user cat your_service_name.service
```

Or just use `ls` to browse:
```bash
ls ~/
# Find your sync folder and note the full path
```

### Complete Configuration Example

For **OX Drive on Mailbox.org**, the config would be:

```python
self.service_name = "mailbox_drive.service"
```

And in `open_ox_drive()`:
```python
ox_path = "/home/username/Data/OX Drive/"
```

---

## Usage

### System Tray Icon

The icon shows your service status:

- 🟢 **Green** = Service idle, all good
- 🟡 **Yellow-Blue pulsing** = Files syncing right now
- 🔴 **Red** = Error or service stopped

### Right-Click Menu

- **Status** - Shows current state (IDLE, SYNCING, ERROR)
- **Message** - Latest log line (helpful for debugging)
- **📁 Open OX Drive** - Opens your sync folder in file manager
- **📋 View Logs** - Opens live journalctl logs in terminal
- **🔄 Restart Service** - Restarts the rclone service
- **❓ Help** - Shows help text with removal instructions
- **❌ Quit** - Stops the monitor

### Hover Tooltip

When you hover over the icon, you'll see:
```
🟡 Mailbox - Syncing
/home/username/Data/OX Drive/some_file.txt
```

---

## Troubleshooting

### Icon doesn't appear in tray

1. Make sure PyQt6 is installed:
   ```bash
   python3 -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
   ```

2. Try running manually to see error messages:
   ```bash
   ~/.local/bin/rclone_tray_monitor.py
   ```

3. Check if your desktop supports system tray:
   ```bash
   # Should not be empty
   echo $XDG_CURRENT_DESKTOP
   ```

### Service not detected

1. Verify service exists and is running:
   ```bash
   systemctl --user status mailbox_drive.service
   ```

2. Check service name is correct in script:
   ```bash
   systemctl --user is-active mailbox_drive.service
   # Should return: active
   ```

3. View recent service logs:
   ```bash
   journalctl --user -u mailbox_drive.service -n 20
   ```

### Icon always red (says "Service stopped")

The service might be inactive. Start it:
```bash
systemctl --user start mailbox_drive.service
```

Check its status:
```bash
systemctl --user status mailbox_drive.service
```

### Modtime warnings showing in tooltip

The script already filters these out. If still seeing them, check your rclone config:
```bash
nano ~/.config/rclone/rclone.conf
```

Look for `--checksum` flag in your remote config.

---

## Uninstall

Remove everything with:

```bash
rm ~/.config/autostart/rclone-mailbox-monitor.desktop
rm ~/.local/bin/rclone_tray_monitor.py
```

Log out and back in, or restart your desktop environment.

---

## Reinstall

If you deleted it and want it back:

```bash
cp rclone_tray_monitor.py ~/.local/bin/
cp rclone-mailbox-monitor.desktop ~/.config/autostart/
chmod +x ~/.local/bin/rclone_tray_monitor.py
```

Then log out and back in.

---

## For Different Services

### Using with Nextcloud instead of Mailbox.org

1. Change service name:
   ```python
   self.service_name = "nextcloud_sync.service"
   ```

2. Change folder path:
   ```python
   ox_path = "/home/username/Nextcloud/"
   ```

3. (Optional) Change display name in Help menu

### Using with Google Drive / OneDrive

Same process - just use your actual service name and folder path.

**To find your service:**
```bash
systemctl --user list-units | grep -i sync
```

---

## How It Works

1. **Monitor Thread**: Runs in background, checks `journalctl` logs every 1-2 seconds
2. **Status Detection**: 
   - Detects file operations (CREATE, MODIFY, DELETE) = Syncing
   - Detects errors in logs = Error state
   - No activity = Idle
3. **Animation Thread**: Updates icon smoothly every 100ms
4. **UI Thread**: PyQt6 handles menu and tray icon display

Everything is non-blocking - your system stays responsive.

---

## Screenshots

### Idle (Green)
System tray shows green circle

### Syncing (Yellow-Blue Pulse)
System tray shows pulsing yellow-to-blue animation for 3 seconds minimum

### Error (Red)
System tray shows red circle when service has errors or is stopped

### Menu
Right-click shows status, folder link, log viewer, and service controls

---

## Notes

- The monitor continues running even when you close the terminal (it's in the tray)
- Clicking the tray icon won't do anything by design (right-click for menu instead)
- The 3-second minimum sync time ensures you see the animation even for quick syncs
- Modtime warnings are automatically filtered from displayed messages
- The script is safe to stop at any time with `Ctrl+C` or via the Quit menu option

---

## License

MIT - Feel free to modify and distribute

---

## Support

If you have issues:

1. Run manually and check output:
   ```bash
   ~/.local/bin/rclone_tray_monitor.py
   ```

2. Check logs:
   ```bash
   journalctl --user -u your_service_name.service -n 50 -e
   ```

3. Verify service is working:
   ```bash
   systemctl --user status your_service_name.service
   ```

Happy syncing! 🚀
