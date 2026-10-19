#!/usr/bin/env python3
import os
import re
import sys
import time
import glob
import shutil
import zipfile
import platform
import threading
import subprocess
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

from custom_rom_flash import (
    get_app_dir,
    get_resource_dir,
    get_adb_bin,
    get_fastboot_bin,
    get_local_pt_dir,
    validate_stock_rom_folder,
    custom_rom_flash_cancunf_gui,
    dirty_flash_update_cancunf_gui,
    stock_rom_flash_cancunf_gui,
    root_phone_cancunf_gui,
    abort_active_process
)

# Enable Windows High-DPI awareness for crisp rendering
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


class CancunfToolkitGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MOTO G54 / G64 5G (CANCUNF) — ALL-IN-ONE FLASHING STUDIO")
        self.geometry("1020x740")
        self.minsize(900, 640)
        self.resizable(True, True)

        # Cyberpunk / Neon Dark Theme Palette
        self.bg_root = "#07090e"
        self.bg_sidebar = "#0d111a"
        self.bg_card = "#111726"
        self.bg_card_border = "#1e293b"
        self.bg_input = "#090d16"
        self.fg_primary = "#f8fafc"
        self.fg_secondary = "#94a3b8"
        self.neon_cyan = "#00f0ff"
        self.neon_blue = "#0284c7"
        self.neon_green = "#10b981"
        self.neon_pink = "#f43f5e"
        self.neon_amber = "#f59e0b"
        self.neon_purple = "#a855f7"

        self.configure(bg=self.bg_root)
        self.is_running = False
        self.stop_event = threading.Event()
        self.action_buttons = []
        self.nav_buttons = {}
        self.views = {}

        # State Variables
        self.initial_zip_var = tk.StringVar()
        self.custom_rom_zip_var = tk.StringVar()
        self.update_rom_zip_var = tk.StringVar()
        self.stock_dir_var = tk.StringVar()
        self.root_img_var = tk.StringVar()
        self.root_part_var = tk.StringVar(value="boot")

        self.device_status_var = tk.StringVar(value="● DISCONNECTED")
        self.tools_status_var = tk.StringVar(value="● CHECKING TOOLS...")
        self.progress_label_var = tk.StringVar(value="IDLE")
        self.status_bar_var = tk.StringVar(
            value="Ready  |  Target Device: Motorola Moto G54 5G / G64 5G (cancunf)  |  Mode: GUI Studio"
        )

        # Validation Status Variables
        self.init_zip_status = tk.StringVar(value="No file selected")
        self.rom_zip_status = tk.StringVar(value="No file selected")
        self.upd_zip_status = tk.StringVar(value="No file selected")
        self.stock_dir_status = tk.StringVar(value="No folder selected")
        self.root_img_status = tk.StringVar(value="No image selected")

        # Trace file inputs for instant validation feedback
        self.initial_zip_var.trace_add("write", lambda *_: self._validate_inputs())
        self.custom_rom_zip_var.trace_add("write", lambda *_: self._validate_inputs())
        self.update_rom_zip_var.trace_add("write", lambda *_: self._validate_inputs())
        self.stock_dir_var.trace_add("write", lambda *_: self._validate_inputs())
        self.root_img_var.trace_add("write", lambda *_: self._validate_inputs())

        self._setup_styles()
        self._build_layout()
        self.switch_view("custom_rom")
        self.refresh_environment_status()

    def _setup_styles(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background=self.bg_root)
        style.configure("Card.TFrame", background=self.bg_card)

        # Primary Neon Cyan/Blue Button
        style.configure(
            "Primary.TButton",
            background=self.neon_blue,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=[16, 9],
            borderwidth=0
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#0ea5e9"), ("disabled", "#1e293b")],
            foreground=[("disabled", "#475569")]
        )

        # Success Neon Green Button
        style.configure(
            "Success.TButton",
            background=self.neon_green,
            foreground="#050811",
            font=("Segoe UI", 10, "bold"),
            padding=[16, 9],
            borderwidth=0
        )
        style.map(
            "Success.TButton",
            background=[("active", "#34d399"), ("disabled", "#1e293b")],
            foreground=[("disabled", "#475569")]
        )

        # Danger Neon Pink/Red Button
        style.configure(
            "Danger.TButton",
            background=self.neon_pink,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=[16, 9],
            borderwidth=0
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#fb7185"), ("disabled", "#1e293b")],
            foreground=[("disabled", "#475569")]
        )

        # Subtle Secondary Button
        style.configure(
            "Secondary.TButton",
            background="#1e293b",
            foreground="#e2e8f0",
            font=("Segoe UI", 9, "bold"),
            padding=[10, 5],
            borderwidth=0
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#334155"), ("disabled", "#0f172a")],
            foreground=[("disabled", "#475569")]
        )

        # Radiobuttons
        style.configure(
            "Card.TRadiobutton",
            background=self.bg_card,
            foreground=self.fg_primary,
            font=("Segoe UI", 10, "bold"),
            indicatorcolor=self.neon_cyan
        )
        style.map("Card.TRadiobutton", background=[("active", self.bg_card)])

        # Progressbar
        style.configure(
            "Neon.Horizontal.TProgressbar",
            troughcolor="#090d16",
            background=self.neon_cyan,
            bordercolor=self.bg_card_border,
            lightcolor=self.neon_cyan,
            darkcolor=self.neon_blue
        )

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ======================================================================
        # 1. TOP HEADER BAR & QUICK REBOOT CONTROLS
        # ======================================================================
        header_bar = tk.Frame(self, bg=self.bg_sidebar, bd=0, highlightthickness=1, highlightbackground=self.bg_card_border)
        header_bar.grid(row=0, column=0, sticky="ew")
        header_bar.grid_columnconfigure(1, weight=1)

        # Brand Title
        brand_frame = tk.Frame(header_bar, bg=self.bg_sidebar)
        brand_frame.grid(row=0, column=0, sticky="w", padx=16, pady=10)

        tk.Label(
            brand_frame, text="⚡ CANCUNF",
            bg=self.bg_sidebar, fg=self.neon_cyan, font=("Consolas", 16, "bold")
        ).pack(side=tk.LEFT)
        tk.Label(
            brand_frame, text=" STUDIO",
            bg=self.bg_sidebar, fg="#ffffff", font=("Consolas", 16, "bold")
        ).pack(side=tk.LEFT)
        tk.Label(
            brand_frame, text="  Moto G54 / G64 5G",
            bg=self.bg_sidebar, fg=self.fg_secondary, font=("Segoe UI", 9, "bold")
        ).pack(side=tk.LEFT, padx=(6, 0))

        # Status Badges (Center-Right)
        badge_frame = tk.Frame(header_bar, bg=self.bg_sidebar)
        badge_frame.grid(row=0, column=1, sticky="e", padx=8)

        self.tools_badge = tk.Label(
            badge_frame, textvariable=self.tools_status_var,
            bg="#131b2e", fg=self.neon_cyan, font=("Consolas", 9, "bold"), padx=10, pady=4
        )
        self.tools_badge.pack(side=tk.LEFT, padx=4)

        self.device_badge = tk.Label(
            badge_frame, textvariable=self.device_status_var,
            bg="#131b2e", fg=self.neon_amber, font=("Consolas", 9, "bold"), padx=10, pady=4
        )
        self.device_badge.pack(side=tk.LEFT, padx=4)

        # Quick Device Action Buttons
        quick_frame = tk.Frame(header_bar, bg=self.bg_sidebar)
        quick_frame.grid(row=0, column=2, sticky="e", padx=(4, 14), pady=8)

        ttk.Button(quick_frame, text="🔄 Check Device", style="Secondary.TButton", command=self.check_device_status).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="Reboot BL", style="Secondary.TButton", command=lambda: self.quick_reboot("bootloader")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="FastbootD", style="Secondary.TButton", command=lambda: self.quick_reboot("fastboot")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="Recovery", style="Secondary.TButton", command=lambda: self.quick_reboot("recovery")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="System", style="Secondary.TButton", command=lambda: self.quick_reboot("system")).pack(side=tk.LEFT, padx=2)

        # ======================================================================
        # 2. SAFETY DISCLAIMER STRIP
        # ======================================================================
        warn_strip = tk.Frame(self, bg="#1f0d16", highlightthickness=1, highlightbackground="#4c1d2e")
        warn_strip.grid(row=1, column=0, sticky="ew")
        tk.Label(
            warn_strip,
            text="⚠️ STRICTLY FOR MOTOROLA MOTO G54 5G & G64 5G (CANCUNF)  •  UNLOCKED BOOTLOADER REQUIRED  •  USE AT YOUR OWN RISK (NO LIABILITY FOR BRICKED DEVICES)",
            bg="#1f0d16", fg="#fda4af", font=("Segoe UI", 8, "bold"), pady=4
        ).pack()

        # ======================================================================
        # 3. MAIN SPLIT WORKSPACE (TOP: SIDEBAR + CARDS, BOTTOM: LIVE CONSOLE)
        # ======================================================================
        self.paned = tk.PanedWindow(self, orient=tk.VERTICAL, bg=self.bg_card_border, sashwidth=4, bd=0)
        self.paned.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)

        # Upper Area: Sidebar + Dynamic Page Container
        upper_area = tk.Frame(self.paned, bg=self.bg_root)
        upper_area.grid_columnconfigure(1, weight=1)
        upper_area.grid_rowconfigure(0, weight=1)
        self.paned.add(upper_area, minsize=310)

        # Left Sidebar
        sidebar = tk.Frame(upper_area, bg=self.bg_sidebar, width=235, highlightthickness=1, highlightbackground=self.bg_card_border)
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        sidebar.grid_propagate(False)

        tk.Label(
            sidebar, text="OPERATIONS MENU",
            bg=self.bg_sidebar, fg=self.fg_secondary, font=("Consolas", 9, "bold"), anchor="w"
        ).pack(fill=tk.X, padx=16, pady=(14, 6))

        self._add_nav_item(sidebar, "custom_rom", "🚀  Clean Flash Custom ROM")
        self._add_nav_item(sidebar, "dirty_rom", "📦  Update ROM (Sideload)")
        self._add_nav_item(sidebar, "stock_rom", "🛠️  Restore Stock Firmware")
        self._add_nav_item(sidebar, "root_phone", "🔓  Root Phone (Boot/Init)")
        self._add_nav_item(sidebar, "platform_tools", "⚙️  Setup ADB & Fastboot")

        # Credits box at bottom of sidebar
        credit_box = tk.Frame(sidebar, bg="#090d16", highlightthickness=1, highlightbackground=self.bg_card_border)
        credit_box.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        tk.Label(
            credit_box,
            text="Guide: CyberKnight777\nOTG: nohajc/termux-adb\nDev: Aman (neonheart711)",
            bg="#090d16", fg=self.fg_secondary, font=("Consolas", 8), justify=tk.LEFT, pady=6, padx=8
        ).pack(anchor="w")

        # Right Page Container
        self.page_container = tk.Frame(upper_area, bg=self.bg_card, highlightthickness=1, highlightbackground=self.bg_card_border)
        self.page_container.grid(row=0, column=1, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self._build_view_custom_rom()
        self._build_view_dirty_rom()
        self._build_view_stock_rom()
        self._build_view_root()
        self._build_view_platform_tools()

        # Lower Area: Live Terminal Console Dock
        console_dock = tk.Frame(self.paned, bg=self.bg_card, highlightthickness=1, highlightbackground=self.bg_card_border)
        console_dock.grid_columnconfigure(0, weight=1)
        console_dock.grid_rowconfigure(1, weight=1)
        self.paned.add(console_dock, minsize=200)

        # Console Toolbar
        c_bar = tk.Frame(console_dock, bg=self.bg_sidebar)
        c_bar.grid(row=0, column=0, sticky="ew")
        c_bar.grid_columnconfigure(0, weight=1)

        tk.Label(
            c_bar, text=" >_ LIVE TERMINAL TELEMETRY",
            bg=self.bg_sidebar, fg=self.neon_green, font=("Consolas", 10, "bold"), pady=6, padx=10
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            c_bar, textvariable=self.progress_label_var,
            bg=self.bg_sidebar, fg=self.neon_cyan, font=("Consolas", 9, "bold")
        ).grid(row=0, column=1, padx=8)

        self.progress = ttk.Progressbar(c_bar, style="Neon.Horizontal.TProgressbar", mode="determinate", length=170, maximum=100)
        self.progress.grid(row=0, column=2, padx=6)

        self.stop_btn = ttk.Button(
            c_bar, text="⏹ Abort Task", style="Danger.TButton",
            command=self.abort_current_task, state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=3, padx=4, pady=3)

        ttk.Button(c_bar, text="📋 Copy", style="Secondary.TButton", command=self.copy_log).grid(row=0, column=4, padx=2)
        ttk.Button(c_bar, text="💾 Save", style="Secondary.TButton", command=self.save_log).grid(row=0, column=5, padx=2)
        ttk.Button(c_bar, text="🧹 Clear", style="Secondary.TButton", command=self.clear_log).grid(row=0, column=6, padx=(2, 8))

        # Console Output Text Widget
        self.log_box = scrolledtext.ScrolledText(
            console_dock,
            bg="#04070d",
            fg="#38bdf8",
            insertbackground="white",
            font=("Consolas", 9),
            relief=tk.FLAT,
            bd=6,
            state=tk.DISABLED
        )
        self.log_box.grid(row=1, column=0, sticky="nsew")

        self.log_box.tag_config("time", foreground="#64748b")
        self.log_box.tag_config("info", foreground="#38bdf8")
        self.log_box.tag_config("success", foreground="#10b981", font=("Consolas", 9, "bold"))
        self.log_box.tag_config("warn", foreground="#facc15")
        self.log_box.tag_config("error", foreground="#f43f5e", font=("Consolas", 9, "bold"))
        self.log_box.tag_config("cmd", foreground="#c084fc")

        # ======================================================================
        # 4. BOTTOM STATUS BAR
        # ======================================================================
        footer = tk.Label(
            self, textvariable=self.status_bar_var,
            bg=self.bg_sidebar, fg=self.fg_secondary, font=("Segoe UI", 9), anchor="w", padx=14, pady=4
        )
        footer.grid(row=3, column=0, sticky="ew")

        self.append_log("[i] Welcome to CANCUNF Studio! Select an operation from the left sidebar.")
        self.append_log("[i] Tip: Drag the divider above the terminal console to resize the log area.")

    # ==========================================================================
    # NAVIGATION & REUSABLE UI BUILDERS
    # ==========================================================================

    def _add_nav_item(self, parent, key, text):
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_sidebar,
            fg=self.fg_secondary,
            activebackground="#162032",
            activeforeground="#ffffff",
            bd=0,
            anchor="w",
            padx=16,
            pady=10,
            cursor="hand2",
            command=lambda k=key: self.switch_view(k)
        )
        btn.pack(fill=tk.X, padx=8, pady=2)
        self.nav_buttons[key] = btn

    def switch_view(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.config(bg="#162238", fg=self.neon_cyan)
            else:
                btn.config(bg=self.bg_sidebar, fg=self.fg_secondary)

        for k, frame in self.views.items():
            if k == key:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_remove()

    def _create_page_header(self, parent, title, subtitle):
        hdr = tk.Frame(parent, bg=self.bg_card)
        hdr.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(16, 8))
        tk.Label(hdr, text=title, bg=self.bg_card, fg="#ffffff", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill=tk.X)
        tk.Label(hdr, text=subtitle, bg=self.bg_card, fg=self.fg_secondary, font=("Segoe UI", 9), anchor="w").pack(fill=tk.X, pady=(2, 0))

    def _create_file_row(self, parent, row, label_text, path_var, status_var, browse_cmd):
        container = tk.Frame(parent, bg="#0b101d", highlightthickness=1, highlightbackground=self.bg_card_border, padx=12, pady=8)
        container.grid(row=row, column=0, columnspan=3, sticky="ew", padx=20, pady=5)
        container.grid_columnconfigure(1, weight=1)

        tk.Label(container, text=label_text, bg="#0b101d", fg=self.fg_primary, font=("Segoe UI", 9, "bold"), width=20, anchor="w").grid(row=0, column=0, sticky="w")

        entry = tk.Entry(
            container, textvariable=path_var, bg=self.bg_input, fg=self.neon_cyan,
            insertbackground="white", relief=tk.FLAT, font=("Consolas", 9)
        )
        entry.grid(row=0, column=1, sticky="ew", padx=8, ipady=5)

        ttk.Button(container, text="Browse...", style="Secondary.TButton", command=browse_cmd).grid(row=0, column=2)

        status_lbl = tk.Label(container, textvariable=status_var, bg="#0b101d", fg=self.fg_secondary, font=("Consolas", 8), anchor="w")
        status_lbl.grid(row=1, column=1, columnspan=2, sticky="w", padx=8, pady=(3, 0))

    # ==========================================================================
    # INDIVIDUAL VIEWS
    # ==========================================================================

    def _build_view_custom_rom(self):
        view = tk.Frame(self.page_container, bg=self.bg_card)
        view.grid_columnconfigure(0, weight=1)
        self.views["custom_rom"] = view

        self._create_page_header(
            view,
            "🚀 Clean Flash Custom ROM (FastbootD + ADB Sideload)",
            "Workflow: Bootloader ➔ FastbootD (verifies is-userspace: yes) ➔ Flash initial_install.zip ➔ Recovery Wipe Data ➔ ADB Sideload ROM"
        )

        self._create_file_row(
            view, 1, "1. Initial Install Zip:", self.initial_zip_var, self.init_zip_status,
            lambda: self._browse_file(self.initial_zip_var, "Select Initial Install Zip", [("Zip Files", "*.zip")])
        )
        self._create_file_row(
            view, 2, "2. Custom ROM Zip:", self.custom_rom_zip_var, self.rom_zip_status,
            lambda: self._browse_file(self.custom_rom_zip_var, "Select Custom ROM Zip", [("Zip Files", "*.zip")])
        )

        act_frame = tk.Frame(view, bg=self.bg_card)
        act_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=12)

        btn = ttk.Button(act_frame, text="⚡ Start Custom ROM Clean Flash", style="Primary.TButton", command=self.start_custom_flash)
        btn.pack(side=tk.LEFT)
        self.action_buttons.append(btn)

        tk.Label(
            act_frame,
            text="  *Stopping at 47% with 'Total xfer: 1.00x' during ADB Sideload is completely normal.",
            bg=self.bg_card, fg=self.fg_secondary, font=("Segoe UI", 9, "italic")
        ).pack(side=tk.LEFT, padx=10)

    def _build_view_dirty_rom(self):
        view = tk.Frame(self.page_container, bg=self.bg_card)
        view.grid_columnconfigure(0, weight=1)
        self.views["dirty_rom"] = view

        self._create_page_header(
            view,
            "📦 Update Custom ROM Build (Dirty Flash / Sideload)",
            "Sideload a newer build of your existing Custom ROM in Recovery without wiping data (Also used for 2nd slot flash on pre-May 2024 firmware)."
        )

        self._create_file_row(
            view, 1, "Custom ROM Zip:", self.update_rom_zip_var, self.upd_zip_status,
            lambda: self._browse_file(self.update_rom_zip_var, "Select Custom ROM Update Zip", [("Zip Files", "*.zip")])
        )

        act_frame = tk.Frame(view, bg=self.bg_card)
        act_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=14)

        btn = ttk.Button(act_frame, text="📦 Start ADB Sideload Update", style="Primary.TButton", command=self.start_dirty_flash)
        btn.pack(side=tk.LEFT)
        self.action_buttons.append(btn)

    def _build_view_stock_rom(self):
        view = tk.Frame(self.page_container, bg=self.bg_card)
        view.grid_columnconfigure(0, weight=1)
        self.views["stock_rom"] = view

        self._create_page_header(
            view,
            "🛠️ Full Clean Flash Stock Firmware (Both Slot A & Slot B)",
            "Pre-verifies all 21 mandatory partition images + dynamically sorts and flashes all super.img_sparsechunk.* files (Android 13/14/15+)."
        )

        self._create_file_row(
            view, 1, "Stock ROM Folder:", self.stock_dir_var, self.stock_dir_status,
            lambda: self._browse_folder(self.stock_dir_var, "Select Extracted Motorola Stock Firmware Folder")
        )

        act_frame = tk.Frame(view, bg=self.bg_card)
        act_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=14)

        btn = ttk.Button(act_frame, text="🔥 Start Full Clean Stock Flash (Wipes Data)", style="Danger.TButton", command=self.start_stock_flash)
        btn.pack(side=tk.LEFT)
        self.action_buttons.append(btn)

    def _build_view_root(self):
        view = tk.Frame(self.page_container, bg=self.bg_card)
        view.grid_columnconfigure(0, weight=1)
        self.views["root_phone"] = view

        self._create_page_header(
            view,
            "🔓 Root Moto G54 / G64 5G (Flash Patched Image)",
            "Flash a Magisk, KernelSU, or APatch patched boot.img, init_boot.img, or vendor_boot.img via Fastboot."
        )

        self._create_file_row(
            view, 1, "Patched Image (.img):", self.root_img_var, self.root_img_status,
            lambda: self._browse_file(self.root_img_var, "Select Patched .img File", [("Image Files", "*.img"), ("All Files", "*.*")])
        )

        part_box = tk.Frame(view, bg=self.bg_card)
        part_box.grid(row=2, column=0, sticky="ew", padx=20, pady=6)
        tk.Label(part_box, text="Target Partition:", bg=self.bg_card, fg=self.fg_primary, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(part_box, text="boot (Standard Magisk / KernelSU)", style="Card.TRadiobutton", variable=self.root_part_var, value="boot").pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(part_box, text="init_boot", style="Card.TRadiobutton", variable=self.root_part_var, value="init_boot").pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(part_box, text="vendor_boot", style="Card.TRadiobutton", variable=self.root_part_var, value="vendor_boot").pack(side=tk.LEFT, padx=8)

        act_frame = tk.Frame(view, bg=self.bg_card)
        act_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=12)

        btn = ttk.Button(act_frame, text="🔓 Flash Patched Root Image", style="Primary.TButton", command=self.start_root_flash)
        btn.pack(side=tk.LEFT)
        self.action_buttons.append(btn)

    def _build_view_platform_tools(self):
        view = tk.Frame(self.page_container, bg=self.bg_card)
        view.grid_columnconfigure(0, weight=1)
        self.views["platform_tools"] = view

        self._create_page_header(
            view,
            "⚙️ Setup & Verify Android SDK Platform Tools",
            "Automatically configure ADB & Fastboot on Windows, Linux, or macOS without manual PATH headaches."
        )

        card1 = tk.Frame(view, bg="#0b101d", highlightthickness=1, highlightbackground=self.bg_card_border, padx=16, pady=12)
        card1.grid(row=1, column=0, sticky="ew", padx=20, pady=6)
        tk.Label(card1, text="Option 1: Portable Official Google Platform Tools (Recommended)", bg="#0b101d", fg=self.neon_green, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(card1, text="Downloads the latest official platform-tools zip directly from Google into this toolkit folder. No Admin/root password needed.", bg="#0b101d", fg=self.fg_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 8))
        btn1 = ttk.Button(card1, text="⚡ Auto-Download & Configure Portable Platform Tools", style="Success.TButton", command=self.download_portable_platform_tools)
        btn1.pack(anchor="w")
        self.action_buttons.append(btn1)

        card2 = tk.Frame(view, bg="#0b101d", highlightthickness=1, highlightbackground=self.bg_card_border, padx=16, pady=12)
        card2.grid(row=2, column=0, sticky="ew", padx=20, pady=6)
        tk.Label(card2, text="Option 2: System-Wide OS Package Manager Installer", bg="#0b101d", fg=self.neon_cyan, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(card2, text="Launches the dedicated OS installer script (Winget/Choco on Windows, APT/Pacman/DNF on Linux, Homebrew on macOS).", bg="#0b101d", fg=self.fg_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 8))
        btn2 = ttk.Button(card2, text="🖥️ Run OS Package Manager Installer Script", style="Secondary.TButton", command=self.run_external_os_installer)
        btn2.pack(anchor="w")
        self.action_buttons.append(btn2)

    # ==========================================================================
    # VALIDATION, LOGGING & DEVICE HELPERS
    # ==========================================================================

    def _validate_inputs(self):
        # 1. Initial Zip
        p1 = self.initial_zip_var.get().strip()
        if not p1:
            self.init_zip_status.set("No file selected")
        elif os.path.isfile(p1):
            sz = os.path.getsize(p1) / (1024 * 1024)
            self.init_zip_status.set(f"✓ Ready: {os.path.basename(p1)} ({sz:.1f} MB)")
        else:
            self.init_zip_status.set("✗ File not found on disk!")

        # 2. Custom ROM Zip
        p2 = self.custom_rom_zip_var.get().strip()
        if not p2:
            self.rom_zip_status.set("No file selected")
        elif os.path.isfile(p2):
            sz = os.path.getsize(p2) / (1024 * 1024)
            self.rom_zip_status.set(f"✓ Ready: {os.path.basename(p2)} ({sz:.1f} MB)")
        else:
            self.rom_zip_status.set("✗ File not found on disk!")

        # 3. Update ROM Zip
        p3 = self.update_rom_zip_var.get().strip()
        if not p3:
            self.upd_zip_status.set("No file selected")
        elif os.path.isfile(p3):
            sz = os.path.getsize(p3) / (1024 * 1024)
            self.upd_zip_status.set(f"✓ Ready: {os.path.basename(p3)} ({sz:.1f} MB)")
        else:
            self.upd_zip_status.set("✗ File not found on disk!")

        # 4. Stock ROM Folder
        p4 = self.stock_dir_var.get().strip()
        if not p4:
            self.stock_dir_status.set("No folder selected")
        elif os.path.isdir(p4):
            missing, sparse = validate_stock_rom_folder(p4)
            if not missing and sparse:
                self.stock_dir_status.set(f"✓ Verified: All 21 partition images + {len(sparse)} super sparsechunks ready!")
            else:
                self.stock_dir_status.set(f"✗ Incomplete folder: {len(missing)} missing files, {len(sparse)} sparsechunks found")
        else:
            self.stock_dir_status.set("✗ Directory not found!")

        # 5. Root Image
        p5 = self.root_img_var.get().strip()
        if not p5:
            self.root_img_status.set("No image selected")
        elif os.path.isfile(p5):
            sz = os.path.getsize(p5) / (1024 * 1024)
            self.root_img_status.set(f"✓ Ready: {os.path.basename(p5)} ({sz:.1f} MB)")
        else:
            self.root_img_status.set("✗ Image file not found!")

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
            ts = time.strftime("[%H:%M:%S] ")
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

            self.log_box.insert(tk.END, ts, "time")
            self.log_box.insert(tk.END, message + "\n", tag)
            self.log_box.see(tk.END)
            self.log_box.config(state=tk.DISABLED)

            # Parse percentage or chunk progress dynamically
            pct_match = re.search(r"\(~?(\d+)%\)", message)
            chunk_match = re.search(r"\((\d+)/(\d+)\)", message)
            if pct_match:
                pct = int(pct_match.group(1))
                self.progress.stop()
                self.progress.config(mode="determinate", value=pct)
                self.progress_label_var.set(f"{pct}%")
            elif chunk_match:
                cur, tot = int(chunk_match.group(1)), int(chunk_match.group(2))
                pct = int((cur / max(tot, 1)) * 100)
                self.progress.stop()
                self.progress.config(mode="determinate", value=pct)
                self.progress_label_var.set(f"CHUNK {cur}/{tot} ({pct}%)")

        self.after(0, _write)

    def clear_log(self):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state=tk.DISABLED)
        self.append_log("[i] Console log cleared.")

    def copy_log(self):
        content = self.log_box.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(content)
        self.append_log("[✓] Console log copied to clipboard.")

    def save_log(self):
        path = filedialog.asksaveasfilename(
            title="Save Flashing Log",
            defaultextension=".txt",
            initialfile="cancunf_flash_log.txt",
            filetypes=[("Text Files", "*.txt")]
        )
        if path:
            content = self.log_box.get("1.0", tk.END)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.append_log(f"[✓] Log saved to: {path}")

    def set_status(self, text):
        self.after(0, lambda: self.status_bar_var.set(f"Status: {text}"))

    def set_busy(self, busy):
        self.is_running = busy
        state = tk.DISABLED if busy else tk.NORMAL
        for btn in self.action_buttons:
            btn.config(state=state)
        self.stop_btn.config(state=tk.NORMAL if busy else tk.DISABLED)
        if busy:
            self.progress_label_var.set("WORKING...")
            self.progress.config(mode="indeterminate")
            self.progress.start(14)
        else:
            self.progress.stop()
            self.progress.config(mode="determinate", value=0)
            self.progress_label_var.set("IDLE")

    def refresh_environment_status(self):
        adb_bin = get_adb_bin()
        fb_bin = get_fastboot_bin()
        has_adb = shutil.which(adb_bin) or os.path.isfile(adb_bin)
        has_fb = shutil.which(fb_bin) or os.path.isfile(fb_bin)

        if has_adb and has_fb:
            self.tools_status_var.set("● TOOLS READY")
            self.tools_badge.config(fg=self.neon_green)
        else:
            self.tools_status_var.set("● TOOLS MISSING")
            self.tools_badge.config(fg=self.neon_pink)

    def check_device_status(self):
        def _check():
            self.refresh_environment_status()
            adb_bin = get_adb_bin()
            fb_bin = get_fastboot_bin()
            kwargs = {"capture_output": True, "text": True}
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            try:
                res_fb = subprocess.run([fb_bin, "devices"], timeout=4, **kwargs)
                fb_out = res_fb.stdout.strip()
                if fb_out:
                    serial = fb_out.split()[0]
                    res_us = subprocess.run([fb_bin, "getvar", "is-userspace"], timeout=4, **kwargs)
                    us_out = (res_us.stdout + res_us.stderr).lower()
                    mode = "FASTBOOTD" if "is-userspace: yes" in us_out else "BOOTLOADER"
                    self.after(0, lambda: self.device_status_var.set(f"● {serial} ({mode})"))
                    self.after(0, lambda: self.device_badge.config(fg=self.neon_green))
                    self.append_log(f"[✓] Device detected in {mode} mode: {fb_out}")
                    return
            except Exception:
                pass

            try:
                res_adb = subprocess.run([adb_bin, "devices"], timeout=4, **kwargs)
                lines = [
                    l.strip() for l in res_adb.stdout.splitlines()
                    if l.strip() and not l.startswith("List of") and not l.startswith("*")
                ]
                if lines:
                    serial_info = lines[0].replace("\t", " ")
                    self.after(0, lambda: self.device_status_var.set(f"● ADB: {serial_info}"))
                    self.after(0, lambda: self.device_badge.config(fg=self.neon_green))
                    self.append_log(f"[✓] Device detected via ADB: {serial_info}")
                    return
            except Exception:
                pass

            self.after(0, lambda: self.device_status_var.set("● DISCONNECTED"))
            self.after(0, lambda: self.device_badge.config(fg=self.neon_pink))
            self.append_log("[!] No device detected in ADB or Fastboot mode.")

        threading.Thread(target=_check, daemon=True).start()

    def quick_reboot(self, target):
        """One-click reboot helper supporting both ADB and Fastboot states."""
        def _reboot():
            adb_bin = get_adb_bin()
            fb_bin = get_fastboot_bin()
            kwargs = {"capture_output": True, "text": True}
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            self.append_log(f"[*] Sending quick reboot command -> {target.upper()}...")
            try:
                res_fb = subprocess.run([fb_bin, "devices"], timeout=4, **kwargs)
                if res_fb.stdout.strip():
                    cmd = [fb_bin, "reboot"] if target == "system" else [fb_bin, "reboot", target]
                    subprocess.run(cmd, timeout=6, **kwargs)
                    self.append_log(f"[✓] Fastboot reboot to '{target}' sent!")
                    return
            except Exception:
                pass

            try:
                cmd = [adb_bin, "reboot"] if target == "system" else [adb_bin, "reboot", target]
                subprocess.run(cmd, timeout=6, **kwargs)
                self.append_log(f"[✓] ADB reboot to '{target}' sent!")
            except Exception as e:
                self.append_log(f"[!] Quick reboot failed: {e}")

        threading.Thread(target=_reboot, daemon=True).start()

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
            self.append_log("[!] Abort requested by user. Terminating active process...")
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
    # OPERATION HANDLERS
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
                initial_zip, rom_zip,
                log_fn=self.append_log, prompt_fn=self.thread_safe_prompt, stop_event=self.stop_event
            )
            self.set_status("Custom ROM Clean Flash Completed!")
            self.after(0, lambda: messagebox.showinfo(
                "Success",
                "Custom ROM Clean Flash Completed!\n\n"
                "Note: If your previous stock ROM was older than May 2024 (Android 14), "
                "reboot to Recovery and sideload the ROM once more using 'Update ROM (Sideload)' "
                "to populate both slots.\n\nOtherwise, select 'Reboot system now' on your phone!"
            ))

        self.run_in_background(task)

    def start_dirty_flash(self):
        rom_zip = self.update_rom_zip_var.get().strip()
        if not os.path.isfile(rom_zip):
            messagebox.showwarning("Missing File", "Please select the Custom ROM Zip file first.")
            return

        def task():
            self.set_status("Running Custom ROM Sideload...")
            dirty_flash_update_cancunf_gui(
                rom_zip, log_fn=self.append_log, prompt_fn=self.thread_safe_prompt, stop_event=self.stop_event
            )
            self.set_status("Custom ROM Sideload Completed!")
            self.after(0, lambda: messagebox.showinfo("Success", "ROM Sideload Completed!"))

        self.run_in_background(task)

    def start_stock_flash(self):
        rom_dir = self.stock_dir_var.get().strip()
        if not os.path.isdir(rom_dir):
            messagebox.showwarning("Missing Folder", "Please select the extracted Motorola Stock ROM folder first.")
            return

        if not messagebox.askyesno(
            "WARNING: Full Clean Stock Flash",
            f"Folder: {rom_dir}\n\n"
            "This will verify all 21 partition images, flash BOTH Slot A & Slot B, and ERASE ALL USERDATA.\n"
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

        if not messagebox.askyesno("Confirm Root Image Flash", f"Flash '{os.path.basename(img_path)}' to partition '{partition}'?"):
            return

        def task():
            self.set_status(f"Flashing {partition} partition...")
            root_phone_cancunf_gui(img_path, partition=partition, log_fn=self.append_log, stop_event=self.stop_event)
            self.set_status(f"Flashed {partition} successfully!")
            self.after(0, lambda: messagebox.showinfo("Success", f"Successfully flashed {partition} and triggered reboot!"))

        self.run_in_background(task)

    def download_portable_platform_tools(self):
        def task():
            sys_os = platform.system().lower()
            if "windows" in sys_os:
                url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
            elif "darwin" in sys_os:
                url = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
            else:
                url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"

            base_dir = get_app_dir()
            zip_target = os.path.join(base_dir, "platform-tools-temp.zip")

            self.set_status("Downloading Official Google Platform Tools...")
            self.append_log(f"[*] Downloading from: {url}")

            urllib.request.urlretrieve(url, zip_target)
            self.append_log("[*] Extracting platform-tools...")

            pt_folder = get_local_pt_dir()
            if os.path.isdir(pt_folder):
                shutil.rmtree(pt_folder, ignore_errors=True)

            with zipfile.ZipFile(zip_target, "r") as zf:
                zf.extractall(base_dir)

            if os.path.isfile(zip_target):
                os.remove(zip_target)

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
        script_dir = get_resource_dir()
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
                    "Please use the green 'Auto-Download & Configure Portable Platform Tools' button above, "
                    "or run './linux-adb-install.sh' from a terminal."
                )
            else:
                messagebox.showerror("Error", "linux-adb-install.sh not found!")


def launch_gui():
    app = CancunfToolkitGUI()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
