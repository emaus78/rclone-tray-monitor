#!/bin/bash

# Rclone Tray Monitor - Easy Installer
set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       RCLONE TRAY MONITOR - INSTALLATION SCRIPT                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [[ ! "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${RED}✗ This script only works on Linux${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Checking Python installation${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"
echo ""

echo -e "${BLUE}Step 2: Checking PyQt6 installation${NC}"
if python3 -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null; then
    echo -e "${GREEN}✓ PyQt6 already installed${NC}"
else
    echo -e "${YELLOW}! Installing PyQt6...${NC}"
    if command -v pacman &> /dev/null; then
        sudo pacman -S python-pyqt6
    elif command -v apt &> /dev/null; then
        sudo apt install python3-pyqt6
    elif command -v dnf &> /dev/null; then
        sudo dnf install python3-pyqt6
    else
        echo -e "${RED}✗ Please install PyQt6 manually using your package manager.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ PyQt6 installed${NC}"
fi
echo ""

echo -e "${BLUE}Step 3: Finding rclone services${NC}"
services=$(systemctl --user list-units 2>/dev/null | grep -i "service.*rclone\|service.*sync" | awk '{print $1}' | head -5)

if [ -z "$services" ]; then
    read -p "Enter your service name (e.g., mailbox_drive.service): " service_name
else
    echo -e "${GREEN}Found these services:${NC}"
    echo "$services" | nl
    read -p "Enter service number or name (default: 1): " service_choice
    
    if [ -z "$service_choice" ]; then
        service_name=$(echo "$services" | head -1)
    elif [[ "$service_choice" =~ ^[0-9]+$ ]]; then
        service_name=$(echo "$services" | sed -n "${service_choice}p")
    else
        service_name="$service_choice"
    fi
fi

echo -e "${GREEN}✓ Using service: $service_name${NC}"
echo ""

echo -e "${BLUE}Step 4: Finding sync folder${NC}"
if systemctl --user cat "$service_name" &>/dev/null; then
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
        read -p "Enter sync folder path: " sync_folder
    fi
else
    read -p "Enter sync folder path: " sync_folder
fi

sync_folder="${sync_folder%/}/"

echo -e "${GREEN}✓ Sync folder: $sync_folder${NC}"
echo ""

echo -e "${BLUE}Step 5: Installing binary & configuration${NC}"
mkdir -p ~/.local/bin
mkdir -p ~/.config/autostart
mkdir -p ~/.config/rclone-tray-monitor

cp rclone_tray_monitor.py ~/.local/bin/rclone_tray_monitor.py
chmod +x ~/.local/bin/rclone_tray_monitor.py

# Generate config.ini cleanly
cat > ~/.config/rclone-tray-monitor/config.ini << EOF
[Settings]
service_name = $service_name
sync_path = $sync_folder
EOF

echo -e "${GREEN}✓ Configuration saved to ~/.config/rclone-tray-monitor/config.ini${NC}"
echo ""

echo -e "${BLUE}Step 6: Creating autostart entry${NC}"
cat > ~/.config/autostart/rclone-mailbox-monitor.desktop << EOF
[Desktop Entry]
Type=Application
Name=Rclone Mailbox Monitor
Comment=Monitor rclone $service_name service
Exec=$HOME/.local/bin/rclone_tray_monitor.py
Icon=utilities-system-monitor
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
