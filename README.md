# ⚡ Motorola Moto G54 / G64 5G (`cancunf`) All-In-One Toolkit (GUI & CLI)

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Termux-00f0ff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.7%2B%20(Zero%20Extra%20Pip%20Deps)-10b981?style=for-the-badge)
![Device](https://img.shields.io/badge/Device-Moto%20G54%20%2F%20G64%205G%20(cancunf)-f43f5e?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-a855f7?style=for-the-badge)

A complete, cross-platform flashing and rooting suite built exclusively for the **Motorola Moto G54 5G** and **Motorola Moto G64 5G** (codename: **`cancunf`**). It features both a modern **Cyberpunk Studio Graphical User Interface (GUI)** and an interactive **Command Line Interface (CLI)**, running natively on **Windows (7/8/10/11)**, **Linux**, **macOS**, and **Android Termux** with **zero external Python package requirements**.

---

## ⚠️ IMPORTANT DISCLAIMER & SAFETY WARNING

> **READ CAREFULLY BEFORE USE:**
> 1. **Strict Device Exclusivity**: This software is engineered **ONLY** for the **Motorola Moto G54 5G and Moto G64 5G (`cancunf`)**. Do **NOT** attempt to use this tool on any other device model.
> 2. **No Liability / Use at Your Own Risk**: Flashing Custom ROMs, Stock Firmware, or Root images involves sensitive system-level operations that carry an inherent risk of bricking your device, causing bootloops, voiding your warranty, or erasing personal data.
> 3. **User Responsibility**: By using this software, you agree that **you are doing so entirely at your own risk**. Neither the developer (`neonheart711`) nor any upstream contributors or guide authors (`CyberKnight777`, `nohajc`, Google, or Motorola) hold any responsibility if your device is damaged, bricked, or rendered unusable. Always back up your personal data and ensure your battery is charged above **50%** before proceeding.

---

## ✨ Key Features

### 🖥️ Dual Interface (CANCUNF Studio GUI + Interactive CLI)
- **Modern Cyberpunk Dashboard GUI**:
  - Built using pure Python `tkinter` / `ttk` (`clam` engine) for consistent dark-mode styling across Windows, Linux, and macOS without extra third-party GUI dependencies.
  - **Sidebar Navigation & Live File Validation**: Instant file/folder verification badges (`✓ Ready` with file size in MB, or `✗ Incomplete/Missing` with exact partition count).
  - **One-Click Quick Reboot Bar**: Check live device connection status (`Bootloader`, `FastbootD`, or `ADB`) and reboot directly to **Bootloader**, **FastbootD**, **Recovery**, or **System** with a single click.
  - **Live Terminal Telemetry Console**: Resizable split-pane console with timestamps (`[HH:MM:SS]`), dynamic progress bar (tracks `adb sideload` percentages and `super` sparsechunk counts), **Stop / Abort Task** button, **Copy Log**, and **Save Log (`.txt`)**.
- **Interactive CLI Mode**:
  - Fast, color-coded terminal menu interface with built-in ANSI fallback (runs even if `colorama` is not installed).
  - Automatically activates on **Android Termux** where desktop GUI is unavailable.

### ⚙️ Universal & Portable Platform Tools Setup
- **⚡ 1-Click Portable Auto-Downloader (GUI)**: Downloads and extracts the latest official Google `platform-tools` (`adb` & `fastboot`) directly into the toolkit folder—no Administrator or `sudo` privileges required.
- **System Package Manager Scripts**:
  - **Windows (7/8/10/11)**: Auto-elevates to Administrator, installs via `winget`, `choco`, or `scoop`, or extracts directly from Google's repository to `C:\adb\platform-tools` and updates System `PATH`.
  - **Linux**: Auto-detects `apt`, `pacman`, `dnf`, `zypper`, `apk`, or `xbps`.
  - **Android Termux (Non-Root OTG)**: Configures `termux-api` and `termux-adb` / `termux-fastboot` for rootless USB OTG flashing from another Android phone.
  - **macOS**: Supports `Homebrew`, `MacPorts`, or direct Google Darwin binary setup.

### 🚀 Safe Custom ROM Flasher & Updater
- **Clean Flash Workflow**: Follows the official `cancunf` flashing instructions:
  1. Reboots from Bootloader into **FastbootD (Userspace Fastboot)**.
  2. Strictly polls and verifies `is-userspace: yes` to prevent accidental Bootloader flashing.
  3. Flashes the `initial_install.zip` (`boot` + `vendor_boot`).
  4. Reboots to Recovery and prompts for **Wipe data / Factory reset**.
  5. Verifies `adb devices` in **sideload** mode before executing `adb sideload <rom.zip>`.
- **Dirty Flash / Second-Slot Sideload**: Easily sideload ROM updates or perform the second-pass sideload required when upgrading from pre-May 2024 (Android 14) stock firmware.

### 🛠️ Dynamic Full Clean Stock Firmware Flasher (Slot A & Slot B)
- **Strict Pre-Flight Verification**: Before running a single fastboot command, verifies that all **21 mandatory firmware images** (`PGPT`, `preloader.img`, `lk.img`, `tee.img`, `mcupm.img`, `pi_img.img`, `sspm.img`, `dtbo.img`, `logo.img`, `spmfw.img`, `scp.img`, `vbmeta.img`, `vbmeta_system.img`, `md1img.img`, `dpm.img`, `gz.img`, `vcp.img`, `gpueb.img`, `efuse.img`, `boot.img`, `vendor_boot.img`) are present in the selected folder to prevent partial flashes or bricks.
- **Dynamic Sparsechunk Sorting**: Automatically detects and numerically sorts all `super.img_sparsechunk.*` files (`0` through `17`, `18`, `21`, or higher) across Android 13, 14, and 15+ stock builds.
- **Full Dual-Slot Restore**: Clean flashes both **Slot A** and **Slot B**, erases `nvdata`, `userdata`, `metadata`, `debug_token`, and clears OEM fastboot flags.

### 🔓 Root Helper
- Flash Magisk, KernelSU, or APatch patched `.img` files directly to **`boot`**, **`init_boot`**, or **`vendor_boot`** partitions.

---

## 📂 Project Structure

```text
cancunf-auto-flash/
├── app.py                    # Main Launcher (Auto-detects OS/Termux, selects GUI or CLI)
├── gui_app.py                # CANCUNF Studio Graphical User Interface (Pure Tkinter/TTK)
├── custom_rom_flash.py       # Core Backend Engine (Custom ROM, Stock ROM, Root & Safety Checks)
├── linux-adb-install.sh      # Universal Linux & Termux (Rootless OTG) ADB/Fastboot Installer
├── mac-adb-install.sh        # macOS ADB/Fastboot Installer (Brew, MacPorts, Direct)
├── windows-adb-install.bat   # Windows 7/8/10/11 ADB/Fastboot Auto-Installer
├── README.md                 # Project Documentation
└── LICENSE                   # MIT License
```

---

## 🚀 How to Run

### Method 1: Run Directly with Python (Zero Extra `pip` Packages Required!)
The toolkit runs out-of-the-box with standard Python 3 (optional: install `colorama` for enhanced CLI colors on older terminals):

```bash
# Clone the repository
git clone [https://github.com/neonheart711/cancunf-auto-flash.git](https://github.com/neonheart711/cancunf-auto-flash.git)
cd cancunf-auto-flash

# Launch interactive mode selector (Choose GUI or CLI)
python app.py

# Launch CANCUNF Studio GUI directly
python app.py --gui

# Launch CLI Mode directly (Default on Android Termux)
python app.py --cli
```

---


## 🙏 Credits & Acknowledgments

- **[CyberKnight777](https://cyberknight777.dev/instructions/cancunf/)**: Special thanks and credit for the official Motorola Moto G54 / G64 (`cancunf`) Custom ROM installation guide and FastbootD workflow instructions.
- **[nohajc (`termux-adb`)](https://github.com/nohajc/termux-adb)**: For enabling rootless ADB & Fastboot over USB OTG inside Android Termux.
- **Google AOSP & Motorola Mobility**: For the official Android SDK Platform Tools (`adb` & `fastboot`) and stock partition flashing sequences.
- **Developer & Maintainer**: **Aman (`neonheart711`)** — Toolkit architecture, cross-platform installers, CANCUNF Studio GUI, and safety automation.

---

## 📄 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
