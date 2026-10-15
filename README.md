# Motorola Moto G54 / G64 5G (`cancunf`) All-In-One Toolkit (GUI & CLI)

A complete, cross-platform flashing and rooting software built exclusively for the **Motorola Moto G54 5G** and **Motorola Moto G64 5G** (codename: **`cancunf`**). It features both a **Graphical User Interface (GUI)** and an interactive **Command Line Interface (CLI)**, running natively on **Windows (7/8/10/11)**, **Linux**, **macOS**, and **Android Termux** with **zero external Python package requirements**.

---

## ⚠️ IMPORTANT DISCLAIMER & SAFETY WARNING

> **READ CAREFULLY BEFORE USE:**
> 1. **Device Exclusivity**: This software is strictly designed **ONLY** for the **Motorola Moto G54 5G and Moto G64 5G (`cancunf`)**. Do NOT attempt to use this tool on any other device model.
> 2. **No Liability / Own Risk**: Flashing Custom ROMs, Stock Firmware, or Root images involves sensitive system-level operations that carry an inherent risk of bricking your device, causing bootloops, voiding your warranty, or erasing personal data.
> 3. **User Responsibility**: By using this software, you agree that **you are doing so entirely at your own risk**. Neither the author (`neonheart711`) nor any upstream contributors or guide authors hold any responsibility if your device is damaged, bricked, or rendered unusable.

---

## ✨ Key Features

- **Dual Interface (GUI + CLI)**:
  - **GUI Mode**: Built with native Python `tkinter` (no third-party GUI packages required) featuring a real-time terminal log console.
  - **CLI Mode**: Fast terminal menu interface; automatically activates on **Android Termux** where desktop GUI is unavailable.
- **Universal Platform Tools Installer**:
  - **Windows**: Automatically installs via `winget`, `choco`, `scoop`, or downloads official Google `platform-tools` directly to `C:\adb\platform-tools` and updates System `PATH`.
  - **Linux**: Auto-detects `apt`, `pacman`, `dnf`, `zypper`, `apk`, or `xbps`.
  - **Termux (Non-Root OTG)**: Configures `termux-api` and `termux-adb` / `termux-fastboot` for rootless USB OTG flashing from another Android phone.
  - **macOS**: Supports `Homebrew`, `MacPorts`, or direct Google repository setup.
- **Safe Custom ROM Clean Flasher**:
  - Follows the official `cancunf` flashing workflow: reboots into `FastbootD`, strictly verifies `is-userspace: yes` to prevent accidental bootloader flashing, flashes `initial_install.zip` (`boot` + `vendor_boot`), guides through Recovery factory reset, and executes `adb sideload`.
- **Dynamic Full Clean Stock Firmware Flasher (Slot A & Slot B)**:
  - Flashes `PGPT`, `preloader.img`, and all Slot A & Slot B partitions (`lk`, `tee`, `mcupm`, `pi_img`, `sspm`, `dtbo`, `logo`, `spmfw`, `scp`, `vbmeta`, `vbmeta_system`, `md1img`, `dpm`, `gz`, `vcp`, `gpueb`, `efuseBackup`, `boot`, `vendor_boot`).
  - Automatically detects and numerically sorts all `super.img_sparsechunk.*` files (`0` through `17`, `18`, `21`, or more) regardless of Android version (Android 13, 14, or 15+).

---

## 🚀 How to Run

### Method 1: Run Directly with Python (No Extra `pip` Packages Needed!)
The toolkit is engineered to run out-of-the-box with standard Python 3 (even without `colorama` installed):

```bash
# Launch interactive mode selector (GUI or CLI)
python app.py

# Or launch GUI directly
python app.py --gui

# Or launch CLI directly (Default on Termux)
python app.py --cli
