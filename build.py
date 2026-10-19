#!/usr/bin/env python3
import os
import sys
import shutil
import platform
import subprocess


def build_executable():
    sys_os = platform.system().lower()
    sep = ";" if os.name == "nt" else ":"

    if "windows" in sys_os:
        out_name = "cancunf-toolkit-windows"
        helper_script = "windows-adb-install.bat"
    elif "darwin" in sys_os:
        out_name = "cancunf-toolkit-macos"
        helper_script = "mac-adb-install.sh"
    else:
        out_name = "cancunf-toolkit-linux"
        helper_script = "linux-adb-install.sh"

    print(f"[*] Detected OS: {platform.system()}")
    print("[*] Installing/Verifying PyInstaller & Colorama...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller", "colorama"], check=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--clean",
        f"--name={out_name}",
        "--hidden-import=gui_app",
        "--hidden-import=custom_rom_flash",
        "--hidden-import=colorama",
        "--hidden-import=tkinter",
        f"--add-data={helper_script}{sep}.",
        "app.py"
    ]

    print(f"[*] Building standalone executable: {out_name}...")
    subprocess.run(cmd, check=True)

    # Clean up temporary build folders
    for folder in ["build", "__pycache__"]:
        if os.path.isdir(folder):
            shutil.rmtree(folder, ignore_errors=True)
    spec_file = f"{out_name}.spec"
    if os.path.isfile(spec_file):
        os.remove(spec_file)

    ext = ".exe" if os.name == "nt" else ""
    final_path = os.path.join("dist", f"{out_name}{ext}")
    print("\n============================================================")
    print(f"[✓] BUILD SUCCESSFUL!")
    print(f"[i] Your standalone software is ready at: {final_path}")
    print("============================================================")


if __name__ == "__main__":
    build_executable()

