import subprocess
import platform


def stock_rom():
     
     current_os = platform.system()
        
    if current_os == "Windows":
        # Windows requires shell=True for built-in shell commands like 'dir'
        result = subprocess.run(["dir"], shell=True, capture_output=True, text=True)
    elif current_os in ["Linux", "Darwin"]:  # Darwin is macOS
        result = subprocess.run(["ls", "-l"], capture_output=True, text=True)
    
    print(result.stdout)