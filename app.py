#!/usr/bin/env python3
import os
import sys
import platform
import subprocess

# Enable native ANSI colors on Windows CMD/PowerShell without requiring colorama
if os.name == "nt":
    os.system("")

try:
    from colorama import Back, Fore, Style, init
    init(autoreset=True)
    red = Fore.RED
    green = Fore.GREEN
    cyan = Fore.CYAN
    yellow = Fore.YELLOW
    reset = Fore.RESET
    red_back = Back.RED
    back_reset = Back.RESET
    bold = Style.BRIGHT
    style_reset = Style.RESET_ALL
except ImportError:
    # Zero-dependency ANSI fallback if colorama is not installed
    red = "\033[0;31m"
    green = "\033[0;32m"
    cyan = "\033[0;36m"
    yellow = "\033[1;33m"
    reset = "\033[0m"
    red_back = "\033[41m"
    back_reset = "\033[49m"
    bold = "\033[1m"
    style_reset = "\033[0m"

from custom_rom_flash import (
    custom_rom_flash_cancunf,
    dirty_flash_update_cancunf,
    stock_rom_flash_cancunf,
    root_phone_cancunf
)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def is_termux():
    return (
        "TERMUX_VERSION" in os.environ
        or os.path.isdir("/data/data/com.termux/files/usr")
    )


def print_banner():
    clear_screen()
    print(f"{cyan}{bold}============================================================{style_reset}")
    print(f"{green}{bold}   Motorola Moto G54 / G64 5G (cancunf) All-In-One Toolkit  {style_reset}")
    print(f"{cyan}{bold}============================================================{style_reset}")
    print(f"{red}{bold}[!] DISCLAIMER / WARNING:{style_reset}")
    print(f"{yellow}This tool is strictly for Motorola Moto G54 5G & Moto G64 5G (cancunf).")
    print("Flashing firmware or rooting carries a risk of bricking your device.")
    print(f"You are solely responsible for any damage. Use at your own risk!{style_reset}\n")


def detect_os_code():
    if is_termux():
        return "2"
    sys_os = platform.system().lower()
    if "windows" in sys_os:
        return "1"
    elif "darwin" in sys_os:
        return "3"
    return "2"


def select_os():
    if is_termux():
        print(f"{yellow}[*] Environment Detected: Android Termux (CLI Mode Only){style_reset}")
        return "2"

    print(f"{bold}Choose your Operating System:{style_reset}")
    print(f"{green}[{red}1{green}]{style_reset}. Windows (7/8/10/11)")
    print(f"{green}[{red}2{green}]{style_reset}. Linux or Termux")
    print(f"{green}[{red}3{green}]{style_reset}. macOS")
    print(f"{green}[{red}4{green}]{style_reset}. Auto-Detect OS (Recommended)")

    choice = input(f"\n\t{cyan}Choose an option (1-4) [Default: 4]: {green}").strip()
    print(style_reset)

    if choice in ["1", "2", "3"]:
        return choice

    detected = detect_os_code()
    os_names = {"1": "Windows", "2": "Linux / Termux", "3": "macOS"}
    print(f"{yellow}[*] Auto-Detected OS: {os_names[detected]}{style_reset}")
    return detected


def adb_fastboot_setup(current_os):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if current_os == "1":
        bat_path = os.path.join(script_dir, "windows-adb-install.bat")
        if os.path.isfile(bat_path):
            subprocess.run([bat_path], shell=True)
        else:
            print(f"{red}[!] Error: windows-adb-install.bat not found!{style_reset}")

    elif current_os == "2":
        sh_path = os.path.join(script_dir, "linux-adb-install.sh")
        if os.path.isfile(sh_path):
            subprocess.run(["chmod", "+x", sh_path])
            subprocess.run(["bash", sh_path])
        else:
            print(f"{red}[!] Error: linux-adb-install.sh not found!{style_reset}")

    elif current_os == "3":
        mac_path = os.path.join(script_dir, "mac-adb-install.sh")
        if os.path.isfile(mac_path):
            subprocess.run(["chmod", "+x", mac_path])
            subprocess.run(["bash", mac_path])
        else:
            print(f"{red}[!] Error: mac-adb-install.sh not found!{style_reset}")


def run_cli_loop():
    print_banner()
    current_os = select_os()

    adb_install = input(
        f"\n{cyan}Do you want to setup/verify Platform Tools (ADB & Fastboot)? (Y/N): {green}"
    ).lower().strip()
    print(style_reset)

    if adb_install == "y":
        adb_fastboot_setup(current_os)
    else:
        print(f"{yellow}[*] Platform Tools setup skipped...{style_reset}")

    while True:
        print(f"\n{cyan}{bold}============================================================{style_reset}")
        print(f"{bold}Choose an Operation (CLI Mode):{style_reset}")
        print(f"{green}[{red}1{green}]{style_reset}. Clean Flash Custom ROM (FastbootD + ADB Sideload)")
        print(f"{green}[{red}2{green}]{style_reset}. Update Custom ROM Build (Dirty Flash / Sideload)")
        print(f"{green}[{red}3{green}]{style_reset}. Full Clean Flash Stock ROM (Both Slot A & Slot B)")
        print(f"{green}[{red}4{green}]{style_reset}. Root Your Phone (Flash Patched Boot / Init_boot)")
        print(f"{green}[{red}5{green}]{style_reset}. Setup / Verify ADB & Fastboot Platform Tools")
        print(f"{green}[{red}6{green}]{style_reset}. Exit")

        option = input(f"\n\t{cyan}Choose an option (1-6): {green}").strip()
        print(style_reset)

        if option == "1":
            custom_rom_flash_cancunf()
        elif option == "2":
            dirty_flash_update_cancunf()
        elif option == "3":
            stock_rom_flash_cancunf()
        elif option == "4":
            root_phone_cancunf()
        elif option == "5":
            adb_fastboot_setup(current_os)
        elif option == "6":
            print(f"{green}{bold}Thank you for using the cancunf Toolkit! Goodbye!{style_reset}")
            sys.exit(0)
        else:
            print(f"{red_back}{bold}{cyan} Invalid Option! Please choose between 1 and 6. {style_reset}")


def main():
    # Support direct command-line flags (--cli or --gui)
    if "--cli" in sys.argv or is_termux():
        run_cli_loop()
        return

    if "--gui" in sys.argv:
        from gui_app import launch_gui
        launch_gui()
        return

    print_banner()
    print(f"{bold}Select Interface Mode:{style_reset}")
    print(f"{green}[{red}1{green}]{style_reset}. Graphical User Interface (GUI Mode - Windows/Linux/macOS)")
    print(f"{green}[{red}2{green}]{style_reset}. Command Line Interface (CLI Mode - Terminal / Termux)")
    print(f"{green}[{red}3{green}]{style_reset}. Exit")

    mode = input(f"\n\t{cyan}Select mode (1-3): {green}").strip()
    print(style_reset)

    if mode == "1":
        try:
            from gui_app import launch_gui
            print(f"{yellow}[*] Launching Graphical User Interface...{style_reset}")
            launch_gui()
        except Exception as e:
            print(f"{red}[!] GUI could not be started ({e}). Falling back to CLI Mode...{style_reset}")
            run_cli_loop()
    elif mode == "2":
        run_cli_loop()
    else:
        print(f"{green}Goodbye!{style_reset}")
        sys.exit(0)


if __name__ == "__main__":
    main()
