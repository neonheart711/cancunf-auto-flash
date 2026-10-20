#!/usr/bin/env python3
import os
import sys
import platform
import subprocess

if os.name == "nt":
    os.system("")

try:
    from colorama import Back, Fore, Style, init
    init(autoreset=True)
    red = Fore.RED
    green = Fore.GREEN
    cyan = Fore.CYAN
    yellow = Fore.YELLOW
    white = Fore.WHITE
    reset = Fore.RESET
    red_back = Back.RED
    bold = Style.BRIGHT
    style_reset = Style.RESET_ALL
except ImportError:
    red = "\033[0;31m"
    green = "\033[0;32m"
    cyan = "\033[0;36m"
    yellow = "\033[1;33m"
    white = "\033[1;37m"
    reset = "\033[0m"
    red_back = "\033[41m"
    bold = "\033[1m"
    style_reset = "\033[0m"

from custom_rom_flash import (
    get_resource_dir,
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
    line = "=" * 68
    print(f"{cyan}{bold}{line}{style_reset}")
    print(
        f"{green}{bold}   Motorola Moto G54 / G64 5G (cancunf) "
        f"All-In-One Toolkit{style_reset}"
    )
    print(f"{cyan}{bold}{line}{style_reset}")
    print(
        f"{red_back}{white}{bold} CRITICAL SEPTEMBER SECURITY UPDATE "
        f"& ARB (ANTI-ROLLBACK) NOTICE {style_reset}"
    )
    print(
        f"{yellow}{bold}* Sept Builds: V1TDS35H.83-20-5-14 & "
        f"V1TDS35H.83-20-5-8-2-1-3{style_reset}"
    )
    print(
        f"{red}{bold}1. STOCK ROM DOWNGRADE = HARD BRICK:{style_reset} "
        f"{yellow}The September update bumps"
    )
    print(
        "   the ARB counter. If you updated to it, DO NOT flash any "
        f"older Stock ROM!{style_reset}"
    )
    print(
        f"{red}{bold}2. CUSTOM ROM BRICK WARNING:{style_reset} "
        f"{yellow}If your device is on the Sept update,"
    )
    print(
        "   flashing A16 or incompatible Custom ROMs will BRICK "
        f"your device!{style_reset}"
    )
    print(f"{cyan}{bold}{'-' * 68}{style_reset}\n")


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
        print(
            f"{yellow}[*] Environment Detected: Android Termux "
            f"(CLI Mode Only){style_reset}"
        )
        return "2"

    print(f"{bold}Choose your Operating System:{style_reset}")
    print(f"{green}[{red}1{green}]{style_reset}. Windows (7/8/10/11)")
    print(f"{green}[{red}2{green}]{style_reset}. Linux or Termux")
    print(f"{green}[{red}3{green}]{style_reset}. macOS")
    print(f"{green}[{red}4{green}]{style_reset}. Auto-Detect OS (Recommended)")

    prompt = f"\n\t{cyan}Choose an option (1-4) [Default: 4]: {green}"
    choice = input(prompt).strip()
    print(style_reset)

    if choice in ["1", "2", "3"]:
        return choice

    detected = detect_os_code()
    os_names = {"1": "Windows", "2": "Linux / Termux", "3": "macOS"}
    print(f"{yellow}[*] Auto-Detected OS: {os_names[detected]}{style_reset}")
    return detected


def adb_fastboot_setup(current_os):
    script_dir = get_resource_dir()

    if current_os == "1":
        bat_path = os.path.join(script_dir, "windows-adb-install.bat")
        if os.path.isfile(bat_path):
            subprocess.run([bat_path], shell=True)
        else:
            print(f"{red}[!] windows-adb-install.bat not found!{style_reset}")

    elif current_os == "2":
        sh_path = os.path.join(script_dir, "linux-adb-install.sh")
        if os.path.isfile(sh_path):
            subprocess.run(["chmod", "+x", sh_path])
            subprocess.run(["bash", sh_path])
        else:
            print(f"{red}[!] linux-adb-install.sh not found!{style_reset}")

    elif current_os == "3":
        mac_path = os.path.join(script_dir, "mac-adb-install.sh")
        if os.path.isfile(mac_path):
            subprocess.run(["chmod", "+x", mac_path])
            subprocess.run(["bash", mac_path])
        else:
            print(f"{red}[!] mac-adb-install.sh not found!{style_reset}")


def run_cli_loop():
    print_banner()
    current_os = select_os()

    prompt_pt = (
        f"\n{cyan}Do you want to setup/verify Platform Tools "
        f"(ADB & Fastboot)? (Y/N): {green}"
    )
    adb_install = input(prompt_pt).lower().strip()
    print(style_reset)

    if adb_install == "y":
        adb_fastboot_setup(current_os)
    else:
        print(f"{yellow}[*] Platform Tools setup skipped...{style_reset}")

    while True:
        print(f"\n{cyan}{bold}{'=' * 68}{style_reset}")
        print(
            f"{red_back}{white}{bold} WARNING: DO NOT DOWNGRADE STOCK ROM "
            f"ON SEPTEMBER+ BOOTLOADER! {style_reset}"
        )
        print(f"{bold}Choose an Operation (CLI Mode):{style_reset}")
        print(
            f"{green}[{red}1{green}]{style_reset}. Clean Flash Custom ROM "
            f"(FastbootD + ADB Sideload) {red}{bold}[SEPT CHECK]{style_reset}"
        )
        print(
            f"{green}[{red}2{green}]{style_reset}. Update Custom ROM Build "
            f"(Dirty Flash / Sideload)"
        )
        print(
            f"{green}[{red}3{green}]{style_reset}. Full Clean Flash Stock ROM "
            f"(Slot A & B) {red}{bold}[ARB BRICK CHECK]{style_reset}"
        )
        print(
            f"{green}[{red}4{green}]{style_reset}. Root Your Phone "
            f"(Flash Patched Boot / Init_boot / Vendor_boot)"
        )
        print(
            f"{green}[{red}5{green}]{style_reset}. Setup / Verify ADB & "
            f"Fastboot Platform Tools"
        )
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
            print(f"{green}{bold}Thank you! Goodbye!{style_reset}")
            sys.exit(0)
        else:
            print(
                f"{red_back}{bold}{white} Invalid Option! "
                f"Choose between 1 and 6. {style_reset}"
            )


def main():
    if "--cli" in sys.argv or is_termux():
        run_cli_loop()
        return

    if "--gui" in sys.argv:
        from gui_app import launch_gui
        launch_gui()
        return

    print_banner()
    print(f"{bold}Select Interface Mode:{style_reset}")
    print(
        f"{green}[{red}1{green}]{style_reset}. Graphical User Interface "
        f"(GUI Mode - Windows/Linux/macOS)"
    )
    print(
        f"{green}[{red}2{green}]{style_reset}. Command Line Interface "
        f"(CLI Mode - Terminal / Termux)"
    )
    print(f"{green}[{red}3{green}]{style_reset}. Exit")

    mode = input(f"\n\t{cyan}Select mode (1-3): {green}").strip()
    print(style_reset)

    if mode == "1":
        try:
            from gui_app import launch_gui
            print(f"{yellow}[*] Launching GUI Studio...{style_reset}")
            launch_gui()
        except Exception as e:
            print(
                f"{red}[!] GUI could not start ({e}). "
                f"Falling back to CLI Mode...{style_reset}"
            )
            run_cli_loop()
    elif mode == "2":
        run_cli_loop()
    else:
        print(f"{green}Goodbye!{style_reset}")
        sys.exit(0)


if __name__ == "__main__":
    main()
