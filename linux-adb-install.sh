#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define color variables
GREEN='\033[0;32m'
GREENB='\033[1;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
REDB='\033[1;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

clear

echo -e "${CYAN}==================================================${RESET}"
echo -e "${CYAN}   Universal ADB & Fastboot Installer for Linux   ${RESET}"
echo -e "${CYAN}==================================================${RESET}"

# Function to handle privilege escalation for standard Linux (Root/Sudo check)
run_priv() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    elif command -v sudo &> /dev/null; then
        sudo "$@"
    else
        echo -e "${REDB}[!] Error: Root or sudo privileges are required to run this script.${RESET}"
        exit 1
    fi
}

# 1. Check if running inside Android Termux (Rootless USB OTG method)
if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux/files/usr" ]; then
    echo -e "${YELLOW}[*] System Detected: Termux (Android - Non-Root Method)${RESET}"
    echo -e "${REDB}[${RESET}1${REDB}] ${GREENB}Environment is being set up; please wait...${RESET}\n"
    sleep 4

    apt update -y
    apt upgrade -y
    termux-setup-storage -y
    apt install curl -y
    apt install termux-api -y
    curl -s https://raw.githubusercontent.com/nohajc/termux-adb/master/install.sh | bash

    clear
    echo -e "${CYAN}==================================================${RESET}"
    echo -e "${CYAN}        Termux ADB Installation Verification      ${RESET}"
    echo -e "${CYAN}==================================================${RESET}"

    # Verify Termux ADB & Fastboot installation
    if command -v termux-adb &> /dev/null; then
        echo -e "${GREENB}[✓] Success: termux-adb is properly installed!${RESET}"
        echo -e "${YELLOW}[i] ADB Version Details:${RESET}"
        termux-adb version | head -n 2
        echo ""
        if command -v termux-fastboot &> /dev/null; then
            echo -e "${GREENB}[✓] Success: termux-fastboot is also installed!${RESET}\n"
        fi
        echo -e "${REDB}[${RESET}*${REDB}]${REDB} Reminder: Install termux-api app (from GitHub or F-Droid)${RESET}"
        echo -e "${REDB}[${RESET}*${REDB}] ${GREENB}Environment is ready!${RESET}\n"
    elif command -v adb &> /dev/null; then
        echo -e "${GREENB}[✓] Success: ADB is properly installed!${RESET}"
        echo -e "${YELLOW}[i] ADB Version Details:${RESET}"
        adb version | head -n 2
        echo ""
        echo -e "${REDB}[${RESET}*${REDB}]${REDB} Reminder: Install termux-api app (from GitHub or F-Droid)${RESET}"
        echo -e "${REDB}[${RESET}*${REDB}] ${GREENB}Environment is ready!${RESET}\n"
    else
        echo -e "${REDB}[✗] Verification Failed: termux-adb was not installed properly.${RESET}"
        echo -e "${YELLOW}[!] Please check your internet connection and run the script again.${RESET}\n"
        exit 1
    fi
    echo -e "${CYAN}==================================================${RESET}"
    exit 0

# 2. Check for APT (Debian, Ubuntu, Kali Linux, Linux Mint, Pop!_OS)
elif command -v apt-get &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: APT (Debian/Ubuntu/Kali-based)${RESET}"
    echo -e "${GREEN}[*] Installing ADB and Fastboot...${RESET}"
    run_priv apt-get update -y
    run_priv apt-get install -y android-sdk-platform-tools adb fastboot

# 3. Check for Pacman (Arch Linux, Manjaro, EndeavourOS, Garuda)
elif command -v pacman &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: Pacman (Arch-based)${RESET}"
    echo -e "${GREEN}[*] Installing android-tools...${RESET}"
    run_priv pacman -Sy --noconfirm android-tools

# 4. Check for DNF (Fedora, RHEL, CentOS, AlmaLinux, Rocky Linux)
elif command -v dnf &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: DNF (Fedora/RHEL-based)${RESET}"
    echo -e "${GREEN}[*] Installing android-tools...${RESET}"
    run_priv dnf install -y android-tools

# 5. Check for Zypper (openSUSE Leap / Tumbleweed)
elif command -v zypper &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: Zypper (openSUSE)${RESET}"
    echo -e "${GREEN}[*] Installing android-tools...${RESET}"
    run_priv zypper --non-interactive install android-tools

# 6. Check for APK (Alpine Linux / postmarketOS)
elif command -v apk &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: APK (Alpine Linux)${RESET}"
    echo -e "${GREEN}[*] Installing android-tools...${RESET}"
    run_priv apk update
    run_priv apk add android-tools

# 7. Check for XBPS (Void Linux)
elif command -v xbps-install &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: XBPS (Void Linux)${RESET}"
    echo -e "${GREEN}[*] Installing android-tools...${RESET}"
    run_priv xbps-install -Sy android-tools

else
    echo -e "${REDB}[!] Error: Unsupported Linux distribution or package manager not found.${RESET}"
    exit 1
fi

echo -e "${CYAN}--------------------------------------------------${RESET}"

# Verify installation for standard Linux distros
if command -v adb &> /dev/null; then
    echo -e "${GREENB}[✓] Installation completed and verified successfully!${RESET}"
    echo -e "${YELLOW}[i] Installed Version:${RESET}"
    adb --version | head -n 2
else
    echo -e "${REDB}[✗] Verification Failed: ADB could not be installed.${RESET}"
    exit 1
fi
echo -e "${CYAN}==================================================${RESET}"
