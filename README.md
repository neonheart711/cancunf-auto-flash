# ⚡ Motorola Moto G54 / G64 5G (`cancunf`) All-In-One Toolkit (GUI & CLI)

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Termux-00f0ff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.7%2B%20(Zero%20Extra%20Pip%20Deps)-10b981?style=for-the-badge)
![Device](https://img.shields.io/badge/Device-Moto%20G54%20%2F%20G64%205G%20(cancunf)-f43f5e?style=for-the-badge)
![Safety](https://img.shields.io/badge/Safety-September%20ARB%20Protection-f59e0b?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-a855f7?style=for-the-badge)

A complete, cross-platform flashing, updating, and rooting studio built exclusively for the **Motorola Moto G54 5G** and **Motorola Moto G64 5G** (codename: **`cancunf`**). It features both a modern **Curved Dark Glassmorphism GUI Studio** and an interactive **Command Line Interface (CLI)**, running natively on **Windows (7/8/10/11 — 64-bit)**, **Linux**, **macOS**, and **Android Termux**.

---

## 🚨 CRITICAL WARNING: SEPTEMBER SECURITY UPDATE & ARB (ANTI-ROLLBACK)

> **MUST READ BEFORE FLASHING STOCK OR CUSTOM ROMS:**
> * **Affected Builds**: Motorola's September Security Update (`V1TDS35H.83-20-5-14` for Global and `V1TDS35H.83-20-5-8-2-1-3` for Brazil) **bumps the ARB (Anti-RollBack) counter once more!**
> 1. **DO NOT DOWNGRADE STOCK FIRMWARE**: If your device has updated to the September patch (or newer), **you CANNOT downgrade to any older Stock Firmware** (such as Android 13 or older Android 14/15 builds). Flashing an older `preloader.img` or `lk.img` on a September+ bootloader will trigger Anti-Rollback protection and **PERMANENTLY HARD BRICK (Dead Boot)** your phone!
> 2. **CUSTOM ROM BRICK RISK**: If you updated to the September security patch on Stock ROM, **do NOT flash A16 or older/incompatible Custom ROMs** — flashing them will lead to a brick! Only flash Custom ROM builds explicitly updated for September+ firmware.
> * *This toolkit includes built-in live Bootloader & XML firmware version checks in both GUI and CLI modes to warn you before flashing.*

---

## ⚠️ General Disclaimer

1. **Strict Device Exclusivity**: Engineered **ONLY** for the **Motorola Moto G54 5G and Moto G64 5G (`cancunf`)**. Do **NOT** use on any other device.
2. **Use at Your Own Risk**: Flashing firmware or root images carries inherent risks. Neither the developer (`neonheart711`) nor upstream contributors (`CyberKnight777`, `nohajc`, Google, or Motorola) hold any responsibility for bricked devices or data loss. Always back up your data and keep battery above **50%**.

---

## ✨ Key Features

* **🖥️ Modern Curved Glass GUI + Interactive CLI**:
  * **CANCUNF Studio GUI**: Android 15 / iOS dark glassmorphic interface with smooth rounded cards, pill buttons, live file/folder verification badges, 1-click Quick Reboot bar (`Bootloader`, `FastbootD`, `Recovery`, `System`), progress bar, and live terminal telemetry console.
  * **CLI Mode**: Color-coded terminal interface that automatically activates on **Android Termux** or when launched with `--cli`.
* **🛡️ September ARB & Pre-Flight Safety Shield**:
  * Queries live device bootloader & fingerprint variables (`fastboot getvar all`).
  * Automatically scans `flashfile.xml` / `servicefile.xml` inside your Stock ROM folder to display the exact target firmware build version before flashing.
  * Verifies all **21 mandatory partition images** (`PGPT`, `preloader.img`, `lk.img`, etc.) and numerically sorts all `super.img_sparsechunk.*` files (`0` to `21+`) for **Slot A & Slot B**.
* **🚀 Official Custom ROM Clean & Dirty Flasher**:
  * Enforces the official `cancunf` FastbootD workflow (`is-userspace: yes` verification ➔ `initial_install.zip` ➔ Recovery Data Wipe ➔ `adb sideload`).
* **⚡ 1-Click Portable Platform Tools Auto-Downloader**:
  * Downloads and configures official Google `adb` & `fastboot` directly inside the toolkit folder without requiring Administrator/`sudo` permissions.

---

## 📋 System Requirements & Prerequisites

### 1. Hardware & Phone Requirements
* A **Motorola Moto G54 5G** or **Moto G64 5G (`cancunf`)** with an **Unlocked Bootloader**.
* A good quality USB Data Cable (or a USB OTG adapter if flashing from another Android phone via Termux).
* **Windows Users Only**: Install [Motorola USB Drivers](https://en-us.support.motorola.com/app/usb-drivers) so your PC detects the phone in Fastboot/Bootloader mode.

### 2. Software Requirements (Only if running from Python Source Code)
> **Note:** If you download the standalone **`.exe` (Windows)**, **Linux**, or **macOS** binaries from the [Releases](https://github.com/neonheart711/cancunf-auto-flash/releases) page, **you do NOT need Python or Tkinter installed!**

If you want to run the `.py` source files directly, install **Python 3.7+** and **`tkinter`** (for GUI mode):

* **Windows (7/8/10/11)**:
  * Download and install Python from [python.org](https://www.python.org/downloads/).
  * During installation, check **"Add python.exe to PATH"** and ensure **"tcl/tk and IDLE"** (Tkinter) is ticked.
* **Ubuntu / Debian / Kali / Linux Mint**:
  * Run: `sudo apt update && sudo apt install python3 python3-tk git -y`
* **Arch Linux / Manjaro**:
  * Run: `sudo pacman -S python tk git`
* **Fedora / RHEL**:
  * Run: `sudo dnf install python3 python3-tkinter git -y`
* **macOS (via Homebrew)**:
  * Run: `brew install python python-tk git`
* **Optional CLI Color Package (All Desktop OS)**:
  * Run: `pip install colorama`

---

## 📱 Android Termux Requirements (Phone-to-Phone USB OTG Flashing)

To flash your Moto G54/G64 from another Android phone (without root) using a USB OTG cable, install both **Termux** and **Termux:API**:

1. **Download & Install Required Apps**:
   * 📥 **Termux App (F-Droid / GitHub)**: [Download Termux APK](https://github.com/termux/termux-app/releases/download/v0.118.3/termux-app_v0.118.3+github-debug_universal.apk)
   * 📥 **Termux:API App (Required for USB OTG permission)**: [Download Termux:API APK](https://github.com/termux/termux-api/releases/download/v0.53.0/termux-api-app_v0.53.0+github.debug.apk) 
   * *(⚠️ Important: Install both apps from the same source—either both from F-Droid or both from GitHub Releases. Do not mix Play Store and F-Droid builds!)*
2. **Install Python & Git inside Termux**:
   * Run: `pkg update && pkg upgrade -y && pkg install python git -y`

---

## 🚀 Installation & Usage Guide

You can use this toolkit in **two ways**: using the **Pre-Built Standalone Executables (`.exe` / Binary)** OR running directly from **Python Source Code**.

### 🏆 Method 1: Run Pre-Built Executables (`.exe` / Binary — No Python Needed!)

1. Go to the **[GitHub Releases Page](https://github.com/neonheart711/cancunf-auto-flash/releases)** and download the file for your operating system:
   * **Windows (64-bit: Win 7/8/10/11)**: `cancunf-toolkit-windows-x86-64.exe`
   * **Linux (64-bit: amd64)**: `cancunf-toolkit-linux-amd64`
   * **macOS**: `cancunf-toolkit-macos`

2. **How to Launch**:
   * **On Windows (`.exe`)**:
     * Simply **Double-Click** `cancunf-toolkit-windows-x86-64.exe` to open the selector, OR run from Command Prompt / PowerShell:
     * Interactive Selector: `cancunf-toolkit-windows-x86-64.exe`
     * Launch GUI Studio directly: `cancunf-toolkit-windows-x86-64.exe --gui`
     * Launch CLI Mode directly: `cancunf-toolkit-windows-x86-64.exe --cli`
   * **On Linux**:
     * Run: `chmod +x cancunf-toolkit-linux-amd64 && ./cancunf-toolkit-linux-amd64 --gui`
   * **On macOS**:
     * Run: `chmod +x cancunf-toolkit-macos && ./cancunf-toolkit-macos --gui`

---

### 🐍 Method 2: Run from Python Source Code (Windows / Linux / macOS / Termux)

1. **Clone the Repository**:
   * Run: `git clone https://github.com/neonheart711/cancunf-auto-flash.git`
   * Run: `cd cancunf-auto-flash`

2. **Run the Toolkit**:
   * **Interactive Mode Selector (Asks GUI or CLI)**: `python app.py`
   * **Launch GUI Studio Directly (Windows / Linux / macOS)**: `python app.py --gui`
   * **Launch CLI Mode Directly (Default on Android Termux)**: `python app.py --cli`
   * *(Note: On Linux/macOS, use `python3` if `python` is not aliased).*

---

## 🛠️ First-Time ADB & Fastboot Setup Inside the Toolkit

* **In GUI Mode**: Click **`5. Setup Platform Tools`** on the left sidebar and click **`⚡ Auto-Download Portable Platform Tools`**. It will automatically download and configure Google's official `adb` and `fastboot` inside the toolkit folder!
* **In CLI Mode / Termux**: When prompted `Do you want to setup/verify Platform Tools (ADB & Fastboot)? (Y/N):`, type **`Y`** and press Enter. On Termux, it will automatically install `termux-adb` and `termux-fastboot` for rootless USB OTG support.

---

## 📂 Project Structure

* `app.py` — Main Entry Launcher (Auto-detects OS/Termux, CLI/GUI router, September ARB alerts)
* `gui_app.py` — Modern Curved Glassmorphic Studio GUI (`tkinter` Canvas vector engine)
* `custom_rom_flash.py` — Core Backend Flashing Engine & XML/Bootloader ARB Safety Verifier
* `build.py` — Standalone PyInstaller Binary Builder Script
* `windows-adb-install.bat` — Windows 7/8/10/11 Platform Tools Auto-Installer
* `linux-adb-install.sh` — Universal Linux & Android Termux (`termux-adb`) Installer
* `mac-adb-install.sh` — macOS Platform Tools Installer
* `README.md` — Complete Documentation & Usage Guide
* `LICENSE` — MIT License

---

## 🙏 Credits & Acknowledgments

* **[CyberKnight777](https://cyberknight777.dev/instructions/cancunf/)**: Official Motorola Moto G54 / G64 (`cancunf`) Custom ROM installation guide, FastbootD workflow, and September ARB community advisories.
* **[nohajc (`termux-adb`)](https://github.com/nohajc/termux-adb)**: Rootless ADB & Fastboot over USB OTG for Android Termux.
* **[NonameBlank007](https://github.com/NonameBlank007/Cancunf_Stock_Flash_Guide)**: Stock ROM partition flashing reference for `cancunf`.
* **Google AOSP & Motorola Mobility**: Official Android SDK Platform Tools and stock firmware structure.
* **Developer & Maintainer**: **Aman (`neonheart711`)** — Toolkit architecture, cross-platform installers, Modern Glass Studio GUI, and ARB safety automation.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
