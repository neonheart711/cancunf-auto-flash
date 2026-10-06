import subprocess


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


def custom_rom_linux():
    check_adb_installed()


def custom_rom_windows():
    check_adb_installed()


custom_rom_linux()