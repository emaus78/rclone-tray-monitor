# Rclone Tray Monitor

A lightweight system tray monitor for **rclone** services on Linux.

It watches an **rclone systemd user service**, displays its current status in the system tray, and provides quick access to logs, your synchronized folder, and service controls.

Originally developed for **Mailbox.org WebDAV**. It can be adapted to other rclone services by changing the service name, folder path, and displayed name.

## Features

- 🟢 Green tray icon when idle
- 🟡 Animated tray icon while syncing
- 🔴 Red tray icon on errors
- Live tooltip showing recent activity
- View systemd journal logs
- Restart the rclone service
- Open the synchronized folder
- Lightweight and fast
- Native PyQt6 application
- Designed for Linux desktops

---

## Requirements

- Python 3
- PyQt6
- rclone
- systemd (user service)
- Linux desktop with system tray support

---

## Configuration

The monitor can be used with **any rclone remote**.

Users only need to configure:

- Display name (shown in the tray)
- systemd service name
- Sync folder

No other code changes are required.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/emaus78/rclone-tray-monitor.git
cd rclone-tray-monitor
```

Install PyQt6.

Arch / Manjaro:

```bash
sudo pacman -S python-pyqt6
```

Ubuntu:

```bash
sudo apt install python3-pyqt6
```

Run:

```bash
python3 rclone_tray_monitor.py
```
## Configuration

The application is configured for my personal Mailbox.org setup.

To use it with your own rclone service, edit:

- systemd service name
- synchronized folder path
- display name shown in the tray

No other code changes should be required.

## Screenshots

### Idle

![](images/idle.png)

### Syncing

![](images/syncing.png)

### Context Menu

![](images/menu.png)

### Help

![](images/help.png)
---

## Roadmap

- [ ] Configuration file
- [ ] Automatic installer
- [ ] Better desktop detection
- [ ] Generic configuration
- [ ] Improved service monitoring

## License

MIT
