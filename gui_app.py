#!/usr/bin/env python3
import os
import sys
import shutil
import zipfile
import platform
import threading
import subprocess
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

from custom_rom_flash import (
    get_adb_bin,
    get_fastboot_bin,
    get_local_pt_dir,
    custom_rom_flash_cancunf_gui,
    dirty_flash_update_cancunf_gui,
    stock_rom_flash_cancunf_gui,
    root_phone_cancunf_gui,
    abort_active_process
)

# Enable High-DPI scaling on Windows so UI text and buttons are sharp and never clipped
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


class CancunfToolkitGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Motorola Moto G54 / G64 5G (cancunf) All-In-One Toolkit")
        self.geometry("880x720")
        self.minsize(780, 620)
        self.resizable(True, True)

        # Theme Palette
        self.bg_main = "#0b0f19"
        self.bg_panel = "#111827"
        self.bg_input = "#1e293b"
        self.fg_text = "#f8fafc"
        self.fg_muted = "#94a3b8"
        self.accent_cyan = "#00f0ff"
        self.accent_blue = "#0284c7"
        self.accent_green = "#10b981"
        self.accent_red = "#e11d48"
        self.accent_warn = "#f43f5e"

        self.configure(bg=self.bg_main)
        self.is_running = False
        self.stop_event = threading.Event()

        # StringVars for file paths
        self.initial_zip_var = tk.StringVar()
        self.custom_rom_zip_var = tk.StringVar()
        self.update_rom_zip_var = tk.StringVar()
        self.stock_dir_var = tk.StringVar()
        self.root_img_var = tk.StringVar()
        self.root_part_var = tk.StringVar(value="boot")
        self.device_status_var = tk.StringVar(value="Device: Click 'Check Device'")
        self.tools_status_var = tk.StringVar(value="Tools: Checking...")
        self.status_bar_var = tk.StringVar(value="Ready | Strict Device Support: Motorola Moto G54 5G / G64 5G (cancunf)")

        self._setup_styles()
        self._build_ui()
        self.refresh_environment_status()

    def _setup_styles(self):
        style = ttk.Style(self)
        # 'clam' supports full custom background/foreground styling across Windows, Linux, and macOS
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background=self.bg_main)
        style.configure("Card.TFrame", background=self.bg_panel)
        style.configure("TLabel", background=self.bg_panel, foreground=self.fg_text, font=("Segoe UI", 10))
        style.configure("Main.TLabel", background=self.bg_main, foreground=self.fg_text, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=self.bg_main, foreground=self.accent_cyan, font=("Consolas", 16, "bold"))

        # Notebook (Tabs)
        style.configure("TNotebook", background=self.bg_main, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#1e293b",
            foreground=self.fg_muted,
            padding=[14, 8],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.accent_blue), ("active", "#334155")],
            foreground=[("selected", "#ffffff"), ("active", "#ffffff")]
        )

        # Primary Action Buttons
        style.configure(
            "Primary.TButton",
            background=self.accent_blue,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=[12, 7],
            borderwidth=0
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#0ea5e9"), ("disabled", "#334155")],
            foreground=[("disabled", "#64748b")]
        )

        # Success / Green Buttons
        style.configure(
            "Success.TButton",
            background=self.accent_green,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=[12, 7],
            borderwidth=0
        )
        style.map(
            "Success.TButton",
            background=[("active", "#059669"), ("disabled", "#334155")],
            foreground=[("disabled", "#64748b")]
        )

        # Danger / Red Buttons
        style.configure(
            "Danger.TButton",
            background=self.accent_red,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=[12, 7],
            borderwidth=0
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#be123c"), ("disabled", "#334155")],
            foreground=[("disabled", "#64748b")]
        )

        # Secondary / Browse Buttons
        style.configure(
            "Secondary.TButton",
            background="#334155",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            padding=[10, 5],
            borderwidth=0
        )
        style.map("Secondary.TButton", background=[("active", "#475569")])

        # Radiobuttons
        style.configure(
            "TRadiobutton",
            background=self.bg_panel,
            foreground=self.fg_text,
            font=("Segoe UI", 10),
            indicatorcolor=self.accent_cyan
        )
        style.map("TRadiobutton", background=[("active", self.bg_panel)])

        # Progressbar
        style.configure(
            "Cyan.Horizontal.TProgressbar",
            troughcolor="#1e293b",
            background=self.accent_cyan,
            bordercolor=self.bg_main,
            lightcolor=self.accent_cyan,
            darkcolor=self.accent_blue
        )

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # 1. Top Header & Device Status Bar
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        top_frame.grid_columnconfigure(0, weight=1)

        title_lbl = ttk.Label(top_frame, text="MOTO G54 / G64 5G (CANCUNF) TOOLKIT", style="Header.TLabel")
        title_lbl.grid(row=0, column=0, sticky="w")

        status_box = ttk.Frame(top_frame)
        status_box.grid(row=0, column=1, sticky="e")

        self.tools_badge = tk.Label(
            status_box, textvariable=self.tools_status_var,
            bg="#1e293b", fg="#38bdf8", font=("Consolas", 9, "bold"), padx=8, pady=4
        )
        self.tools_badge.pack(side=tk.LEFT, padx=4)

        self.device_badge = tk.Label(
            status_box, textvariable=self.device_status_var,
            bg="#1e293b", fg="#facc15", font=("Consolas", 9, "bold"), padx=8, pady=4
        )
        self.device_badge.pack(side=tk.LEFT, padx=4)

        check_btn = ttk.Button(status_box, text="Check Device", style="Secondary.TButton", command=self.check_device_status)
        check_btn.pack(side=tk.LEFT, padx=(4, 0))

        # 2. Safety Warning Banner
        warn_lbl = tk.Label(
            self,
            text="⚠️ WARNING: Strictly for Motorola Moto G54 5G / G64 5G (cancunf) ONLY! Ensure Bootloader is unlocked.\n"
                 "You are solely responsible for any bricked devices or data loss. Proceed at your own risk!",
            bg="#2a1215", fg="#fda4af", font=("Segoe UI", 9, "bold"), pady=6, padx=10
        )
        warn_lbl.grid(row=1, column=0, sticky="ew", padx=16, pady=4)

        # 3. Tabbed Operations Control Panel
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=2, column=0, sticky="ew", padx=16, pady=6)

        self.action_buttons = []
        self._build_tab_custom_rom()
        self._build_tab_dirty_update()
        self._build_tab_stock_rom()
        self._build_tab_root()
        self._build_tab_platform_tools()

        # 4. Live Terminal Output Console & Controls
        console_container = ttk.Frame(self)
        console_container.grid(row=3, column=0, sticky="nsew", padx=16, pady=(4, 8))
        console_container.grid_columnconfigure(0, weight=1)
        console_container.grid_rowconfigure(1, weight=1)

        log_header = ttk.Frame(console_container)
        log_header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        log_header.grid_columnconfigure(0, weight=1)

        ttk.Label(
            log_header, text="LIVE FLASHING & ADB/FASTBOOT CONSOLE:",
            style="Main.TLabel", foreground=self.accent_green, font=("Consolas", 10, "bold")
        ).grid(row=0, column=0, sticky="w")

        self.progress = ttk.Progressbar(log_header, style="Cyan.Horizontal.TProgressbar", mode="determinate", length=180)
        self.progress.grid(row=0, column=1, padx=10)

        self.stop_btn = ttk.Button(
            log_header, text="Stop / Abort Task", style="Danger.TButton",
            command=self.abort_current_task, state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=2, padx=4)

        clear_btn = ttk.Button(log_header, text="Clear Log", style="Secondary.TButton", command=self.clear_log)
        clear_btn.grid(row=0, column=3, padx=(4, 0))

        self.log_box = scrolledtext.ScrolledText(
            console_container,
            bg="#050811",
            fg="#38bdf8",
            insertbackground="white",
            font=("Consolas", 9),
            relief=tk.FLAT,
             bd=2,
            state=tk.DISABLED
        )
        self.log_box.grid(row=1, column=0, sticky="nsew")

        # Configure color tags inside log console
        self.log_box.tag_config("info", foreground="#38bdf8")
        self.log_box.tag_config("success", foreground="#10b981")
        self.log_box.tag_config("warn", foreground="#facc15")
        self.log_box.tag_config("error", foreground="#f43f5e")
        self.log_box.tag_config("cmd", foreground="#c084fc")

        # 5. Bottom Status Bar
        status_bar = tk.Label(
            self, textvariable=self.status_bar_var,
            bg="#1e293b", fg="#cbd5e1", font=("Segoe UI", 9), anchor="w", padx=10, pady=4
        )
        status_bar.grid(row=4, column=0, sticky="ew")

        self.append_log("[i] Moto G54 / G64 5G (cancunf) Toolkit initialized.")
        self.append_log("[i] Select a tab above, choose your files, and click Start.")

    def _create_file_selector(self, parent, row, label_text, var, browse_cmd):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=12, pady=6)
        entry = tk.Entry(
            parent, textvariable=var, bg=self.bg_input, fg="#ffffff",
            insertbackground="white", relief=tk.FLAT, font=("Consolas", 9)
        )
        entry.grid(row=row, column=1, sticky="ew", padx=8, pady=6, ipady=4)
        btn = ttk.Button(parent, text="Browse...", style="Secondary.TButton", command=browse_cmd)
        btn.grid(row=row, column=2, padx=12, pady=6)

    def _build_tab_custom_rom(self):
        tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=10)
        tab.grid_columnconfigure(1, weight=1)
        self.notebook.add(tab, text="1. Clean Flash Custom ROM")

        ttk.Label(
            tab,
            text="Follows official cancunf guide: Reboot FastbootD -> Verify userspace -> Flash initial_install.zip -> Recovery Wipe -> Sideload ROM",
            foreground=self.fg_muted
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(2, 8))

        self._create_file_selector(
            tab, 1, "Initial Install Zip:", self.initial_zip_var,
            lambda: self._browse_file(self.initial_zip_var, "Select Initial Install Zip", [("Zip Files", "*.zip")])
        )
        self._create_file_selector(
            tab, 2, "Custom ROM Zip:", self.custom_rom_zip_var,
            lambda: self._browse_file(self.custom_rom_zip_var, "Select Custom ROM Zip", [("Zip Files", "*.zip")])
        )

        btn = ttk.Button(tab, text="Start Custom ROM Clean Flash", style="Primary.TButton", command=self.start_custom_flash)
        btn.grid(row=3, column=0, columnspan=3, pady=(10, 4))
        self.action_buttons.append(btn)

    def _build_tab_dirty_update(self):
        tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=10)
        tab.grid_columnconfigure(1, weight=1)
        self.notebook.add(tab, text="2. Update ROM (Sideload)")

        ttk.Label(
            tab,
            text="Dirty flash a newer build of your current Custom ROM via Recovery ADB Sideload (No Data Wipe).",
            foreground=self.fg_muted
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(2, 8))

        self._create_file_selector(
            tab, 1, "New ROM Update Zip:", self.update_rom_zip_var,
            lambda: self._browse_file(self.update_rom_zip_var, "Select New Custom ROM Zip", [("Zip Files", "*.zip")])
        )

        btn = ttk.Button(tab, text="Start ROM Update Sideload", style="Primary.TButton", command=self.start_dirty_flash)
        btn.grid(row=2, column=0, columnspan=3, pady=(14, 4))
        self.action_buttons.append(btn)

    def _build_tab_stock_rom(self):
        tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=10)
        tab.grid_columnconfigure(1, weight=1)
        self.notebook.add(tab, text="3. Stock ROM Clean Flash")

        ttk.Label(
            tab,
            text="Flashes BOTH Slot A & Slot B partitions, dynamically flashes all super.img_sparsechunk.* files, and wipes userdata.",
            foreground=self.fg_muted
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(2, 8))

        self._create_file_selector(
            tab, 1, "Extracted Stock Folder:", self.stock_dir_var,
            lambda: self._browse_folder(self.stock_dir_var, "Select Extracted Motorola Stock Firmware Folder")
        )

        btn = ttk.Button(tab, text="Start Full Clean Stock Flash (Slot A & B)", style="Danger.TButton", command=self.start_stock_flash)
        btn.grid(row=2, column=0, columnspan=3, pady=(14, 4))
        self.action_buttons.append(btn)

    def _build_tab_root(self):
        tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=10)
        tab.grid_columnconfigure(1, weight=1)
        self.notebook.add(tab, text="4. Root Phone")

        ttk.Label(
            tab,
            text="Flash a Magisk, KernelSU, or APatch patched image in Bootloader mode.",
            foreground=self.fg_muted
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(2, 8))

        self._create_file_selector(
            tab, 1, "Patched Image (.img):", self.root_img_var,
            lambda: self._browse_file(self.root_img_var, "Select Patched .img File", [("Image Files", "*.img"), ("All Files", "*.*")])
        )

        radio_frame = ttk.Frame(tab, style="Card.TFrame")
        radio_frame.grid(row=2, column=0, columnspan=3, sticky="w", padx=12, pady=4)
        ttk.Label(radio_frame, text="Target Partition:").pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(radio_frame, text="boot (Standard Magisk / KernelSU)", variable=self.root_part_var, value="boot").pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(radio_frame, text="init_boot", variable=self.root_part_var, value="init_boot").pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(radio_frame, text="vendor_boot", variable=self.root_part_var, value="vendor_boot").pack(side=tk.LEFT, padx=8)

        btn = ttk.Button(tab, text="Flash Patched Root Image", style="Primary.TButton", command=self.start_root_flash)
        btn.grid(row=3, column=0, columnspan=3, pady=(10, 4))
        self.action_buttons.append(btn)

    def _build_tab_platform_tools(self):
        tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=10)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        self.notebook.add(tab, text="5. Setup ADB & Fastboot")

        ttk.Label(
            tab,
            text="Install or update Android SDK Platform Tools (ADB & Fastboot) on your system:",
            foreground=self.fg_muted
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 12))

        btn_portable = ttk.Button(
            tab,
            text="⚡ Auto-Download Official Google Platform Tools (Recommended / No Admin Needed)",
            style="Success.TButton",
            command=self.download_portable_platform_tools
        )
        btn_portable.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=6)
        self.action_buttons.append(btn_portable)

        btn_os_script = ttk.Button(
            tab,
            text="🖥️ Run System Package Manager Script (Winget / APT / Pacman / DNF / Brew)",
            style="Secondary.TButton",
            command=self.run_external_os_installer
        )
        btn_os_script.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=6)
        self.action_buttons.append(btn_os_script)

    def _browse_file(self, target_var, title, filetypes):
        path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if path:
            target_var.set(path)

    def _browse_folder(self, target_var, title):
        path = filedialog.askdirectory(title=title)
        if path:
            target_var.set(path)

    def append_log(self, message):
        def _write():
            self.log_box.config(state=tk.NORMAL)
            tag = "info"
            if "[✓]" in message or "COMPLETED" in message or "Success" in message:
                tag = "success"
            elif "[!]" in message or "Warning" in message or "ACTION REQUIRED" in message:
                tag = "warn"
            elif "[✗]" in message or "[ERROR]" in message or "Failed" in message:
                tag = "error"
            elif "--> Executing:" in message:
                tag = "cmd"

            self.log_box.insert(tk.END, message + "\n", tag)
            self.log_box.see(tk.END)
            self.log_box.config(state=tk.DISABLED)

        self.after(0, _write)

    def clear_log(self):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state=tk.DISABLED)
        self.append_log("[i] Console log cleared.")

    def set_status(self, text):
        self.after(0, lambda: self.status_bar_var.set(f"Status: {text}"))

    def set_busy(self, busy):
        self.is_running = busy
        state = tk.DISABLED if busy else tk.NORMAL
        for btn in self.action_buttons:
            btn.config(state=state)
        self.stop_btn.config(state=tk.NORMAL if busy else tk.DISABLED)
        if busy:
            self.progress.config(mode="indeterminate")
            self.progress.start(12)
        else:
            self.progress.stop()
            self.progress.config(mode="determinate", value=0)

    def refresh_environment_status(self):
        adb_bin = get_adb_bin()
        fb_bin = get_fastboot_bin()
        has_adb = shutil.which(adb_bin) or os.path.isfile(adb_bin)
        has_fb = shutil.which(fb_bin) or os.path.isfile(fb_bin)

        if has_adb and has_fb:
            self.tools_status_var.set("Tools: ADB & Fastboot Ready ✓")
            self.tools_badge.config(fg="#10b981")
        else:
            self.tools_status_var.set("Tools: Not Installed (Open Tab 5)")
            self.tools_badge.config(fg="#f43f5e")

    def check_device_status(self):
        def _check():
            self.refresh_environment_status()
            adb_bin = get_adb_bin()
            fb_bin = get_fastboot_bin()
            kwargs = {"capture_output": True, "text": True}
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            # Check Fastboot first
            try:
                res_fb = subprocess.run([fb_bin, "devices"], timeout=4, **kwargs)
                fb_out = res_fb.stdout.strip()
                if fb_out:
                    serial = fb_out.split()[0]
                    # Check if userspace fastbootd
                    res_us = subprocess.run([fb_bin, "getvar", "is-userspace"], timeout=4, **kwargs)
                    us_out = (res_us.stdout + res_us.stderr).lower()
                    mode = "FastbootD" if "is-userspace: yes" in us_out else "Bootloader"
                    self.after(0, lambda: self.device_status_var.set(f"Device: {serial} ({mode})"))
                    self.after(0, lambda: self.device_badge.config(fg="#10b981"))
                    self.append_log(f"[✓] Device detected in {mode} mode: {fb_out}")
                    return
            except Exception:
                pass

            # Check ADB next
            try:
                res_adb = subprocess.run([adb_bin, "devices"], timeout=4, **kwargs)
                lines = [l.strip() for l in res_adb.stdout.splitlines() if l.strip() and not l.startswith("List of")]
                if lines:
                    serial_info = lines[0]
                    self.after(0, lambda: self.device_status_var.set(f"Device: {serial_info}"))
                    self.after(0, lambda: self.device_badge.config(fg="#10b981"))
                    self.append_log(f"[✓] Device detected via ADB: {serial_info}")
                    return
            except Exception:
                pass

            self.after(0, lambda: self.device_status_var.set("Device: Disconnected"))
            self.after(0, lambda: self.device_badge.config(fg="#f43f5e"))
            self.append_log("[!] No device detected in ADB or Fastboot mode.")

        threading.Thread(target=_check, daemon=True).start()

    def thread_safe_prompt(self, message):
        event = threading.Event()
        result = {"ok": False}

        def _ask():
            result["ok"] = messagebox.askokcancel("Action Required on Phone", message)
            event.set()

        self.after(0, _ask)
        event.wait()
        return result["ok"]

    def abort_current_task(self):
        if self.is_running:
            self.stop_event.set()
            abort_active_process()
            self.append_log("[!] Abort requested by user. Terminating active command...")
            self.set_status("Task Aborted")

    def run_in_background(self, target_fn):
        if self.is_running:
            return
        self.stop_event.clear()
        self.set_busy(True)

        def _worker():
            try:
                target_fn()
            except Exception as e:
                self.append_log(f"[ERROR] {e}")
                self.after(0, lambda err=str(e): messagebox.showerror("Operation Failed", err))
                self.set_status("Operation failed")
            finally:
                self.after(0, lambda: self.set_busy(False))
                self.after(0, self.refresh_environment_status)

        threading.Thread(target=_worker, daemon=True).start()

    # ==========================================================================
    # TASK HANDLERS
    # ==========================================================================

    def start_custom_flash(self):
        initial_zip = self.initial_zip_var.get().strip()
        rom_zip = self.custom_rom_zip_var.get().strip()

        if not os.path.isfile(initial_zip):
            messagebox.showwarning("Missing File", "Please select a valid Initial Install Zip file first.")
            return
        if not os.path.isfile(rom_zip):
            messagebox.showwarning("Missing File", "Please select a valid Custom ROM Zip file first.")
            return

        if not messagebox.askyesno(
            "Confirm Custom ROM Clean Flash",
            "Make sure your Moto G54/G64 is connected in Bootloader Mode (Power + Volume Down).\n\n"
            "All user data will be wiped in Recovery.\nDo you want to start?"
        ):
            return

        def task():
            self.set_status("Running Custom ROM Clean Flash...")
            custom_rom_flash_cancunf_gui(
                initial_zip,
                rom_zip,
                log_fn=self.append_log,
                prompt_fn=self.thread_safe_prompt,
                stop_event=self.stop_event
            )
            self.set_status("Custom ROM Clean Flash Completed!")
            self.after(0, lambda: messagebox.showinfo("Success", "Custom ROM Clean Flash Completed!"))

        self.run_in_background(task)

    def start_dirty_flash(self):
        rom_zip = self.update_rom_zip_var.get().strip()
        if not os.path.isfile(rom_zip):
            messagebox.showwarning("Missing File", "Please select the new Custom ROM Update Zip file first.")
            return

        def task():
            self.set_status("Running Custom ROM Update (ADB Sideload)...")
            dirty_flash_update_cancunf_gui(
                rom_zip,
                log_fn=self.append_log,
                prompt_fn=self.thread_safe_prompt,
                stop_event=self.stop_event
            )
            self.set_status("Custom ROM Update Completed!")
            self.after(0, lambda: messagebox.showinfo("Success", "ROM Update Completed!"))

        self.run_in_background(task)

    def start_stock_flash(self):
        rom_dir = self.stock_dir_var.get().strip()
        if not os.path.isdir(rom_dir):
            messagebox.showwarning("Missing Folder", "Please select the extracted Motorola Stock ROM folder first.")
            return

        if not messagebox.askyesno(
            "WARNING: Full Clean Stock Flash",
            f"Folder: {rom_dir}\n\n"
            "This will flash BOTH Slot A & Slot B and ERASE ALL USERDATA.\n"
            "Ensure your phone is connected in Bootloader Mode.\n\nProceed with Full Clean Flash?"
        ):
            return

        def task():
            self.set_status("Flashing Stock Firmware on Slot A & Slot B...")
            stock_rom_flash_cancunf_gui(rom_dir, log_fn=self.append_log, stop_event=self.stop_event)
            self.set_status("Stock Firmware Flash Completed!")
            self.after(0, lambda: messagebox.showinfo(
                "Success", "Full Clean Stock Flash Completed!\nPress the Power button on your phone to reboot."
            ))

        self.run_in_background(task)

    def start_root_flash(self):
        img_path = self.root_img_var.get().strip()
        partition = self.root_part_var.get().strip()
        if not os.path.isfile(img_path):
            messagebox.showwarning("Missing File", f"Please select your patched {partition}.img file first.")
            return

        if not messagebox.askyesno(
            "Confirm Root Image Flash",
            f"Flash '{os.path.basename(img_path)}' to partition '{partition}'?"
        ):
            return

        def task():
            self.set_status(f"Flashing {partition} partition...")
            root_phone_cancunf_gui(img_path, partition=partition, log_fn=self.append_log, stop_event=self.stop_event)
            self.set_status(f"Flashed {partition} successfully!")
            self.after(0, lambda: messagebox.showinfo("Success", f"Successfully flashed {partition} and triggered reboot!"))

        self.run_in_background(task)

    def download_portable_platform_tools(self):
        """Downloads official Google platform-tools zip directly into the toolkit folder without needing Admin/Sudo."""
        def task():
            sys_os = platform.system().lower()
            if "windows" in sys_os:
                url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
            elif "darwin" in sys_os:
                url = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
            else:
                url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"

            base_dir = os.path.dirname(os.path.abspath(__file__))
            zip_target = os.path.join(base_dir, "platform-tools-temp.zip")
            extract_dir = base_dir

            self.set_status("Downloading Official Google Platform Tools...")
            self.append_log(f"[*] Downloading from: {url}")

            urllib.request.urlretrieve(url, zip_target)
            self.append_log("[*] Extracting platform-tools...")

            pt_folder = get_local_pt_dir()
            if os.path.isdir(pt_folder):
                shutil.rmtree(pt_folder, ignore_errors=True)

            with zipfile.ZipFile(zip_target, "r") as zf:
                zf.extractall(extract_dir)

            if os.path.isfile(zip_target):
                os.remove(zip_target)

            # Set executable permissions on Linux / macOS
            if os.name != "nt":
                for bin_name in ["adb", "fastboot"]:
                    bin_path = os.path.join(pt_folder, bin_name)
                    if os.path.isfile(bin_path):
                        os.chmod(bin_path, 0o755)

            adb_bin = get_adb_bin()
            self.append_log(f"[✓] Portable Platform Tools installed at: {pt_folder}")
            res = subprocess.run([adb_bin, "--version"], capture_output=True, text=True)
            if res.stdout:
                self.append_log(res.stdout.strip())
            self.set_status("Platform Tools Installed & Verified!")
            self.after(0, lambda: messagebox.showinfo("Success", "Official Google Platform Tools downloaded and verified!"))

        self.run_in_background(task)

    def run_external_os_installer(self):
        """Launches the OS-specific installer script in a visible terminal window so sudo/UAC prompts never hang."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys_os = platform.system().lower()

        if "windows" in sys_os:
            bat = os.path.join(script_dir, "windows-adb-install.bat")
            if os.path.isfile(bat):
                self.append_log("[*] Launching windows-adb-install.bat in an external window...")
                subprocess.Popen(["cmd.exe", "/c", "start", "", bat], shell=True)
            else:
                messagebox.showerror("Error", "windows-adb-install.bat not found!")
        elif "darwin" in sys_os:
            mac = os.path.join(script_dir, "mac-adb-install.sh")
            if os.path.isfile(mac):
                os.chmod(mac, 0o755)
                self.append_log("[*] Opening mac-adb-install.sh in macOS Terminal...")
                subprocess.Popen(["open", "-a", "Terminal", mac])
            else:
                messagebox.showerror("Error", "mac-adb-install.sh not found!")
        else:
            sh = os.path.join(script_dir, "linux-adb-install.sh")
            if os.path.isfile(sh):
                os.chmod(sh, 0o755)
                self.append_log("[*] Launching linux-adb-install.sh...")
                for term in ["x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal", "xterm"]:
                    if shutil.which(term):
                        if term == "gnome-terminal":
                            subprocess.Popen([term, "--", "bash", sh])
                        else:
                            subprocess.Popen([term, "-e", f"bash '{sh}'"])
                        return
                messagebox.showinfo(
                    "Run in Terminal",
                    "Please use the green 'Auto-Download Official Google Platform Tools' button above, "
                    "or run './linux-adb-install.sh' from a terminal."
                )
            else:
                messagebox.showerror("Error", "linux-adb-install.sh not found!")


def launch_gui():
    app = CancunfToolkitGUI()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
