from colorama import Back, Fore, Style
from custom_rom import custom_rom_linux, custom_rom_windows
from stock_rom import stock_rom_linux, stock_rom_windows
from device_root import root_linux, root_windows
import platform
import subprocess

current_os = platform.system().lower()

red = Fore.RED
green = Fore.GREEN
cyan = Fore.CYAN
reset = Fore.RESET

green_back = Back.GREEN
green_red = Back.RED

back_reset = Back.RESET

bolt = Style.BRIGHT
style_reset = Style.RESET_ALL



def process():
    print(f"{bolt}Chose a option\n{green+"["}{red+"1"}{green+"]"}{reset}. Custom ROM Flash\n{green+"["}{red+"2"}{green+"]"}{reset}. Stock ROM Flash\n{green+"["}{red+"3"}{green+"]"}{reset}. Root Your Phone")
    option = input(f"\t{cyan}Chose a option: {green}").split()
    print(reset+style_reset+back_reset)

    if option == "1":
        if current_os == "linux" or current_os == "darwin":
            custom_rom_linux()
        elif current_os == "windows":
            custom_rom_windows()
    elif option == "2":
        if current_os == "linux" or current_os == "darwin":
            stock_rom_linux()
        elif current_os == "windows":
            stock_rom_windows()
    elif option == "3":
        if current_os == "linux" or current_os == "darwin":
            root_linux()
        elif current_os == "windows":
            root_windows()
    else:
        print(f"{green_red+bolt+cyan} Invalid Option {reset+back_reset+style_reset}")


def check_adb_installed():
    try:
        result = subprocess.run(
            ["adb", "--version"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        print("ADB is not installed or not available on PATH.")
        return False

    if result.returncode != 0:
        print("ADB was found, but could not be run.")
        return False

    print(f"ADB is installed: {result.stdout.strip()}")
    return True

process()