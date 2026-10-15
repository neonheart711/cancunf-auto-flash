from colorama import Back, Fore, Style, init
import subprocess

init()

red = Fore.RED
green = Fore.GREEN
cyan = Fore.CYAN
reset = Fore.RESET

green_back = Back.GREEN
red_back = Back.RED
back_reset = Back.RESET

bold = Style.BRIGHT
style_reset = Style.RESET_ALL

print(f"{bold}Choose an option:\n{green}[{red}1{green}]{reset}. Windows\n{green}[{red}2{green}]{reset}. Linux or Termux\n{green}[{red}3{green}]{reset}. MacOS")

current_os = input(f"\t{cyan}Choose an option: {green}").strip()
print(reset + style_reset + back_reset)


def adb_fastboot_setup():
    if current_os == "1":
        subprocess.run(["windows-adb-install.bat"], shell=True)
        
    elif current_os == "2":
        subprocess.run(["bash", "linux-adb-install.sh"])
        
    elif current_os == "3":
        subprocess.run(["chmod", "+x", "mac-adb-install.sh"])
        subprocess.run(["./mac-adb-install.sh"])
    else:
        print(f"{red_back}{bold}{cyan} Invalid OS Option! {reset}{back_reset}{style_reset}")


def custom_rom_linux():
    print(f"{green}[*] Starting Custom ROM Flash for Linux/macOS...{reset}")

def custom_rom_windows():
    print(f"{green}[*] Starting Custom ROM Flash for Windows...{reset}")

def stock_rom_linux():
    print(f"{green}[*] Starting Stock ROM Flash for Linux/macOS...{reset}")

def stock_rom_windows():
    print(f"{green}[*] Starting Stock ROM Flash for Windows...{reset}")

def root_linux():
    print(f"{green}[*] Starting Rooting Process for Linux/macOS...{reset}")

def root_windows():
    print(f"{green}[*] Starting Rooting Process for Windows...{reset}")


adb_install = input("Do you want to setup Platform tools (Y/N): ").lower().strip()

if adb_install == "y":
    adb_fastboot_setup()
else:
    print("Platform Tools setup skipped...")


def process():
    print(f"\n{bold}Choose an option:\n{green}[{red}1{green}]{reset}. Custom ROM Flash\n{green}[{red}2{green}]{reset}. Stock ROM Flash\n{green}[{red}3{green}]{reset}. Root Your Phone")
    option = input(f"\t{cyan}Choose an option: {green}").strip()
    print(reset + style_reset + back_reset)

    if option == "1":
        if current_os in ["2", "3"]:
            custom_rom_linux()
        elif current_os == "1":
            custom_rom_windows()
    elif option == "2":
        if current_os in ["2", "3"]:
            stock_rom_linux()
        elif current_os == "1":
            stock_rom_windows()
    elif option == "3":
        if current_os in ["2", "3"]:
            root_linux()
        elif current_os == "1":
            root_windows()
    else:
        print(f"{red_back}{bold}{cyan} Invalid Option {reset}{back_reset}{style_reset}")


process()
