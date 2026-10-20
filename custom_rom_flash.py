#!/usr/bin/env python3
import os
import re
import sys
import time
import glob
import shutil
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
    red_bg = Back.RED
    bg_reset = Back.RESET
    bold = Style.BRIGHT
    style_reset = Style.RESET_ALL
except ImportError:
    red = "\033[0;31m"
    green = "\033[0;32m"
    cyan = "\033[0;36m"
    yellow = "\033[1;33m"
    white = "\033[1;37m"
    reset = "\033[0m"
    red_bg = "\033[41m"
    bg_reset = "\033[49m"
    bold = "\033[1m"
    style_reset = "\033[0m"

_ACTIVE_PROCESS = None

SEPT_ARB_BUILDS = [
    "83-20-5-14",
    "83-20-5-8-2-1-3",
    "V1TDS35H.83-20-5-14",
    "V1TDS35H.83-20-5-8-2-1-3",
]

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
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_local_pt_dir():
    return os.path.join(get_app_dir(), "platform-tools")


def get_adb_bin():
    exe = "adb.exe" if os.name == "nt" else "adb"
    local_adb = os.path.join(get_local_pt_dir(), exe)
    if os.path.isfile(local_adb):
        return local_adb
    if shutil.which("termux-adb"):
        return "termux-adb"
    if shutil.which("adb"):
        return "adb"
    win_adb = r"C:\adb\platform-tools\adb.exe"
    if os.name == "nt" and os.path.isfile(win_adb):
        return win_adb
    return "adb"


def get_fastboot_bin():
    exe = "fastboot.exe" if os.name == "nt" else "fastboot"
    local_fb = os.path.join(get_local_pt_dir(), exe)
    if os.path.isfile(local_fb):
        return local_fb
    if shutil.which("termux-fastboot"):
        return "termux-fastboot"
    if shutil.which("fastboot"):
        return "fastboot"
    win_fb = r"C:\adb\platform-tools\fastboot.exe"
    if os.name == "nt" and os.path.isfile(win_fb):
        return win_fb
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
    def _sort_key(path):
        ext = path.rsplit(".", 1)[-1]
        if ext.isdigit():
            return (0, int(ext))
        return (1, ext)

    return sorted(file_list, key=_sort_key)


def detect_stock_folder_version(rom_dir):
    """
    Reads flashfile.xml / servicefile.xml or folder name to identify
    the target Stock ROM build version before flashing.
    """
    if not rom_dir or not os.path.isdir(rom_dir):
        return "Unknown (No XML metadata found)"

    for xml_name in ["flashfile.xml", "servicefile.xml", "efuse.xml"]:
        xml_path = os.path.join(rom_dir, xml_name)
        if os.path.isfile(xml_path):
            try:
                with open(xml_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                m = re.search(r'software_version="([^"]+)"', content)
                if m:
                    return m.group(1)
                m2 = re.search(r'(V1TDS35H\.[0-9\-]+|U1TDS34M\.[0-9\-]+|T1TDS33\.[0-9\-]+)', content)
                if m2:
                    return m2.group(1)
            except Exception:
                pass

    folder_name = os.path.basename(os.path.normpath(rom_dir))
    return folder_name


def validate_stock_rom_folder(rom_dir):
    missing = [
        f for f in REQUIRED_STOCK_FILES
        if not os.path.isfile(os.path.join(rom_dir, f))
    ]
    pattern = os.path.join(rom_dir, "super.img_sparsechunk.*")
    sparse_files = sort_sparsechunks(glob.glob(pattern))
    return missing, sparse_files


def print_september_arb_cli_banner(mode="stock"):
    border = "=" * 68
    print(f"\n{red}{bold}{border}{style_reset}")
    print(
        f"{red_bg}{white}{bold} CRITICAL WARNING: SEPTEMBER SECURITY "
        f"UPDATE & ARB BUMP NOTICE {style_reset}"
    )
    print(f"{red}{bold}{border}{style_reset}")
    print(
        f"{yellow}{bold}Official Community Notice "
        f"(Moto G54 / G64 5G - cancunf):{style_reset}"
    )
    print(
        f"{white}* September builds: V1TDS35H.83-20-5-14 (Global) & "
        f"V1TDS35H.83-20-5-8-2-1-3 (Brazil){style_reset}"
    )
    print(
        f"{white}* These updates BUMP the ARB (Anti-RollBack) "
        f"counter once more!{style_reset}"
    )
    if mode == "stock":
        print(
            f"{red}{bold}1. DO NOT DOWNGRADE:{style_reset} "
            f"{yellow}If your phone updated to the September patch,"
        )
        print(
            "   you CANNOT downgrade to any older Stock Firmware "
            f"(A13 or older A14/A15)!{style_reset}"
        )
        print(
            f"{red}{bold}2. HARD BRICK RISK:{style_reset} "
            f"{yellow}Flashing older Stock preloader/lk on a"
        )
        print(
            "   September+ bootloader WILL trigger ARB and "
            f"PERMANENTLY HARD BRICK your phone!{style_reset}"
        )
    else:
        print(
            f"{red}{bold}1. A16 CUSTOM ROM BRICK:{style_reset} "
            f"{yellow}If you updated to the September patch"
        )
        print(
            "   on Stock ROM, DO NOT flash A16 or incompatible "
            f"Custom ROMs (IT WILL BRICK)!{style_reset}"
        )
        print(
            f"{red}{bold}2. A17 / UPDATED FW:{style_reset} "
            f"{yellow}Only flash Custom ROM builds explicitly updated"
        )
        print(f"   for September+ firmware.{style_reset}")
    print(f"{red}{bold}{border}{style_reset}\n")


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
            err = (
                "[!] No device detected in Fastboot mode! "
                "Connect phone in Bootloader Mode (Power + Vol Down)."
            )
            print(f"{red}{bold}{err}{reset}")
            if log_fn:
                log_fn(err)
            return False
        ok = f"[OK] Fastboot Device Connected: {out}"
        print(f"{green}{ok}{reset}")
        if log_fn:
            log_fn(ok)
        return True
    except FileNotFoundError:
        err = f"[!] Error: '{fastboot_bin}' not found! Install Platform Tools."
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


def check_bootloader_brick_risk(rom_dir=None, log_fn=None):
    fastboot_bin = get_fastboot_bin()
    kwargs = {"capture_output": True, "text": True}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    bl_version = "Unknown"
    fingerprint = "Unknown"
    ro_build = "Unknown"

    try:
        r_all = subprocess.run(
            [fastboot_bin, "getvar", "all"], timeout=6, **kwargs
        )
        all_text = r_all.stdout + "\n" + r_all.stderr
        for line in all_text.splitlines():
            low = line.lower()
            if "version-bootloader:" in low:
                bl_version = line.split("version-bootloader:", 1)[-1].strip()
            elif "ro.build.fingerprint:" in low:
                part = line.split("ro.build.fingerprint:", 1)[-1].strip()
                if part:
                    fingerprint = part if fingerprint == "Unknown" else fingerprint + part
            elif "ro.build.version.incremental:" in low:
                ro_build = line.split("ro.build.version.incremental:", 1)[-1].strip()
    except Exception:
        pass

    target_rom_ver = detect_stock_folder_version(rom_dir) if rom_dir else "N/A (Custom ROM)"

    combined = f"{bl_version} {fingerprint} {ro_build}".lower()
    is_sept = any(tag.lower() in combined for tag in SEPT_ARB_BUILDS)

    bld_disp = ro_build if ro_build != "Unknown" else fingerprint
    info_msg = (
        f"[*] Phone Bootloader: {bl_version} | Phone Build: {bld_disp} "
        f"| Selected Folder: {target_rom_ver}"
    )
    print(f"{cyan}{bold}{info_msg}{reset}")
    if log_fn:
        log_fn(info_msg)

    if is_sept:
        status_line = (
            "[DANGER] SEPTEMBER+ ARB BOOTLOADER DETECTED ON YOUR DEVICE! "
            "DO NOT DOWNGRADE!"
        )
    else:
        status_line = (
            "[!] Verify your device patch level carefully before flashing!"
        )

    warn_box = (
        "EXTREME DANGER: SEPTEMBER SECURITY UPDATE & ARB BRICK WARNING\n\n"
        f"{status_line}\n"
        f"* Phone Current Bootloader : {bl_version}\n"
        f"* Phone Current Build      : {bld_disp}\n"
        f"* Selected ROM Package     : {target_rom_ver}\n\n"
        "OFFICIAL COMMUNITY NOTICE (MOTO G54 / G64 5G):\n"
        "1. The September Security Update (V1TDS35H.83-20-5-14 Global / "
        "V1TDS35H.83-20-5-8-2-1-3 Brazil) bumps the ARB (Anti-RollBack) "
        "counter once more!\n"
        "2. STOCK ROM DOWNGRADE = HARD BRICK: If your phone ever installed "
        "the September update (or newer), you CANNOT downgrade to any older "
        "Stock Firmware (A13 or older A14/A15). Flashing older "
        "preloader.img / lk.img will permanently HARD BRICK your phone!\n"
        "3. CUSTOM ROM BRICK RISK: If you updated to the September patch, "
        "flashing A16 or incompatible Custom ROMs will ALSO lead to a brick!\n\n"
        "* Proceed ONLY if your selected ROM is EQUAL TO or NEWER than your "
        "phone's bootloader!"
    )
    return is_sept, warn_box


def check_adb_sideload_connection(log_fn=None):
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
            if l.strip()
            and not l.startswith("List of")
            and not l.startswith("*")
        ]
        for line in lines:
            low = line.lower()
            if "sideload" in low or "device" in low or "recovery" in low:
                ok = f"[OK] ADB Device Detected: {line}"
                print(f"{green}{ok}{reset}")
                if log_fn:
                    log_fn(ok)
                return True

        err = (
            "[!] Phone not detected in ADB Sideload mode! "
            "In Recovery, select 'Apply update' -> 'Apply from ADB'."
        )
        print(f"{red}{bold}{err}{reset}")
        if log_fn:
            log_fn(err)
        return False
    except FileNotFoundError:
        err = f"[!] Error: '{adb_bin}' not found! Install Platform Tools."
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
    fastboot_bin = get_fastboot_bin()
    for attempt in range(1, 5):
        if stop_event and stop_event.is_set():
            raise RuntimeError("Operation aborted by user.")
        if check_fastboot_connection(log_fn=log_fn):
            _, out = run_cmd_stream(
                [fastboot_bin, "getvar", "is-userspace"],
                log_fn=log_fn, stop_event=stop_event
            )
            if "is-userspace: yes" in out.lower():
                return True, out
        if attempt < 4:
            wait_msg = (
                f"[*] Waiting for FastbootD USB connection "
                f"(Attempt {attempt}/4)..."
            )
            print(f"{yellow}{wait_msg}{reset}")
            if log_fn:
                log_fn(wait_msg)
            time.sleep(2)
    return False, "is-userspace: yes not detected"


def run_cmd_stream(cmd_list, log_fn=None, stop_event=None):
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
    low = output_text.lower()
    if "total xfer:" in low or ret_code == 0:
        if (
            "error:" not in low
            and "cannot read" not in low
            and "no devices/emulators found" not in low
        ):
            return True
    return False


# ==============================================================================
# CLI FUNCTIONS
# ==============================================================================

def custom_rom_flash_cancunf():
    adb_bin = get_adb_bin()
    fastboot_bin = get_fastboot_bin()

    print_september_arb_cli_banner(mode="custom")

    ack_prompt = (
        f"{yellow}Have you read the September Update Custom ROM "
        f"brick warning above? (yes/no): {green}"
    )
    ack = input(ack_prompt).strip().lower()
    print(reset)
    if ack not in ("y", "yes"):
        print(f"{yellow}[*] Custom ROM flash cancelled for safety.{reset}")
        return

    p_init = f"{cyan}Drag & drop or enter [Initial Install Zip]: {green}"
    initial_zip = clean_path(input(p_init))
    if not os.path.isfile(initial_zip):
        print(f"{red}{bold}[!] File not found: {initial_zip}{reset}")
        return

    p_rom = f"{cyan}Drag & drop or enter [Custom ROM Zip]: {green}"
    rom_zip = clean_path(input(p_rom))
    if not os.path.isfile(rom_zip):
        print(f"{red}{bold}[!] File not found: {rom_zip}{reset}")
        return

    print(
        f"\n{yellow}[*] Step 1: Boot phone into Bootloader Mode "
        f"(Power + Volume Down).{reset}"
    )
    input(f"{cyan}Press Enter when connected in Bootloader Mode...{reset}")
    if not check_fastboot_connection():
        return

    check_bootloader_brick_risk()

    print(f"\n{yellow}[*] Step 2: Rebooting into FastbootD Mode...{reset}")
    run_cmd_stream([fastboot_bin, "reboot", "fastboot"])
    input(
        f"{cyan}Wait until phone displays FastbootD menu, "
        f"then press Enter...{reset}"
    )

    print(f"\n{yellow}[*] Step 3: Verifying FastbootD state...{reset}")
    ok_us, out_us = verify_userspace_fastbootd()
    if not ok_us:
        print(
            f"{red}{bold}[!] Safety Stop: 'is-userspace: yes' not confirmed! "
            f"Output:{reset}\n{out_us}"
        )
        return
    print(f"{green}{bold}[OK] Device is safely in FastbootD mode!{reset}")

    print(f"\n{yellow}[*] Step 4: Flashing Initial Install Zip...{reset}")
    code, _ = run_cmd_stream(
        [fastboot_bin, "--skip-reboot", "update", initial_zip]
    )
    if code != 0:
        print(f"{red}{bold}[X] Failed flashing Initial Install Zip!{reset}")
        return

    print(f"\n{yellow}[*] Step 5: Rebooting into Recovery Mode...{reset}")
    run_cmd_stream([fastboot_bin, "reboot", "recovery"])

    print(f"\n{cyan}{bold}--- ACTION REQUIRED ON PHONE ---{reset}")
    print(f"{yellow}1. In Recovery: Select 'Wipe data / Factory reset'.")
    print(f"2. Select 'Apply update' -> 'Apply from ADB'.{reset}")

    while True:
        input(f"\n{cyan}Press Enter when phone is in ADB Sideload...{reset}")
        if check_adb_sideload_connection():
            break
        retry = input(f"{yellow}Retry ADB check? (y/n): {reset}").lower()
        if retry.strip() != "y":
            return

    print(f"\n{yellow}[*] Step 6: Sideloading Custom ROM Zip...{reset}")
    code, out = run_cmd_stream([adb_bin, "sideload", rom_zip])
    if not verify_sideload_result(code, out):
        print(f"{red}{bold}[X] Sideload failed! Check output above.{reset}")
        return

    print(f"\n{green}{bold}{'=' * 60}{reset}")
    print(f"{green}{bold}[OK] Custom ROM Clean Flash Completed!{reset}")
    print(
        f"{yellow}[i] If coming from pre-May 2024 stock ROM, "
        f"sideload once more.{reset}"
    )
    print(f"{green}[*] Select 'Reboot system now' on your phone!{reset}")
    print(f"{green}{bold}{'=' * 60}{reset}")


def dirty_flash_update_cancunf():
    adb_bin = get_adb_bin()
    print_september_arb_cli_banner(mode="custom")

    rom_zip = clean_path(
        input(f"\n{cyan}Drag & drop or enter [ROM Zip]: {green}")
    )
    if not os.path.isfile(rom_zip):
        print(f"{red}{bold}[!] Error: ROM zip not found!{reset}")
        return

    print(f"\n{yellow}[*] Rebooting device into Recovery Mode...{reset}")
    run_cmd_stream([adb_bin, "reboot", "recovery"])

    while True:
        input(
            f"{cyan}In Recovery, select 'Apply update' -> 'Apply from ADB', "
            f"then press Enter...{reset}"
        )
        if check_adb_sideload_connection():
            break
        if input(f"{yellow}Retry ADB check? (y/n): {reset}").lower() != "y":
            return

    code, out = run_cmd_stream([adb_bin, "sideload", rom_zip])
    if verify_sideload_result(code, out):
        print(f"\n{green}{bold}[OK] Update Completed! Reboot phone.{reset}")
    else:
        print(f"\n{red}{bold}[X] Sideload failed!{reset}")


def stock_rom_flash_cancunf():
    print_september_arb_cli_banner(mode="stock")

    ack_prompt = (
        f"{yellow}Do you want to proceed to Bootloader & "
        f"Firmware verification? (yes/no): {green}"
    )
    initial_ack = input(ack_prompt).strip().lower()
    print(reset)
    if initial_ack not in ("y", "yes"):
        print(f"{yellow}[*] Cancelled safely.{reset}")
        return

    p_dir = f"\n{cyan}Drag & drop [Extracted Stock ROM Folder]: {green}"
    rom_dir = clean_path(input(p_dir))
    if os.path.isfile(rom_dir):
        rom_dir = os.path.dirname(rom_dir)
    if not os.path.isdir(rom_dir):
        print(f"{red}{bold}[!] Folder not found!{reset}")
        return

    missing, sparse_files = validate_stock_rom_folder(rom_dir)
    if missing:
        print(f"{red}{bold}[!] Missing required firmware files:{reset}")
        for m in missing:
            print(f"    {red}- {m}{reset}")
        return

    if not sparse_files:
        print(f"{red}{bold}[!] No 'super.img_sparsechunk.*' found!{reset}")
        return

    rom_ver = detect_stock_folder_version(rom_dir)
    print(
        f"\n{green}[OK] All 21 partition images + {len(sparse_files)} "
        f"sparsechunks verified! (Package: {rom_ver}){reset}"
    )

    print(
        f"\n{yellow}[*] Step 1: Connect phone in Bootloader Mode "
        f"(Power + Volume Down).{reset}"
    )
    input(f"{cyan}Press Enter when connected in Bootloader Mode...{reset}")
    if not check_fastboot_connection():
        return

    print(f"\n{yellow}[*] Step 2: Querying Bootloader version...{reset}")
    _, warn_text = check_bootloader_brick_risk(rom_dir=rom_dir)
    print(f"\n{red}{bold}{'=' * 68}{reset}")
    print(f"{yellow}{bold}{warn_text}{reset}")
    print(f"{red}{bold}{'=' * 68}{reset}")

    c_prompt = (
        f"\n{red}{bold}CRITICAL SAFETY CONFIRMATION (ANTI-ROLLBACK):{reset}\n"
        f"Are you 100% sure the Stock ROM is EQUAL TO or NEWER than "
        f"your current bootloader?\n"
        f"Type {cyan}'I UNDERSTAND THE BRICK RISK'{reset} to proceed: {green}"
    )
    confirm_arb = input(c_prompt).strip()
    print(reset)

    if confirm_arb != "I UNDERSTAND THE BRICK RISK":
        print(f"{yellow}[*] Stock ROM flash cancelled. Brick avoided!{reset}")
        return

    w_prompt = (
        f"{cyan}Final Confirmation: Type 'YES' to wipe userdata and "
        f"flash Slot A & B: {green}"
    )
    if input(w_prompt).strip() != "YES":
        print(f"{yellow}[*] Stock flash cancelled by user.{reset}")
        return

    try:
        execute_stock_flash_sequence(rom_dir, sparse_files)
    except Exception as e:
        print(f"\n{red}{bold}[X] Stock Flash Aborted: {e}{reset}")


def execute_stock_flash_sequence(
    rom_dir, sparse_files, log_fn=None, stop_event=None
):
    fastboot_bin = get_fastboot_bin()

    def log_both(msg, color=yellow):
        print(f"\n{color}{bold}{msg}{reset}")
        if log_fn:
            log_fn(msg)

    def fb(*args):
        code, _ = run_cmd_stream(
            [fastboot_bin] + list(args),
            log_fn=log_fn, stop_event=stop_event
        )
        if code != 0:
            raise RuntimeError(f"Fastboot failed: fastboot {' '.join(args)}")
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
        ("vbmeta_system_a", "vbmeta_system.img"),
        ("vbmeta_system_b", "vbmeta_system.img"),
        ("md1img_a", "md1img.img"), ("md1img_b", "md1img.img"),
        ("dpm_a", "dpm.img"), ("dpm_b", "dpm.img"),
        ("gz_a", "gz.img"), ("gz_b", "gz.img"),
        ("vcp_a", "vcp.img"), ("vcp_b", "vcp.img"),
        ("gpueb_a", "gpueb.img"), ("gpueb_b", "gpueb.img"),
        ("efuseBackup", "efuse.img"),
        ("boot_a", "boot.img"), ("boot_b", "boot.img"),
        ("vendor_boot_a", "vendor_boot.img"),
        ("vendor_boot_b", "vendor_boot.img"),
    ]
    for part, img in ab_part_2:
        flash_part(part, img)

    tot = len(sparse_files)
    log_both(f"[3/4] Flashing Super Partition ({tot} sparsechunks)...")
    for idx, chunk_path in enumerate(sparse_files):
        chunk_name = os.path.basename(chunk_path)
        c_msg = f"[*] Flashing super chunk ({idx + 1}/{tot}): {chunk_name}"
        print(f"{green}{c_msg}{reset}")
        if log_fn:
            log_fn(c_msg)
        fb("flash", "super", chunk_path)

    log_both("[4/4] Wiping Userdata, Metadata & Clearing OEM Flags...")
    fb("erase", "userdata")
    fb("erase", "metadata")
    fb("erase", "debug_token")
    fb("oem", "fb_mode_clear")
    run_cmd_stream(
        [fastboot_bin, "oem", "config", "unset", "console"],
        log_fn=log_fn, stop_event=stop_event
    )
    run_cmd_stream(
        [fastboot_bin, "oem", "config", "unset", "cmdl"],
        log_fn=log_fn, stop_event=stop_event
    )

    log_both(
        "[OK] FULL CLEAN FLASH COMPLETED! PRESS POWER BUTTON TO REBOOT!",
        color=green
    )


def root_phone_cancunf():
    fastboot_bin = get_fastboot_bin()
    print(f"\n{cyan}{bold}{'=' * 60}{reset}")
    print(f"{cyan}{bold}   Root Moto G54/G64 (Flash Patched Image){reset}")
    print(f"{cyan}{bold}{'=' * 60}{reset}")
    print(f"{green}[{red}1{green}]{reset}. boot (Magisk / KernelSU)")
    print(f"{green}[{red}2{green}]{reset}. init_boot")
    print(f"{green}[{red}3{green}]{reset}. vendor_boot")

    part_choice = input(f"\n\t{cyan}Select partition (1-3): {green}").strip()
    part_map = {"1": "boot", "2": "init_boot", "3": "vendor_boot"}
    partition = part_map.get(part_choice, "boot")

    img_path = clean_path(
        input(f"{cyan}Drag & drop patched [{partition}.img]: {green}")
    )
    if not os.path.isfile(img_path):
        print(f"{red}{bold}[!] File not found: {img_path}{reset}")
        return

    input(f"\n{cyan}Connect phone in Bootloader Mode and press Enter...{reset}")
    if not check_fastboot_connection():
        return

    code, _ = run_cmd_stream([fastboot_bin, "flash", partition, img_path])
    if code == 0:
        print(f"{green}{bold}[OK] Flashed {partition}! Rebooting...{reset}")
        run_cmd_stream([fastboot_bin, "reboot"])
    else:
        print(f"{red}{bold}[X] Failed flashing {partition}!{reset}")


# ==============================================================================
# GUI HANDLERS
# ==============================================================================

def custom_rom_flash_cancunf_gui(
    initial_zip, rom_zip, log_fn=None, prompt_fn=None, stop_event=None
):
    adb_bin = get_adb_bin()
    fastboot_bin = get_fastboot_bin()

    if not check_fastboot_connection(log_fn=log_fn):
        raise RuntimeError(
            "No device detected in Bootloader Mode! Connect phone first."
        )

    _, warn_text = check_bootloader_brick_risk(log_fn=log_fn)
    if prompt_fn:
        msg = (
            warn_text
            + "\n\nClick OK ONLY if you have verified that this Custom ROM "
            "is compatible with your current bootloader!"
        )
        if not prompt_fn(msg):
            raise RuntimeError("Cancelled after September Update safety check.")

    if log_fn:
        log_fn("[*] Step 1: Rebooting into FastbootD Mode...")
    code, _ = run_cmd_stream(
        [fastboot_bin, "reboot", "fastboot"],
        log_fn=log_fn, stop_event=stop_event
    )
    if code != 0:
        raise RuntimeError("Failed to execute 'fastboot reboot fastboot'.")

    if prompt_fn and not prompt_fn(
        "Wait for your phone screen to enter FastbootD Mode.\n\n"
        "Click OK once the phone displays the FastbootD menu."
    ):
        raise RuntimeError("Operation cancelled by user.")

    if log_fn:
        log_fn("[*] Step 2: Verifying FastbootD (is-userspace) state...")
    ok_us, out_us = verify_userspace_fastbootd(
        log_fn=log_fn, stop_event=stop_event
    )
    if not ok_us:
        raise RuntimeError(
            f"Safety Stop: Device is NOT in FastbootD mode ({out_us})."
        )

    if log_fn:
        log_fn("[OK] Device is safely in FastbootD mode!")
        log_fn("[*] Step 3: Flashing Initial Install Zip...")

    code, _ = run_cmd_stream(
        [fastboot_bin, "--skip-reboot", "update", initial_zip],
        log_fn=log_fn, stop_event=stop_event
    )
    if code != 0:
        raise RuntimeError("Failed flashing Initial Install Zip!")

    if log_fn:
        log_fn("[*] Step 4: Rebooting into Recovery Mode...")
    run_cmd_stream(
        [fastboot_bin, "reboot", "recovery"],
        log_fn=log_fn, stop_event=stop_event
    )

    while True:
        if prompt_fn and not prompt_fn(
            "ACTION REQUIRED ON PHONE:\n\n"
            "1. In Recovery, select 'Wipe data / Factory reset'.\n"
            "2. Select 'Apply update' -> 'Apply from ADB'.\n\n"
            "Click OK once phone is waiting in ADB Sideload mode."
        ):
            raise RuntimeError("Operation cancelled before ADB Sideload.")

        if check_adb_sideload_connection(log_fn=log_fn):
            break

    if log_fn:
        log_fn("[*] Step 5: Sideloading Custom ROM Zip (47% is normal)...")
    code, out = run_cmd_stream(
        [adb_bin, "sideload", rom_zip],
        log_fn=log_fn, stop_event=stop_event
    )
    if not verify_sideload_result(code, out):
        raise RuntimeError("ADB Sideload failed! Check console log.")

    if log_fn:
        log_fn("[OK] Sideload finished! Select 'Reboot system now' on phone.")


def dirty_flash_update_cancunf_gui(
    rom_zip, log_fn=None, prompt_fn=None, stop_event=None
):
    adb_bin = get_adb_bin()
    if log_fn:
        log_fn("[*] Rebooting device into Recovery Mode...")
    run_cmd_stream(
        [adb_bin, "reboot", "recovery"],
        log_fn=log_fn, stop_event=stop_event
    )

    while True:
        if prompt_fn and not prompt_fn(
            "On phone Recovery menu:\n"
            "Select 'Apply update' -> 'Apply from ADB'.\n\n"
            "Click OK when ready in ADB Sideload mode."
        ):
            raise RuntimeError("Update cancelled by user.")

        if check_adb_sideload_connection(log_fn=log_fn):
            break

    if log_fn:
        log_fn("[*] Sideloading ROM Update...")
    code, out = run_cmd_stream(
        [adb_bin, "sideload", rom_zip],
        log_fn=log_fn, stop_event=stop_event
    )
    if not verify_sideload_result(code, out):
        raise RuntimeError("ADB Sideload failed! Check console log.")

    if log_fn:
        log_fn("[OK] ROM Update completed! Reboot your phone.")


def stock_rom_flash_cancunf_gui(
    rom_dir, log_fn=None, prompt_fn=None, stop_event=None
):
    missing, sparse_files = validate_stock_rom_folder(rom_dir)
    if missing:
        raise RuntimeError(
            "Missing critical firmware files:\n" + ", ".join(missing[:8])
        )

    if not sparse_files:
        raise RuntimeError("No 'super.img_sparsechunk.*' files found!")

    if not check_fastboot_connection(log_fn=log_fn):
        raise RuntimeError("Phone not detected in Bootloader mode!")

    _, warn_text = check_bootloader_brick_risk(rom_dir=rom_dir, log_fn=log_fn)
    if prompt_fn:
        msg = (
            warn_text
            + "\n\nClick OK ONLY if your Stock ROM package is EQUAL TO "
            "or NEWER than your device's bootloader patch level!"
        )
        if not prompt_fn(msg):
            raise RuntimeError(
                "Cancelled after September update Anti-Rollback check."
            )

    if log_fn:
        log_fn(
            f"[OK] Pre-check passed: 21 images + "
            f"{len(sparse_files)} super chunks verified."
        )

    execute_stock_flash_sequence(
        rom_dir, sparse_files, log_fn=log_fn, stop_event=stop_event
    )


def root_phone_cancunf_gui(
    img_path, partition="boot", log_fn=None, stop_event=None
):
    fastboot_bin = get_fastboot_bin()
    if not check_fastboot_connection(log_fn=log_fn):
        raise RuntimeError("Phone not detected in Bootloader mode!")

    if log_fn:
        log_fn(f"[*] Flashing {partition} with {os.path.basename(img_path)}...")
    code, _ = run_cmd_stream(
        [fastboot_bin, "flash", partition, img_path],
        log_fn=log_fn, stop_event=stop_event
    )
    if code != 0:
        raise RuntimeError(f"Failed to flash {partition} partition!")

    if log_fn:
        log_fn("[OK] Patched image flashed! Rebooting device...")
    run_cmd_stream(
        [fastboot_bin, "reboot"], log_fn=log_fn, stop_event=stop_event
    )
