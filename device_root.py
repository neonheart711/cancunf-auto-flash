import subprocess


def root_linux():
    
    result = subprocess.run(["adb", "--version"], capture_output=True, text=True)

    print(result.stdout)

def root_windows():
    
    result = subprocess.run(["ls", "-l"], capture_output=True, text=True)

    print(result.stdout)