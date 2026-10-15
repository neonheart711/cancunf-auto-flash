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
echo -e "${CYAN}   Universal ADB & Fastboot Installer for macOS   ${RESET}"
echo -e "${CYAN}==================================================${RESET}"

# Ensure this script is running on macOS
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo -e "${REDB}[!] Error: This script is designed exclusively for macOS.${RESET}"
    exit 1
fi

MACOS_VER=$(sw_vers -productVersion)
ARCH=$(uname -m)
echo -e "${YELLOW}[*] System Detected: macOS ${MACOS_VER} (${ARCH})${RESET}"

# 1. Check for Homebrew (Most popular macOS package manager)
if command -v brew &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: Homebrew${RESET}"
    echo -e "${GREEN}[*] Installing android-platform-tools via Homebrew...${RESET}"
    brew install --cask android-platform-tools || brew upgrade --cask android-platform-tools

# 2. Check for MacPorts
elif command -v port &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: MacPorts${RESET}"
    echo -e "${GREEN}[*] Installing android-platform-tools via MacPorts...${RESET}"
    sudo port selfupdate
    sudo port install android-platform-tools

# 3. Fallback: Direct Official Google Download (No Package Manager needed)
else
    echo -e "${YELLOW}[*] No package manager (Homebrew/MacPorts) found.${RESET}"
    echo -e "${GREEN}[*] Using Direct Official Google Repository...${RESET}"

    INSTALL_DIR="$HOME/.android-sdk-macosx"
    ZIP_FILE="/tmp/platform-tools-latest-darwin.zip"

    echo -e "${GREEN}[*] Downloading latest platform-tools for macOS...${RESET}"
    curl -L "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip" -o "$ZIP_FILE"

    echo -e "${GREEN}[*] Extracting files to ${INSTALL_DIR}...${RESET}"
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    unzip -q "$ZIP_FILE" -d "$INSTALL_DIR"
    rm -f "$ZIP_FILE"

    PT_PATH="$INSTALL_DIR/platform-tools"
    export PATH="$PATH:$PT_PATH"

    # Add to Zsh and Bash profiles permanently
    for PROFILE in "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.bashrc"; do
        if [ -f "$PROFILE" ] || [ "$PROFILE" = "$HOME/.zshrc" ]; then
            if ! grep -q "$PT_PATH" "$PROFILE" 2>/dev/null; then
                echo "" >> "$PROFILE"
                echo "# Android Platform Tools" >> "$PROFILE"
                echo "export PATH=\"\$PATH:$PT_PATH\"" >> "$PROFILE"
            fi
        fi
    done
    echo -e "${GREEN}[*] Added platform-tools to your shell PATH.${RESET}"
fi

echo -e "${CYAN}--------------------------------------------------${RESET}"

# Verify installation on macOS
if command -v adb &> /dev/null; then
    echo -e "${GREENB}[✓] Installation completed and verified successfully!${RESET}"
    echo -e "${YELLOW}[i] Installed ADB Version:${RESET}"
    adb --version | head -n 2
    echo ""
    if command -v fastboot &> /dev/null; then
        echo -e "${GREENB}[✓] Fastboot is also verified and ready!${RESET}"
    fi
else
    echo -e "${REDB}[✗] Verification Failed: ADB could not be installed.${RESET}"
    exit 1
fi
echo -e "${CYAN}==================================================${RESET}"
