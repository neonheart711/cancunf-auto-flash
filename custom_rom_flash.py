#!/usr/bin/env python3
import os
import sys
import time
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

# Mandatory Stock ROM files required by official flashfile scripts (A13/A14/A15)
REQUIRED_STOCK_FILES = [
    "PGPT",
    "preloader.img",
    "lk.img",
    "tee.img",
    "mcupm.img",
    "pi_img.img",
    "sspm.img",
    "dtbo.img",
    "logo.img",
    "spmfw.img",
    "scp.img",
    "vbmeta.img",
    "vbmeta_system.img",
    "md1img.img",
    "dpm.img",
    "gz.img",
    "vcp.img",
    "gpueb.img",
    "efuse.img",
    "boot.img",
    "vendor_boot.img",
]


def get_app_dir():
    """Directory where the executable or main script resides (for portable platform-tools)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir():
    """Directory where bundled scripts (.bat/.sh) reside (supports PyInstaller _MEIPASS)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_local_pt_dir():
    return os.path.join(get_app_dir(), "platform-tools")


def get_adb_bin():
    local_adb = os.path.join(get_local_pt_dir(), "adb.exe" if os.name == "nt" else "adb")
    if os.path.isfile(local_adb):
        return local_adb
    if shutil.which("termux-adb"):
        return "termux-adb"
    if shutil.which("adb"):
        return "adb"
    if os.name == "nt" and os.path.isfile(r"C:\adb\platform-tools\adb.exe"):
        return r"C:\adb\platform-tools\adb.exe"
    return "adb"


def get_fastboot_bin():
    local_fb = os.path.join(get_local_pt_dir(), "fastboot.exe" if os.name == "nt" else "fastboot")
    if os.path.isfile(local_fb):
        return local_fb
    if shutil.which("termux-fastboot"):
        return "termux-fastboot"
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


def sort_sparsechunks(file_list):
    """Safely sort super.img_sparsechunk.* numerically without raising TypeError."""
    def _sort_key(path):
        ext = path.rsplit(".", 1)[-1]
        if ext.isdigit():
            return (0, int(ext))
        return (1, ext)

    return sorted(file_list, key=_sort_key)


def validate_stock_rom_folder(rom_dir):
    """Verify all required partition images and super sparsechunks exist before flashing."""
    missing = [f for f in REQUIRED_STOCK_FILES if not os.path.isfile(os.path.join(rom_dir, f))]
    sparse_files = sort_sparsechunks(glob.glob(os.path.join(rom_dir, "super.img_sparsechunk.*")))
    return missing, sparse_files


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
        res = subprocess.run([fastboot_bin, "devices"], timeout=8, **kwargs)
        out = res.stdout.strip()
        if not out:
            err = "[!] No device detected in Fastboot mode! Connect phone in Bootloader Mode (Power + Vol Down)."
            print(f"{red}{bold}{err}{reset}")
            if log_fn:
                log_fn(err)
            return False
        ok = f"[✓] Fastboot Device Connected: {out}"
        print(f"{green}{ok}{reset}")
        if log_fn:
            log_fn(ok)
        return True
    except FileNotFoundError:
        err = f"[!] Error: '{fastboot_bin}' not found! Please install Platform Tools first."
        print(f"{red}{bold}{err}{reset}")
        if log_fn:
            log_fn(err)
        return False
    except subprocess.TimeoutExpired:
        err = "[!] Fastboot check timed out. Check USB cable or drivers."
        print(f"{red}{bold}{err}{reset}")
        if log_fn:
            log_fn(err)
        return False


def check_adb_sideload_connection(log_fn=None):
    """Verify the phone is actually in 'sideload' mode via 'adb devices' before sideloading."""
    adb_bin = get_adb_bin()
    msg = "[*] Checking ADB Sideload connection..."
    print(f"\n{yellow}{msg}{reset}")
    if log_fn:
        log_fn(msg)

    kwargs = {"capture_output": True, "text": True}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    try:
        subprocess.run([adb_bin, "start-server"], timeout=6, **kwargs)
        res = subprocess.run([adb_bin, "devices"], timeout=6, **kwargs)
        lines = [
            l.strip() for l in res.stdout.splitlines()
            if l.strip() and not l.startswith("List of") and not l.startswith("*")
        ]
        for line in lines:
            if "sideload" in line.lower() or "device" in line.lower() or "recovery" in line.lower():
                ok = f"[✓] ADB Device Detected: {line}"
                print(f"{green}{ok}{reset}")
                if log_fn:
                    log_fn(ok)
                return True

        err = "[!] Phone not detected in ADB Sideload mode! On phone Recovery, select 'Apply update' -> 'Apply from ADB'."
        print(f"{red}{bold}{err}{reset}")
        if log_fn:
            log_fn(err)
        return False
    except FileNotFoundError:
        err = f"[!] Error: '{adb_bin}' not found! Install Platform Tools first."
        print(f"{red}{bold}{err}{reset}")
        if log_fn:
            log_fn(err)
        return False
    except Exception as e:
        err = f"[!] ADB check failed: {e}"
        if log_fn:
            log_fn(err)
        return False


def verify_userspace_fastbootd(log_fn=None, stop_event=None):
    """Polls fastboot getvar is-userspace up to 4 times to allow USB re-enumeration after rebooting to fastbootd."""
    fastboot_bin = get_fastboot_bin()
    for attempt in range(1, 5):
        if stop_event and stop_event.is_set():
            raise RuntimeError("Operation aborted by user.")
        if check_fastboot_connection(log_fn=log_fn):
            _, out = run_cmd_stream([fastboot_bin, "getvar", "is-userspace"], log_fn=log_fn, stop_event=stop_event)
            if "is-userspace: yes" in out.lower():
                return True, out
        if attempt < 4:
            wait_msg = f"[*] Waiting for FastbootD USB connection (Attempt {attempt}/4)..."
            print(f"{yellow}{wait_msg}{reset}")
            if log_fn:
                log_fn(wait_msg)
            time.sleep(2)
    return False, "is-userspace: yes not detected"


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
        "stdin": subprocess.DEVNULL,
    }
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


def verify_sideload_result(ret_code, output_text):
    """
    ADB sideload on AOSP/Lineage/YAAP recovery often stops at 47% and prints 'Total xfer: 1.00x'
    (sometimes with returncode 0 or 1), whereas real errors print 'cannot read', 'failed to connect', or 'error:'.
    """
    low = output_text.lower()
    if "total xfer:" in low or ret_code == 0:
        if "error:" not in low and "cannot read" not in low and "no devices/emulators found" not in low:
            return True
    return False


# ==============================================================================
# CLI FUNCTIONS
# ==============================================================================

def custom_rom_flash_cancunf():
    adb_bin = get_adb_bin()
    fastboot_bin = get_fastboot_bin()

    print(f"\n{cyan}{bold}============================================================{reset}")
    print(f"{cyan}{bold}   Moto G54/G64 (cancunf) Custom ROM Clean Flasher          {reset}")
    print(f"{cyan}{bold}============================================================{reset}")
    print(f"{yellow}[!] Prerequisite: Bootloader must already be unlocked.{reset}")
    print(f"{yellow}[!] All user data will be wiped in Recovery. Backup first!{reset}\n")

    initial_zip = clean_path(input(f"{cyan}Drag & drop or enter path to [Initial Install Zip]: {green}"))
    if not os.path.isfile(initial_zip):
        print(f"{red}{bold}[!] Error: Initial install zip not found at: {initial_zip}{reset}")
        return

    rom_zip = clean_path(input(f"{cyan}Drag & drop or enter path to [Custom ROM Zip]: {green}"))
    if not os.path.isfile(rom_zip):
        print(f"{red}{bold}[!] Error: ROM zip not found at: {rom_zip}{reset}")
        return

    print(f"\n{yellow}[*] Step 1: Boot phone into Bootloader Mode (Power + Volume Down).{reset}")
    input(f"{cyan}Press Enter when connected in Bootloader Mode...{reset}")
    if not check_fastboot_connection():
        return

    print(f"\n{yellow}[*] Step 2: Rebooting into FastbootD (Userspace Fastboot) Mode...{reset}")
    run_cmd_stream([fastboot_bin, "reboot", "fastboot"])
    input(f"{cyan}Wait until phone displays the FastbootD menu, then press Enter...{reset}")

    print(f"\n{yellow}[*] Step 3: Verifying FastbootD (is-userspace: yes) state...{reset}")
    ok_us, out_us = verify_userspace_fastbootd()
    if not ok_us:
        print(f"{red}{bold}[!] Safety Stop: 'is-userspace: yes' not confirmed! Output:{reset}\n{out_us}")
        print(f"{red}[!] Never flash initial_install.zip in standard Bootloader mode!{reset}")
        return
    print(f"{green}{bold}[✓] Confirmed: Device is safely in FastbootD mode!{reset}")

    print(f"\n{yellow}[*] Step 4: Flashing Initial Install Zip (boot + vendor_boot)...{reset}")
    code, _ = run_cmd_stream([fastboot_bin, "--skip-reboot", "update", initial_zip])
    if code != 0:
        print(f"{red}{bold}[✗] Failed flashing Initial Install Zip! Aborting.{reset}")
        return

    print(f"\n{yellow}[*] Step 5: Rebooting into Recovery Mode...{reset}")
    run_cmd_stream([fastboot_bin, "reboot", "recovery"])

    print(f"\n{cyan}{bold}---------------- ACTION REQUIRED ON PHONE ----------------{reset}")
    print(f"{yellow}1. In Recovery: Select 'Wipe data / Factory reset' and format /data.")
    print(f"2. Go back to main Recovery menu and select 'Apply update' -> 'Apply from ADB'.{reset}")
    print(f"{cyan}{bold}----------------------------------------------------------{reset}")

    while True:
        input(f"\n{cyan}Press Enter once phone is waiting in ADB Sideload mode...{reset}")
        if check_adb_sideload_connection():
            break
        retry = input(f"{yellow}Retry checking ADB Sideload connection? (y/n): {reset}").strip().lower()
        if retry != "y":
            return

    print(f"\n{yellow}[*] Step 6: Sideloading Custom ROM Zip (Stopping at 47% with 'Total xfer: 1.00x' is normal)...{reset}")
    code, out = run_cmd_stream([adb_bin, "sideload", rom_zip])
    if not verify_sideload_result(code, out):
        print(f"{red}{bold}[✗] Sideload failed! Check output above and try again.{reset}")
        return

    print(f"\n{green}{bold}============================================================{reset}")
    print(f"{green}{bold}[✓] Custom ROM Clean Flash Completed!{reset}")
    print(f"{yellow}[i] Pre-May 2024 Stock Firmware Note: If your previous stock ROM was older than")
    print(f"    May 2024 (Android 14), reboot to Recovery and sideload the ROM a second time")
    print(f"    (without wiping data) to populate both Slot A & Slot B.{reset}")
    print(f"{green}[*] Otherwise, select 'Reboot system now' on your phone!{reset}")
    print(f"{green}{bold}============================================================{reset}")


def dirty_flash_update_cancunf():
    adb_bin = get_adb_bin()
    rom_zip = clean_path(input(f"\n{cyan}Drag & drop or enter path to new [ROM Zip]: {green}"))
    if not os.path.isfile(rom_zip):
        print(f"{red}{bold}[!] Error: ROM zip not found!{reset}")
        return

    print(f"\n{yellow}[*] Attempting to reboot device into Recovery Mode...{reset}")
    run_cmd_stream([adb_bin, "reboot", "recovery"])

    while True:
        input(f"{cyan}In Recovery, select 'Apply update' -> 'Apply from ADB', then press Enter...{reset}")
        if check_adb_sideload_connection():
            break
        if input(f"{yellow}Retry ADB check? (y/n): {reset}").strip().lower() != "y":
            return

    code, out = run_cmd_stream([adb_bin, "sideload", rom_zip])
    if verify_sideload_result(code, out):
        print(f"\n{green}{bold}[✓] Update Completed! Select 'Reboot system now' on your phone.{reset}")
    else:
        print(f"\n{red}{bold}[✗] Sideload failed! Please check the error output above.{reset}")


def stock_rom_flash_cancunf():
    print(f"\n{cyan}{bold}============================================================{reset}")
    print(f"{cyan}{bold}     Flashing BOTH SLOT A and SLOT B (STOCK FIRMWARE)       {reset}")
    print(f"{cyan}{bold}                FULL CLEAN FLASH (cancunf)                  {reset}")
    print(f"{cyan}{bold}============================================================{reset}")

    rom_dir = clean_path(input(f"\n{cyan}Drag & drop or enter [Extracted Stock ROM Folder]: {green}"))
    if os.path.isfile(rom_dir):
        rom_dir = os.path.dirname(rom_dir)
    if not os.path.isdir(rom_dir):
        print(f"{red}{bold}[!] Folder not found!{reset}")
        return

    missing, sparse_files = validate_stock_rom_folder(rom_dir)
    if missing:
        print(f"{red}{bold}[!] Safety Check Failed! The following required firmware files are missing:{reset}")
        for m in missing:
            print(f"    {red}- {m}{reset}")
        print(f"{yellow}[i] Please extract the complete Motorola Stock Firmware zip before flashing.{reset}")
        return

    if not sparse_files:
        print(f"{red}{bold}[!] Safety Check Failed: No 'super.img_sparsechunk.*' files found!{reset}")
        return

    print(f"\n{green}[✓] All 21 partition images + {len(sparse_files)} super sparsechunks verified!{reset}")
    if input(f"{cyan}Type 'YES' in uppercase to wipe userdata and clean flash Slot A & B: {green}").strip() != "YES":
        print(f"{yellow}[*] Cancelled.{reset}")
        return

    input(f"\n{cyan}Connect phone in Bootloader Mode (Power + Volume Down) and press Enter...{reset}")
    if not check_fastboot_connection():
        return

    try:
        execute_stock_flash_sequence(rom_dir, sparse_files)
    except Exception as e:
        print(f"\n{red}{bold}[✗] Stock Flash Aborted: {e}{reset}")


def execute_stock_flash_sequence(rom_dir, sparse_files, log_fn=None, stop_event=None):
    """Executes the exact official Motorola cancunf Slot A & Slot B clean flash sequence."""
    fastboot_bin = get_fastboot_bin()

    def log_both(msg, color=yellow):
        print(f"\n{color}{bold}{msg}{reset}")
        if log_fn:
            log_fn(msg)

    def fb(*args):
        code, _ = run_cmd_stream([fastboot_bin] + list(args), log_fn=log_fn, stop_event=stop_event)
        if code != 0:
            raise RuntimeError(f"Fastboot command failed: fastboot {' '.join(args)}")
        return code

    def flash_part(partition, filename):
        file_path = os.path.join(rom_dir, filename)
        fb("flash", partition, file_path)

    log_both("[1/4] Flashing Partition Table (GPT) & Preloader...")
    fb("--set-active=a")
    flash_part("gpt", "PGPT")
    fb("getvar", "max-sparse-size")
    fb("oem", "fb_mode_set")
    flash_part("preloader", "preloader.img")

    log_both("[2/4] Flashing Slot A & Slot B Firmware Partitions...")
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

    log_both(f"[3/4] Flashing Super Partition ({len(sparse_files)} sparsechunks)...")
    for idx, chunk_path in enumerate(sparse_files):
        chunk_name = os.path.basename(chunk_path)
        c_msg = f"[*] Flashing super chunk ({idx + 1}/{len(sparse_files)}): {chunk_name}"
        print(f"{green}{c_msg}{reset}")
        if log_fn:
            log_fn(c_msg)
        fb("flash", "super", chunk_path)

    log_both("[4/4] Wiping Userdata, Metadata & Clearing Fastboot OEM Flags...")
    fb("erase", "userdata")
    fb("erase", "metadata")
    fb("erase", "debug_token")
    fb("oem", "fb_mode_clear")
    # 'oem config unset' may return non-zero on some locked/unlocked states, run safely
    run_cmd_stream([fastboot_bin, "oem", "config", "unset", "console"], log_fn=log_fn, stop_event=stop_event)
    run_cmd_stream([fastboot_bin, "oem", "config", "unset", "cmdl"], log_fn=log_fn, stop_event=stop_event)

    log_both("[✓] FULL CLEAN FLASH COMPLETED! PRESS POWER BUTTON ON PHONE TO REBOOT!", color=green)


def root_phone_cancunf():
    fastboot_bin = get_fastboot_bin()
    print(f"\n{cyan}{bold}============================================================{reset}")
    print(f"{cyan}{bold}      Root Moto G54/G64 (Flash Patched Image)               {reset}")
    print(f"{cyan}{bold}============================================================{reset}")
    print(f"{green}[{red}1{green}]{reset}. boot        (Standard Magisk / KernelSU patched boot.img)")
    print(f"{green}[{red}2{green}]{reset}. init_boot   (Patched init_boot.img)")
    print(f"{green}[{red}3{green}]{reset}. vendor_boot (Patched vendor_boot.img)")

    part_choice = input(f"\n\t{cyan}Select partition (1-3): {green}").strip()
    part_map = {"1": "boot", "2": "init_boot", "3": "vendor_boot"}
    partition = part_map.get(part_choice, "boot")

    img_path = clean_path(input(f"{cyan}Drag & drop patched [{partition}.img]: {green}"))
    if not os.path.isfile(img_path):
        print(f"{red}{bold}[!] Error: File not found at: {img_path}{reset}")
        return

    input(f"\n{cyan}Connect phone in Bootloader Mode and press Enter...{reset}")
    if not check_fastboot_connection():
        return

    code, _ = run_cmd_stream([fastboot_bin, "flash", partition, img_path])
    if code == 0:
        print(f"{green}{bold}[✓] Successfully flashed {partition}! Rebooting phone...{reset}")
        run_cmd_stream([fastboot_bin, "reboot"])
    else:
        print(f"{red}{bold}[✗] Failed flashing {partition}!{reset}")


# ==============================================================================
# GUI HANDLERS
# ==============================================================================

def custom_rom_flash_cancunf_gui(initial_zip, rom_zip, log_fn=None, prompt_fn=None, stop_event=None):
    adb_bin = get_adb_bin()
    fastboot_bin = get_fastboot_bin()

    if not check_fastboot_connection(log_fn=log_fn):
        raise RuntimeError("No device detected in Bootloader/Fastboot mode! Connect phone in Bootloader Mode first.")

    if log_fn:
        log_fn("[*] Step 1: Rebooting device into FastbootD (Userspace Fastboot) Mode...")
    code, _ = run_cmd_stream([fastboot_bin, "reboot", "fastboot"], log_fn=log_fn, stop_event=stop_event)
    if code != 0:
        raise RuntimeError("Failed to execute 'fastboot reboot fastboot'.")

    if prompt_fn and not prompt_fn(
        "Wait for your phone screen to enter FastbootD Mode.\n\n"
        "Click OK once the phone displays the FastbootD menu."
    ):
        raise RuntimeError("Operation cancelled by user.")

    if log_fn:
        log_fn("[*] Step 2: Verifying FastbootD (is-userspace) state...")
    ok_us, out_us = verify_userspace_fastbootd(log_fn=log_fn, stop_event=stop_event)
    if not ok_us:
        raise RuntimeError(
            f"Safety Stop: Device is NOT in FastbootD mode ({out_us}). "
            "Never flash initial_install.zip in standard Bootloader mode!"
        )

    if log_fn:
        log_fn("[✓] Confirmed: Device is safely in FastbootD (userspace) mode!")
        log_fn("[*] Step 3: Flashing Initial Install Zip (boot + vendor_boot)...")

    code, _ = run_cmd_stream([fastboot_bin, "--skip-reboot", "update", initial_zip], log_fn=log_fn, stop_event=stop_event)
    if code != 0:
        raise RuntimeError("Failed flashing Initial Install Zip!")

    if log_fn:
        log_fn("[*] Step 4: Rebooting into Recovery Mode...")
    run_cmd_stream([fastboot_bin, "reboot", "recovery"], log_fn=log_fn, stop_event=stop_event)

    while True:
        if prompt_fn and not prompt_fn(
            "ACTION REQUIRED ON PHONE:\n\n"
            "1. In Recovery, select 'Wipe data / Factory reset' and format /data.\n"
            "2. Go back to the main Recovery menu and select 'Apply update' -> 'Apply from ADB'.\n\n"
            "Click OK once your phone is waiting in ADB Sideload mode."
        ):
            raise RuntimeError("Operation cancelled before ADB Sideload.")

        if check_adb_sideload_connection(log_fn=log_fn):
            break

    if log_fn:
        log_fn("[*] Step 5: Sideloading Custom ROM Zip (Stopping at 47% with 'Total xfer: 1.00x' is normal)...")
    code, out = run_cmd_stream([adb_bin, "sideload", rom_zip], log_fn=log_fn, stop_event=stop_event)
    if not verify_sideload_result(code, out):
        raise RuntimeError("ADB Sideload failed! Check the console log for details.")

    if log_fn:
        log_fn("[✓] Sideload finished! Note: If coming from pre-May 2024 stock firmware, sideload once more in Recovery.")
        log_fn("[✓] Otherwise, select 'Reboot system now' on your phone!")


def dirty_flash_update_cancunf_gui(rom_zip, log_fn=None, prompt_fn=None, stop_event=None):
    adb_bin = get_adb_bin()
    if log_fn:
        log_fn("[*] Attempting to reboot device into Recovery Mode...")
    run_cmd_stream([adb_bin, "reboot", "recovery"], log_fn=log_fn, stop_event=stop_event)

    while True:
        if prompt_fn and not prompt_fn(
            "On your phone's Recovery menu:\n"
            "Select 'Apply update' -> 'Apply from ADB'.\n\n"
            "Click OK when the phone is ready in ADB Sideload mode."
        ):
            raise RuntimeError("Update cancelled by user.")

        if check_adb_sideload_connection(log_fn=log_fn):
            break

    if log_fn:
        log_fn("[*] Sideloading ROM Update...")
    code, out = run_cmd_stream([adb_bin, "sideload", rom_zip], log_fn=log_fn, stop_event=stop_event)
    if not verify_sideload_result(code, out):
        raise RuntimeError("ADB Sideload failed! Check console log for details.")

    if log_fn:
        log_fn("[✓] ROM Update completed! Select 'Reboot system now' on your phone.")


def stock_rom_flash_cancunf_gui(rom_dir, log_fn=None, stop_event=None):
    missing, sparse_files = validate_stock_rom_folder(rom_dir)
    if missing:
        raise RuntimeError(
            "Safety Stop! The selected Stock ROM folder is missing critical firmware files:\n"
            + ", ".join(missing[:8]) + ("..." if len(missing) > 8 else "")
        )

    if not sparse_files:
        raise RuntimeError("No 'super.img_sparsechunk.*' files found in the selected folder!")

    if not check_fastboot_connection(log_fn=log_fn):
        raise RuntimeError("Phone not detected in Bootloader/Fastboot mode!")

    if log_fn:
        log_fn(f"[✓] Pre-check passed: All 21 firmware images + {len(sparse_files)} super chunks verified.")

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
