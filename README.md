# Rclone Tray Monitor

A lightweight Linux system tray application for monitoring **any rclone systemd user service**.

Originally developed for **Mailbox.org WebDAV**, but it works with **Google Drive, OneDrive, Dropbox, Nextcloud, Proton Drive, WebDAV, S3, and any other rclone remote** by changing just a few configuration values.

---

## Features

- 🟢 Tray icon when idle
- 🟡 Animated icon while syncing
- 🔴 Error indication
- Live tooltip showing recent activity
- Open your sync folder
- View live service logs
- Restart the rclone service
- Lightweight and fast
- Uses `journalctl` to detect activity

---

## Requirements

- Linux
- Python 3
- PyQt6
- rclone
- systemd user service

---

## Installation

Coming soon.

---

## Configuration

The monitor can be used with **any rclone remote**.

Users only need to configure:

- Display name (shown in the tray)
- systemd service name
- Sync folder

No other code changes are required.

---

## Screenshots

### Idle

*(coming soon)*

### Syncing

*(coming soon)*

### Context Menu

*(coming soon)*

### Help

*(coming soon)*

---

## License

MIT
