#!/bin/bash

# Rclone Tray Monitor - Easy Installer
# This script sets up everything needed to run the monitor

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       RCLONE TRAY MONITOR - INSTALLATION SCRIPT                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ ! "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${RED}✗ This script only works on Linux${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Checking Python installation${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3 first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found$(NC)"
echo ""

echo -e "${BLUE}Step 2: Checking PyQt6 installation${NC}"
if python3 -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null; then
    echo -e "${GREEN}✓ PyQt6 already installed${NC}"
else
    echo -e "${YELLOW}! PyQt6 not found. Installing...${NC}"
    
    # Detect distro and install PyQt6
    if command -v pacman &> /dev/null; then
        echo -e "${BLUE}  Installing for Arch/Manjaro...${NC}"
        sudo pacman -S python-pyqt6
    elif command -v apt &> /dev/null; then
        echo -e "${BLUE}  Installing for Ubuntu/Debian...${NC}"
        sudo apt install python3-pyqt6
    elif command -v dnf &> /dev/null; then
        echo -e "${BLUE}  Installing for Fedora...${NC}"
        sudo dnf install python3-pyqt6
    else
        echo -e "${RED}✗ Could not detect package manager. Please install PyQt6 manually.${NC}"
        echo "  Arch: sudo pacman -S python-pyqt6"
        echo "  Ubuntu: sudo apt install python3-pyqt6"
        echo "  Fedora: sudo dnf install python3-pyqt6"
        exit 1
    fi
    echo -e "${GREEN}✓ PyQt6 installed${NC}"
fi
echo ""

echo -e "${BLUE}Step 3: Finding rclone services${NC}"
services=$(systemctl --user list-units 2>/dev/null | grep -i "service.*rclone\|service.*sync" | awk '{print $1}' | head -5)

if [ -z "$services" ]; then
    echo -e "${YELLOW}! No rclone services found in systemd${NC}"
    echo "  Services found:"
    systemctl --user list-units | grep "service" | head -5
    
    read -p "Enter your service name (e.g., mailbox_drive.service): " service_name
else
    echo -e "${GREEN}Found these services:${NC}"
    echo "$services" | nl
    echo ""
    read -p "Enter service number or name (default: 1): " service_choice
    
    if [ -z "$service_choice" ]; then
        service_name=$(echo "$services" | head -1)
    elif [[ "$service_choice" =~ ^[0-9]+$ ]]; then
        service_name=$(echo "$services" | sed -n "${service_choice}p")
    else
        service_name="$service_choice"
    fi
fi

# Verify service exists
if ! systemctl --user is-active --quiet "$service_name" 2>/dev/null && ! systemctl --user cat "$service_name" &>/dev/null; then
    echo -e "${YELLOW}⚠ Warning: Service '$service_name' not found or not active${NC}"
    read -p "Continue anyway? (y/n): " continue_choice
    if [[ "$continue_choice" != "y" ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓ Using service: $service_name${NC}"
echo ""

echo -e "${BLUE}Step 4: Finding sync folder${NC}"
# Try to find the sync folder from systemd service
if systemctl --user cat "$service_name" &>/dev/null; then
    # Extract possible paths from service file
    possible_paths=$(systemctl --user cat "$service_name" | grep -oP '/home/[^/\s]+/[^\s]+' | sort -u)
    
    if [ ! -z "$possible_paths" ]; then
        echo -e "${GREEN}Found possible paths:${NC}"
        echo "$possible_paths" | nl
        read -p "Enter path number or custom path (default: 1): " path_choice
        
        if [ -z "$path_choice" ]; then
            sync_folder=$(echo "$possible_paths" | head -1)
        elif [[ "$path_choice" =~ ^[0-9]+$ ]]; then
            sync_folder=$(echo "$possible_paths" | sed -n "${path_choice}p")
        else
            sync_folder="$path_choice"
        fi
    else
        read -p "Enter your sync folder path (e.g., /home/username/Data/OX Drive/): " sync_folder
    fi
else
    read -p "Enter your sync folder path (e.g., /home/username/Data/OX Drive/): " sync_folder
fi

# Normalize path
sync_folder="${sync_folder%/}/"  # Ensure trailing slash

if [ ! -d "${sync_folder%/}" ]; then
    echo -e "${YELLOW}⚠ Warning: Folder '$sync_folder' does not exist yet${NC}"
fi

echo -e "${GREEN}✓ Sync folder: $sync_folder${NC}"
echo ""

echo -e "${BLUE}Step 5: Creating directories${NC}"
mkdir -p ~/.local/bin
mkdir -p ~/.config/autostart
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

echo -e "${BLUE}Step 6: Setting up script${NC}"

# Find the script file
if [ -f "./rclone_tray_monitor.py" ]; then
    script_source="./rclone_tray_monitor.py"
elif [ -f "rclone_tray_monitor.py" ]; then
    script_source="rclone_tray_monitor.py"
else
    echo -e "${RED}✗ rclone_tray_monitor.py not found in current directory${NC}"
    exit 1
fi

# Copy and modify the script
cp "$script_source" ~/.local/bin/rclone_tray_monitor.py

# Modify service name and path in the script
sed -i "s|self.service_name = \"mailbox_drive.service\"|self.service_name = \"$service_name\"|g" ~/.local/bin/rclone_tray_monitor.py
sed -i "s|ox_path = \"/home/username/Data/OX Drive/\"|ox_path = \"$sync_folder\"|g" ~/.local/bin/rclone_tray_monitor.py

chmod +x ~/.local/bin/rclone_tray_monitor.py
echo -e "${GREEN}✓ Script installed and configured${NC}"
echo ""

echo -e "${BLUE}Step 7: Creating autostart entry${NC}"

# Get username
username=$USER
home_dir=$HOME

# Create desktop file
cat > ~/.config/autostart/rclone-mailbox-monitor.desktop << EOF
[Desktop Entry]
Type=Application
Name=Rclone Mailbox Monitor
Comment=Monitor rclone mailbox_drive service
Exec=$home_dir/.local/bin/rclone_tray_monitor.py
Icon=folder-sync
Terminal=false
Categories=Utility;System;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

echo -e "${GREEN}✓ Autostart entry created${NC}"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    INSTALLATION COMPLETE! ✓                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Configuration:"
echo -e "  Service: ${GREEN}$service_name${NC}"
echo -e "  Folder:  ${GREEN}$sync_folder${NC}"
echo ""
echo "What to do next:"
echo ""
echo "  1. Test the monitor manually:"
echo -e "     ${BLUE}~/.local/bin/rclone_tray_monitor.py${NC}"
echo ""
echo "  2. Log out and back in to auto-start the monitor on login"
echo ""
echo "  3. Or start it now in background:"
echo -e "     ${BLUE}~/.local/bin/rclone_tray_monitor.py &${NC}"
echo ""
echo "Help:"
echo "  Right-click the tray icon for menu"
echo "  Select '❓ Help' for uninstall instructions"
echo ""
echo "All done! Happy syncing 🚀"
echo ""
