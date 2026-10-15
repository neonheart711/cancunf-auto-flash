#!/usr/bin/env python3
import os
import glob
import shutil
import subprocess

if os.name == "nt":
    os.system("")

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    red = Fore.RED
    green = Fore.GREEN
    cyan = Fore.CYAN
    yellow = Fore.YELLOW
    reset = Fore.RESET
    bold = Style.BRIGHT
except ImportError:
    red = "\033[0;31m"
    green = "\033[0;32m"
    cyan = "\033[0;36m"
    yellow = "\033[1;33m"
    reset = "\033[0m"
    bold = "\033[1m"

_ACTIVE_PROCESS = None


def get_local_pt_dir():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "platform-tools")


def get_adb_bin():
    # 1. Check portable platform-tools inside toolkit folder
    local_adb = os.path.join(get_local_pt_dir(), "adb.exe" if os.name == "nt" else "adb")
    if os.path.isfile(local_adb):
        return local_adb
    # 2. Check Termux rootless adb
    if shutil.which("termux-adb"):
        return "termux-adb"
    # 3. Check system PATH or C:\adb\platform-tools
    if shutil.which("adb"):
        return "adb"
    if os.name == "nt" and os.path.isfile(r"C:\adb\platform-tools\adb.exe"):
        return r"C:\adb\platform-tools\adb.exe"
    return "adb"


def get_fastboot_bin():
    # 1. Check portable platform-tools inside toolkit folder
    local_fb = os.path.join(get_local_pt_dir(), "fastboot.exe" if os.name == "nt" else "fastboot")
    if os.path.isfile(local_fb):
        return local_fb
    # 2. Check Termux rootless fastboot
    if shutil.which("termux-fastboot"):
        return "termux-fastboot"
    # 3. Check system PATH or C:\adb\platform-tools
    if shutil.which("fastboot"):
        return "fastboot"
    if os.name == "nt" and os.path.isfile(r"C:\adb\platform-tools\fastboot.exe"):
        return r"C:\adb\platform-tools\fastboot.exe"
    return "fastboot"


def abort_active_process():
    global _ACTIVE_PROCESS
    if _ACTIVE_PROCESS and _ACTIVE_PROCESS.poll() is None:
        try:
            _ACTIVE_PROCESS.terminate()
        except Exception:
            pass


def clean_path(path_str):
    return path_str.strip().strip("'").strip('"').strip()


def check_fastboot_connection(log_fn=None):
    fastboot_bin = get_fastboot_bin()
    msg = "[*] Checking Fastboot connection..."
    print(f"\n{yellow}{msg}{reset}")
    if log_fn:
        log_fn(msg)

    kwargs = {"capture_output": True, "text": True}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    try:
        res = subprocess.run([fastboot_bin, "devices"], timeout=6, **kwargs)
        out = res.stdout.strip()
        if not out:
            err = "[!] No device detected in Fastboot mode! Connect phone in Bootloader Mode (Power + Vol Down)."
            print(f"{red}{bold}{err}{reset}")
            if log_fn:
                log_fn(err)
            return False
        ok = f"[✓] Device Connected: {out}"
        print(f"{green}{ok}{reset}")
        if log_fn:
            log_fn(ok)
        return True
    except FileNotFoundError:
        err = f"[!] Error: '{fastboot_bin}' not found! Open Tab 5 to install Platform Tools."
        print(f"{red}{bold}{err}{reset}")
        if log_fn:
            log_fn(err)
        return False
    except subprocess.TimeoutExpired:
        err = "[!] Fastboot check timed out. Check USB cable or drivers."
        if log_fn:
            log_fn(err)
        return False


def run_cmd_stream(cmd_list, log_fn=None, stop_event=None):
    """Streams stdout/stderr live (handling carriage returns) without flashing black CMD windows on Windows."""
    global _ACTIVE_PROCESS
    if stop_event and stop_event.is_set():
        raise RuntimeError("Operation aborted by user.")

    cmd_str = " ".join(cmd_list)
    print(f"{cyan}--> Executing: {cmd_str}{reset}")
    if log_fn:
        log_fn(f"--> Executing: {cmd_str}")

    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        " stdin": subprocess.DEVNULL,
    }
    del kwargs[" stdin"]
    kwargs["stdin"] = subprocess.DEVNULL
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    _ACTIVE_PROCESS = subprocess.Popen(cmd_list, **kwargs)
    output_lines = []
    buffer = bytearray()

    if _ACTIVE_PROCESS.stdout:
        while True:
            if stop_event and stop_event.is_set():
                abort_active_process()
                raise RuntimeError("Operation aborted by user.")

            ch = _ACTIVE_PROCESS.stdout.read(1)
            if not ch:
                if buffer:
                    line = buffer.decode("utf-8", errors="replace").strip()
                    if line:
                        print(line)
                        output_lines.append(line)
                        if log_fn:
                            log_fn(line)
                break

            if ch in (b"\n", b"\r"):
                line = buffer.decode("utf-8", errors="replace").strip()
                buffer.clear()
                if line:
                    print(line)
                    output_lines.append(line)
                    if log_fn:
                        log_fn(line)
            else:
                buffer.extend(ch)

    _ACTIVE_PROCESS.wait()
    ret_code = _ACTIVE_PROCESS.returncode
    _ACTIVE_PROCESS = None
    return ret_code, "\n".join(output_lines)


# ==============================================================================
# CLI FUNCTIONS
# ==============================================================================

def custom_rom_flash_cancunf():
    adb_bin = get_adb_bin()
    fastboot_bin = get_fastboot_bin()

    print(f"\n{cyan}{bold}============================================================{reset}")
    print(f"{cyan}{bold}   Moto G54/G64 (cancunf) Custom ROM Clean Flasher          {reset}")
    print(f"{cyan}{bold}============================================================{reset}")
    print(f"{yellow}[!] Prerequisite: Bootloader must already be unlocked.{reset}\n")

    initial_zip = clean_path(input(f"{cyan}Drag & drop or enter path to [Initial Install Zip]: {green}"))
    if not os.path.isfile(initial_zip):
        print(f"{red}{bold}[!] Error: Initial install zip not found at: {initial_zip}{reset}")
        return

    rom_zip = clean_path(input(f"{cyan}Drag & drop or enter path to [Custom ROM Zip]: {green}"))
    if not os.path.isfile(rom_zip):
        print(f"{red}{bold}[!] Error: ROM zip not found at: {rom_zip}{reset}")
        return

    input(f"\n{cyan}Boot phone into Bootloader Mode (Power + Volume Down) and press Enter...{reset}")
    if not check_fastboot_connection():
        return

    print(f"\n{yellow}[*] Rebooting into FastbootD (Userspace Fastboot) Mode...{reset}")
    subprocess.run([fastboot_bin, "reboot", "fastboot"])
    input(f"{cyan}Wait until phone displays FastbootD screen, then press Enter...{reset}")

    res = subprocess.run([fastboot_bin, "getvar", "is-userspace"], capture_output=True, text=True)
    output = (res.stdout + res.stderr).lower()
    if "is-userspace: yes" not in output:
        print(f"{red}{bold}[!] Safety Stop: 'is-userspace: yes' not confirmed! Output:{reset}\n{output}")
        if input(f"{yellow}Force continue anyway? (y/n): {reset}").strip().lower() != "y":
            return

    print(f"\n{yellow}[*] Flashing Initial Install Zip...{reset}")
    if subprocess.run([fastboot_bin, "--skip-reboot", "update", initial_zip]).returncode != 0:
        print(f"{red}{bold}[✗] Failed flashing Initial Install Zip!{reset}")
        return

    subprocess.run([fastboot_bin, "reboot", "recovery"])
    print(f"\n{yellow}1. In Recovery: Select 'Wipe data / Factory reset' and format data.")
    print(f"2. Select 'Apply update' -> 'Apply from ADB'.{reset}")
    input(f"\n{cyan}Press Enter once phone is in ADB Sideload mode...{reset}")

    subprocess.run([adb_bin, "sideload", rom_zip])
    print(f"\n{green}{bold}[✓] Clean Flash Completed! Select 'Reboot system now' on your phone.{reset}")


def dirty_flash_update_cancunf():
    adb_bin = get_adb_bin()
    rom_zip = clean_path(input(f"\n{cyan}Drag & drop or enter path to new [ROM Zip]: {green}"))
    if not os.path.isfile(rom_zip):
        print(f"{red}{bold}[!] Error: ROM zip not found!{reset}")
        return

    subprocess.run([adb_bin, "reboot", "recovery"])
    input(f"{cyan}In Recovery, select 'Apply update' -> 'Apply from ADB', then press Enter...{reset}")
    subprocess.run([adb_bin, "sideload", rom_zip])
    print(f"\n{green}{bold}[✓] Update Completed!{reset}")


def stock_rom_flash_cancunf():
    rom_dir = clean_path(input(f"\n{cyan}Drag & drop or enter [Extracted Stock ROM Folder]: {green}"))
    if os.path.isfile(rom_dir):
        rom_dir = os.path.dirname(rom_dir)
    if not os.path.isdir(rom_dir):
        print(f"{red}{bold}[!] Folder not found!{reset}")
        return

    sparse_files = glob.glob(os.path.join(rom_dir, "super.img_sparsechunk.*"))
    sparse_files.sort(key=lambda x: int(x.split(".")[-1]) if x.split(".")[-1].isdigit() else x)

    if not os.path.isfile(os.path.join(rom_dir, "PGPT")) or not sparse_files:
        print(f"{red}{bold}[!] Invalid folder: PGPT or super.img_sparsechunk.* missing!{reset}")
        return

    if input(f"{cyan}Type 'YES' to wipe userdata and clean flash Slot A & B: {green}").strip() != "YES":
        return

    input(f"\n{cyan}Connect phone in Bootloader Mode and press Enter...{reset}")
    if not check_fastboot_connection():
        return

    execute_stock_flash_sequence(rom_dir, sparse_files)


def execute_stock_flash_sequence(rom_dir, sparse_files, log_fn=None, stop_event=None):
    fastboot_bin = get_fastboot_bin()

    def fb(*args):
        code, _ = run_cmd_stream([fastboot_bin] + list(args), log_fn=log_fn, stop_event=stop_event)
        return code

    def flash_part(partition, filename):
        file_path = os.path.join(rom_dir, filename)
        if os.path.isfile(file_path):
            code = fb("flash", partition, file_path)
            if code != 0:
                raise RuntimeError(f"Failed flashing '{partition}' ({filename}).")
        else:
            msg = f"[!] Skipping {partition} ({filename} not present in firmware folder)"
            print(f"{yellow}{msg}{reset}")
            if log_fn:
                log_fn(msg)

    if log_fn:
        log_fn("[1/4] Flashing GPT & Preloader...")
    fb("--set-active=a")
    flash_part("gpt", "PGPT")
    fb("getvar", "max-sparse-size")
    fb("oem", "fb_mode_set")
    flash_part("preloader", "preloader.img")

    if log_fn:
        log_fn("[2/4] Flashing Slot A & Slot B Partitions...")
    ab_part_1 = [
        ("lk_a", "lk.img"), ("lk_b", "lk.img"),
        ("tee_a", "tee.img"), ("tee_b", "tee.img"),
        ("mcupm_a", "mcupm.img"), ("mcupm_b", "mcupm.img"),
        ("pi_img_a", "pi_img.img"), ("pi_img_b", "pi_img.img"),
        ("sspm_a", "sspm.img"), ("sspm_b", "sspm.img"),
        ("dtbo_a", "dtbo.img"), ("dtbo_b", "dtbo.img"),
        ("logo_a", "logo.img"), ("logo_b", "logo.img"),
    ]
    for part, img in ab_part_1:
        flash_part(part, img)

    fb("erase", "nvdata")

    ab_part_2 = [
        ("spmfw_a", "spmfw.img"), ("spmfw_b", "spmfw.img"),
        ("scp_a", "scp.img"), ("scp_b", "scp.img"),
        ("vbmeta_a", "vbmeta.img"), ("vbmeta_b", "vbmeta.img"),
        ("vbmeta_system_a", "vbmeta_system.img"), ("vbmeta_system_b", "vbmeta_system.img"),
        ("md1img_a", "md1img.img"), ("md1img_b", "md1img.img"),
        ("dpm_a", "dpm.img"), ("dpm_b", "dpm.img"),
        ("gz_a", "gz.img"), ("gz_b", "gz.img"),
        ("vcp_a", "vcp.img"), ("vcp_b", "vcp.img"),
        ("gpueb_a", "gpueb.img"), ("gpueb_b", "gpueb.img"),
        ("efuseBackup", "efuse.img"),
        ("boot_a", "boot.img"), ("boot_b", "boot.img"),
        ("vendor_boot_a", "vendor_boot.img"), ("vendor_boot_b", "vendor_boot.img"),
    ]
    for part, img in ab_part_2:
        flash_part(part, img)

    if log_fn:
        log_fn(f"[3/4] Flashing Super Partition ({len(sparse_files)} sparsechunks)...")
    for idx, chunk_path in enumerate(sparse_files):
        chunk_name = os.path.basename(chunk_path)
        if log_fn:
            log_fn(f"[*] Flashing super chunk ({idx + 1}/{len(sparse_files)}): {chunk_name}")
        if fb("flash", "super", chunk_path) != 0:
            raise RuntimeError(f"Failed flashing super sparsechunk: {chunk_name}")

    if log_fn:
        log_fn("[4/4] Wiping Userdata, Metadata & Clearing Fastboot OEM Flags...")
    fb("erase", "userdata")
    fb("erase", "metadata")
    fb("erase", "debug_token")
    fb("oem", "fb_mode_clear")
    fb("oem", "config", "unset", "console")
    fb("oem", "config", "unset", "cmdl")

    if log_fn:
        log_fn("[✓] FULL CLEAN FLASH COMPLETED! PRESS POWER BUTTON TO REBOOT!")


def root_phone_cancunf():
    fastboot_bin = get_fastboot_bin()
    part_choice = input(f"\n{cyan}Select partition (1=boot, 2=init_boot): {green}").strip()
    partition = "init_boot" if part_choice == "2" else "boot"
    img_path = clean_path(input(f"{cyan}Drag & drop patched [{partition}.img]: {green}"))
    if not os.path.isfile(img_path) or not check_fastboot_connection():
        return
    if subprocess.run([fastboot_bin, "flash", partition, img_path]).returncode == 0:
        subprocess.run([fastboot_bin, "reboot"])


# ==============================================================================
# GUI HANDLERS
# ==============================================================================

def custom_rom_flash_cancunf_gui(initial_zip, rom_zip, log_fn=None, prompt_fn=None, stop_event=None):
    adb_bin = get_adb_bin()
    fastboot_bin = get_fastboot_bin()

    if not check_fastboot_connection(log_fn=log_fn):
        raise RuntimeError("No device detected in Bootloader/Fastboot mode!")

    if log_fn:
        log_fn("[*] Step 1: Rebooting device into FastbootD (Userspace Fastboot) Mode...")
    run_cmd_stream([fastboot_bin, "reboot", "fastboot"], log_fn=log_fn, stop_event=stop_event)

    if prompt_fn and not prompt_fn(
        "Wait for your phone screen to enter FastbootD Mode.\n\n"
        "Click OK once the phone displays the FastbootD menu."
    ):
        raise RuntimeError("Operation cancelled by user.")

    if log_fn:
        log_fn("[*] Step 2: Verifying FastbootD (is-userspace) state...")
    _, out = run_cmd_stream([fastboot_bin, "getvar", "is-userspace"], log_fn=log_fn, stop_event=stop_event)
    if "is-userspace: yes" not in out.lower():
        raise RuntimeError(
            "Safety Stop: Device is NOT in FastbootD mode ('is-userspace: yes' not returned). "
            "Never flash initial_install.zip in standard Bootloader mode!"
        )

    if log_fn:
        log_fn("[*] Step 3: Flashing Initial Install Zip (boot + vendor_boot)...")
    code, _ = run_cmd_stream([fastboot_bin, "--skip-reboot", "update", initial_zip], log_fn=log_fn, stop_event=stop_event)
    if code != 0:
        raise RuntimeError("Failed flashing Initial Install Zip!")

    if log_fn:
        log_fn("[*] Step 4: Rebooting into Recovery Mode...")
    run_cmd_stream([fastboot_bin, "reboot", "recovery"], log_fn=log_fn, stop_event=stop_event)

    if prompt_fn and not prompt_fn(
        "ACTION REQUIRED ON PHONE:\n\n"
        "1. In Recovery, select 'Wipe data / Factory reset' and format /data.\n"
        "2. Go back to the main Recovery menu and select 'Apply update' -> 'Apply from ADB'.\n\n"
        "Click OK once your phone is waiting in ADB Sideload mode."
    ):
        raise RuntimeError("Operation cancelled before ADB Sideload.")

    if log_fn:
        log_fn("[*] Step 5: Sideloading Custom ROM Zip (Stopping at 47% with 'Total xfer: 1.00x' is normal)...")
    run_cmd_stream([adb_bin, "sideload", rom_zip], log_fn=log_fn, stop_event=stop_event)
    if log_fn:
        log_fn("[✓] Sideload finished! Select 'Reboot system now' on your phone.")


def dirty_flash_update_cancunf_gui(rom_zip, log_fn=None, prompt_fn=None, stop_event=None):
    adb_bin = get_adb_bin()
    if log_fn:
        log_fn("[*] Attempting to reboot device into Recovery Mode...")
    run_cmd_stream([adb_bin, "reboot", "recovery"], log_fn=log_fn, stop_event=stop_event)

    if prompt_fn and not prompt_fn(
        "On your phone's Recovery menu:\n"
        "Select 'Apply update' -> 'Apply from ADB'.\n\n"
        "Click OK when the phone is ready in ADB Sideload mode."
    ):
        raise RuntimeError("Update cancelled by user.")

    if log_fn:
        log_fn("[*] Sideloading ROM Update...")
    run_cmd_stream([adb_bin, "sideload", rom_zip], log_fn=log_fn, stop_event=stop_event)
    if log_fn:
        log_fn("[✓] ROM Update completed! Select 'Reboot system now' on your phone.")


def stock_rom_flash_cancunf_gui(rom_dir, log_fn=None, stop_event=None):
    pgpt_path = os.path.join(rom_dir, "PGPT")
    boot_path = os.path.join(rom_dir, "boot.img")
    if not os.path.isfile(pgpt_path) or not os.path.isfile(boot_path):
        raise RuntimeError("Invalid Stock ROM folder: 'PGPT' or 'boot.img' missing inside selected directory!")

    sparse_files = glob.glob(os.path.join(rom_dir, "super.img_sparsechunk.*"))
    sparse_files.sort(key=lambda x: int(x.split(".")[-1]) if x.split(".")[-1].isdigit() else x)

    if not sparse_files:
        raise RuntimeError("No 'super.img_sparsechunk.*' files found in the selected folder!")

    if not check_fastboot_connection(log_fn=log_fn):
        raise RuntimeError("Phone not detected in Bootloader/Fastboot mode!")

    execute_stock_flash_sequence(rom_dir, sparse_files, log_fn=log_fn, stop_event=stop_event)


def root_phone_cancunf_gui(img_path, partition="boot", log_fn=None, stop_event=None):
    fastboot_bin = get_fastboot_bin()
    if not check_fastboot_connection(log_fn=log_fn):
        raise RuntimeError("Phone not detected in Bootloader/Fastboot mode!")

    if log_fn:
        log_fn(f"[*] Flashing {partition} partition with {os.path.basename(img_path)}...")
    code, _ = run_cmd_stream([fastboot_bin, "flash", partition, img_path], log_fn=log_fn, stop_event=stop_event)
    if code != 0:
        raise RuntimeError(f"Failed to flash {partition} partition!")

    if log_fn:
        log_fn("[✓] Patched image flashed! Rebooting device...")
    run_cmd_stream([fastboot_bin, "reboot"], log_fn=log_fn, stop_event=stop_event)
