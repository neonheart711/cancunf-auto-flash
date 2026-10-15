#!/usr/bin/env bash

set -e

GREEN='\033[0;32m'
GREENB='\033[1;32m'
CYAN='\033[0;36m'
REDB='\033[1;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

clear

echo -e "${CYAN}==================================================${RESET}"
echo -e "${CYAN}   Universal ADB & Fastboot Installer for macOS   ${RESET}"
echo -e "${CYAN}==================================================${RESET}"

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo -e "${REDB}[!] Error: This script is designed exclusively for macOS.${RESET}"
    exit 1
fi

if command -v brew &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: Homebrew${RESET}"
    brew install --cask android-platform-tools || brew upgrade --cask android-platform-tools
elif command -v port &> /dev/null; then
    echo -e "${YELLOW}[*] Package Manager Detected: MacPorts${RESET}"
    sudo port selfupdate
    sudo port install android-platform-tools
else
    echo -e "${YELLOW}[*] Using Direct Official Google Repository...${RESET}"
    INSTALL_DIR="$HOME/.android-sdk-macosx"
    ZIP_FILE="/tmp/platform-tools-latest-darwin.zip"

    curl -L "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip" -o "$ZIP_FILE"
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    unzip -q "$ZIP_FILE" -d "$INSTALL_DIR"
    rm -f "$ZIP_FILE"

    PT_PATH="$INSTALL_DIR/platform-tools"
    export PATH="$PATH:$PT_PATH"

    for PROFILE in "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.bashrc"; do
        if [ -f "$PROFILE" ] || [ "$PROFILE" = "$HOME/.zshrc" ]; then
            if ! grep -q "$PT_PATH" "$PROFILE" 2>/dev/null; then
                echo -e "\n# Android Platform Tools\nexport PATH=\"\$PATH:$PT_PATH\"" >> "$PROFILE"
            fi
        fi
    done
fi

echo -e "${CYAN}--------------------------------------------------${RESET}"

if command -v adb &> /dev/null; then
    echo -e "${GREENB}[✓] Installation completed and verified successfully!${RESET}"
    adb --version | head -n 2
else
    echo -e "${REDB}[✗] Verification Failed: ADB could not be installed.${RESET}"
    exit 1
fi
echo -e "${CYAN}==================================================${RESET}"
