#!/usr/bin/env python3
import os
import re
import sys
import time
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
    detect_stock_folder_version,
    validate_stock_rom_folder,
    custom_rom_flash_cancunf_gui,
    dirty_flash_update_cancunf_gui,
    stock_rom_flash_cancunf_gui,
    root_phone_cancunf_gui,
    abort_active_process
)

if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def _draw_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1,
        x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r,
        x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
        x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r,
        x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class GlassCard(tk.Canvas):
    """Modern curved glassmorphic container with subtle specular border."""
    def __init__(
        self, parent, bg_parent="#0b1120", fill="#111a2e",
        outline="#23324d", radius=16, pad_x=16, pad_y=12, **kwargs
    ):
        super().__init__(
            parent, bg=bg_parent, highlightthickness=0, bd=0, **kwargs
        )
        self.fill = fill
        self.outline = outline
        self.radius = radius
        self.pad_x = pad_x
        self.pad_y = pad_y

        self.inner = tk.Frame(self, bg=fill)
        self.inner_win = self.create_window(
            pad_x, pad_y, window=self.inner, anchor="nw"
        )
        self.bind("<Configure>", self._on_resize)
        self.inner.bind("<Configure>", self._on_inner_configure)

    def _on_inner_configure(self, _event=None):
        req_h = self.inner.winfo_reqheight() + (self.pad_y * 2)
        if self.winfo_height() < req_h:
            self.config(height=req_h)

    def _on_resize(self, event):
        self.delete("glass_bg")
        w, h = max(event.width, 20), max(event.height, 20)
        _draw_rounded_rect(
            self, 2, 2, w - 2, h - 2, self.radius,
            fill=self.fill, outline=self.outline, width=1.5, tags="glass_bg"
        )
        self.tag_lower("glass_bg")
        self.coords(self.inner_win, self.pad_x, self.pad_y)
        self.itemconfigure(
            self.inner_win,
            width=max(w - (self.pad_x * 2), 10)
        )


class ModernPillButton(tk.Canvas):
    """iOS / Android 15 inspired smooth pill-shaped interactive button."""
    def __init__(
        self, parent, text, command=None, bg_parent="#0b1120",
        fill="#0ea5e9", hover_fill="#38bdf8", text_color="#ffffff",
        outline="#38bdf8", width=210, height=38, radius=19,
        font=("Segoe UI", 9, "bold")
    ):
        super().__init__(
            parent, width=width, height=height, bg=bg_parent,
            highlightthickness=0, bd=0, cursor="hand2"
        )
        self.text = text
        self.command = command
        self.fill = fill
        self.hover_fill = hover_fill
        self.text_color = text_color
        self.outline = outline
        self.w = width
        self.h = height
        self.radius = radius
        self.font = font
        self.disabled = False
        self._hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)
        self.bind("<Configure>", self._redraw)
        self._redraw()

    def set_disabled(self, is_disabled):
        self.disabled = is_disabled
        self.config(cursor="arrow" if is_disabled else "hand2")
        self._redraw()

    def _redraw(self, event=None):
        if event:
            self.w, self.h = event.width, event.height
        self.delete("all")
        if self.disabled:
            bg_c = "#162033"
            bd_c = "#1e293b"
            fg_c = "#475569"
        else:
            bg_c = self.hover_fill if self._hovered else self.fill
            bd_c = "#7dd3fc" if self._hovered else self.outline
            fg_c = self.text_color

        _draw_rounded_rect(
            self, 2, 2, self.w - 2, self.h - 2, self.radius,
            fill=bg_c, outline=bd_c, width=1.5
        )
        self.create_text(
            self.w / 2, self.h / 2, text=self.text,
            fill=fg_c, font=self.font
        )

    def _on_enter(self, _e):
        if not self.disabled:
            self._hovered = True
            self._redraw()

    def _on_leave(self, _e):
        if not self.disabled:
            self._hovered = False
            self._redraw()

    def _on_click(self, _e):
        if not self.disabled and self.command:
            self.command()


class CancunfToolkitGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚡ CANCUNF STUDIO — MOTO G54 / G64 5G FLASHING SUITE")
        self.geometry("1100x800")
        self.minsize(960, 680)
        self.resizable(True, True)

        # Glassmorphism Dark Theme Palette (Android 15 / iOS Dark Inspired)
        self.bg_root = "#050811"        # Deep AMOLED Midnight
        self.bg_glass = "#0b1120"       # Frosted Main Panel
        self.bg_card = "#111a2e"        # Elevated Glass Card
        self.bg_card_alt = "#0d1526"    # Subtle Inner Glass
        self.bd_glass = "#1e293b"       # Specular Edge Border
        self.bd_glow = "#00f0ff"        # Cyber Neon Cyan Glow
        self.fg_primary = "#f8fafc"     # Pure Crisp White
        self.fg_secondary = "#94a3b8"   # Soft Slate Muted
        self.neon_cyan = "#00f0ff"
        self.neon_blue = "#0284c7"
        self.neon_green = "#10b981"
        self.neon_pink = "#e11d48"
        self.neon_amber = "#f59e0b"

        self.configure(bg=self.bg_root)
        self.is_running = False
        self.stop_event = threading.Event()
        self.action_buttons = []
        self.nav_pills = {}
        self.views = {}

        self.initial_zip_var = tk.StringVar()
        self.custom_rom_zip_var = tk.StringVar()
        self.update_rom_zip_var = tk.StringVar()
        self.stock_dir_var = tk.StringVar()
        self.root_img_var = tk.StringVar()
        self.root_part_var = tk.StringVar(value="boot")

        self.device_status_var = tk.StringVar(value="● DISCONNECTED")
        self.tools_status_var = tk.StringVar(value="● CHECKING TOOLS")
        self.progress_label_var = tk.StringVar(value="READY")
        self.status_bar_var = tk.StringVar(
            value="System Ready  •  Device: Moto G54 / G64 5G (cancunf)  •  September ARB Shield Active"
        )

        self.init_zip_status = tk.StringVar(value="No file selected")
        self.rom_zip_status = tk.StringVar(value="No file selected")
        self.upd_zip_status = tk.StringVar(value="No file selected")
        self.stock_dir_status = tk.StringVar(value="No folder selected")
        self.root_img_status = tk.StringVar(value="No image selected")

        self.initial_zip_var.trace_add("write", lambda *_: self._validate())
        self.custom_rom_zip_var.trace_add("write", lambda *_: self._validate())
        self.update_rom_zip_var.trace_add("write", lambda *_: self._validate())
        self.stock_dir_var.trace_add("write", lambda *_: self._validate())
        self.root_img_var.trace_add("write", lambda *_: self._validate())

        self._setup_ttk_styles()
        self._build_glass_ui()
        self.switch_view("custom_rom")
        self.refresh_environment_status()

    def _setup_ttk_styles(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "Card.TRadiobutton", background=self.bg_card,
            foreground=self.fg_primary, font=("Segoe UI", 10, "bold"),
            indicatorcolor=self.neon_cyan
        )
        style.map("Card.TRadiobutton", background=[("active", self.bg_card)])

        style.configure(
            "Neon.Horizontal.TProgressbar", troughcolor="#050811",
            background=self.neon_cyan, bordercolor=self.bd_glass
        )

    def _build_glass_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ======================================================================
        # 1. FLOATING CURVED TOP HEADER BAR
        # ======================================================================
        top_wrap = tk.Frame(self, bg=self.bg_root)
        top_wrap.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))
        top_wrap.grid_columnconfigure(0, weight=1)

        header_card = GlassCard(
            top_wrap, bg_parent=self.bg_root, fill=self.bg_glass,
            outline="#1e293b", radius=18, pad_x=16, pad_y=8, height=58
        )
        header_card.grid(row=0, column=0, sticky="ew")
        hdr = header_card.inner
        hdr.grid_columnconfigure(1, weight=1)

        brand = tk.Frame(hdr, bg=self.bg_glass)
        brand.grid(row=0, column=0, sticky="w")
        tk.Label(
            brand, text="⚡ CANCUNF", bg=self.bg_glass,
            fg=self.neon_cyan, font=("Consolas", 16, "bold")
        ).pack(side=tk.LEFT)
        tk.Label(
            brand, text=" STUDIO", bg=self.bg_glass,
            fg="#ffffff", font=("Consolas", 16, "bold")
        ).pack(side=tk.LEFT)
        tk.Label(
            brand, text="  •  MOTO G54 / G64 5G", bg=self.bg_glass,
            fg=self.fg_secondary, font=("Segoe UI", 9, "bold")
        ).pack(side=tk.LEFT, padx=6)

        badges = tk.Frame(hdr, bg=self.bg_glass)
        badges.grid(row=0, column=1, sticky="e", padx=10)
        self.tools_badge = tk.Label(
            badges, textvariable=self.tools_status_var, bg="#050811",
            fg=self.neon_cyan, font=("Consolas", 9, "bold"), padx=12, pady=5
        )
        self.tools_badge.pack(side=tk.LEFT, padx=4)
        self.device_badge = tk.Label(
            badges, textvariable=self.device_status_var, bg="#050811",
            fg=self.neon_amber, font=("Consolas", 9, "bold"), padx=12, pady=5
        )
        self.device_badge.pack(side=tk.LEFT, padx=4)

        q_bar = tk.Frame(hdr, bg=self.bg_glass)
        q_bar.grid(row=0, column=2, sticky="e")
        ModernPillButton(
            q_bar, "🔄 Check", command=self.check_device_status,
            bg_parent=self.bg_glass, fill="#162033", hover_fill="#1e293b",
            outline="#334155", width=80, height=30, radius=15,
            font=("Segoe UI", 8, "bold")
        ).pack(side=tk.LEFT, padx=2)

        for lbl, mode in [
            ("Bootloader", "bootloader"),
            ("FastbootD", "fastboot"),
            ("Recovery", "recovery"),
            ("System", "system")
        ]:
            ModernPillButton(
                q_bar, lbl, command=lambda m=mode: self.quick_reboot(m),
                bg_parent=self.bg_glass, fill="#111a2e", hover_fill="#1e293b",
                outline="#23324d", width=78, height=30, radius=15,
                font=("Segoe UI", 8, "bold")
            ).pack(side=tk.LEFT, padx=2)

        # ======================================================================
        # 2. CURVED CRIMSON GLASS ARB SAFETY BANNER
        # ======================================================================
        alert_wrap = tk.Frame(self, bg=self.bg_root)
        alert_wrap.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 4))
        alert_wrap.grid_columnconfigure(0, weight=1)

        alert_card = GlassCard(
            alert_wrap, bg_parent=self.bg_root, fill="#280911",
            outline="#f43f5e", radius=14, pad_x=14, pad_y=6, height=36
        )
        alert_card.grid(row=0, column=0, sticky="ew")
        tk.Label(
            alert_card.inner,
            text="🚨 CRITICAL ARB SHIELD: SEPTEMBER UPDATE (V1TDS35H.83-20-5-14 / 83-20-5-8-2-1-3) BUMPS ANTI-ROLLBACK! NEVER DOWNGRADE STOCK ROM OR FLASH A16 ROMS — WILL HARD BRICK!",
            bg="#280911", fg="#fecdd3", font=("Segoe UI", 8, "bold")
        ).pack(fill=tk.X)

        # ======================================================================
        # 3. MAIN SPLIT WORKSPACE (CURVED SIDEBAR + GLASS STAGE + CONSOLE)
        # ======================================================================
        self.paned = tk.PanedWindow(
            self, orient=tk.VERTICAL, bg=self.bg_root, sashwidth=6, bd=0
        )
        self.paned.grid(row=2, column=0, sticky="nsew", padx=14, pady=4)

        upper = tk.Frame(self.paned, bg=self.bg_root)
        upper.grid_columnconfigure(1, weight=1)
        upper.grid_rowconfigure(0, weight=1)
        self.paned.add(upper, minsize=395)

        # Left Curved Frosted Sidebar
        sidebar_card = GlassCard(
            upper, bg_parent=self.bg_root, fill=self.bg_glass,
            outline=self.bd_glass, radius=20, pad_x=12, pad_y=14, width=250
        )
        sidebar_card.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        sidebar_card.grid_propagate(False)
        sb = sidebar_card.inner

        tk.Label(
            sb, text="STUDIO MODULES", bg=self.bg_glass,
            fg=self.fg_secondary, font=("Consolas", 9, "bold"), anchor="w"
        ).pack(fill=tk.X, padx=8, pady=(2, 10))

        self._add_nav_pill(sb, "custom_rom", "🚀  Clean Flash Custom ROM")
        self._add_nav_pill(sb, "dirty_rom", "📦  Update ROM (Sideload)")
        self._add_nav_pill(sb, "stock_rom", "🛠️  Restore Stock Firmware")
        self._add_nav_pill(sb, "root_phone", "🔓  Root Phone (Boot/Init)")
        self._add_nav_pill(sb, "platform_tools", "⚙️  Setup Platform Tools")

        credit_glass = GlassCard(
            sb, bg_parent=self.bg_glass, fill="#070b14",
            outline="#1e293b", radius=14, pad_x=10, pad_y=8, height=68
        )
        credit_glass.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 2))
        tk.Label(
            credit_glass.inner,
            text="Guide : CyberKnight777\nOTG   : nohajc/termux-adb\nAuthor: Aman (neonheart711)",
            bg="#070b14", fg=self.fg_secondary, font=("Consolas", 8),
            justify=tk.LEFT, anchor="w"
        ).pack(fill=tk.X)

        # Right Main Glass Stage
        self.stage_card = GlassCard(
            upper, bg_parent=self.bg_root, fill=self.bg_glass,
            outline=self.bd_glass, radius=20, pad_x=18, pad_y=14
        )
        self.stage_card.grid(row=0, column=1, sticky="nsew")
        self.page_container = self.stage_card.inner
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self._build_view_custom_rom()
        self._build_view_dirty_rom()
        self._build_view_stock_rom()
        self._build_view_root()
        self._build_view_platform_tools()

        # Bottom Curved Terminal Telemetry Dock
        console_card = GlassCard(
            self.paned, bg_parent=self.bg_root, fill=self.bg_glass,
            outline=self.bd_glass, radius=20, pad_x=14, pad_y=10
        )
        self.paned.add(console_card, minsize=185)
        c_in = console_card.inner
        c_in.grid_columnconfigure(0, weight=1)
        c_in.grid_rowconfigure(1, weight=1)

        c_bar = tk.Frame(c_in, bg=self.bg_glass)
        c_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        c_bar.grid_columnconfigure(0, weight=1)

        tk.Label(
            c_bar, text="● LIVE TERMINAL TELEMETRY", bg=self.bg_glass,
            fg=self.neon_green, font=("Consolas", 10, "bold")
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            c_bar, textvariable=self.progress_label_var, bg=self.bg_glass,
            fg=self.neon_cyan, font=("Consolas", 9, "bold")
        ).grid(row=0, column=1, padx=10)

        self.progress = ttk.Progressbar(
            c_bar, style="Neon.Horizontal.TProgressbar",
            mode="determinate", length=170, maximum=100
        )
        self.progress.grid(row=0, column=2, padx=8)

        self.stop_btn = ModernPillButton(
            c_bar, "⏹ Abort", command=self.abort_current_task,
            bg_parent=self.bg_glass, fill="#be123c", hover_fill="#f43f5e",
            outline="#f43f5e", width=86, height=28, radius=14,
            font=("Segoe UI", 8, "bold")
        )
        self.stop_btn.set_disabled(True)
        self.stop_btn.grid(row=0, column=3, padx=4)

        for col_idx, (txt, cmd) in enumerate([
            ("Copy", self.copy_log),
            ("Save", self.save_log),
            ("Clear", self.clear_log)
        ], start=4):
            ModernPillButton(
                c_bar, txt, command=cmd, bg_parent=self.bg_glass,
                fill="#162033", hover_fill="#1e293b", outline="#334155",
                width=64, height=28, radius=14, font=("Segoe UI", 8, "bold")
            ).grid(row=0, column=col_idx, padx=2)

        self.log_box = scrolledtext.ScrolledText(
            c_in, bg="#04070e", fg="#38bdf8", insertbackground="white",
            font=("Consolas", 9), relief=tk.FLAT, bd=8, state=tk.DISABLED
        )
        self.log_box.grid(row=1, column=0, sticky="nsew")

        self.log_box.tag_config("time", foreground="#64748b")
        self.log_box.tag_config("info", foreground="#38bdf8")
        self.log_box.tag_config(
            "success", foreground="#10b981", font=("Consolas", 9, "bold")
        )
        self.log_box.tag_config("warn", foreground="#facc15")
        self.log_box.tag_config(
            "error", foreground="#fb7185", font=("Consolas", 9, "bold")
        )
        self.log_box.tag_config("cmd", foreground="#c084fc")

        # 4. Sleek Status Bar
        footer = tk.Label(
            self, textvariable=self.status_bar_var, bg=self.bg_root,
            fg=self.fg_secondary, font=("Segoe UI", 9), anchor="w",
            padx=18, pady=4
        )
        footer.grid(row=3, column=0, sticky="ew")

        self.append_log("[i] CANCUNF Modern Glass Studio initialized.")
        self.append_log(
            "🚨 [SAFETY] September Security Update (83-20-5-14) ARB "
            "Protection is active across all flashing modules."
        )

    def _add_nav_pill(self, parent, key, text):
        canvas = tk.Canvas(
            parent, height=40, bg=self.bg_glass,
            highlightthickness=0, bd=0, cursor="hand2"
        )
        canvas.pack(fill=tk.X, pady=3)
        self.nav_pills[key] = {"canvas": canvas, "text": text, "active": False}
        canvas.bind("<ButtonRelease-1>", lambda _e, k=key: self.switch_view(k))
        canvas.bind("<Configure>", lambda _e, k=key: self._draw_nav_pill(k))

    def _draw_nav_pill(self, key):
        item = self.nav_pills[key]
        c = item["canvas"]
        c.delete("all")
        w = max(c.winfo_width(), 210)
        h = max(c.winfo_height(), 40)
        if item["active"]:
            _draw_rounded_rect(
                c, 2, 2, w - 2, h - 2, 16,
                fill="#13233f", outline=self.neon_cyan, width=1.5
            )
            fg = self.neon_cyan
        else:
            _draw_rounded_rect(
                c, 2, 2, w - 2, h - 2, 16,
                fill="#0d1526", outline="#19253d", width=1
            )
            fg = self.fg_secondary
        c.create_text(
            16, h / 2, text=item["text"], fill=fg,
            font=("Segoe UI", 9, "bold"), anchor="w"
        )

    def switch_view(self, key):
        for k, item in self.nav_pills.items():
            item["active"] = (k == key)
            self._draw_nav_pill(k)
        for k, frame in self.views.items():
            if k == key:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_remove()

    def _create_header(self, parent, title, subtitle):
        hdr = tk.Frame(parent, bg=self.bg_glass)
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(
            hdr, text=title, bg=self.bg_glass, fg="#ffffff",
            font=("Segoe UI", 14, "bold"), anchor="w"
        ).pack(fill=tk.X)
        tk.Label(
            hdr, text=subtitle, bg=self.bg_glass, fg=self.fg_secondary,
            font=("Segoe UI", 9), anchor="w"
        ).pack(fill=tk.X, pady=(2, 0))

    def _create_danger_glass(self, parent, row, title_text, body_text):
        card = GlassCard(
            parent, bg_parent=self.bg_glass, fill="#260810",
            outline="#f43f5e", radius=16, pad_x=14, pad_y=8, height=78
        )
        card.grid(row=row, column=0, sticky="ew", pady=4)
        tk.Label(
            card.inner, text=title_text, bg="#260810", fg="#fda4af",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill=tk.X)
        tk.Label(
            card.inner, text=body_text, bg="#260810", fg="#fecdd3",
            font=("Segoe UI", 8), justify=tk.LEFT, anchor="w"
        ).pack(fill=tk.X, pady=(2, 0))

    def _create_glass_file_row(
        self, parent, row, label_text, path_var, st_var, cmd
    ):
        card = GlassCard(
            parent, bg_parent=self.bg_glass, fill=self.bg_card,
            outline="#23324d", radius=16, pad_x=14, pad_y=8, height=64
        )
        card.grid(row=row, column=0, sticky="ew", pady=4)
        f = card.inner
        f.grid_columnconfigure(1, weight=1)

        tk.Label(
            f, text=label_text, bg=self.bg_card, fg=self.fg_primary,
            font=("Segoe UI", 9, "bold"), width=20, anchor="w"
        ).grid(row=0, column=0, sticky="w")

        entry = tk.Entry(
            f, textvariable=path_var, bg="#070b14", fg=self.neon_cyan,
            insertbackground="white", relief=tk.FLAT, font=("Consolas", 9),
            highlightthickness=1, highlightbackground="#1e293b",
            highlightcolor=self.neon_cyan
        )
        entry.grid(row=0, column=1, sticky="ew", padx=10, ipady=4)

        ModernPillButton(
            f, "Browse...", command=cmd, bg_parent=self.bg_card,
            fill="#1e293b", hover_fill="#334155", outline="#38bdf8",
            width=92, height=28, radius=14, font=("Segoe UI", 8, "bold")
        ).grid(row=0, column=2)

        tk.Label(
            f, textvariable=st_var, bg=self.bg_card, fg=self.fg_secondary,
            font=("Consolas", 8), anchor="w"
        ).grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=(2, 0))

    def _build_view_custom_rom(self):
        v = tk.Frame(self.page_container, bg=self.bg_glass)
        v.grid_columnconfigure(0, weight=1)
        self.views["custom_rom"] = v
        self._create_header(
            v, "🚀 Clean Flash Custom ROM (FastbootD + ADB Sideload)",
            "Automated safe pipeline: Bootloader ➔ FastbootD (is-userspace) ➔ initial_install.zip ➔ Wipe ➔ Sideload"
        )
        self._create_danger_glass(
            v, 1,
            "🚨 SEPTEMBER SECURITY UPDATE WARNING (CUSTOM ROM BRICK RISK):",
            "• If your phone updated to the September Patch (V1TDS35H.83-20-5-14 / 83-20-5-8-2-1-3), DO NOT flash A16 or incompatible Custom ROMs — flashing them WILL BRICK your device!"
        )
        self._create_glass_file_row(
            v, 2, "1. Initial Install Zip:", self.initial_zip_var,
            self.init_zip_status,
            lambda: self._browse_file(self.initial_zip_var, "Select Initial Zip")
        )
        self._create_glass_file_row(
            v, 3, "2. Custom ROM Zip:", self.custom_rom_zip_var,
            self.rom_zip_status,
            lambda: self._browse_file(self.custom_rom_zip_var, "Select ROM Zip")
        )
        act = tk.Frame(v, bg=self.bg_glass)
        act.grid(row=4, column=0, sticky="ew", pady=(10, 2))
        btn = ModernPillButton(
            act, "⚡ Start Custom ROM Clean Flash",
            command=self.start_custom_flash, bg_parent=self.bg_glass,
            fill="#0284c7", hover_fill="#0ea5e9", outline=self.neon_cyan,
            width=260, height=40, radius=20
        )
        btn.pack(side=tk.LEFT)
        self.action_buttons.append(btn)

    def _build_view_dirty_rom(self):
        v = tk.Frame(self.page_container, bg=self.bg_glass)
        v.grid_columnconfigure(0, weight=1)
        self.views["dirty_rom"] = v
        self._create_header(
            v, "📦 Update Custom ROM Build (Dirty Flash / Sideload)",
            "Sideload a newer build of your Custom ROM in Recovery without wiping data."
        )
        self._create_danger_glass(
            v, 1,
            "🚨 SEPTEMBER SECURITY UPDATE WARNING (SIDELOAD BRICK RISK):",
            "• Do NOT sideload A16 or pre-September Custom ROM builds if your device bootloader has been updated to the September Security Patch!"
        )
        self._create_glass_file_row(
            v, 2, "Custom ROM Zip:", self.update_rom_zip_var,
            self.upd_zip_status,
            lambda: self._browse_file(self.update_rom_zip_var, "Select ROM Zip")
        )
        act = tk.Frame(v, bg=self.bg_glass)
        act.grid(row=3, column=0, sticky="ew", pady=(12, 2))
        btn = ModernPillButton(
            act, "📦 Start ADB Sideload Update",
            command=self.start_dirty_flash, bg_parent=self.bg_glass,
            fill="#0284c7", hover_fill="#0ea5e9", outline=self.neon_cyan,
            width=240, height=40, radius=20
        )
        btn.pack(side=tk.LEFT)
        self.action_buttons.append(btn)

    def _build_view_stock_rom(self):
        v = tk.Frame(self.page_container, bg=self.bg_glass)
        v.grid_columnconfigure(0, weight=1)
        self.views["stock_rom"] = v
        self._create_header(
            v, "🛠️ Full Clean Flash Stock Firmware (Slot A & Slot B)",
            "Pre-verifies Bootloader ARB status, XML build metadata & all 21 mandatory partition images."
        )
        self._create_danger_glass(
            v, 1,
            "🚨 EXTREME DANGER: SEPTEMBER UPDATE ARB (ANTI-ROLLBACK) COUNTER BUMP!",
            "• The September update (V1TDS35H.83-20-5-14 / 83-20-5-8-2-1-3) bumps the ARB counter once more!\n"
            "• If your phone has the September update installed, YOU CANNOT DOWNGRADE to older Stock Firmware (A13/A14). Downgrading WILL PERMANENTLY HARD BRICK (Dead Boot) your phone!"
        )
        self._create_glass_file_row(
            v, 2, "Stock ROM Folder:", self.stock_dir_var,
            self.stock_dir_status,
            lambda: self._browse_folder(self.stock_dir_var, "Select Stock Folder")
        )
        act = tk.Frame(v, bg=self.bg_glass)
        act.grid(row=3, column=0, sticky="ew", pady=(10, 2))
        btn = ModernPillButton(
            act, "🔥 Verify Bootloader & Start Clean Stock Flash",
            command=self.start_stock_flash, bg_parent=self.bg_glass,
            fill="#be123c", hover_fill="#e11d48", outline="#fda4af",
            width=310, height=40, radius=20
        )
        btn.pack(side=tk.LEFT)
        self.action_buttons.append(btn)

    def _build_view_root(self):
        v = tk.Frame(self.page_container, bg=self.bg_glass)
        v.grid_columnconfigure(0, weight=1)
        self.views["root_phone"] = v
        self._create_header(
            v, "🔓 Root Moto G54 / G64 5G (Flash Patched Image)",
            "Flash a Magisk, KernelSU, or APatch patched boot.img, init_boot.img, or vendor_boot.img via Fastboot."
        )
        self._create_glass_file_row(
            v, 1, "Patched Image (.img):", self.root_img_var,
            self.root_img_status,
            lambda: self._browse_file(
                self.root_img_var, "Select Image",
                [("Image Files", "*.img"), ("All Files", "*.*")]
            )
        )
        p_card = GlassCard(
            v, bg_parent=self.bg_glass, fill=self.bg_card,
            outline="#23324d", radius=16, pad_x=14, pad_y=10, height=48
        )
        p_card.grid(row=2, column=0, sticky="ew", pady=6)
        tk.Label(
            p_card.inner, text="Target Partition:", bg=self.bg_card,
            fg=self.fg_primary, font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 16))
        for p_name in ["boot", "init_boot", "vendor_boot"]:
            ttk.Radiobutton(
                p_card.inner, text=p_name, style="Card.TRadiobutton",
                variable=self.root_part_var, value=p_name
            ).pack(side=tk.LEFT, padx=10)

        act = tk.Frame(v, bg=self.bg_glass)
        act.grid(row=3, column=0, sticky="ew", pady=(10, 2))
        btn = ModernPillButton(
            act, "🔓 Flash Patched Root Image",
            command=self.start_root_flash, bg_parent=self.bg_glass,
            fill="#0284c7", hover_fill="#0ea5e9", outline=self.neon_cyan,
            width=240, height=40, radius=20
        )
        btn.pack(side=tk.LEFT)
        self.action_buttons.append(btn)

    def _build_view_platform_tools(self):
        v = tk.Frame(self.page_container, bg=self.bg_glass)
        v.grid_columnconfigure(0, weight=1)
        self.views["platform_tools"] = v
        self._create_header(
            v, "⚙️ Setup & Verify Android SDK Platform Tools",
            "Automatically configure ADB & Fastboot on Windows, Linux, or macOS."
        )
        c1 = GlassCard(
            v, bg_parent=self.bg_glass, fill=self.bg_card,
            outline="#10b981", radius=16, pad_x=16, pad_y=12, height=105
        )
        c1.grid(row=1, column=0, sticky="ew", pady=6)
        tk.Label(
            c1.inner,
            text="Option 1: Portable Official Google Platform Tools (Recommended)",
            bg=self.bg_card, fg=self.neon_green, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")
        tk.Label(
            c1.inner,
            text="Downloads the latest official platform-tools zip directly into this toolkit folder.",
            bg=self.bg_card, fg=self.fg_secondary, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 8))
        b1 = ModernPillButton(
            c1.inner, "⚡ Auto-Download Portable Platform Tools",
            command=self.download_portable_platform_tools,
            bg_parent=self.bg_card, fill="#059669", hover_fill="#10b981",
            outline="#34d399", width=290, height=34, radius=17
        )
        b1.pack(anchor="w")
        self.action_buttons.append(b1)

        c2 = GlassCard(
            v, bg_parent=self.bg_glass, fill=self.bg_card,
            outline="#23324d", radius=16, pad_x=16, pad_y=12, height=85
        )
        c2.grid(row=2, column=0, sticky="ew", pady=6)
        tk.Label(
            c2.inner, text="Option 2: System-Wide OS Package Manager Installer",
            bg=self.bg_card, fg=self.neon_cyan, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 6))
        b2 = ModernPillButton(
            c2.inner, "🖥️ Run OS Package Manager Script",
            command=self.run_external_os_installer,
            bg_parent=self.bg_card, fill="#1e293b", hover_fill="#334155",
            outline="#38bdf8", width=250, height=32, radius=16
        )
        b2.pack(anchor="w")
        self.action_buttons.append(b2)

    def _validate(self):
        for var, st in [
            (self.initial_zip_var, self.init_zip_status),
            (self.custom_rom_zip_var, self.rom_zip_status),
            (self.update_rom_zip_var, self.upd_zip_status),
            (self.root_img_var, self.root_img_status),
        ]:
            p = var.get().strip()
            if not p:
                st.set("No file selected")
            elif os.path.isfile(p):
                mb = os.path.getsize(p) / (1024 * 1024)
                st.set(f"✓ Ready: {os.path.basename(p)} ({mb:.1f} MB)")
            else:
                st.set("✗ File not found!")

        p4 = self.stock_dir_var.get().strip()
        if not p4:
            self.stock_dir_status.set("No folder selected")
        elif os.path.isdir(p4):
            missing, sparse = validate_stock_rom_folder(p4)
            ver = detect_stock_folder_version(p4)
            if not missing and sparse:
                self.stock_dir_status.set(
                    f"✓ Verified: 21 images + {len(sparse)} chunks ({ver})"
                )
            else:
                self.stock_dir_status.set(
                    f"✗ Incomplete folder: {len(missing)} missing files"
                )
        else:
            self.stock_dir_status.set("✗ Directory not found!")

    def _browse_file(self, target_var, title, filetypes=None):
        if filetypes is None:
            filetypes = [("Zip Files", "*.zip"), ("All Files", "*.*")]
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
            if "[OK]" in message or "COMPLETED" in message:
                tag = "success"
            elif "[!]" in message or "WARNING" in message or "DANGER" in message or "🚨" in message:
                tag = "warn"
            elif "[X]" in message or "[ERROR]" in message:
                tag = "error"
            elif "--> Executing:" in message:
                tag = "cmd"

            self.log_box.insert(tk.END, ts, "time")
            self.log_box.insert(tk.END, message + "\n", tag)
            self.log_box.see(tk.END)
            self.log_box.config(state=tk.DISABLED)

            pct_m = re.search(r"\(~?(\d+)%\)", message)
            chk_m = re.search(r"\((\d+)/(\d+)\)", message)
            if pct_m:
                pct = int(pct_m.group(1))
                self.progress.stop()
                self.progress.config(mode="determinate", value=pct)
                self.progress_label_var.set(f"{pct}%")
            elif chk_m:
                cur, tot = int(chk_m.group(1)), int(chk_m.group(2))
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
        self.append_log("[OK] Console log copied to clipboard.")

    def save_log(self):
        path = filedialog.asksaveasfilename(
            title="Save Log", defaultextension=".txt",
            initialfile="cancunf_flash_log.txt"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_box.get("1.0", tk.END))
            self.append_log(f"[OK] Log saved to: {path}")

    def set_status(self, text):
        self.after(0, lambda: self.status_bar_var.set(f"Status: {text}"))

    def set_busy(self, busy):
        self.is_running = busy
        for btn in self.action_buttons:
            btn.set_disabled(busy)
        self.stop_btn.set_disabled(not busy)
        if busy:
            self.progress_label_var.set("WORKING...")
            self.progress.config(mode="indeterminate")
            self.progress.start(14)
        else:
            self.progress.stop()
            self.progress.config(mode="determinate", value=0)
            self.progress_label_var.set("READY")

    def refresh_environment_status(self):
        adb_b, fb_b = get_adb_bin(), get_fastboot_bin()
        ok_a = shutil.which(adb_b) or os.path.isfile(adb_b)
        ok_f = shutil.which(fb_b) or os.path.isfile(fb_b)
        if ok_a and ok_f:
            self.tools_status_var.set("● TOOLS READY")
            self.tools_badge.config(fg=self.neon_green)
        else:
            self.tools_status_var.set("● TOOLS MISSING")
            self.tools_badge.config(fg=self.neon_pink)

    def check_device_status(self):
        def _check():
            self.refresh_environment_status()
            adb_b, fb_b = get_adb_bin(), get_fastboot_bin()
            kw = {"capture_output": True, "text": True}
            if os.name == "nt":
                kw["creationflags"] = subprocess.CREATE_NO_WINDOW
            try:
                r_fb = subprocess.run([fb_b, "devices"], timeout=4, **kw)
                if r_fb.stdout.strip():
                    ser = r_fb.stdout.strip().split()[0]
                    r_u = subprocess.run(
                        [fb_b, "getvar", "is-userspace"], timeout=4, **kw
                    )
                    u_out = (r_u.stdout + r_u.stderr).lower()
                    m = "FASTBOOTD" if "is-userspace: yes" in u_out else "BL"
                    self.after(
                        0, lambda: self.device_status_var.set(f"● {ser} ({m})")
                    )
                    self.after(
                        0, lambda: self.device_badge.config(fg=self.neon_green)
                    )
                    return
            except Exception:
                pass
            try:
                r_a = subprocess.run([adb_b, "devices"], timeout=4, **kw)
                lines = [
                    l.strip() for l in r_a.stdout.splitlines()
                    if l.strip()
                    and not l.startswith("List of")
                    and not l.startswith("*")
                ]
                if lines:
                    self.after(
                        0, lambda: self.device_status_var.set(f"● ADB: {lines[0]}")
                    )
                    self.after(
                        0, lambda: self.device_badge.config(fg=self.neon_green)
                    )
                    return
            except Exception:
                pass
            self.after(0, lambda: self.device_status_var.set("● DISCONNECTED"))
            self.after(0, lambda: self.device_badge.config(fg=self.neon_pink))
        threading.Thread(target=_check, daemon=True).start()

    def quick_reboot(self, target):
        def _reboot():
            adb_b, fb_b = get_adb_bin(), get_fastboot_bin()
            kw = {"capture_output": True, "text": True}
            if os.name == "nt":
                kw["creationflags"] = subprocess.CREATE_NO_WINDOW
            try:
                if subprocess.run([fb_b, "devices"], timeout=4, **kw).stdout.strip():
                    cmd = [fb_b, "reboot"] if target == "system" else [fb_b, "reboot", target]
                    subprocess.run(cmd, timeout=6, **kw)
                    return
            except Exception:
                pass
            try:
                cmd = [adb_b, "reboot"] if target == "system" else [adb_b, "reboot", target]
                subprocess.run(cmd, timeout=6, **kw)
            except Exception as e:
                self.append_log(f"[!] Reboot failed: {e}")
        threading.Thread(target=_reboot, daemon=True).start()

    def thread_safe_prompt(self, message):
        event = threading.Event()
        result = {"ok": False}

        def _ask():
            result["ok"] = messagebox.askokcancel(
                "🚨 CRITICAL SEPTEMBER ARB SAFETY CHECK", message
            )
            event.set()

        self.after(0, _ask)
        event.wait()
        return result["ok"]

    def abort_current_task(self):
        if self.is_running:
            self.stop_event.set()
            abort_active_process()
            self.append_log("[!] Abort requested by user.")

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
                self.after(
                    0, lambda err=str(e): messagebox.showerror("Stopped", err)
                )
                self.set_status("Operation stopped")
            finally:
                self.after(0, lambda: self.set_busy(False))
                self.after(0, self.refresh_environment_status)

        threading.Thread(target=_worker, daemon=True).start()

    def start_custom_flash(self):
        i_zip = self.initial_zip_var.get().strip()
        r_zip = self.custom_rom_zip_var.get().strip()
        if not os.path.isfile(i_zip) or not os.path.isfile(r_zip):
            messagebox.showwarning("Missing", "Select valid Initial & ROM zips.")
            return
        msg = (
            "IMPORTANT:\n"
            "If your phone is on the September Security Update "
            "(V1TDS35H.83-20-5-14 / 83-20-5-8-2-1-3), flashing A16 or "
            "incompatible Custom ROMs WILL BRICK YOUR DEVICE!\n\n"
            "Connect Moto G54/G64 in Bootloader Mode. Proceed?"
        )
        if not messagebox.askyesno("🚨 SEPTEMBER UPDATE WARNING", msg):
            return

        def task():
            self.set_status("Running Custom ROM Clean Flash...")
            custom_rom_flash_cancunf_gui(
                i_zip, r_zip, log_fn=self.append_log,
                prompt_fn=self.thread_safe_prompt, stop_event=self.stop_event
            )
            self.set_status("Custom ROM Flash Completed!")
            self.after(0, lambda: messagebox.showinfo(
                "Success", "Custom ROM Clean Flash Completed!"
            ))

        self.run_in_background(task)

    def start_dirty_flash(self):
        r_zip = self.update_rom_zip_var.get().strip()
        if not os.path.isfile(r_zip):
            messagebox.showwarning("Missing", "Select a ROM zip file.")
            return
        msg = (
            "Ensure this ROM build is compatible with your current "
            "bootloader patch level (Do NOT sideload A16 ROMs on September+ "
            "stock bootloader).\n\nProceed with ADB Sideload?"
        )
        if not messagebox.askyesno("🚨 Confirm Sideload Update", msg):
            return

        def task():
            self.set_status("Running Custom ROM Sideload...")
            dirty_flash_update_cancunf_gui(
                r_zip, log_fn=self.append_log,
                prompt_fn=self.thread_safe_prompt, stop_event=self.stop_event
            )
            self.set_status("ROM Sideload Completed!")
            self.after(0, lambda: messagebox.showinfo(
                "Success", "Custom ROM Update Completed!"
            ))

        self.run_in_background(task)

    def start_stock_flash(self):
        r_dir = self.stock_dir_var.get().strip()
        if not os.path.isdir(r_dir):
            messagebox.showwarning("Missing", "Select extracted Stock ROM folder.")
            return
        ver = detect_stock_folder_version(r_dir)
        msg = (
            f"Selected Stock Firmware: {ver}\n\n"
            "The September Security Update (V1TDS35H.83-20-5-14 / "
            "83-20-5-8-2-1-3) bumps the ARB (Anti-RollBack) counter!\n\n"
            "* DO NOT downgrade to any older Stock Firmware (A13 or older "
            "A14/A15) if you updated to the September patch!\n"
            "* Downgrading WILL PERMANENTLY HARD BRICK your device!\n\n"
            "Ensure phone is in Bootloader Mode. Proceed to live check?"
        )
        if not messagebox.askyesno("🚨 EXTREME DANGER: ARB BUMP", msg):
            return

        def task():
            self.set_status("Verifying Bootloader & Flashing Stock ROM...")
            stock_rom_flash_cancunf_gui(
                r_dir, log_fn=self.append_log,
                prompt_fn=self.thread_safe_prompt, stop_event=self.stop_event
            )
            self.set_status("Stock Firmware Flash Completed!")
            self.after(0, lambda: messagebox.showinfo(
                "Success",
                "Full Clean Stock Flash Completed!\n"
                "Press Power button on phone to reboot."
            ))

        self.run_in_background(task)

    def start_root_flash(self):
        img = self.root_img_var.get().strip()
        part = self.root_part_var.get().strip()
        if not os.path.isfile(img):
            messagebox.showwarning("Missing", f"Select valid {part}.img file.")
            return
        if not messagebox.askyesno("Confirm", f"Flash to {part}?"):
            return

        def task():
            self.set_status(f"Flashing {part} partition...")
            root_phone_cancunf_gui(
                img, partition=part, log_fn=self.append_log,
                stop_event=self.stop_event
            )
            self.set_status(f"Flashed {part} successfully!")
            self.after(0, lambda: messagebox.showinfo(
                "Success", f"Successfully flashed {part} and rebooted!"
            ))

        self.run_in_background(task)

    def download_portable_platform_tools(self):
        def task():
            s = platform.system().lower()
            if "windows" in s:
                u = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
            elif "darwin" in s:
                u = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
            else:
                u = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
            b_dir = get_app_dir()
            z_tmp = os.path.join(b_dir, "pt-temp.zip")
            self.set_status("Downloading Platform Tools...")
            urllib.request.urlretrieve(u, z_tmp)
            if os.path.isdir(get_local_pt_dir()):
                shutil.rmtree(get_local_pt_dir(), ignore_errors=True)
            with zipfile.ZipFile(z_tmp, "r") as zf:
                zf.extractall(b_dir)
            if os.path.isfile(z_tmp):
                os.remove(z_tmp)
            if os.name != "nt":
                for b in ["adb", "fastboot"]:
                    bp = os.path.join(get_local_pt_dir(), b)
                    if os.path.isfile(bp):
                        os.chmod(bp, 0o755)
            self.set_status("Platform Tools Ready!")
            self.after(
                0, lambda: messagebox.showinfo("Success", "Tools Ready!")
            )
        self.run_in_background(task)

    def run_external_os_installer(self):
        s_dir, s_os = get_resource_dir(), platform.system().lower()
        if "windows" in s_os:
            bat = os.path.join(s_dir, "windows-adb-install.bat")
            if os.path.isfile(bat):
                subprocess.Popen(["cmd.exe", "/c", "start", "", bat], shell=True)
        else:
            f_sh = "mac-adb-install.sh" if "darwin" in s_os else "linux-adb-install.sh"
            sh = os.path.join(s_dir, f_sh)
            if os.path.isfile(sh):
                os.chmod(sh, 0o755)
                if "darwin" in s_os:
                    subprocess.Popen(["open", "-a", "Terminal", sh])
                else:
                    subprocess.Popen(["x-terminal-emulator", "-e", f"bash '{sh}'"])


def launch_gui():
    app = CancunfToolkitGUI()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
