import subprocess


def stock_rom_linux():
    
    result = subprocess.run(["ls", "-l"], capture_output=True, text=True)

    print(result.stdout)

def stock_rom_windows():
    
    result = subprocess.run(["ls", "-l"], capture_output=True, text=True)

    print(result.stdout)