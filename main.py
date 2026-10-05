from colorama import Back, Fore, Style
from custom_rom import custom_rom
from stock_rom import stock_rom
from device_root import root_device
import platform

current_os = platform.system()

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
    print(f"Chose a option\n{green+"["}{red+"1"}{green+"]"}{reset}. Custom ROM Flash\n{green+"["}{red+"2"}{green+"]"}{reset}. Stock ROM Flash\n{green+"["}{red+"3"}{green+"]"}{reset}. Root Your Phone")
    option = input(f"\t{cyan}Chose a option: {green}").split()
    print(reset)

    if option == "1":
        custom_rom()
    elif option == "2":
        stock_rom()
    elif option == "3":
        root_device()
    else:
        print(f"{green_red+bolt+cyan} Invalid Option {reset+back_reset+style_reset}")

process()