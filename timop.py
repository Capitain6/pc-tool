import os
import sys
import subprocess
import threading
import string
import random
import socket
import hashlib
import urllib.request
import json
import time
import psutil
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from collections import deque

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.units import cm
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# ============================================================
#  PC TOOL  v1.0
# ============================================================

VERSION     = "1.0"
APP_NAME    = "PC Tool"
GITHUB_REPO = "Capitaine6/pc-tool"   # pour la vérification des mises à jour
APP_DIR   = os.path.join(os.environ.get("APPDATA", ""), "PCTool")
LOG_FILE  = os.path.join(APP_DIR, "historique.log")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

# Processus systèmes protégés (module-level pour être partagé)
PROTECTED_PROCESSES = {
    "System", "System Idle Process", "Registry",
    "svchost.exe", "explorer.exe", "dwm.exe", "csrss.exe",
    "winlogon.exe", "lsass.exe", "services.exe", "smss.exe",
    "wininit.exe", "fontdrvhost.exe", "sihost.exe", "taskhostw.exe",
    "spoolsv.exe", "SearchIndexer.exe", "MsMpEng.exe", "NisSrv.exe",
    "SecurityHealthService.exe", "SgrmBroker.exe", "WmiPrvSE.exe",
    "python.exe", "pythonw.exe", "pc_tool.exe",
}

# ── Paramètres par défaut ────────────────────────────────────
DEFAULT_SETTINGS = {
    "theme":            "dark",
    "lang":             "fr",
    "accent":           "#2196f3",
    "refresh_rate":     2,
    "alert_cpu":        85,
    "alert_ram":        85,
    "alert_disk":       90,
    "alert_uptime":     48,
    "dns_primary":      "1.1.1.1",
    "dns_secondary":    "1.0.0.1",
    "tray_enabled":     True,
    "sched_enabled":    False,
    "sched_day":        "Lundi",
    "sched_hour":       "08:00",
    "startup_page":     "Dashboard",
}

# ── Thèmes ───────────────────────────────────────────────────
THEMES = {
    "dark": {
        "BG": "#0a0a0a", "SURFACE": "#141414", "RAISED": "#1e1e1e",
        "CARD": "#242424", "BORDER": "#2a2a2a", "TEXT": "#f0f0f0", "MUTED": "#888888",
    },
    "light": {
        "BG": "#f5f5f5", "SURFACE": "#ffffff", "RAISED": "#eeeeee",
        "CARD": "#e8e8e8", "BORDER": "#cccccc", "TEXT": "#111111", "MUTED": "#555555",
    },
}

GREEN  = "#4caf50"; GREEN2 = "#2e7d32"
ORANGE = "#ff9800"; RED    = "#f44336"; RED2 = "#b71c1c"
BLUE   = "#2196f3"; BLUE2  = "#1565c0"
PURPLE = "#9c27b0"; CYAN   = "#00bcd4"

FONT_TITLE = ("Arial", 26, "bold")
FONT_HEAD  = ("Arial", 15, "bold")
FONT_BODY  = ("Arial", 13)
FONT_SMALL = ("Arial", 12)
FONT_TINY  = ("Arial", 10)
FONT_MONO  = ("Courier New", 12)
FONT_BIG   = ("Arial", 34, "bold")
FONT_MED   = ("Arial", 20, "bold")

BLOATWARE = [
    "mcafee","norton","avast","avg","coupon","babylon","conduit",
    "opencandy","mywebsearch","ask toolbar","weatherbug","bonzi",
    "gator","kazaa","limewire","zango","hotbar","ilivid","yontoo",
    "delta search","sweet page","browser manager","rocket tab",
    "search protect","spigot","crossrider","wajam","lollipop",
    "superfish","shopper","deals","savings","optimizer pro",
    "advanced systemcare","iobit","reimage","pckeeper","mackeeper",
    "registry cleaner","speedupmypc","driver booster","driver easy",
    "regclean","winzip driver","pc speed up",
]

# ════════════════════════════════════════════════════════════
# TRADUCTIONS
# ════════════════════════════════════════════════════════════
LANGS = {
    "fr": {
        "dashboard": "Dashboard", "monitor": "Moniteur", "system": "Système",
        "clean": "Nettoyage", "security": "Sécurité", "network": "Réseau",
        "tools": "Outils Windows", "history": "Historique",
        "uninstaller": "Désinstalleur",
        "health": "Score de santé", "calc_health": "🧮  Calculer santé",
        "quick_actions": "⚡  Actions rapides", "alerts": "🔔  Alertes système",
        "no_alert": "✅  Aucune alerte — PC en bonne santé",
        "emergency": "MODE URGENCE", "settings": "⚙️  Paramètres",
        "about": "ℹ️  À propos", "save": "💾  Sauvegarder",
        "close": "✕  Fermer", "launch": "▶  Lancer", "open": "▶  Ouvrir",
        "result_console": "CONSOLE DE RÉSULTATS",
        "save_log": "Sauvegarder", "clear": "Effacer",
        "theme_light": "☀️  Clair", "theme_dark": "🌙  Sombre",
        "ready": "Prêt", "done": "✔  Terminé !",
        "repair_all": "▶  Tout réparer maintenant",
        "scan_now": "🔍  Scanner maintenant",
        "bloat_title": "🕵️  Détection bloatware",
        "pdf_report": "📄  Exporter en PDF",
        "refresh": "🔄  Actualiser",
        "kill_proc": "✖",
        "sort_by": "Trier par :",
        "filter": "Filtrer :",
        "auto_refresh": "Auto-refresh",
        "confirm_title": "Confirmation",
        "confirm_clean_temp": "Supprimer tous les fichiers temporaires ?\nCette action est irréversible.",
        "confirm_recycle": "Vider définitivement la corbeille ?\nCette action est irréversible.",
        "confirm_chkdsk": "Lancer la vérification disque ?\nLe PC devra peut-être redémarrer.",
        "confirm_restore": "Supprimer les anciens points de restauration ?\nSeul le dernier sera conservé.",
        "confirm_repair": "Lancer la réparation complète ?\n(Temp + Corbeille + DNS + SFC + DISM)\nCela peut prendre plusieurs minutes.",
        "confirm_emergency": "⚠️  Activer le MODE URGENCE ?\nDes processus gourmands seront fermés de force.",
        "confirm_winget": "Mettre à jour TOUS les logiciels ?\nCela peut prendre plusieurs minutes.",
        "warn_wifi": "⚠️  Les mots de passe WiFi s'affichent en clair.\nAssurez-vous qu'aucun tiers ne voit votre écran.",
    },
    "en": {
        "dashboard": "Dashboard", "monitor": "Monitor", "system": "System",
        "clean": "Cleaning", "security": "Security", "network": "Network",
        "tools": "Windows Tools", "history": "History",
        "uninstaller": "Uninstaller",
        "health": "PC Health Score", "calc_health": "🧮  Calculate health",
        "quick_actions": "⚡  Quick actions", "alerts": "🔔  System alerts",
        "no_alert": "✅  No alerts — PC is healthy",
        "emergency": "EMERGENCY MODE", "settings": "⚙️  Settings",
        "about": "ℹ️  About", "save": "💾  Save",
        "close": "✕  Close", "launch": "▶  Launch", "open": "▶  Open",
        "result_console": "RESULTS CONSOLE",
        "save_log": "Save log", "clear": "Clear",
        "theme_light": "☀️  Light", "theme_dark": "🌙  Dark",
        "ready": "Ready", "done": "✔  Done!",
        "repair_all": "▶  Fix everything now",
        "scan_now": "🔍  Scan now",
        "bloat_title": "🕵️  Bloatware detection",
        "pdf_report": "📄  Export as PDF",
        "refresh": "🔄  Refresh",
        "kill_proc": "✖",
        "sort_by": "Sort by:",
        "filter": "Filter:",
        "auto_refresh": "Auto-refresh",
        "confirm_title": "Confirmation",
        "confirm_clean_temp": "Delete all temporary files?\nThis action cannot be undone.",
        "confirm_recycle": "Empty the recycle bin permanently?\nThis action cannot be undone.",
        "confirm_chkdsk": "Run disk check?\nThe PC may need to restart.",
        "confirm_restore": "Delete old restore points?\nOnly the latest will be kept.",
        "confirm_repair": "Run full repair?\n(Temp + Recycle + DNS + SFC + DISM)\nThis may take several minutes.",
        "confirm_emergency": "⚠️  Activate EMERGENCY MODE?\nHigh-usage processes will be force-closed.",
        "confirm_winget": "Update ALL software?\nThis may take several minutes.",
        "warn_wifi": "⚠️  WiFi passwords will be shown in plain text.\nMake sure no one else can see your screen.",
    }
}

ACCENT_COLORS = {
    "Bleu":   "#2196f3",
    "Vert":   "#4caf50",
    "Violet": "#9c27b0",
    "Orange": "#ff9800",
    "Cyan":   "#00bcd4",
    "Rouge":  "#f44336",
    "Rose":   "#e91e63",
    "Jaune":  "#ffc107",
}

# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════
def ensure_dir():
    os.makedirs(APP_DIR, exist_ok=True)

def T(key, settings):
    lang = settings.get("lang", "fr")
    return LANGS.get(lang, LANGS["fr"]).get(key, LANGS["fr"].get(key, key))

def load_settings():
    ensure_dir()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            s = json.load(f)
        for k, v in DEFAULT_SETTINGS.items():
            s.setdefault(k, v)
        return s
    except Exception:
        return dict(DEFAULT_SETTINGS)

def save_settings(s):
    ensure_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)

def get_theme_colors(theme_name):
    t = THEMES.get(theme_name, THEMES["dark"])
    return t["BG"], t["SURFACE"], t["RAISED"], t["CARD"], t["BORDER"], t["TEXT"], t["MUTED"]

def hex_to_rgb(hex_color):
    """Convertit #rrggbb en tuple (r, g, b). Retourne (33, 150, 243) par défaut."""
    try:
        h = hex_color.lstrip("#")
        if len(h) != 6:
            raise ValueError
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except Exception:
        return 33, 150, 243

def darken_hex(hex_color, factor=0.7):
    """Assombrit une couleur hex d'un facteur donné."""
    r, g, b = hex_to_rgb(hex_color)
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"

def make_alpha_hex(hex_color, alpha_pct=40):
    """Retourne hex + suffixe alpha approximé pour tk Canvas (simule transparence)."""
    try:
        h = hex_color.lstrip("#")
        if len(h) != 6:
            return hex_color
        # Mélange avec noir (0,0,0) selon alpha
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        a = alpha_pct / 100
        r2 = int(r * a); g2 = int(g * a); b2 = int(b * a)
        return f"#{r2:02x}{g2:02x}{b2:02x}"
    except Exception:
        return hex_color

def toast_notify(title, message):
    """Notification Windows native via PowerShell."""
    try:
        script = (
            f"Add-Type -AssemblyName System.Windows.Forms; "
            f"$n = New-Object System.Windows.Forms.NotifyIcon; "
            f"$n.Icon = [System.Drawing.SystemIcons]::Information; "
            f"$n.Visible = $true; "
            f"$n.ShowBalloonTip(4000, '{title}', '{message}', "
            f"[System.Windows.Forms.ToolTipIcon]::Warning); "
            f"Start-Sleep 5; $n.Dispose()"
        )
        subprocess.Popen(
            f'PowerShell -WindowStyle Hidden -Command "{script}"',
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


# ════════════════════════════════════════════════════════════
# SPLASH SCREEN
# ════════════════════════════════════════════════════════════
class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        w, h = 460, 260
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.configure(bg="#0a0a0a")
        self.lift()
        self.attributes("-topmost", True)

        border = tk.Frame(self, bg=BLUE, bd=0)
        border.place(x=0, y=0, width=w, height=3)

        tk.Label(self, text="💻", font=("Arial", 48), bg="#0a0a0a", fg=BLUE).place(x=w//2-32, y=30)
        tk.Label(self, text="PC Tool", font=("Arial", 28, "bold"),
                 bg="#0a0a0a", fg="#f0f0f0").place(x=w//2-60, y=100)
        tk.Label(self, text=f"Version {VERSION}  —  Outil informatique complet",
                 font=("Arial", 11), bg="#0a0a0a", fg="#666666").place(x=w//2-155, y=142)

        self._status = tk.Label(self, text="Démarrage…",
                                font=("Arial", 10), bg="#0a0a0a", fg="#444444")
        self._status.place(x=w//2-40, y=200)

        self._bar_bg = tk.Frame(self, bg="#1e1e1e", height=4)
        self._bar_bg.place(x=40, y=228, width=w-80, height=4)
        self._bar = tk.Frame(self, bg=BLUE, height=4)
        self._bar.place(x=40, y=228, width=0, height=4)

        self._progress = 0
        self._animate()

    def set_status(self, text):
        self._status.configure(text=text)

    def _animate(self):
        if self._progress < 380:
            self._progress += 6
            self._bar.place(x=40, y=228, width=self._progress, height=4)
            self.after(12, self._animate)

    def set_done(self):
        self._bar.place(x=40, y=228, width=380, height=4)


# ════════════════════════════════════════════════════════════
# APPLICATION PRINCIPALE
# ════════════════════════════════════════════════════════════
class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        ensure_dir()

        self.settings = load_settings()
        self._apply_theme(self.settings["theme"], init=True)

        # ── State
        self._net_prev       = psutil.net_io_counters()
        self._cpu_history    = deque([0]*60, maxlen=60)
        self._ram_history    = deque([0]*60, maxlen=60)
        self._net_history    = deque([0]*60, maxlen=60)
        self._alert_shown    = set()
        self._health_score   = 100
        self._proc_running   = False
        self._sched_thread   = None
        self._cancel_scan    = False   # flag d'annulation pour scans longs
        self._about_open     = False

        self.withdraw()
        self.title(f"{APP_NAME}  v{VERSION}")
        self.geometry("1420x960")
        self.resizable(True, True)

        splash = SplashScreen(self)
        self.update()

        steps = [
            ("Chargement de l'interface…",   0.3),
            ("Initialisation des modules…",  0.4),
            ("Lecture des paramètres…",      0.2),
            ("Prêt !",                       0.1),
        ]
        for msg, delay in steps:
            splash.set_status(msg)
            self.update()
            time.sleep(delay)

        splash.set_done()
        self.update()
        time.sleep(0.3)
        splash.destroy()

        self._build()
        self.deiconify()
        self._tick()
        self._start_scheduler()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ────────────────────────────────────────────────────────
    def _apply_theme(self, theme_name, init=False):
        self.settings["theme"] = theme_name
        ctk.set_appearance_mode("dark" if theme_name == "dark" else "light")
        self.BG, self.SURFACE, self.RAISED, self.CARD, self.BORDER, self.TEXT, self.MUTED = \
            get_theme_colors(theme_name)
        global BLUE, BLUE2
        BLUE  = self.settings.get("accent", "#2196f3")
        BLUE2 = darken_hex(BLUE, 0.7)
        if not init:
            self.configure(fg_color=self.BG)

    def _t(self, key):
        return T(key, self.settings)

    # ────────────────────────────────────────────────────────
    # CONFIRMATION DIALOG
    # ────────────────────────────────────────────────────────
    def _confirm(self, message, title=None):
        """Boîte de confirmation avant toute action destructive."""
        title = title or self._t("confirm_title")
        return messagebox.askyesno(title, message, icon="warning", parent=self)

    def _log_exc(self, context, exc):
        """Log une exception avec contexte plutôt que de l'avaler silencieusement."""
        self._log(f"   ✖  [{context}] {type(exc).__name__}: {exc}")

    # ────────────────────────────────────────────────────────
    def _on_close(self):
        if self.settings.get("tray_enabled", False) and TRAY_AVAILABLE:
            self.withdraw()
            self._start_tray_icon()
        else:
            self.quit()
            self.destroy()

    def _start_tray_icon(self):
        def make_icon():
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([4, 4, 60, 60], fill="#2196f3")
            draw.rectangle([16, 18, 48, 38], fill="white")
            draw.rectangle([28, 38, 36, 44], fill="white")
            draw.rectangle([22, 44, 42, 46], fill="white")
            return img

        def on_show(icon, item):
            icon.stop()
            self._tray_icon = None
            self.after(0, self.deiconify)
            self.after(0, self.lift)
            self.after(0, self.focus_force)

        def on_quit(icon, item):
            icon.stop()
            self._tray_icon = None
            self.after(0, self.quit)
            self.after(0, self.destroy)

        lang = self.settings.get("lang", "fr")
        lbl_show = "Ouvrir PC Tool" if lang == "fr" else "Open PC Tool"
        lbl_quit = "Quitter" if lang == "fr" else "Quit"

        menu = pystray.Menu(
            pystray.MenuItem(lbl_show, on_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lbl_quit, on_quit),
        )
        icon = pystray.Icon("pctool", make_icon(), f"PC Tool v{VERSION}", menu)
        self._tray_icon = icon
        t = threading.Thread(target=icon.run, daemon=True)
        t.start()

    # ════════════════════════════════════════════════════════
    # BUILD UI
    # ════════════════════════════════════════════════════════
    def _build(self):
        # ── EN-TÊTE
        hdr = ctk.CTkFrame(self, fg_color=self.SURFACE,
                           border_width=1, border_color=self.BORDER, corner_radius=0)
        hdr.pack(fill="x")
        ih = ctk.CTkFrame(hdr, fg_color="transparent")
        ih.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(ih, text="💻  PC Tool", font=FONT_TITLE, text_color=self.TEXT).pack(side="left")
        ctk.CTkLabel(ih, text=f"v{VERSION}", font=FONT_SMALL, text_color=BLUE).pack(
            side="left", padx=(6,0), pady=(8,0))

        hdr_right = ctk.CTkFrame(ih, fg_color="transparent")
        hdr_right.pack(side="right")

        self.theme_btn = ctk.CTkButton(
            hdr_right,
            text=self._t("theme_light") if self.settings["theme"]=="dark" else self._t("theme_dark"),
            command=self._toggle_theme,
            fg_color=self.RAISED, hover_color=self.CARD, text_color=self.TEXT,
            font=FONT_SMALL, corner_radius=8, height=30, width=100,
            border_width=1, border_color=self.BORDER)
        self.theme_btn.pack(side="left", padx=(0,8))

        ctk.CTkButton(hdr_right, text=self._t("settings"),
                      command=self._open_settings,
                      fg_color=self.RAISED, hover_color=self.CARD, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=120,
                      border_width=1, border_color=self.BORDER).pack(side="left", padx=(0,8))

        ctk.CTkButton(hdr_right, text=self._t("about"),
                      command=self._open_about,
                      fg_color=self.RAISED, hover_color=self.CARD, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=110,
                      border_width=1, border_color=self.BORDER).pack(side="left", padx=(0,8))

        self.update_btn = ctk.CTkButton(
            hdr_right, text="🔍  Mises à jour",
            command=lambda: self.do_check_update(btn=self.update_btn),
            fg_color=self.RAISED, hover_color=self.CARD, text_color=self.MUTED,
            font=FONT_SMALL, corner_radius=8, height=30, width=130,
            border_width=1, border_color=self.BORDER)
        self.update_btn.pack(side="left", padx=(0,16))

        stats_row = ctk.CTkFrame(hdr_right, fg_color="transparent")
        stats_row.pack(side="left")
        self.lbl_score = ctk.CTkLabel(stats_row, text="Santé ―/100",
                                       font=("Arial",12,"bold"), text_color=GREEN, width=130)
        self.lbl_cpu   = ctk.CTkLabel(stats_row, text="CPU  0%",
                                       font=FONT_SMALL, text_color=self.MUTED, width=90)
        self.lbl_ram   = ctk.CTkLabel(stats_row, text="RAM  0%",
                                       font=FONT_SMALL, text_color=self.MUTED, width=90)
        self.lbl_net   = ctk.CTkLabel(stats_row, text="NET  0 KB/s",
                                       font=FONT_SMALL, text_color=self.MUTED, width=110)
        self.lbl_time  = ctk.CTkLabel(stats_row, text="00:00:00",
                                       font=FONT_SMALL, text_color=self.MUTED, width=76)
        for w in (self.lbl_score, self.lbl_cpu, self.lbl_ram, self.lbl_net, self.lbl_time):
            w.pack(side="left", padx=6)

        ctk.CTkFrame(self, height=1, fg_color=self.BORDER, corner_radius=0).pack(fill="x")

        # ── CORPS
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(body, fg_color=self.SURFACE, width=215,
                                    corner_radius=0, border_width=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._pages    = {}
        self._nav_btns = {}
        self._current  = None

        content_area = ctk.CTkFrame(body, fg_color="transparent")
        content_area.pack(side="left", fill="both", expand=True)

        # ── CONSOLE
        out_frame = ctk.CTkFrame(content_area, fg_color=self.SURFACE,
                                 border_width=1, border_color=self.BORDER, corner_radius=0)
        out_frame.pack(side="bottom", fill="x")
        out_top = ctk.CTkFrame(out_frame, fg_color="transparent")
        out_top.pack(fill="x", padx=12, pady=(8,2))
        ctk.CTkLabel(out_top, text=f"📋  {self._t('result_console')}",
                     font=("Arial",12,"bold"), text_color=self.MUTED).pack(side="left")
        br = ctk.CTkFrame(out_top, fg_color="transparent")
        br.pack(side="right")
        for txt, cmd in [(f"💾  {self._t('save_log')}", self._save_log),
                         (f"🗑  {self._t('clear')}", self._clear)]:
            ctk.CTkButton(br, text=txt, command=cmd,
                          fg_color=self.RAISED, hover_color=self.CARD, text_color=self.MUTED,
                          font=FONT_TINY, corner_radius=6, height=24,
                          border_width=1, border_color=self.BORDER).pack(side="left", padx=(0,6))
        self.output = ctk.CTkTextbox(out_frame, height=280, fg_color=self.RAISED,
                                      text_color=self.TEXT, font=FONT_MONO,
                                      border_color=self.BORDER, border_width=1, corner_radius=8)
        self.output.pack(fill="x", padx=12, pady=(0,10))

        self.page_area = ctk.CTkFrame(content_area, fg_color="transparent")
        self.page_area.pack(fill="both", expand=True)

        # Build pages
        self._build_page_dashboard()
        self._build_page_moniteur()
        self._build_page_systeme()
        self._build_page_nettoyage()
        self._build_page_securite()
        self._build_page_reseau()
        self._build_page_outils()
        self._build_page_desinstalleur()
        self._build_page_rapport()
        self._build_page_historique()

        # Sidebar nav
        ctk.CTkLabel(self.sidebar, text="NAVIGATION",
                     font=FONT_TINY, text_color=self.MUTED).pack(pady=(18,6))

        lang_pages = {
            "Dashboard":      (self._t("dashboard"), "📊"),
            "Moniteur":       (self._t("monitor"),   "📈"),
            "Système":        (self._t("system"),    "🖥"),
            "Nettoyage":      (self._t("clean"),     "🧹"),
            "Sécurité":       (self._t("security"),  "🔒"),
            "Réseau":         (self._t("network"),   "🌐"),
            "Outils Windows": (self._t("tools"),     "🔧"),
            "Désinstalleur":  (self._t("uninstaller"),"🗑"),
            "Rapport":        ("Rapport",             "📄"),
            "Historique":     (self._t("history"),   "📋"),
        }
        for name, (label, icon) in lang_pages.items():
            b = ctk.CTkButton(
                self.sidebar, text=f"  {icon}  {label}",
                command=lambda n=name: self._show(n),
                fg_color="transparent", hover_color=self.RAISED,
                text_color=self.MUTED, font=FONT_BODY,
                anchor="w", corner_radius=8, height=44, border_width=0)
            b.pack(fill="x", padx=8, pady=2)
            self._nav_btns[name] = b

        ctk.CTkFrame(self.sidebar, height=1, fg_color=self.BORDER).pack(fill="x", pady=8)
        ctk.CTkButton(self.sidebar, text=f"🚨  {self._t('emergency')}",
                      command=self.do_mode_urgence,
                      fg_color=RED2, hover_color=RED, text_color=self.TEXT,
                      font=("Arial",12,"bold"), corner_radius=8, height=44).pack(
                          fill="x", padx=8, pady=(0,8))

        # ── Raccourcis clavier
        self.bind("<Control-s>", lambda e: self._save_log())
        self.bind("<Control-r>", lambda e: self._refresh_proc_table() if self._current == "Moniteur" else None)
        self.bind("<F5>",        lambda e: self._refresh_proc_table() if self._current == "Moniteur" else None)
        self.bind("<Control-l>", lambda e: self._clear())
        self.bind("<Escape>",    lambda e: self._close_about_if_open())

        start_page = self.settings.get("startup_page", "Dashboard")
        self._show(start_page if start_page in self._pages else "Dashboard")

    def _close_about_if_open(self):
        if self._about_open:
            self._about_open = False
            try:
                for widget in self.winfo_children():
                    if isinstance(widget, ctk.CTkFrame) and widget.winfo_width() < 500:
                        widget.destroy()
            except Exception:
                pass

    # ── NAVIGATION
    def _show(self, name):
        if self._current:
            self._pages[self._current].pack_forget()
            self._nav_btns[self._current].configure(
                fg_color="transparent", text_color=self.MUTED)
        self._pages[name].pack(fill="both", expand=True)
        self._nav_btns[name].configure(fg_color=self.RAISED, text_color=self.TEXT)
        self._current = name
        if name == "Moniteur" and not self._proc_running:
            self._start_proc_monitor()

    # ── LOG
    def _log(self, msg):
        ts   = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}]  {msg}\n"
        self.output.insert("end", line)
        self.output.see("end")
        try:
            ensure_dir()
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass
        if self._current == "Historique":
            self._refresh_historique()

    def _clear(self):
        self.output.delete("0.0", "end")

    def _save_log(self):
        try:
            content = self.output.get("0.0", "end")
            desktop = os.path.join(os.environ.get("USERPROFILE",""), "Desktop")
            fname   = f"pctool_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            fpath   = os.path.join(desktop, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            self._log(f"✔  Log sauvegardé : {fpath}")
        except Exception as e:
            self._log_exc("_save_log", e)

    def _run(self, cmd, label):
        def t():
            self._log(f"▶  {label}")
            try:
                proc = subprocess.Popen(cmd, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in proc.stdout:
                    d = line.decode("cp850", errors="replace").rstrip()
                    if d.strip(): self._log(f"   {d}")
                proc.wait()
                self._log(f"✔  {label}  —  terminé\n")
            except Exception as e:
                self._log_exc(label, e)
        threading.Thread(target=t, daemon=True).start()

    def _open(self, cmd, label):
        self._log(f"▶  Ouverture : {label}")
        os.system(f"start {cmd}")

    def _run_sync(self, cmd, label):
        self._log(f"   ▷ {label}…")
        try:
            proc = subprocess.Popen(cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in proc.stdout:
                d = line.decode("cp850", errors="replace").rstrip()
                if d.strip(): self._log(f"      {d}")
            proc.wait()
        except Exception as e:
            self._log_exc(label, e)

    # ════════════════════════════════════════════════════════
    # THÈME
    # ════════════════════════════════════════════════════════
    def _toggle_theme(self):
        new = "light" if self.settings["theme"] == "dark" else "dark"
        self._apply_theme(new)
        save_settings(self.settings)
        self._rebuild_ui()

    def _rebuild_ui(self):
        self._apply_theme(self.settings["theme"])
        self._cancel_scan = True   # annuler les scans en cours
        for widget in self.winfo_children():
            widget.destroy()
        self._pages = {}; self._nav_btns = {}; self._current = None
        self._proc_running = False
        self._cancel_scan  = False
        self._build()

    # ════════════════════════════════════════════════════════
    # PARAMÈTRES
    # ════════════════════════════════════════════════════════
    def _open_settings(self):
        from tkinter import ttk

        win = tk.Toplevel(self)
        win.title("Paramètres — PC Tool")
        win.geometry("520x800")
        win.configure(bg="#111111")
        win.resizable(True, True)
        win.transient(self)
        win.focus_force()
        win.lift()
        win.protocol("WM_DELETE_WINDOW", win.destroy)

        hdr = tk.Frame(win, bg="#1a1a1a", height=50)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚙️  Paramètres", bg="#1a1a1a", fg="#f0f0f0",
                 font=("Arial",13,"bold")).pack(side="left", padx=16)
        tk.Button(hdr, text="✕  Fermer", command=win.destroy,
                  bg="#c62828", fg="white", font=("Arial",11,"bold"),
                  relief="flat", bd=0, padx=12, pady=4,
                  activebackground="#f44336", cursor="hand2").pack(side="right", padx=10, pady=8)

        def do_save():
            old_lang   = self.settings.get("lang", "fr")
            old_accent = self.settings.get("accent", "#2196f3")
            self.settings["sched_enabled"] = sched_var.get()
            self.settings["sched_day"]     = day_var.get()
            self.settings["sched_hour"]    = hour_var.get()
            self.settings["tray_enabled"]  = tray_var.get()
            self.settings["startup_page"]  = startup_var.get()
            self.settings["dns_primary"]   = dns_p.get().strip()
            self.settings["dns_secondary"] = dns_s.get().strip()
            self.settings["lang"]          = lang_var.get()
            self.settings["accent"]        = accent_var.get()
            self.settings["refresh_rate"]  = refresh_var.get()
            save_settings(self.settings)
            self._start_scheduler()
            self._log("✔  Paramètres sauvegardés\n")
            win.destroy()
            needs_rebuild = (lang_var.get() != old_lang or accent_var.get() != old_accent)
            if needs_rebuild:
                self.after(100, self._rebuild_ui)

        save_bar = tk.Frame(win, bg="#1b5e20", height=46)
        save_bar.pack(fill="x", side="top")
        save_bar.pack_propagate(False)
        tk.Button(save_bar, text="💾  Sauvegarder les paramètres",
                  command=do_save,
                  bg="#1b5e20", fg="white", font=("Arial",12,"bold"),
                  relief="flat", bd=0, activebackground="#2e7d32",
                  cursor="hand2").pack(fill="both", expand=True)

        mid = tk.Frame(win, bg="#111111")
        mid.pack(fill="both", expand=True)
        vsb = tk.Scrollbar(mid, orient="vertical", bg="#222222")
        vsb.pack(side="right", fill="y")
        canvas = tk.Canvas(mid, bg="#111111", highlightthickness=0, yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.config(command=canvas.yview)
        inner = tk.Frame(canvas, bg="#111111")
        cw = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_inner_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_configure(e):
            canvas.itemconfig(cw, width=e.width)
        inner.bind("<Configure>", on_inner_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        win.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        def section(text):
            tk.Label(inner, text=text, bg="#111111", fg="#2196f3",
                     font=("Arial",12,"bold")).pack(anchor="w", padx=16, pady=(16,2))
            tk.Frame(inner, bg="#333333", height=1).pack(fill="x", padx=16, pady=(0,6))

        def entry_field(parent, label, default):
            tk.Label(parent, text=label, bg="#1e1e1e", fg="#999999",
                     font=("Arial",10)).pack(anchor="w", padx=10, pady=(6,2))
            e = tk.Entry(parent, bg="#2a2a2a", fg="#f0f0f0",
                         insertbackground="#f0f0f0", font=("Arial",11),
                         relief="flat", bd=6, highlightthickness=1,
                         highlightbackground="#333333", highlightcolor="#2196f3")
            e.insert(0, default)
            e.pack(fill="x", padx=10, pady=(0,4))
            return e

        def slider_field(parent, label, key, from_, to_):
            f = tk.Frame(parent, bg="#1e1e1e")
            f.pack(fill="x", padx=10, pady=4)
            top = tk.Frame(f, bg="#1e1e1e")
            top.pack(fill="x", padx=8, pady=(6,0))
            tk.Label(top, text=label, bg="#1e1e1e", fg="#e0e0e0",
                     font=("Arial",11)).pack(side="left")
            vv = tk.StringVar(value=str(self.settings[key]))
            tk.Label(top, textvariable=vv, bg="#1e1e1e", fg="#2196f3",
                     font=("Arial",11,"bold"), width=4).pack(side="right")
            def on_slide(v, k=key, var=vv):
                self.settings[k] = int(float(v))
                var.set(str(int(float(v))))
            tk.Scale(f, from_=from_, to=to_, orient="horizontal",
                     command=on_slide, bg="#1e1e1e", fg="#f0f0f0",
                     troughcolor="#333333", highlightthickness=0,
                     activebackground="#2196f3", showvalue=False,
                     sliderlength=20, bd=0, width=14).pack(fill="x", padx=8, pady=(2,8))

        section("🔔  Seuils d'alertes")
        alert_f = tk.Frame(inner, bg="#1e1e1e")
        alert_f.pack(fill="x", padx=16, pady=4)
        slider_field(alert_f, "Alerte CPU (%)",    "alert_cpu",    50, 99)
        slider_field(alert_f, "Alerte RAM (%)",    "alert_ram",    50, 99)
        slider_field(alert_f, "Alerte disque (%)","alert_disk",   50, 99)
        slider_field(alert_f, "Alerte uptime (h)","alert_uptime", 6, 168)

        section("🌐  DNS par défaut")
        dns_f = tk.Frame(inner, bg="#1e1e1e")
        dns_f.pack(fill="x", padx=16, pady=4)
        dns_p = entry_field(dns_f, "DNS primaire",   self.settings["dns_primary"])
        dns_s = entry_field(dns_f, "DNS secondaire", self.settings["dns_secondary"])

        section("⏰  Planificateur de nettoyage")
        sched_f = tk.Frame(inner, bg="#1e1e1e")
        sched_f.pack(fill="x", padx=16, pady=4)
        sched_var = tk.BooleanVar(value=self.settings["sched_enabled"])
        tk.Checkbutton(sched_f, text="  Activer le nettoyage automatique",
                       variable=sched_var, bg="#1e1e1e", fg="#f0f0f0",
                       selectcolor="#2a2a2a", activebackground="#1e1e1e",
                       font=("Arial",11), cursor="hand2").pack(anchor="w", padx=8, pady=6)
        sr = tk.Frame(sched_f, bg="#1e1e1e")
        sr.pack(fill="x", padx=8, pady=(0,8))
        tk.Label(sr, text="Jour :", bg="#1e1e1e", fg="#999999",
                 font=("Arial",10)).pack(side="left")
        day_var = tk.StringVar(value=self.settings["sched_day"])
        ttk.Combobox(sr, textvariable=day_var, width=11, state="readonly",
                     values=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
                     ).pack(side="left", padx=(4,14))
        tk.Label(sr, text="Heure :", bg="#1e1e1e", fg="#999999",
                 font=("Arial",10)).pack(side="left")
        hour_var = tk.StringVar(value=self.settings["sched_hour"])
        ttk.Combobox(sr, textvariable=hour_var, width=7, state="readonly",
                     values=["06:00","07:00","08:00","09:00","12:00","18:00","22:00"]
                     ).pack(side="left", padx=(4,0))

        section("⚙️  Général")
        gen_f = tk.Frame(inner, bg="#1e1e1e")
        gen_f.pack(fill="x", padx=16, pady=4)
        tray_var = tk.BooleanVar(value=self.settings["tray_enabled"])
        tk.Checkbutton(gen_f, text="  Minimiser dans la barre des tâches",
                       variable=tray_var, bg="#1e1e1e", fg="#f0f0f0",
                       selectcolor="#2a2a2a", activebackground="#1e1e1e",
                       font=("Arial",11), cursor="hand2").pack(anchor="w", padx=8, pady=6)
        tk.Label(gen_f, text="Page de démarrage :", bg="#1e1e1e", fg="#999999",
                 font=("Arial",10)).pack(anchor="w", padx=8, pady=(4,2))
        startup_var = tk.StringVar(value=self.settings["startup_page"])
        ttk.Combobox(gen_f, textvariable=startup_var, width=24, state="readonly",
                     values=["Dashboard","Moniteur","Système","Nettoyage",
                             "Sécurité","Réseau","Outils Windows","Désinstalleur","Rapport","Historique"]
                     ).pack(anchor="w", padx=8, pady=(0,8))

        section("🎨  Apparence")
        lang_f = tk.Frame(inner, bg="#1e1e1e")
        lang_f.pack(fill="x", padx=16, pady=4)
        tk.Label(lang_f, text="Langue / Language", bg="#1e1e1e", fg="#cccccc",
                 font=("Arial",11,"bold")).pack(anchor="w", padx=8, pady=(8,4))
        lang_var = tk.StringVar(value=self.settings.get("lang","fr"))
        lang_row = tk.Frame(lang_f, bg="#1e1e1e")
        lang_row.pack(anchor="w", padx=8)
        for code, flag, label in [("fr","🇫🇷","  Français"), ("en","🇬🇧","  English")]:
            tk.Radiobutton(lang_row, text=f"{flag}{label}", variable=lang_var, value=code,
                           bg="#1e1e1e", fg="#f0f0f0", selectcolor="#2a2a2a",
                           activebackground="#1e1e1e", font=("Arial",11),
                           cursor="hand2").pack(side="left", padx=(0,20), pady=4)

        tk.Label(lang_f, text="Couleur d'accentuation", bg="#1e1e1e", fg="#cccccc",
                 font=("Arial",11,"bold")).pack(anchor="w", padx=8, pady=(12,6))
        accent_var = tk.StringVar(value=self.settings.get("accent","#2196f3"))
        accent_sel_lbl = tk.Label(lang_f,
            text=f"  Sélectionné : {self.settings.get('accent','#2196f3')}",
            bg="#1e1e1e", fg="#888888", font=("Arial",10))
        accent_sel_lbl.pack(anchor="w", padx=8, pady=(0,6))

        accent_btns = {}
        colors_row1 = tk.Frame(lang_f, bg="#1e1e1e")
        colors_row1.pack(anchor="w", padx=8, pady=(0,4))
        colors_row2 = tk.Frame(lang_f, bg="#1e1e1e")
        colors_row2.pack(anchor="w", padx=8, pady=(0,8))

        items = list(ACCENT_COLORS.items())
        for i, (name, hex_col) in enumerate(items):
            row = colors_row1 if i < 4 else colors_row2
            cur = self.settings.get("accent","#2196f3")
            relief = "solid" if hex_col == cur else "flat"
            def make_select(h=hex_col, n=name):
                accent_var.set(h)
                accent_sel_lbl.configure(text=f"  Sélectionné : {h}", fg=h)
                for nn, bb in accent_btns.items():
                    bb.configure(relief="flat", bd=2)
                accent_btns[n].configure(relief="solid", bd=3)
            btn = tk.Button(row, bg=hex_col, width=6, height=2,
                           relief=relief, bd=3 if relief=="solid" else 2,
                           cursor="hand2", activebackground=hex_col,
                           command=make_select)
            btn.pack(side="left", padx=3)
            accent_btns[name] = btn

        tk.Label(lang_f, text="Fréquence actualisation moniteur (secondes)",
                 bg="#1e1e1e", fg="#cccccc", font=("Arial",11,"bold")).pack(
                     anchor="w", padx=8, pady=(12,4))
        refresh_var = tk.IntVar(value=self.settings.get("refresh_rate", 2))
        rr_lbl_var = tk.StringVar(value=f"{self.settings.get('refresh_rate',2)}s")
        rr_top = tk.Frame(lang_f, bg="#1e1e1e")
        rr_top.pack(fill="x", padx=8)
        tk.Label(rr_top, textvariable=rr_lbl_var, bg="#1e1e1e", fg="#2196f3",
                 font=("Arial",12,"bold")).pack(side="right")
        def on_refresh(v):
            refresh_var.set(int(float(v)))
            rr_lbl_var.set(f"{int(float(v))}s")
        tk.Scale(lang_f, from_=1, to=10, orient="horizontal",
                 command=on_refresh, bg="#1e1e1e", fg="#f0f0f0",
                 troughcolor="#333333", highlightthickness=0,
                 activebackground="#2196f3", showvalue=False,
                 sliderlength=20, bd=0, width=14).pack(fill="x", padx=8, pady=(0,12))

        # ══ SECTION MISES À JOUR
        section("🔄  Mises à jour")
        upd_f = tk.Frame(inner, bg="#1e1e1e")
        upd_f.pack(fill="x", padx=16, pady=4)
        tk.Label(upd_f,
                 text=f"Version actuelle : v{VERSION}   —   Repo : github.com/{GITHUB_REPO}",
                 bg="#1e1e1e", fg="#888888", font=("Arial",10)).pack(anchor="w", padx=8, pady=(8,6))

        upd_state = {"btn": None}
        def do_upd_check():
            b = upd_state["btn"]
            if b: b.configure(text="🔄  Vérification…", state="disabled")
            class BtnProxy:
                def configure(self_, **kw):
                    if b is None: return
                    if "text"  in kw: b.configure(text=kw["text"])
                    if "state" in kw: b.configure(state=kw["state"])
            self.do_check_update(btn=BtnProxy())

        upd_btn = tk.Button(upd_f, text="🔍  Vérifier les mises à jour",
                            command=do_upd_check,
                            bg="#1565c0", fg="white", font=("Arial",11,"bold"),
                            relief="flat", bd=0, padx=14, pady=8,
                            activebackground="#2196f3", cursor="hand2")
        upd_btn.pack(anchor="w", padx=8, pady=(0,12))
        upd_state["btn"] = upd_btn

        tk.Frame(inner, bg="#111111", height=20).pack()

    def _open_about(self):
        if self._about_open:
            return
        self._about_open = True

        overlay = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=12,
                               border_width=2, border_color=BLUE)
        overlay.place(relx=0.5, rely=0.5, anchor="center", width=420, height=340)

        def close_about():
            overlay.destroy()
            self._about_open = False

        ctk.CTkLabel(overlay, text="💻", font=("Arial", 48)).pack(pady=(20,4))
        ctk.CTkLabel(overlay, text=f"PC Tool  v{VERSION}",
                     font=("Arial", 20, "bold"), text_color=self.TEXT).pack()
        ctk.CTkLabel(overlay, text="Outil d'entretien informatique complet",
                     font=FONT_SMALL, text_color=self.MUTED).pack(pady=(4,12))

        info = ctk.CTkFrame(overlay, fg_color=self.RAISED, corner_radius=10,
                            border_width=1, border_color=self.BORDER)
        info.pack(fill="x", padx=30, pady=4)
        for label, val in [
            ("Version",    VERSION),
            ("Python",     sys.version.split()[0]),
            ("Config",     APP_DIR),
            ("PDF",        "✔ disponible" if PDF_AVAILABLE else "✖ pip install reportlab"),
        ]:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=label, font=FONT_SMALL,
                         text_color=self.MUTED, width=80, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=FONT_SMALL,
                         text_color=self.TEXT, anchor="w").pack(side="left")

        ctk.CTkButton(overlay, text="Fermer  [Echap]", command=close_about,
                      fg_color=self.RAISED, hover_color=self.BORDER, text_color=self.MUTED,
                      font=FONT_SMALL, corner_radius=8, height=34, width=140,
                      border_width=1, border_color=self.BORDER).pack(pady=16)

    # ════════════════════════════════════════════════════════
    # PLANIFICATEUR
    # ════════════════════════════════════════════════════════
    def _start_scheduler(self):
        if self._sched_thread and self._sched_thread.is_alive():
            return
        if not self.settings.get("sched_enabled", False):
            return
        def sched_loop():
            DAYS = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
            while True:
                now         = datetime.now()
                target_day  = self.settings.get("sched_day","Lundi")
                target_hour = self.settings.get("sched_hour","08:00")
                cur_day     = DAYS[now.weekday()]
                cur_time    = now.strftime("%H:%M")
                if cur_day == target_day and cur_time == target_hour:
                    self._log(f"⏰  Nettoyage planifié ({target_day} {target_hour})")
                    self.do_quick_clean(scheduled=True)
                    time.sleep(70)
                time.sleep(30)
        self._sched_thread = threading.Thread(target=sched_loop, daemon=True)
        self._sched_thread.start()

    # ════════════════════════════════════════════════════════
    # VÉRIFICATION DES MISES À JOUR
    # ════════════════════════════════════════════════════════
    def do_check_update(self, btn=None):
        """Vérifie si une nouvelle version est disponible sur GitHub."""
        if btn:
            btn.configure(text="🔄  Vérification…", state="disabled")

        def t():
            try:
                url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
                req = urllib.request.Request(url, headers={"User-Agent": "PCTool"})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode())

                latest_tag  = data.get("tag_name", "").lstrip("v")
                release_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                release_name = data.get("name", f"v{latest_tag}")

                # Comparaison de version (ex: "1.0" vs "1.1")
                def ver_tuple(v):
                    try: return tuple(int(x) for x in v.split("."))
                    except Exception: return (0,)

                current = ver_tuple(VERSION)
                latest  = ver_tuple(latest_tag)

                def update_ui():
                    if btn:
                        btn.configure(text="🔍  Vérifier les mises à jour", state="normal")
                    if latest > current:
                        # Nouvelle version disponible → popup
                        self._show_update_popup(latest_tag, release_name, release_url)
                    elif latest == current:
                        messagebox.showinfo(
                            "✅  PC Tool est à jour",
                            f"Vous utilisez déjà la dernière version : v{VERSION}",
                            parent=self)
                    else:
                        messagebox.showinfo(
                            "ℹ️  Version locale",
                            f"Version locale (v{VERSION}) plus récente que la release (v{latest_tag}).",
                            parent=self)

                self.after(0, update_ui)

            except urllib.error.URLError:
                def no_net():
                    if btn: btn.configure(text="🔍  Vérifier les mises à jour", state="normal")
                    messagebox.showerror(
                        "Erreur réseau",
                        "Impossible de contacter GitHub.\nVérifiez votre connexion internet.",
                        parent=self)
                self.after(0, no_net)
            except Exception as e:
                def err():
                    if btn: btn.configure(text="🔍  Vérifier les mises à jour", state="normal")
                    messagebox.showerror("Erreur", str(e), parent=self)
                self.after(0, err)

        threading.Thread(target=t, daemon=True).start()

    def _show_update_popup(self, latest_tag, release_name, release_url):
        """Popup élégant quand une mise à jour est disponible."""
        popup = ctk.CTkToplevel(self)
        popup.title("Mise à jour disponible")
        popup.geometry("440x280")
        popup.configure(fg_color=self.BG)
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()
        popup.after(100, popup.focus_force)

        # Centrer
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - 440) // 2
        y = self.winfo_y() + (self.winfo_height() - 280) // 2
        popup.geometry(f"440x280+{x}+{y}")

        # Bordure colorée en haut
        ctk.CTkFrame(popup, height=4, fg_color=GREEN, corner_radius=0).pack(fill="x")

        ctk.CTkLabel(popup, text="🎉", font=("Arial", 42)).pack(pady=(18, 4))
        ctk.CTkLabel(popup, text="Nouvelle version disponible !",
                     font=("Arial", 16, "bold"), text_color=GREEN).pack()
        ctk.CTkLabel(popup, text=f"v{VERSION}  →  v{latest_tag}   ({release_name})",
                     font=FONT_SMALL, text_color=self.MUTED).pack(pady=(4, 16))

        ctk.CTkFrame(popup, height=1, fg_color=self.BORDER).pack(fill="x", padx=30)

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(pady=20)

        def open_release():
            import webbrowser
            webbrowser.open(release_url)
            popup.destroy()

        ctk.CTkButton(btn_row, text="⬇️  Télécharger la mise à jour",
                      command=open_release,
                      fg_color=GREEN2, hover_color=GREEN, text_color=self.TEXT,
                      font=FONT_BODY, corner_radius=10, height=42, width=220).pack(side="left", padx=(0,10))
        ctk.CTkButton(btn_row, text="Plus tard",
                      command=popup.destroy,
                      fg_color=self.RAISED, hover_color=self.CARD, text_color=self.MUTED,
                      font=FONT_SMALL, corner_radius=10, height=42, width=100,
                      border_width=1, border_color=self.BORDER).pack(side="left")

    # ════════════════════════════════════════════════════════
    # PAGE  DASHBOARD
    # ════════════════════════════════════════════════════════
    def _build_page_dashboard(self):
        page = ctk.CTkScrollableFrame(self.page_area, fg_color=self.BG)
        self._pages["Dashboard"] = page

        title_row = ctk.CTkFrame(page, fg_color="transparent")
        title_row.pack(fill="x", padx=14, pady=(12,6))
        ctk.CTkLabel(title_row, text="📊  Tableau de bord",
                     font=FONT_HEAD, text_color=self.TEXT).pack(side="left")
        ctk.CTkButton(title_row, text="🧮  Calculer santé",
                      command=self._calc_health_score,
                      fg_color=GREEN2, hover_color=GREEN, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=150).pack(side="right")

        score_card = ctk.CTkFrame(page, fg_color=self.RAISED, corner_radius=12,
                                  border_width=1, border_color=self.BORDER)
        score_card.pack(fill="x", padx=14, pady=6)
        si = ctk.CTkFrame(score_card, fg_color="transparent")
        si.pack(fill="x", padx=16, pady=14)
        left = ctk.CTkFrame(si, fg_color="transparent")
        left.pack(side="left", fill="y")
        ctk.CTkLabel(left, text="Score de santé du PC",
                     font=FONT_HEAD, text_color=self.MUTED).pack(anchor="w")
        self.lbl_score_big = ctk.CTkLabel(left, text="―/100",
                                           font=FONT_BIG, text_color=GREEN)
        self.lbl_score_big.pack(anchor="w")
        self.lbl_score_detail = ctk.CTkLabel(left,
            text="Cliquez sur 'Calculer santé' pour analyser.",
            font=FONT_SMALL, text_color=self.MUTED)
        self.lbl_score_detail.pack(anchor="w", pady=(4,0))

        self.score_bar = ctk.CTkProgressBar(si, height=10, corner_radius=5,
                                             progress_color=GREEN, fg_color=self.BORDER,
                                             width=200)
        self.score_bar.set(0)
        self.score_bar.pack(side="right", padx=20)

        metrics_row = ctk.CTkFrame(page, fg_color="transparent")
        metrics_row.pack(fill="x", padx=14, pady=6)
        metrics_row.grid_columnconfigure((0,1,2,3), weight=1)
        self._metric_cards  = {}
        self._canvas_graphs = {}

        for i, (key, label, icon, color) in enumerate([
            ("cpu",  "CPU",    "⚡", BLUE),
            ("ram",  "RAM",    "🧠", PURPLE),
            ("disk", "Disque", "💾", ORANGE),
            ("net",  "Réseau", "🌐", CYAN),
        ]):
            card = ctk.CTkFrame(metrics_row, fg_color=self.RAISED, corner_radius=10,
                                border_width=1, border_color=self.BORDER)
            card.grid(row=0, column=i, padx=6, pady=6, sticky="ew")
            ci = ctk.CTkFrame(card, fg_color="transparent")
            ci.pack(padx=12, pady=10, fill="x")
            ctk.CTkLabel(ci, text=f"{icon}  {label}",
                         font=FONT_SMALL, text_color=self.MUTED).pack(anchor="w")
            val_lbl = ctk.CTkLabel(ci, text="0%", font=FONT_MED, text_color=color)
            val_lbl.pack(anchor="w")
            bg_col = "#111111" if self.settings["theme"]=="dark" else "#e0e0e0"
            canvas = tk.Canvas(ci, height=40, bg=bg_col,
                               highlightthickness=0, bd=0)
            canvas.pack(fill="x", pady=(4,0))
            self._canvas_graphs[key] = (canvas, color, bg_col)
            bar = ctk.CTkProgressBar(ci, height=5, corner_radius=2,
                                     progress_color=color, fg_color=self.BORDER)
            bar.set(0)
            bar.pack(fill="x", pady=(4,0))
            self._metric_cards[key] = (val_lbl, bar)

        ctk.CTkLabel(page, text="⚡  Actions rapides",
                     font=FONT_HEAD, text_color=self.TEXT).pack(anchor="w", padx=14, pady=(10,4))
        act_grid = ctk.CTkFrame(page, fg_color="transparent")
        act_grid.pack(fill="x", padx=14, pady=4)
        act_grid.grid_columnconfigure((0,1,2,3), weight=1)
        for i, (txt, sub, fn, col) in enumerate([
            ("🧹  Nettoyage rapide",  "Temp + Corbeille + DNS",   self.do_quick_clean,  GREEN2),
            ("🔧  Réparer tout",      "SFC + DISM + nettoyage",   self.do_repair_all,   BLUE2),
            ("🔒  Scan virus",        "Windows Defender complet", self.do_scan_virus,   PURPLE),
            ("📊  Infos système",     "CPU + RAM + Disques",      self.do_infos_all,    ORANGE),
        ]):
            f = ctk.CTkFrame(act_grid, fg_color=self.RAISED, corner_radius=10,
                             border_width=1, border_color=self.BORDER)
            f.grid(row=0, column=i, padx=6, pady=6, sticky="ew")
            fi = ctk.CTkFrame(f, fg_color="transparent")
            fi.pack(padx=12, pady=12, fill="x")
            ctk.CTkLabel(fi, text=txt, font=FONT_BODY, text_color=self.TEXT).pack(anchor="w")
            ctk.CTkLabel(fi, text=sub, font=FONT_TINY, text_color=self.MUTED).pack(anchor="w", pady=(2,6))
            ctk.CTkButton(fi, text="▶", command=fn,
                          fg_color=col, hover_color=BLUE2, text_color=self.TEXT,
                          font=FONT_SMALL, corner_radius=6, height=28, width=40).pack(anchor="w")

        alert_card = ctk.CTkFrame(page, fg_color=self.RAISED, corner_radius=12,
                                  border_width=1, border_color=self.BORDER)
        alert_card.pack(fill="x", padx=14, pady=6)
        ai = ctk.CTkFrame(alert_card, fg_color="transparent")
        ai.pack(fill="x", padx=14, pady=12)
        ctk.CTkLabel(ai, text="🔔  Alertes système",
                     font=FONT_SMALL, text_color=self.MUTED).pack(anchor="w")
        self.alert_box = ctk.CTkTextbox(ai, height=80, fg_color=self.BG,
                                         text_color=GREEN, font=FONT_MONO,
                                         border_width=0, corner_radius=6)
        self.alert_box.pack(fill="x", pady=(6,0))
        self.alert_box.insert("end", "  ✅  Aucune alerte — PC en bonne santé\n")

        # Raccourcis clavier affiché
        ctk.CTkLabel(page,
            text="  ⌨️  Raccourcis : Ctrl+S sauvegarder log  •  Ctrl+L effacer  •  F5 actualiser moniteur  •  Echap fermer panneau",
            font=FONT_TINY, text_color=self.MUTED).pack(anchor="w", padx=14, pady=(4,8))

    # ════════════════════════════════════════════════════════
    # PAGE  MONITEUR DE PROCESSUS
    # ════════════════════════════════════════════════════════
    def _build_page_moniteur(self):
        page = ctk.CTkFrame(self.page_area, fg_color=self.BG)
        self._pages["Moniteur"] = page

        hdr = ctk.CTkFrame(page, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(12,6))
        ctk.CTkLabel(hdr, text="📈  Moniteur de processus",
                     font=FONT_HEAD, text_color=self.TEXT).pack(side="left")

        ctrl = ctk.CTkFrame(hdr, fg_color="transparent")
        ctrl.pack(side="right")
        ctk.CTkLabel(ctrl, text="F5 ou bouton pour actualiser",
                     font=FONT_SMALL, text_color=self.MUTED).pack(side="left", padx=(0,12))
        ctk.CTkButton(ctrl, text="🔄  Actualiser [F5]", command=self._refresh_proc_table,
                      fg_color=BLUE, hover_color=BLUE2, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=32, width=150).pack(side="left", padx=(0,8))

        filt = ctk.CTkFrame(page, fg_color=self.SURFACE,
                            corner_radius=8, border_width=1, border_color=self.BORDER)
        filt.pack(fill="x", padx=14, pady=4)
        fi = ctk.CTkFrame(filt, fg_color="transparent")
        fi.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(fi, text="Trier par :", font=FONT_SMALL,
                     text_color=self.MUTED).pack(side="left", padx=(0,8))
        self.proc_sort_var = ctk.StringVar(value="CPU %")
        ctk.CTkOptionMenu(fi, values=["CPU %","RAM %","Nom","PID"],
                          variable=self.proc_sort_var,
                          fg_color=self.RAISED, button_color=BLUE,
                          font=FONT_SMALL, width=120,
                          command=lambda _: self._refresh_proc_table()).pack(side="left", padx=(0,12))

        ctk.CTkLabel(fi, text="Filtrer :", font=FONT_SMALL,
                     text_color=self.MUTED).pack(side="left", padx=(0,8))
        self.proc_filter_entry = ctk.CTkEntry(fi,
            placeholder_text="Nom du processus…",
            fg_color=self.RAISED, text_color=self.TEXT,
            border_color=self.BORDER, font=FONT_SMALL, width=200)
        self.proc_filter_entry.pack(side="left")
        self.proc_filter_entry.bind("<KeyRelease>", lambda _: self._refresh_proc_table())

        cols_frame = ctk.CTkFrame(page, fg_color=self.SURFACE,
                                  corner_radius=0, border_width=0)
        cols_frame.pack(fill="x", padx=14, pady=(4,0))
        cols_inner = ctk.CTkFrame(cols_frame, fg_color="transparent")
        cols_inner.pack(fill="x", padx=8, pady=6)
        for txt, w in [("PID",8),("Processus",30),("CPU %",8),("RAM %",8),
                       ("RAM Mo",8),("Statut",10),("Action",8)]:
            ctk.CTkLabel(cols_inner, text=txt, font=("Arial",11,"bold"),
                         text_color=self.MUTED, width=w*10, anchor="w").pack(side="left", padx=4)

        self.proc_scroll = ctk.CTkScrollableFrame(page, fg_color=self.BG)
        self.proc_scroll.pack(fill="both", expand=True, padx=14, pady=(0,6))
        self._proc_rows  = []
        self._proc_running = False

    def _start_proc_monitor(self):
        self._proc_running = True
        self.after(0, self._refresh_proc_table)

    def _refresh_proc_table(self):
        filt = self.proc_filter_entry.get().lower().strip()
        sort = self.proc_sort_var.get()

        try:
            procs = []
            for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent",
                                           "memory_info","status"]):
                try:
                    info = p.info
                    if filt and filt not in (info["name"] or "").lower():
                        continue
                    procs.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if sort == "CPU %":   procs.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
            elif sort == "RAM %": procs.sort(key=lambda x: x["memory_percent"] or 0, reverse=True)
            elif sort == "Nom":   procs.sort(key=lambda x: (x["name"] or "").lower())
            elif sort == "PID":   procs.sort(key=lambda x: x["pid"] or 0)

            for widget in self.proc_scroll.winfo_children():
                widget.destroy()

            for i, info in enumerate(procs[:60]):
                cpu    = info["cpu_percent"] or 0
                ram    = info["memory_percent"] or 0
                mem_mb = (info["memory_info"].rss // 1024 // 1024) if info["memory_info"] else 0
                status = info.get("status","?")
                name   = info["name"] or "?"
                pid    = info["pid"] or 0
                is_prot = name in PROTECTED_PROCESSES

                bg_col  = self.RAISED if i%2==0 else self.CARD
                cpu_col = RED if cpu>50 else (ORANGE if cpu>20 else self.TEXT)
                ram_col = RED if ram>30 else (ORANGE if ram>15 else self.TEXT)

                row = ctk.CTkFrame(self.proc_scroll, fg_color=bg_col,
                                   corner_radius=4, border_width=0)
                row.pack(fill="x", pady=1)
                ri = ctk.CTkFrame(row, fg_color="transparent")
                ri.pack(fill="x", padx=8, pady=4)

                ctk.CTkLabel(ri, text=str(pid), font=FONT_MONO,
                             text_color=self.MUTED, width=80, anchor="w").pack(side="left", padx=4)
                name_display = ("🔒 " if is_prot else "") + name[:30]
                ctk.CTkLabel(ri, text=name_display, font=FONT_SMALL,
                             text_color=self.MUTED if is_prot else self.TEXT,
                             width=300, anchor="w").pack(side="left", padx=4)
                ctk.CTkLabel(ri, text=f"{cpu:.1f}%", font=FONT_MONO,
                             text_color=cpu_col, width=80, anchor="w").pack(side="left", padx=4)
                ctk.CTkLabel(ri, text=f"{ram:.1f}%", font=FONT_MONO,
                             text_color=ram_col, width=80, anchor="w").pack(side="left", padx=4)
                ctk.CTkLabel(ri, text=f"{mem_mb} Mo", font=FONT_MONO,
                             text_color=self.MUTED, width=80, anchor="w").pack(side="left", padx=4)
                ctk.CTkLabel(ri, text=status, font=FONT_TINY,
                             text_color=self.MUTED, width=100, anchor="w").pack(side="left", padx=4)

                # Bouton tuer : désactivé visuellement pour les processus protégés
                if is_prot:
                    ctk.CTkLabel(ri, text="🔒", font=FONT_TINY,
                                 text_color=self.MUTED, width=36).pack(side="left", padx=4)
                else:
                    ctk.CTkButton(ri, text="✖", width=32, height=24,
                                  command=lambda p=pid, n=name: self._kill_proc(p, n),
                                  fg_color=RED2, hover_color=RED, text_color=self.TEXT,
                                  font=FONT_TINY, corner_radius=4).pack(side="left", padx=4)

        except Exception as e:
            self._log_exc("Moniteur", e)

    def _kill_proc(self, pid, name):
        if name in PROTECTED_PROCESSES:
            self._log(f"✖  Refusé : {name} est un processus système protégé.")
            return
        if not self._confirm(
            f"Terminer le processus ?\n\n  {name}  (PID {pid})\n\nCette action peut provoquer une perte de données non sauvegardées."
        ):
            return
        try:
            p = psutil.Process(pid)
            p.terminate()
            self._log(f"✔  Processus terminé : {name} (PID {pid})\n")
            self._refresh_proc_table()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self._log_exc(f"kill {name}", e)

    # ════════════════════════════════════════════════════════
    # PAGE  SYSTÈME
    # ════════════════════════════════════════════════════════
    def _build_page_systeme(self):
        page = ctk.CTkScrollableFrame(self.page_area, fg_color=self.BG)
        self._pages["Système"] = page
        self._mk_section_title(page, "🖥  Informations système")
        grid = ctk.CTkFrame(page, fg_color="transparent")
        grid.pack(fill="x", padx=14)
        grid.grid_columnconfigure((0,1), weight=1)
        tools = [
            ("Infos CPU & mémoire",    "Processeur, RAM totale/utilisée, cœurs.",       self.do_infos_cpu),
            ("Infos GPU",              "Carte graphique, VRAM et pilote vidéo.",         self.do_infos_gpu),
            ("Processus actifs",       "Top 15 processus les plus gourmands.",           self.do_procs),
            ("Batterie / Laptop",      "Charge, statut et temps restant.",              self.do_battery),
            ("Températures",           "Température CPU et composants.",                 self.do_temps),
            ("Infos disque (SSD/HDD)", "Espace + type pour chaque partition.",           self.do_disque),
            ("Uptime du PC",           "Depuis combien de temps le PC est allumé.",      self.do_uptime),
            ("Pilotes installés",      "Liste des pilotes avec version et date.",        self.do_drivers),
            ("Démarrage Windows",      "Programmes lancés automatiquement.",             self.do_startup),
            ("Version Windows",        "Version exacte et numéro de build.",            self.do_winver),
        ]
        for i, (t, d, fn) in enumerate(tools):
            self._mk_btn_run(grid, t, d, fn).grid(row=i//2, column=i%2, padx=8, pady=8, sticky="ew")

    # ════════════════════════════════════════════════════════
    # PAGE  NETTOYAGE
    # ════════════════════════════════════════════════════════
    def _build_page_nettoyage(self):
        page = ctk.CTkScrollableFrame(self.page_area, fg_color=self.BG)
        self._pages["Nettoyage"] = page
        self._mk_section_title(page, "🧹  Nettoyage & maintenance")

        repair_card = ctk.CTkFrame(page, fg_color=self.CARD, corner_radius=12,
                                   border_width=2, border_color=BLUE)
        repair_card.pack(fill="x", padx=14, pady=(0,10))
        ri = ctk.CTkFrame(repair_card, fg_color="transparent")
        ri.pack(padx=16, pady=14, fill="x")
        ctk.CTkLabel(ri, text="🔧  Réparation & nettoyage automatique complet",
                     font=FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(ri, text="Temp → Corbeille → DNS → SFC → DISM  —  tout en un clic.",
                     font=FONT_SMALL, text_color=self.MUTED, wraplength=700).pack(anchor="w", pady=(4,8))
        pr = ctk.CTkFrame(ri, fg_color="transparent")
        pr.pack(fill="x")
        self.repair_progress = ctk.CTkProgressBar(pr, height=8, corner_radius=4,
                                                   progress_color=BLUE, fg_color=self.BORDER)
        self.repair_progress.set(0)
        self.repair_progress.pack(side="left", fill="x", expand=True, padx=(0,12))
        self.repair_label = ctk.CTkLabel(pr, text="Prêt",
                                          font=FONT_SMALL, text_color=self.MUTED, width=160)
        self.repair_label.pack(side="left")
        ctk.CTkButton(ri, text="▶  Tout réparer maintenant",
                      command=self.do_repair_all,
                      fg_color=BLUE, hover_color=BLUE2, text_color=self.TEXT,
                      font=FONT_BODY, corner_radius=10, height=40, width=240).pack(anchor="w", pady=(10,0))

        grid = ctk.CTkFrame(page, fg_color="transparent")
        grid.pack(fill="x", padx=14)
        grid.grid_columnconfigure((0,1), weight=1)
        tools = [
            ("Vider les fichiers temporaires",        "Supprime les fichiers inutiles dans Temp.",         self.do_clean_temp),
            ("Analyser les gros fichiers (top 20)",   "Trouve les fichiers les plus volumineux sur C:",    self.do_big_files),
            ("Mettre à jour les applications",        "winget upgrade — tous les logiciels.",              self.do_winget),
            ("Vider le cache DNS",                    "Résout les problèmes de connexion internet.",       self.do_flush_dns),
            ("Vider la corbeille",                    "Supprime définitivement les fichiers en attente.",  self.do_recycle),
            ("Supprimer anciens points restauration", "Garde uniquement le dernier point.",                self.do_clean_restore),
            ("Vérifier le disque C:",                 "Détecte et corrige les erreurs sur le disque.",     self.do_chkdsk),
            ("Nettoyage disque Windows",              "Outil intégré de nettoyage Windows.",               self.do_cleanmgr),
        ]
        for i, (t, d, fn) in enumerate(tools):
            self._mk_btn_run(grid, t, d, fn).grid(row=i//2, column=i%2, padx=8, pady=8, sticky="ew")

    # ════════════════════════════════════════════════════════
    # PAGE  SÉCURITÉ
    # ════════════════════════════════════════════════════════
    def _build_page_securite(self):
        page = ctk.CTkScrollableFrame(self.page_area, fg_color=self.BG)
        self._pages["Sécurité"] = page
        self._mk_section_title(page, "🔒  Sécurité")

        bloat_card = ctk.CTkFrame(page, fg_color=self.CARD, corner_radius=12,
                                  border_width=2, border_color=ORANGE)
        bloat_card.pack(fill="x", padx=14, pady=(0,10))
        bi = ctk.CTkFrame(bloat_card, fg_color="transparent")
        bi.pack(padx=16, pady=14, fill="x")
        ctk.CTkLabel(bi, text="🕵️  Détection de logiciels suspects / bloatware",
                     font=FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(bi, text="Signale adwares, toolbars et optimiseurs douteux installés sur ce PC.",
                     font=FONT_SMALL, text_color=self.MUTED, wraplength=700).pack(anchor="w", pady=(4,8))
        ctk.CTkButton(bi, text="🔍  Scanner maintenant",
                      command=self.do_detect_bloatware,
                      fg_color=ORANGE, hover_color="#e65100", text_color=self.TEXT,
                      font=FONT_BODY, corner_radius=10, height=40, width=200).pack(anchor="w")

        grid = ctk.CTkFrame(page, fg_color="transparent")
        grid.pack(fill="x", padx=14)
        grid.grid_columnconfigure((0,1), weight=1)
        tools = [
            ("Scan antivirus complet",        "Analyse complète avec Windows Defender.",        self.do_scan_virus),
            ("Mise à jour des définitions",   "Met à jour la base de données virus.",           self.do_update_defender),
            ("Générer un mot de passe fort",  "20 caractères, copié dans le presse-papiers.",  self.do_gen_pwd),
            ("Ports ouverts inhabituels",     "Détecte les ports en écoute hors standards.",   self.do_ports_suspects),
            ("WiFi enregistrés",              "⚠ Affiche les réseaux et mots de passe.",       self.do_wifi_saved),
            ("Comptes administrateurs",       "Liste les comptes avec droits admin.",          self.do_admin_accounts),
            ("Connexions réseau actives",     "Tous les programmes connectés à internet.",     self.do_netstat),
            ("Pare-feu Windows",             "Ouvre les paramètres du pare-feu.",             self.do_firewall),
        ]
        for i, (t, d, fn) in enumerate(tools):
            self._mk_btn_run(grid, t, d, fn).grid(row=i//2, column=i%2, padx=8, pady=8, sticky="ew")

    # ════════════════════════════════════════════════════════
    # PAGE  RÉSEAU
    # ════════════════════════════════════════════════════════
    def _build_page_reseau(self):
        page = ctk.CTkScrollableFrame(self.page_area, fg_color=self.BG)
        self._pages["Réseau"] = page
        self._mk_section_title(page, "🌐  Réseau & connexions")

        grid1 = ctk.CTkFrame(page, fg_color="transparent")
        grid1.pack(fill="x", padx=14)
        grid1.grid_columnconfigure((0,1,2), weight=1)
        for i, (t, d, fn) in enumerate([
            ("IP locale & publique",   "Votre IP box et IP internet.",                         self.do_ip_info),
            ("Config réseau complète", "Détails toutes les cartes (ipconfig /all).",           lambda: self._run("ipconfig /all","Config réseau")),
            ("DNS configurés",         "Serveurs DNS actifs sur toutes les cartes.",           self.do_dns_info),
        ]):
            self._mk_btn_run(grid1, t, d, fn).grid(row=0, column=i, padx=8, pady=8, sticky="ew")

        ctk.CTkFrame(page, height=1, fg_color=self.BORDER).pack(fill="x", padx=14, pady=8)
        ping_card = ctk.CTkFrame(page, fg_color=self.RAISED, corner_radius=10,
                                 border_width=1, border_color=self.BORDER)
        ping_card.pack(fill="x", padx=14, pady=6)
        pi = ctk.CTkFrame(ping_card, fg_color="transparent")
        pi.pack(padx=12, pady=12, fill="x")
        ctk.CTkLabel(pi, text="Ping personnalisé", font=FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        pr = ctk.CTkFrame(pi, fg_color="transparent")
        pr.pack(fill="x", pady=(6,0))
        self.ping_entry = ctk.CTkEntry(pr, placeholder_text="ex: google.com ou 192.168.1.1",
                                       fg_color=self.SURFACE, text_color=self.TEXT,
                                       border_color=self.BORDER, font=FONT_SMALL, width=320)
        self.ping_entry.pack(side="left", padx=(0,10))
        ctk.CTkButton(pr, text="▶  Lancer", command=self.do_ping_custom,
                      fg_color=BLUE, hover_color=BLUE2, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=120).pack(side="left")

        grid2 = ctk.CTkFrame(page, fg_color="transparent")
        grid2.pack(fill="x", padx=14)
        grid2.grid_columnconfigure((0,1,2), weight=1)
        for i, (t, d, fn) in enumerate([
            ("Ping Google",        "5 pings vers 8.8.8.8.",                         lambda: self._run("ping -n 5 8.8.8.8","Ping Google")),
            ("Traceroute Google",  "Chemin des paquets jusqu'à Google.",             lambda: self._run("tracert -d google.com","Traceroute")),
            ("Benchmark DNS",      "Temps de réponse de 4 serveurs DNS.",            self.do_dns_benchmark),
        ]):
            self._mk_btn_run(grid2, t, d, fn).grid(row=0, column=i, padx=8, pady=8, sticky="ew")

        ctk.CTkFrame(page, height=1, fg_color=self.BORDER).pack(fill="x", padx=14, pady=8)
        grid3 = ctk.CTkFrame(page, fg_color="transparent")
        grid3.pack(fill="x", padx=14)
        grid3.grid_columnconfigure((0,1,2), weight=1)
        for i, (t, d, fn) in enumerate([
            ("Appareils réseau local", "Scanne et liste tous les appareils.", self.do_scan_local),
            ("Partages réseau",        "Dossiers et imprimantes partagés.",   lambda: self._run("net view","Partages")),
            ("Table ARP",              "IP ↔ adresse MAC des appareils.",     lambda: self._run("arp -a","Table ARP")),
        ]):
            self._mk_btn_run(grid3, t, d, fn).grid(row=0, column=i, padx=8, pady=8, sticky="ew")

        ctk.CTkFrame(page, height=1, fg_color=self.BORDER).pack(fill="x", padx=14, pady=8)
        dns_card = ctk.CTkFrame(page, fg_color=self.RAISED, corner_radius=10,
                                border_width=1, border_color=self.BORDER)
        dns_card.pack(fill="x", padx=14, pady=6)
        di = ctk.CTkFrame(dns_card, fg_color="transparent")
        di.pack(padx=12, pady=12, fill="x")
        ctk.CTkLabel(di, text="⚡  Changer le DNS rapidement",
                     font=FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        dr = ctk.CTkFrame(di, fg_color="transparent")
        dr.pack(fill="x", pady=(8,0))
        for lbl, p, s in [
            ("☁️  Cloudflare (1.1.1.1)", "1.1.1.1","1.0.0.1"),
            ("🔵  Google (8.8.8.8)",      "8.8.8.8","8.8.4.4"),
            ("🛡  OpenDNS",               "208.67.222.222","208.67.220.220"),
        ]:
            ctk.CTkButton(dr, text=lbl,
                          command=lambda p=p, s=s: self.do_set_dns(p,s),
                          fg_color=self.RAISED, hover_color=self.CARD, text_color=self.TEXT,
                          font=FONT_SMALL, corner_radius=8, height=34,
                          border_width=1, border_color=self.BORDER).pack(side="left", padx=(0,10))

    # ════════════════════════════════════════════════════════
    # PAGE  OUTILS WINDOWS
    # ════════════════════════════════════════════════════════
    def _build_page_outils(self):
        page = ctk.CTkScrollableFrame(self.page_area, fg_color=self.BG)
        self._pages["Outils Windows"] = page
        self._mk_section_title(page, "🔧  Outils & raccourcis Windows")

        util_row = ctk.CTkFrame(page, fg_color="transparent")
        util_row.pack(fill="x", padx=14)
        util_row.grid_columnconfigure((0,1), weight=1)

        cap = ctk.CTkFrame(util_row, fg_color=self.RAISED, corner_radius=10,
                           border_width=1, border_color=self.BORDER)
        cap.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        ci = ctk.CTkFrame(cap, fg_color="transparent")
        ci.pack(padx=12, pady=12, fill="x")
        ctk.CTkLabel(ci, text="📸  Capture d'écran", font=FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(ci, text="Sauvegarde horodatée sur le Bureau.",
                     font=FONT_SMALL, text_color=self.MUTED).pack(anchor="w", pady=(2,6))
        ctk.CTkButton(ci, text="▶  Capturer", command=self.do_screenshot,
                      fg_color=BLUE, hover_color=BLUE2, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=120).pack(anchor="w")

        hash_c = ctk.CTkFrame(util_row, fg_color=self.RAISED, corner_radius=10,
                              border_width=1, border_color=self.BORDER)
        hash_c.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        hi = ctk.CTkFrame(hash_c, fg_color="transparent")
        hi.pack(padx=12, pady=12, fill="x")
        ctk.CTkLabel(hi, text="🔑  Hash SHA-256", font=FONT_HEAD, text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(hi, text="Vérifie l'intégrité d'un fichier téléchargé.",
                     font=FONT_SMALL, text_color=self.MUTED).pack(anchor="w", pady=(2,6))
        hr = ctk.CTkFrame(hi, fg_color="transparent")
        hr.pack(fill="x")
        self.hash_entry = ctk.CTkEntry(hr, placeholder_text="C:\\chemin\\fichier.exe",
                                       fg_color=self.SURFACE, text_color=self.TEXT,
                                       border_color=self.BORDER, font=FONT_SMALL)
        self.hash_entry.pack(side="left", fill="x", expand=True, padx=(0,8))
        ctk.CTkButton(hr, text="▶", command=self.do_hash_from_entry,
                      fg_color=BLUE, hover_color=BLUE2, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=40).pack(side="left")

        ctk.CTkFrame(page, height=1, fg_color=self.BORDER).pack(fill="x", padx=14, pady=8)

        ctk.CTkLabel(page, text="  🩺  Diagnostic & réparation",
                     font=FONT_BODY, text_color=self.MUTED).pack(anchor="w", padx=14)
        grid1 = ctk.CTkFrame(page, fg_color="transparent")
        grid1.pack(fill="x", padx=14)
        grid1.grid_columnconfigure((0,1,2), weight=1)
        for i, (t, d, fn) in enumerate([
            ("Diagnostic RAM",     "Teste la RAM (redémarrage).",             lambda: self._open("mdsched.exe","RAM")),
            ("Réparer SFC",        "Répare les fichiers corrompus.",           lambda: self._run("sfc /scannow","SFC")),
            ("Réparation DISM",    "Répare l'image Windows en profondeur.",   lambda: self._run("DISM /Online /Cleanup-Image /RestoreHealth","DISM")),
            ("Antivirus MRT",      "Outil anti-malware Microsoft.",           lambda: self._open("MRT","MRT")),
            ("Infos système",      "Résumé complet matériel et logiciels.",   lambda: self._open("msinfo32","msinfo32")),
            ("Moniteur fiabilité", "Historique pannes et plantages.",         lambda: self._open("perfmon /rel","Fiabilité")),
        ]):
            self._mk_btn_open(grid1, t, d, fn).grid(row=i//3, column=i%3, padx=8, pady=8, sticky="ew")

        ctk.CTkFrame(page, height=1, fg_color=self.BORDER).pack(fill="x", padx=14, pady=8)
        ctk.CTkLabel(page, text="  ⚙️  Configuration système",
                     font=FONT_BODY, text_color=self.MUTED).pack(anchor="w", padx=14)
        grid2 = ctk.CTkFrame(page, fg_color="transparent")
        grid2.pack(fill="x", padx=14)
        grid2.grid_columnconfigure((0,1,2), weight=1)
        for i, (t, d, fn) in enumerate([
            ("Propriétés système", "Paramètres avancés, variables.",      lambda: self._open("sysdm.cpl","Propriétés")),
            ("Config démarrage",   "Programmes au démarrage.",            lambda: self._open("msconfig","msconfig")),
            ("Alimentation",       "Plans d'énergie Windows.",            lambda: self._open("powercfg.cpl","Alimentation")),
            ("Options Internet",   "Proxy, sécurité, connexions.",       lambda: self._open("inetcpl.cpl","Internet")),
            ("Éditeur registre",   "Paramètres internes (prudence !).",   lambda: self._open("regedit","Regedit")),
            ("Variables d'env.",   "PATH, TEMP, USERPROFILE…",           lambda: self._open("rundll32 sysdm.cpl,EditEnvironmentVariables","Env")),
        ]):
            self._mk_btn_open(grid2, t, d, fn).grid(row=i//3, column=i%3, padx=8, pady=8, sticky="ew")

        ctk.CTkFrame(page, height=1, fg_color=self.BORDER).pack(fill="x", padx=14, pady=8)
        ctk.CTkLabel(page, text="  📂  Gestionnaires",
                     font=FONT_BODY, text_color=self.MUTED).pack(anchor="w", padx=14)
        grid3 = ctk.CTkFrame(page, fg_color="transparent")
        grid3.pack(fill="x", padx=14)
        grid3.grid_columnconfigure((0,1,2), weight=1)
        for i, (t, d, fn) in enumerate([
            ("Périphériques",   "Pilotes et matériels.",        lambda: self._open("devmgmt.msc","Périphériques")),
            ("Gestion disques", "Partitions et formats.",       lambda: self._open("diskmgmt.msc","Disques")),
            ("Services",        "Services en arrière-plan.",    lambda: self._open("services.msc","Services")),
            ("Planificateur",   "Tâches automatiques.",        lambda: self._open("taskschd.msc","Planificateur")),
            ("Applications",    "Toutes les apps installées.", lambda: self._open("shell:appsfolder","Apps")),
            ("Désinstaller",    "Supprimer des logiciels.",    lambda: self._open("appwiz.cpl","Désinstaller")),
        ]):
            self._mk_btn_open(grid3, t, d, fn).grid(row=i//3, column=i%3, padx=8, pady=8, sticky="ew")

    # ════════════════════════════════════════════════════════
    # PAGE  DÉSINSTALLEUR
    # ════════════════════════════════════════════════════════
    def _build_page_desinstalleur(self):
        page = ctk.CTkFrame(self.page_area, fg_color=self.BG)
        self._pages["Désinstalleur"] = page
        self._mk_section_title(page, "🗑  Désinstalleur en masse")

        ctrl = ctk.CTkFrame(page, fg_color="transparent")
        ctrl.pack(fill="x", padx=14, pady=(0,8))
        ctk.CTkButton(ctrl, text="🔄  Charger la liste", command=self._load_installed_apps,
                      fg_color=BLUE, hover_color=BLUE2, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=32, width=160).pack(side="left", padx=(0,8))
        ctk.CTkButton(ctrl, text="🗑  Désinstaller la sélection", command=self._uninstall_selected,
                      fg_color=RED2, hover_color=RED, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=32, width=210).pack(side="left", padx=(0,8))
        self.desinst_count_lbl = ctk.CTkLabel(ctrl, text="", font=FONT_SMALL, text_color=self.MUTED)
        self.desinst_count_lbl.pack(side="left", padx=8)

        filt_row = ctk.CTkFrame(page, fg_color="transparent")
        filt_row.pack(fill="x", padx=14, pady=(0,6))
        ctk.CTkLabel(filt_row, text="Filtrer :", font=FONT_SMALL, text_color=self.MUTED).pack(side="left", padx=(0,8))
        self.desinst_filter = ctk.CTkEntry(filt_row, placeholder_text="Nom du logiciel…",
                                            fg_color=self.RAISED, text_color=self.TEXT,
                                            border_color=self.BORDER, font=FONT_SMALL, width=280)
        self.desinst_filter.pack(side="left")
        self.desinst_filter.bind("<KeyRelease>", lambda _: self._filter_apps())

        hdr = ctk.CTkFrame(page, fg_color=self.SURFACE, corner_radius=0)
        hdr.pack(fill="x", padx=14, pady=(4,0))
        hi = ctk.CTkFrame(hdr, fg_color="transparent")
        hi.pack(fill="x", padx=8, pady=6)
        ctk.CTkLabel(hi, text="☑", font=("Arial",11,"bold"), text_color=self.MUTED, width=30).pack(side="left")
        ctk.CTkLabel(hi, text="Nom", font=("Arial",11,"bold"), text_color=self.MUTED, anchor="w").pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(hi, text="Version", font=("Arial",11,"bold"), text_color=self.MUTED, width=110).pack(side="left")
        ctk.CTkLabel(hi, text="Éditeur", font=("Arial",11,"bold"), text_color=self.MUTED, width=150).pack(side="left")

        self.desinst_scroll = ctk.CTkScrollableFrame(page, fg_color=self.BG)
        self.desinst_scroll.pack(fill="both", expand=True, padx=14, pady=(0,6))
        self._app_list = []
        self._app_vars = []
        ctk.CTkLabel(self.desinst_scroll,
                     text="Cliquez sur 'Charger la liste' pour afficher les logiciels installés.",
                     font=FONT_SMALL, text_color=self.MUTED).pack(pady=40)

    def _load_installed_apps(self):
        def t():
            self._log("▶  Chargement des logiciels installés…")
            try:
                proc = subprocess.Popen(
                    "PowerShell -Command \"Get-ItemProperty "
                    "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,"
                    "HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
                    "Where-Object {$_.DisplayName -ne $null} | "
                    "Select-Object DisplayName,DisplayVersion,Publisher,UninstallString | "
                    "Sort-Object DisplayName | ConvertTo-Json -Compress\"",
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = proc.stdout.read().decode("utf-8", errors="replace").strip()
                proc.wait()
                if out.startswith("[") or out.startswith("{"):
                    raw = json.loads(out)
                    if isinstance(raw, dict): raw = [raw]
                    apps = []
                    for item in raw:
                        name   = (item.get("DisplayName") or "").strip()
                        ver    = (item.get("DisplayVersion") or "").strip()
                        pub    = (item.get("Publisher") or "").strip()
                        uninst = (item.get("UninstallString") or "").strip()
                        if name: apps.append((name, ver, pub, uninst))
                    self._app_list = apps
                    self.after(0, self._render_app_list)
                    self._log(f"   ✔  {len(apps)} logiciels trouvés\n")
                else:
                    self._log("   ✖  Impossible de lire la liste (réessayez en admin)\n")
            except Exception as e:
                self._log_exc("_load_installed_apps", e)
        threading.Thread(target=t, daemon=True).start()

    def _render_app_list(self, filter_text=""):
        for w in self.desinst_scroll.winfo_children(): w.destroy()
        self._app_vars = []
        shown = 0
        for name, ver, pub, uninst in self._app_list:
            if filter_text and filter_text.lower() not in name.lower(): continue
            var = ctk.BooleanVar(value=False)
            is_bloat = any(b in name.lower() for b in BLOATWARE)
            bg_col = "#2d1a1a" if is_bloat else (self.RAISED if shown%2==0 else self.CARD)
            row = ctk.CTkFrame(self.desinst_scroll, fg_color=bg_col, corner_radius=4)
            row.pack(fill="x", pady=1)
            ri = ctk.CTkFrame(row, fg_color="transparent")
            ri.pack(fill="x", padx=8, pady=3)
            ctk.CTkCheckBox(ri, text="", variable=var, width=30,
                            fg_color=BLUE, hover_color=BLUE2,
                            border_color=self.BORDER).pack(side="left")
            col = RED if is_bloat else self.TEXT
            ctk.CTkLabel(ri, text=("⚠ " if is_bloat else "") + name[:44],
                         font=FONT_SMALL, text_color=col, anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(ri, text=ver[:16], font=FONT_TINY, text_color=self.MUTED, width=110).pack(side="left")
            ctk.CTkLabel(ri, text=pub[:20], font=FONT_TINY, text_color=self.MUTED, width=150).pack(side="left")
            self._app_vars.append((var, name, uninst))
            shown += 1
        self.desinst_count_lbl.configure(text=f"{shown} logiciel(s)  •  ⚠ rouge = suspect")

    def _filter_apps(self):
        self._render_app_list(self.desinst_filter.get().strip())

    def _uninstall_selected(self):
        selected = [(name, uninst) for var, name, uninst in self._app_vars if var.get()]
        if not selected:
            self._log("✖  Aucun logiciel sélectionné.\n")
            return
        names = "\n".join(f"  • {n}" for n, _ in selected[:8])
        if len(selected) > 8: names += f"\n  … et {len(selected)-8} autre(s)"
        if not self._confirm(
            f"Désinstaller {len(selected)} logiciel(s) ?\n\n{names}\n\nCette action est irréversible."
        ):
            return
        def t():
            self._log(f"▶  Désinstallation de {len(selected)} logiciel(s)…")
            for name, uninst in selected:
                self._log(f"   ▷ {name}…")
                try:
                    if uninst:
                        subprocess.run(uninst, shell=True, timeout=120)
                        self._log(f"   ✔  {name} désinstallé")
                    else:
                        self._log(f"   ✖  {name} — pas de désinstalleur trouvé")
                except Exception as e:
                    self._log_exc(f"uninstall {name}", e)
            self._log("✔  Terminé\n")
            self.after(1000, self._load_installed_apps)
        threading.Thread(target=t, daemon=True).start()

    # ════════════════════════════════════════════════════════
    # PAGE  RAPPORT
    # ════════════════════════════════════════════════════════
    def _build_page_rapport(self):
        page = ctk.CTkScrollableFrame(self.page_area, fg_color=self.BG)
        self._pages["Rapport"] = page
        self._mk_section_title(page, "📄  Générateur de rapport système")

        card = ctk.CTkFrame(page, fg_color=self.RAISED, corner_radius=12,
                            border_width=2, border_color=BLUE)
        card.pack(fill="x", padx=14, pady=(0,10))
        ci = ctk.CTkFrame(card, fg_color="transparent")
        ci.pack(padx=16, pady=16, fill="x")
        ctk.CTkLabel(ci, text="Choisissez les sections à inclure :",
                     font=FONT_HEAD, text_color=self.TEXT).pack(anchor="w", pady=(0,10))

        self._rapport_opts = {}
        og = ctk.CTkFrame(ci, fg_color="transparent")
        og.pack(fill="x")
        og.grid_columnconfigure((0,1,2), weight=1)
        for i, (key, label) in enumerate([
            ("cpu",      "✅  CPU & mémoire"),
            ("disque",   "✅  Disques"),
            ("reseau",   "✅  Réseau"),
            ("proc",     "✅  Processus actifs"),
            ("securite", "✅  Sécurité"),
            ("startup",  "✅  Démarrage"),
        ]):
            var = ctk.BooleanVar(value=True)
            self._rapport_opts[key] = var
            ctk.CTkCheckBox(og, text=label, variable=var,
                            fg_color=BLUE, hover_color=BLUE2,
                            text_color=self.TEXT, font=FONT_SMALL,
                            border_color=self.BORDER).grid(row=i//3, column=i%3, padx=8, pady=4, sticky="w")

        btn_row = ctk.CTkFrame(ci, fg_color="transparent")
        btn_row.pack(anchor="w", pady=(12,0))
        ctk.CTkButton(btn_row, text="📄  Générer le rapport (.txt)",
                      command=self._generate_rapport,
                      fg_color=BLUE, hover_color=BLUE2, text_color=self.TEXT,
                      font=FONT_BODY, corner_radius=10, height=44, width=250).pack(side="left", padx=(0,12))

        pdf_color = GREEN2 if PDF_AVAILABLE else self.MUTED
        pdf_txt = "📑  Exporter en PDF" if PDF_AVAILABLE else "📑  PDF (pip install reportlab)"
        ctk.CTkButton(btn_row, text=pdf_txt,
                      command=self._export_pdf_rapport,
                      fg_color=pdf_color, hover_color=GREEN, text_color=self.TEXT,
                      font=FONT_BODY, corner_radius=10, height=44, width=250).pack(side="left")

        self._mk_section_title(page, "👁  Aperçu")
        self.rapport_preview = ctk.CTkTextbox(page, height=340,
                                               fg_color=self.RAISED, text_color=self.TEXT,
                                               font=("Courier New", 11),
                                               border_color=self.BORDER, border_width=1, corner_radius=8)
        self.rapport_preview.pack(fill="x", padx=14, pady=(0,14))
        self.rapport_preview.insert("end", "  Le rapport apparaîtra ici après génération.\n")

    def _collect_rapport_data(self):
        """Collecte les données du rapport et retourne (lines, data_dict)."""
        lines = []
        sep   = "=" * 58
        lines += [sep, f"  PC TOOL v{VERSION}  —  RAPPORT SYSTÈME",
                  f"  {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}", sep]
        data = {}

        if self._rapport_opts.get("cpu", ctk.BooleanVar(value=True)).get():
            lines += ["", "  CPU & MÉMOIRE", "-"*40]
            try:
                pct = psutil.cpu_percent(interval=1); ram = psutil.virtual_memory()
                data["cpu_pct"]      = pct
                data["ram_total_go"] = ram.total//1024**3
                data["ram_used_mo"]  = ram.used//1024**2
                data["ram_pct"]      = ram.percent
                data["ram_free_mo"]  = ram.available//1024**2
                lines += [f"  CPU         : {pct}%",
                          f"  RAM totale  : {ram.total//1024**3} Go",
                          f"  RAM utilisée: {ram.used//1024**2} Mo ({ram.percent}%)",
                          f"  RAM libre   : {ram.available//1024**2} Mo"]
            except Exception as e:
                lines.append(f"  Erreur : {e}")

        if self._rapport_opts.get("disque", ctk.BooleanVar(value=True)).get():
            lines += ["", "  DISQUES", "-"*40]
            data["disques"] = []
            for p in psutil.disk_partitions():
                try:
                    u = psutil.disk_usage(p.mountpoint)
                    entry = f"  {p.mountpoint}  {u.used//1024**3}/{u.total//1024**3} Go ({u.percent}%)"
                    lines.append(entry)
                    data["disques"].append(entry.strip())
                except Exception:
                    pass

        if self._rapport_opts.get("reseau", ctk.BooleanVar(value=True)).get():
            lines += ["", "  RÉSEAU", "-"*40]
            try:
                h = socket.gethostname()
                lines.append(f"  Nom PC      : {h}")
                lines.append(f"  IP locale   : {socket.gethostbyname(h)}")
                try:
                    ip = urllib.request.urlopen("https://api.ipify.org", timeout=4).read().decode()
                    lines.append(f"  IP publique : {ip}")
                except Exception:
                    lines.append("  IP publique : non disponible")
            except Exception as e:
                lines.append(f"  Erreur : {e}")

        if self._rapport_opts.get("proc", ctk.BooleanVar(value=True)).get():
            lines += ["", "  TOP 10 PROCESSUS (CPU)", "-"*40]
            try:
                procs = sorted(psutil.process_iter(["name","cpu_percent","memory_percent"]),
                               key=lambda p: p.info["cpu_percent"], reverse=True)[:10]
                for p in procs:
                    lines.append(
                        f"  {p.info['name'][:28]:<28}  CPU {p.info['cpu_percent']:5.1f}%  RAM {p.info['memory_percent']:4.1f}%")
            except Exception as e:
                lines.append(f"  Erreur : {e}")

        if self._rapport_opts.get("securite", ctk.BooleanVar(value=True)).get():
            lines += ["", "  SÉCURITÉ", "-"*40]
            try:
                uptime_h = (datetime.now()-datetime.fromtimestamp(psutil.boot_time())).total_seconds()/3600
                lines.append(f"  Uptime          : {uptime_h:.1f}h")
                suspects = [c for c in psutil.net_connections(kind="inet")
                            if c.laddr and c.laddr.port not in {80,443,8080,3389,22,53,135,445,139}
                            and c.status=="LISTEN"]
                lines.append(f"  Ports suspects  : {len(suspects)}")
            except Exception as e:
                lines.append(f"  Erreur : {e}")

        if self._rapport_opts.get("startup", ctk.BooleanVar(value=True)).get():
            lines += ["", "  DÉMARRAGE", "-"*40]
            try:
                proc = subprocess.Popen(
                    "reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = proc.stdout.read().decode("cp850", errors="replace"); proc.wait()
                for line in out.splitlines():
                    if line.strip() and "HKEY" not in line:
                        lines.append(f"  {line.strip()[:65]}")
            except Exception as e:
                lines.append(f"  Erreur : {e}")

        lines += ["", sep, f"  Score de santé : {self._health_score}/100", sep]
        return lines, data

    def _generate_rapport(self):
        def t():
            self._log("▶  Génération du rapport…")
            lines, _ = self._collect_rapport_data()
            report_text = "\n".join(lines)
            desktop = os.path.join(os.environ.get("USERPROFILE",""), "Desktop")
            fname   = f"rapport_pc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            fpath   = os.path.join(desktop, fname)
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(report_text)
                self._log(f"   ✔  Rapport .txt sauvegardé : {fpath}\n")
            except Exception as e:
                self._log_exc("rapport txt", e)
            def upd():
                self.rapport_preview.delete("0.0","end")
                self.rapport_preview.insert("end", report_text)
            self.after(0, upd)
        threading.Thread(target=t, daemon=True).start()

    def _export_pdf_rapport(self):
        if not PDF_AVAILABLE:
            self._log("✖  reportlab non installé. Exécutez : pip install reportlab\n")
            return
        def t():
            self._log("▶  Export PDF en cours…")
            lines, _ = self._collect_rapport_data()
            desktop  = os.path.join(os.environ.get("USERPROFILE",""), "Desktop")
            fname    = f"rapport_pc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            fpath    = os.path.join(desktop, fname)
            try:
                doc = SimpleDocTemplate(fpath, pagesize=A4,
                                        leftMargin=2*cm, rightMargin=2*cm,
                                        topMargin=2*cm, bottomMargin=2*cm)
                styles  = getSampleStyleSheet()
                story   = []

                # Styles personnalisés
                title_style = ParagraphStyle("title",
                    parent=styles["Title"], fontSize=18, spaceAfter=6,
                    textColor=rl_colors.HexColor("#2196f3"))
                head_style  = ParagraphStyle("head",
                    parent=styles["Heading2"], fontSize=12, spaceBefore=12,
                    textColor=rl_colors.HexColor("#4caf50"))
                body_style  = ParagraphStyle("body",
                    parent=styles["Normal"], fontSize=9, fontName="Courier",
                    leading=13)
                sep_style   = ParagraphStyle("sep",
                    parent=styles["Normal"], fontSize=8, textColor=rl_colors.grey)

                story.append(Paragraph(f"💻 PC Tool v{VERSION} — Rapport système", title_style))
                story.append(Paragraph(datetime.now().strftime("%d/%m/%Y à %H:%M:%S"), sep_style))
                story.append(HRFlowable(width="100%", thickness=1,
                                        color=rl_colors.HexColor("#2196f3")))
                story.append(Spacer(1, 0.3*cm))

                section_headers = {"CPU & MÉMOIRE", "DISQUES", "RÉSEAU",
                                   "TOP 10 PROCESSUS (CPU)", "SÉCURITÉ", "DÉMARRAGE"}

                for line in lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("="):
                        continue
                    # Détection en-têtes de section
                    is_head = any(h in stripped for h in section_headers)
                    is_sep  = set(stripped) <= {"-", "="}
                    if is_sep:
                        story.append(HRFlowable(width="100%", thickness=0.5,
                                                color=rl_colors.lightgrey))
                    elif is_head:
                        story.append(Spacer(1, 0.2*cm))
                        story.append(Paragraph(stripped, head_style))
                    else:
                        # Échapper les caractères spéciaux HTML pour reportlab
                        safe = stripped.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        story.append(Paragraph(safe, body_style))

                story.append(Spacer(1, 0.5*cm))
                story.append(HRFlowable(width="100%", thickness=1,
                                        color=rl_colors.HexColor("#4caf50")))
                story.append(Paragraph(f"Score de santé : {self._health_score}/100",
                                       ParagraphStyle("score", parent=styles["Normal"],
                                                      fontSize=14, textColor=rl_colors.HexColor("#4caf50"),
                                                      fontName="Helvetica-Bold")))

                doc.build(story)
                self._log(f"   ✔  Rapport PDF sauvegardé : {fpath}\n")
                # Ouvrir automatiquement
                os.startfile(fpath)
            except Exception as e:
                self._log_exc("export PDF", e)
        threading.Thread(target=t, daemon=True).start()

    # ════════════════════════════════════════════════════════
    # PAGE  HISTORIQUE
    # ════════════════════════════════════════════════════════
    def _build_page_historique(self):
        page = ctk.CTkFrame(self.page_area, fg_color=self.BG)
        self._pages["Historique"] = page
        self._mk_section_title(page, "📋  Historique des actions")

        btn_row = ctk.CTkFrame(page, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0,8))
        ctk.CTkButton(btn_row, text="🔄  Actualiser", command=self._refresh_historique,
                      fg_color=self.RAISED, hover_color=self.CARD, text_color=self.MUTED,
                      font=FONT_SMALL, corner_radius=8, height=30, width=120,
                      border_width=1, border_color=self.BORDER).pack(side="left", padx=(0,8))
        ctk.CTkButton(btn_row, text="🗑  Vider l'historique", command=self._clear_historique,
                      fg_color=RED2, hover_color=RED, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=160).pack(side="left")

        self.histo_box = ctk.CTkTextbox(page, fg_color=self.RAISED, text_color=self.TEXT,
                                         font=FONT_MONO, border_color=self.BORDER,
                                         border_width=1, corner_radius=8)
        self.histo_box.pack(fill="both", expand=True, padx=14, pady=(0,14))
        self._refresh_historique()

    def _refresh_historique(self):
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                self.histo_box.delete("0.0","end")
                self.histo_box.insert("end", content)
                self.histo_box.see("end")
            else:
                self.histo_box.delete("0.0","end")
                self.histo_box.insert("end","Aucun historique enregistré.\n")
        except Exception as e:
            self._log_exc("refresh_historique", e)

    def _clear_historique(self):
        if not self._confirm("Effacer tout l'historique des actions ?\nCette action est irréversible."):
            return
        try:
            if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
            self.histo_box.delete("0.0","end")
            self.histo_box.insert("end","Historique effacé.\n")
        except Exception as e:
            self._log_exc("clear_historique", e)

    # ════════════════════════════════════════════════════════
    # HELPERS UI
    # ════════════════════════════════════════════════════════
    def _mk_section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=FONT_HEAD,
                     text_color=self.MUTED).pack(anchor="w", padx=14, pady=(14,4))
        ctk.CTkFrame(parent, height=1, fg_color=self.BORDER).pack(fill="x", padx=14, pady=(0,8))

    def _mk_btn_run(self, parent, text, desc, cmd, color=BLUE):
        frame = ctk.CTkFrame(parent, fg_color=self.RAISED, corner_radius=10,
                             border_width=1, border_color=self.BORDER)
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(inner, text=text, font=FONT_HEAD, text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(inner, text=desc, font=FONT_SMALL, text_color=self.MUTED,
                     anchor="w", wraplength=290).pack(anchor="w", pady=(2,6))
        ctk.CTkButton(inner, text="▶  Lancer", command=cmd,
                      fg_color=color, hover_color=BLUE2, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=120).pack(anchor="w")
        return frame

    def _mk_btn_open(self, parent, text, desc, cmd):
        frame = ctk.CTkFrame(parent, fg_color=self.RAISED, corner_radius=10,
                             border_width=1, border_color=self.BORDER)
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(inner, text=text, font=FONT_HEAD, text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(inner, text=desc, font=FONT_SMALL, text_color=self.MUTED,
                     anchor="w", wraplength=290).pack(anchor="w", pady=(2,6))
        ctk.CTkButton(inner, text="▶  Ouvrir", command=cmd,
                      fg_color=self.RAISED, hover_color=self.CARD, text_color=self.TEXT,
                      font=FONT_SMALL, corner_radius=8, height=30, width=120,
                      border_width=1, border_color=self.BORDER).pack(anchor="w")
        return frame

    # ════════════════════════════════════════════════════════
    # SCORE DE SANTÉ
    # ════════════════════════════════════════════════════════
    def _calc_health_score(self):
        def t():
            self._log("▶  Calcul du score de santé…")
            score = 100; details = []
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                if cpu > 90:   score -= 20; details.append(f"CPU critique ({cpu:.0f}%)")
                elif cpu > 70: score -= 10; details.append(f"CPU élevé ({cpu:.0f}%)")
                if ram > 90:   score -= 20; details.append(f"RAM critique ({ram:.0f}%)")
                elif ram > 75: score -= 10; details.append(f"RAM élevée ({ram:.0f}%)")
                for p in psutil.disk_partitions():
                    try:
                        u = psutil.disk_usage(p.mountpoint)
                        if u.percent > 95:   score -= 20; details.append(f"Disque {p.mountpoint} plein ({u.percent:.0f}%)")
                        elif u.percent > 85: score -= 10; details.append(f"Disque {p.mountpoint} chargé ({u.percent:.0f}%)")
                    except Exception:
                        pass
                uptime_h = (datetime.now()-datetime.fromtimestamp(psutil.boot_time())).total_seconds()/3600
                if uptime_h > 72:  score -= 10; details.append(f"PC allumé {uptime_h:.0f}h")
                n_procs = len(psutil.pids())
                if n_procs > 300: score -= 10; details.append(f"{n_procs} processus actifs")
            except Exception as e:
                self._log_exc("calc_health", e)
            score = max(0, min(100, score))
            self._health_score = score
            color = GREEN if score>=75 else (ORANGE if score>=50 else RED)
            def upd():
                self.lbl_score_big.configure(text=f"{score}/100", text_color=color)
                self.score_bar.set(score/100)
                self.score_bar.configure(progress_color=color)
                self.lbl_score.configure(text=f"Santé  {score}/100", text_color=color)
                msg = "✅  PC en bonne santé !" if not details else "⚠  " + "  •  ".join(details[:3])
                self.lbl_score_detail.configure(text=msg)
            self.after(0, upd)
            self._log(f"   Score : {score}/100")
            for d in details: self._log(f"   ⚠  {d}")
            if not details: self._log("   ✔  Aucun problème\n")
            else: self._log("")
        threading.Thread(target=t, daemon=True).start()

    # ════════════════════════════════════════════════════════
    # GRAPHIQUES CANVAS — CORRIGÉ
    # ════════════════════════════════════════════════════════
    def _draw_canvas_graph(self, key, history, color, bg_col):
        """Dessine le graphique temps réel. Utilise make_alpha_hex au lieu de concaténation naïve."""
        try:
            canvas, col, bg = self._canvas_graphs[key]
            canvas.delete("all")
            data = list(history)[-40:]
            if not data or max(data) == 0:
                return
            W = canvas.winfo_width() or 200
            H = canvas.winfo_height() or 40
            if W < 10: return
            max_val = 100
            step    = W / max(len(data)-1, 1)
            points  = []
            for i, v in enumerate(data):
                x = i * step
                y = H - (v / max_val) * (H - 4) - 2
                points.append((x, y))
            if len(points) >= 2:
                fill_pts = [(points[0][0], H)] + points + [(points[-1][0], H)]
                flat     = [c for pt in fill_pts for c in pt]
                fill_col = make_alpha_hex(col, 35)   # ← corrigé : pas de concaténation "col + 44"
                canvas.create_polygon(flat, fill=fill_col, outline="", smooth=True)
                flat_line = [c for pt in points for c in pt]
                canvas.create_line(flat_line, fill=col, width=2, smooth=True)
        except Exception:
            pass  # Le canvas peut être détruit lors d'un rebuild

    # ════════════════════════════════════════════════════════
    # LOGIQUE SYSTÈME
    # ════════════════════════════════════════════════════════
    def do_infos_all(self):
        self.do_infos_cpu()
        self.after(500, self.do_disque)

    def do_infos_cpu(self):
        def t():
            self._log("▶  Infos CPU & mémoire")
            try:
                cpu_count = psutil.cpu_count(logical=False)
                cpu_log   = psutil.cpu_count(logical=True)
                freq      = psutil.cpu_freq()
                pct       = psutil.cpu_percent(interval=1)
                ram       = psutil.virtual_memory()
                self._log(f"   Processeur     {cpu_count} cœurs physiques / {cpu_log} logiques")
                if freq:
                    self._log(f"   Fréquence      {freq.current:.0f} MHz  (max {freq.max:.0f} MHz)")
                self._log(f"   Utilisation    {pct}%")
                self._log(f"   RAM totale     {ram.total//1024**3} Go")
                self._log(f"   RAM utilisée   {ram.used//1024**2} Mo  ({ram.percent}%)")
                self._log(f"   RAM libre      {ram.available//1024**2} Mo\n")
            except Exception as e:
                self._log_exc("infos_cpu", e)
        threading.Thread(target=t, daemon=True).start()

    def do_infos_gpu(self):
        def t():
            self._log("▶  Infos GPU")
            try:
                proc = subprocess.Popen(
                    "wmic path win32_VideoController get Name,AdapterRAM,DriverVersion /format:list",
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = proc.stdout.read().decode("cp850", errors="replace"); proc.wait()
                for line in out.splitlines():
                    line = line.strip()
                    if not line: continue
                    if line.startswith("Name="):           self._log(f"   Carte  {line[5:]}")
                    elif line.startswith("AdapterRAM="):
                        try: self._log(f"   VRAM   {int(line[11:])//1024**2} Mo")
                        except Exception: pass
                    elif line.startswith("DriverVersion="): self._log(f"   Pilote {line[14:]}")
            except Exception as e:
                self._log_exc("infos_gpu", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_battery(self):
        def t():
            self._log("▶  Batterie")
            try:
                batt = psutil.sensors_battery()
                if batt is None:
                    self._log("   Aucune batterie (PC fixe ou non détectée)")
                else:
                    self._log(f"   Charge  {batt.percent:.1f}%  —  {'En charge' if batt.power_plugged else 'Sur batterie'}")
                    if batt.secsleft > 0 and not batt.power_plugged:
                        self._log(f"   Restant {str(timedelta(seconds=int(batt.secsleft)))}")
            except Exception as e:
                self._log_exc("battery", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_procs(self):
        def t():
            self._log("▶  Top 15 processus (CPU)")
            try:
                procs = sorted(
                    psutil.process_iter(["pid","name","cpu_percent","memory_percent"]),
                    key=lambda p: p.info["cpu_percent"], reverse=True)[:15]
                for p in procs:
                    self._log(f"   {p.info['name']:<35}  CPU {p.info['cpu_percent']:5.1f}%  RAM {p.info['memory_percent']:4.1f}%")
            except Exception as e:
                self._log_exc("do_procs", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_uptime(self):
        def t():
            try:
                boot = datetime.fromtimestamp(psutil.boot_time())
                up   = datetime.now() - boot
                h, r = divmod(int(up.total_seconds()), 3600); m, s = divmod(r, 60)
                self._log(f"▶  Uptime : démarré le {boot.strftime('%d/%m/%Y à %H:%M:%S')}  →  {h}h {m}min {s}s\n")
            except Exception as e:
                self._log_exc("uptime", e)
        threading.Thread(target=t, daemon=True).start()

    def do_temps(self):
        def t():
            self._log("▶  Températures")
            try:
                cmd = ("PowerShell -Command \"Get-WmiObject MSAcpi_ThermalZoneTemperature "
                       "-Namespace root/wmi | Select-Object InstanceName,CurrentTemperature | Format-List\"")
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = proc.stdout.read().decode("cp850", errors="replace"); proc.wait()
                found = False; instance = ""
                for line in out.strip().splitlines():
                    line = line.strip()
                    if line.startswith("InstanceName"):
                        instance = line.split(":",1)[-1].strip()
                    elif line.startswith("CurrentTemperature"):
                        try:
                            c = (int(line.split(":",1)[-1].strip())/10)-273.15
                            self._log(f"   {instance or 'Zone'}  →  {c:.1f} °C"); found=True
                        except Exception:
                            pass
                if not found:
                    self._log("   Non disponible — utilisez HWiNFO64 ou Core Temp")
            except Exception as e:
                self._log_exc("do_temps", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_disque(self):
        def t():
            self._log("▶  Infos disques")
            try:
                for p in psutil.disk_partitions():
                    try:
                        u = psutil.disk_usage(p.mountpoint)
                        self._log(
                            f"   {p.mountpoint}  →  {u.used//1024**3} Go / {u.total//1024**3} Go "
                            f"({u.percent}%)  libre: {u.free//1024**3} Go")
                    except Exception:
                        pass
            except Exception as e:
                self._log_exc("do_disque", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_drivers(self):
        self._run('PowerShell -Command "Get-WmiObject Win32_PnPSignedDriver | '
                  'Select-Object DeviceName,DriverVersion,DriverDate | '
                  'Sort-Object DriverDate -Descending | Format-Table -AutoSize"',
                  "Pilotes installés")

    def do_startup(self):
        self._run("reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                  "Démarrage Windows")

    def do_winver(self):
        self._run("ver", "Version Windows")

    # ════════════════════════════════════════════════════════
    # LOGIQUE NETTOYAGE — avec confirmations
    # ════════════════════════════════════════════════════════
    def do_quick_clean(self, scheduled=False):
        """Nettoyage rapide. Si scheduled=True, pas de confirmation (tâche planifiée)."""
        if not scheduled:
            if not self._confirm(self._t("confirm_clean_temp")):
                return
        self._do_clean_temp_silent()
        self.after(500, self._do_recycle_silent)
        self.after(1000, self.do_flush_dns)

    def do_repair_all(self):
        if not self._confirm(self._t("confirm_repair")):
            return
        steps = [
            (0.12, "Nettoyage Temp…",   lambda: self._run_sync("del /q /f /s %TEMP%\\*","Temp")),
            (0.26, "Vidage corbeille…", lambda: self._run_sync(
                'PowerShell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"',"Corbeille")),
            (0.40, "Cache DNS…",        lambda: self._run_sync("ipconfig /flushdns","DNS")),
            (0.65, "SFC…",             lambda: self._run_sync("sfc /scannow","SFC")),
            (0.90, "DISM…",            lambda: self._run_sync("DISM /Online /Cleanup-Image /RestoreHealth","DISM")),
            (1.00, "✔  Terminé !",     lambda: None),
        ]
        def t():
            self._log("▶  Réparation automatique complète")
            for prog, label, fn in steps:
                self.after(0, lambda p=prog, l=label: (
                    self.repair_progress.set(p),
                    self.repair_label.configure(text=l)))
                fn()
            self._log("✔  Réparation complète terminée\n")
            self.after(3000, lambda: self.repair_label.configure(text="Prêt"))
        threading.Thread(target=t, daemon=True).start()

    def do_clean_temp(self):
        if not self._confirm(self._t("confirm_clean_temp")):
            return
        self._do_clean_temp_silent()

    def _do_clean_temp_silent(self):
        """Nettoyage Temp sans confirmation (utilisé par quick_clean et repair_all)."""
        def t():
            import shutil
            self._log("▶  Nettoyage Temp")
            temp = os.environ.get("TEMP",""); count = 0; errors = 0
            try:
                for f in os.listdir(temp):
                    try:
                        fp = os.path.join(temp, f)
                        if os.path.isfile(fp):   os.remove(fp); count += 1
                        elif os.path.isdir(fp):  shutil.rmtree(fp, ignore_errors=True); count += 1
                    except Exception:
                        errors += 1
            except Exception as e:
                self._log_exc("clean_temp", e)
            self._log(f"   ✔  {count} éléments supprimés ({errors} ignorés)\n")
        threading.Thread(target=t, daemon=True).start()

    def do_big_files(self):
        """Analyse les gros fichiers avec ThreadPoolExecutor — pas de freeze UI."""
        self._cancel_scan = False
        def t():
            self._log("▶  Gros fichiers C: (top 20, patientez…)")
            files = []
            SKIP_DIRS = {"Windows","System Volume Information","$Recycle.Bin",
                         "Program Files","Program Files (x86)"}
            MIN_SIZE_MB = 100  # n'analyse que les fichiers > 100 Mo

            def scan_dir(dirpath):
                results = []
                try:
                    with os.scandir(dirpath) as it:
                        for entry in it:
                            if self._cancel_scan: return results
                            try:
                                if entry.is_file(follow_symlinks=False):
                                    size = entry.stat().st_size
                                    if size >= MIN_SIZE_MB * 1024 * 1024:
                                        results.append((size, entry.path))
                                elif entry.is_dir(follow_symlinks=False):
                                    if entry.name not in SKIP_DIRS:
                                        results.extend(scan_dir(entry.path))
                            except (PermissionError, OSError):
                                pass
                except (PermissionError, OSError):
                    pass
                return results

            try:
                files = scan_dir("C:\\")
                files.sort(reverse=True)
                self._log(f"   Fichiers > {MIN_SIZE_MB} Mo trouvés : {len(files)}")
                for size, path in files[:20]:
                    mb = size / 1024 / 1024
                    label = f"{mb/1024:6.2f} Go" if mb >= 1024 else f"{mb:6.0f} Mo"
                    self._log(f"   {label}  →  {path}")
                if not files:
                    self._log("   ✔  Aucun fichier volumineux trouvé")
            except Exception as e:
                self._log_exc("big_files", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_clean_restore(self):
        if not self._confirm(self._t("confirm_restore")):
            return
        self._run("vssadmin delete shadows /for=C: /oldest /quiet",
                  "Anciens points de restauration")

    def do_winget(self):
        if not self._confirm(self._t("confirm_winget")):
            return
        self._run("winget upgrade --all --include-unknown", "Mise à jour applications")

    def do_chkdsk(self):
        if not self._confirm(self._t("confirm_chkdsk")):
            return
        self._run("chkdsk C: /f /r", "Vérification disque C:")

    def do_recycle(self):
        if not self._confirm(self._t("confirm_recycle")):
            return
        self._do_recycle_silent()

    def _do_recycle_silent(self):
        self._run('PowerShell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"',
                  "Vider corbeille")

    def do_flush_dns(self):
        self._run("ipconfig /flushdns", "Vider cache DNS")

    def do_cleanmgr(self):
        self._open("cleanmgr", "Nettoyage disque Windows")

    # ════════════════════════════════════════════════════════
    # LOGIQUE SÉCURITÉ
    # ════════════════════════════════════════════════════════
    def do_detect_bloatware(self):
        def t():
            self._log("▶  Détection bloatware…")
            try:
                proc = subprocess.Popen(
                    'PowerShell -Command "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName | Format-List"',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = proc.stdout.read().decode("cp850", errors="replace"); proc.wait()
                found = []
                for line in out.splitlines():
                    if "DisplayName" not in line: continue
                    name = line.split(":",1)[-1].strip()
                    if any(b in name.lower() for b in BLOATWARE):
                        found.append(name)
                if found:
                    self._log(f"   ⚠  {len(found)} logiciel(s) suspect(s) :")
                    for f in found: self._log(f"      🔴  {f}")
                else:
                    self._log("   ✔  Aucun logiciel suspect détecté")
            except Exception as e:
                self._log_exc("detect_bloatware", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_scan_virus(self):
        self._run(r'"%ProgramFiles%\Windows Defender\MpCmdRun.exe" -Scan -ScanType 2',
                  "Scan antivirus complet")

    def do_update_defender(self):
        self._run(r'"%ProgramFiles%\Windows Defender\MpCmdRun.exe" -SignatureUpdate',
                  "Mise à jour définitions")

    def do_gen_pwd(self):
        def t():
            chars = string.ascii_letters + string.digits + "!@#$%^&*_-+=?"
            pwd   = "".join(random.SystemRandom().choice(chars) for _ in range(20))
            self._log(f"▶  Mot de passe fort  →  {pwd}")
            self._log("   ✔  Copié dans le presse-papiers\n")
            self.clipboard_clear(); self.clipboard_append(pwd)
        threading.Thread(target=t, daemon=True).start()

    def do_hash_from_entry(self):
        path = self.hash_entry.get().strip()
        if not path:
            self._log("✖  Entrez un chemin de fichier.")
            return
        def t():
            self._log(f"▶  SHA-256 : {path}")
            try:
                sha256 = hashlib.sha256()
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256.update(chunk)
                result = sha256.hexdigest()
                self._log(f"   SHA-256  →  {result}")
                self.clipboard_clear(); self.clipboard_append(result)
                self._log("   ✔  Copié dans le presse-papiers\n")
            except FileNotFoundError:
                self._log(f"   ✖  Fichier introuvable : {path}\n")
            except Exception as e:
                self._log_exc("hash", e)
        threading.Thread(target=t, daemon=True).start()

    def do_netstat(self):
        self._run("netstat -ano", "Connexions réseau actives")

    def do_ports_suspects(self):
        def t():
            self._log("▶  Ports inhabituels")
            NORMAUX = {80,443,8080,8443,3389,22,53,135,445,139,5040,7680}
            try:
                suspects = []
                for c in psutil.net_connections(kind="inet"):
                    if c.laddr and c.laddr.port not in NORMAUX and c.status == "LISTEN":
                        try: name = psutil.Process(c.pid).name() if c.pid else "?"
                        except (psutil.NoSuchProcess, psutil.AccessDenied): name = "?"
                        suspects.append((c.laddr.port, name, c.pid or 0))
                if suspects:
                    for port, proc, pid in sorted(suspects):
                        self._log(f"   Port {port:<6}  →  {proc}  (PID {pid})")
                else:
                    self._log("   ✔  Aucun port inhabituel en écoute")
            except Exception as e:
                self._log_exc("ports_suspects", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_wifi_saved(self):
        """Affiche les réseaux WiFi et mots de passe — avec avertissement explicite."""
        # Avertissement AVANT d'afficher les mots de passe
        if not self._confirm(self._t("warn_wifi")):
            return
        def t():
            self._log("▶  WiFi enregistrés  [⚠ mots de passe en clair]")
            try:
                proc = subprocess.Popen("netsh wlan show profiles", shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = proc.stdout.read().decode("cp850", errors="replace"); proc.wait()
                profiles = [l.split(":")[1].strip() for l in out.splitlines()
                            if "Profil" in l or "Profile" in l or "All User" in l]
                for name in profiles:
                    self._log(f"   Réseau : {name}")
                    try:
                        p2 = subprocess.Popen(
                            f'netsh wlan show profile name="{name}" key=clear',
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        details = p2.stdout.read().decode("cp850", errors="replace"); p2.wait()
                        for l in details.splitlines():
                            if "Contenu de la clé" in l or "Key Content" in l:
                                pwd = l.split(":")[1].strip() if ":" in l else "N/A"
                                self._log(f"             MDP : {pwd}")
                    except Exception:
                        pass
            except Exception as e:
                self._log_exc("wifi_saved", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_admin_accounts(self):
        self._run("net localgroup Administrateurs 2>nul || net localgroup Administrators",
                  "Comptes admin")

    def do_firewall(self):
        self._open("wf.msc", "Pare-feu Windows")

    # ════════════════════════════════════════════════════════
    # LOGIQUE RÉSEAU
    # ════════════════════════════════════════════════════════
    def do_ip_info(self):
        def t():
            self._log("▶  IP")
            try:
                h = socket.gethostname()
                self._log(f"   Nom PC      {h}")
                self._log(f"   IP locale   {socket.gethostbyname(h)}")
            except Exception as e:
                self._log_exc("ip_local", e)
            try:
                ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
                self._log(f"   IP publique {ip}")
            except Exception:
                self._log("   IP publique non disponible (pas de connexion ?)")
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_dns_info(self):
        def t():
            self._log("▶  DNS configurés")
            try:
                proc = subprocess.Popen(
                    'PowerShell -Command "Get-DnsClientServerAddress | '
                    'Where-Object {$_.AddressFamily -eq 2} | '
                    'Format-Table InterfaceAlias,ServerAddresses -AutoSize"',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = proc.stdout.read().decode("cp850", errors="replace"); proc.wait()
                for line in out.splitlines():
                    if line.strip(): self._log(f"   {line}")
            except Exception as e:
                self._log_exc("dns_info", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_ping_custom(self):
        target = self.ping_entry.get().strip()
        if not target:
            self._log("✖  Entrez une adresse IP ou un nom de domaine.")
            return
        self._run(f"ping -n 5 {target}", f"Ping → {target}")

    def do_dns_benchmark(self):
        def t():
            self._log("▶  Benchmark DNS")
            for name, ip in [
                ("Cloudflare (1.1.1.1)","1.1.1.1"),
                ("Google (8.8.8.8)","8.8.8.8"),
                ("OpenDNS (208.67.222.222)","208.67.222.222"),
                ("Quad9 (9.9.9.9)","9.9.9.9"),
            ]:
                try:
                    proc = subprocess.Popen(f"ping -n 4 {ip}", shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    out = proc.stdout.read().decode("cp850", errors="replace"); proc.wait()
                    avg = next((l.strip().split("=")[-1].strip()
                                for l in out.splitlines()
                                if "Moyenne" in l or "Average" in l), "timeout")
                    self._log(f"   {name:<30}  →  {avg}")
                except Exception as e:
                    self._log_exc(f"dns_bench {ip}", e)
            self._log("")
        threading.Thread(target=t, daemon=True).start()

    def do_scan_local(self):
        """Scan réseau local avec ThreadPoolExecutor — ne bloque plus l'UI."""
        self._cancel_scan = False
        def t():
            self._log("▶  Scan réseau local (patientez…)")
            try:
                base  = ".".join(socket.gethostbyname(socket.gethostname()).split(".")[:3])
                self._log(f"   Plage : {base}.1 → {base}.254")
                found = 0
                lock  = threading.Lock()

                def check(i):
                    nonlocal found
                    if self._cancel_scan: return
                    ip = f"{base}.{i}"
                    try:
                        proc = subprocess.Popen(f"ping -n 1 -w 400 {ip}", shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        out = proc.stdout.read().decode("cp850", errors="replace")
                        proc.wait()
                        if "TTL=" in out or "ttl=" in out:
                            try: host = socket.gethostbyaddr(ip)[0]
                            except Exception: host = "?"
                            with lock:
                                found += 1
                                self._log(f"   ✔  {ip:<18} ({host})")
                    except Exception:
                        pass

                # MAX 50 workers au lieu de 254 threads en simultané
                with ThreadPoolExecutor(max_workers=50) as executor:
                    executor.map(check, range(1, 255))

                self._log(f"\n   Total : {found} appareil(s)\n")
            except Exception as e:
                self._log_exc("scan_local", e)
        threading.Thread(target=t, daemon=True).start()

    def do_set_dns(self, primary, secondary):
        def t():
            self._log(f"▶  DNS → {primary} / {secondary}")
            try:
                proc = subprocess.Popen(
                    'PowerShell -Command "(Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | Select-Object -First 1).Name"',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                adapter = proc.stdout.read().decode("cp850", errors="replace").strip(); proc.wait()
                if not adapter:
                    self._log("   ✖  Aucune carte réseau active détectée"); return
                subprocess.run(
                    f"PowerShell -Command \"Set-DnsClientServerAddress -InterfaceAlias '{adapter}' "
                    f"-ServerAddresses ('{primary}','{secondary}')\"",
                    shell=True)
                self._log(f"   ✔  DNS appliqué sur {adapter}")
                subprocess.run("ipconfig /flushdns", shell=True)
                self._log("   ✔  Cache DNS vidé\n")
            except Exception as e:
                self._log_exc("set_dns", e)
        threading.Thread(target=t, daemon=True).start()

    # ════════════════════════════════════════════════════════
    # MODE URGENCE — avec confirmation
    # ════════════════════════════════════════════════════════
    def do_mode_urgence(self):
        if not self._confirm(self._t("confirm_emergency")):
            return
        def t():
            self._log("🚨  MODE URGENCE")
            killed = 0
            try:
                for p in sorted(psutil.process_iter(["pid","name","cpu_percent","memory_percent"]),
                                key=lambda x: x.info["cpu_percent"], reverse=True):
                    if killed >= 5: break
                    if p.info["name"] in PROTECTED_PROCESSES: continue
                    if p.info["cpu_percent"] > 30 or p.info["memory_percent"] > 15:
                        try:
                            p.terminate()
                            self._log(f"   ✔ Fermé : {p.info['name']} (CPU {p.info['cpu_percent']:.0f}%)")
                            killed += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            except Exception as e:
                self._log_exc("mode_urgence_procs", e)

            if killed == 0:
                self._log("   Aucun processus excessif trouvé.")

            try:
                subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
                subprocess.run(
                    'PowerShell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"',
                    shell=True, capture_output=True)
            except Exception as e:
                self._log_exc("mode_urgence_clean", e)

            import shutil
            temp = os.environ.get("TEMP","")
            try:
                for f in os.listdir(temp):
                    try:
                        fp = os.path.join(temp, f)
                        if os.path.isfile(fp):  os.remove(fp)
                        elif os.path.isdir(fp): shutil.rmtree(fp, ignore_errors=True)
                    except Exception:
                        pass
            except Exception:
                pass

            try:
                ram_after = psutil.virtual_memory().percent
                self._log(f"   ✔  Mode urgence terminé — RAM : {ram_after:.0f}%\n")
                toast_notify("PC Tool — Mode urgence", "Ressources libérées avec succès !")
            except Exception:
                pass
        threading.Thread(target=t, daemon=True).start()

    # ════════════════════════════════════════════════════════
    # CAPTURE
    # ════════════════════════════════════════════════════════
    def do_screenshot(self):
        def t():
            self._log("▶  Capture d'écran")
            try:
                desktop = os.path.join(os.environ.get("USERPROFILE",""), "Desktop")
                ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
                fp  = os.path.join(desktop, f"capture_{ts}.png")
                cmd = (
                    f"PowerShell -Command \""
                    f"Add-Type -AssemblyName System.Windows.Forms;"
                    f"$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
                    f"$b=New-Object System.Drawing.Bitmap($s.Width,$s.Height);"
                    f"$g=[System.Drawing.Graphics]::FromImage($b);"
                    f"$g.CopyFromScreen($s.Location,[System.Drawing.Point]::Empty,$s.Size);"
                    f"$b.Save('{fp}');$g.Dispose();$b.Dispose()\""
                )
                subprocess.run(cmd, shell=True)
                self._log(f"   ✔  Sauvegardée : {fp}\n")
            except Exception as e:
                self._log_exc("screenshot", e)
        threading.Thread(target=t, daemon=True).start()

    # ════════════════════════════════════════════════════════
    # BOUCLE TICK
    # ════════════════════════════════════════════════════════
    def _tick(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self._cpu_history.append(cpu)
            self._ram_history.append(ram)

            cur   = psutil.net_io_counters()
            delta = (cur.bytes_sent - self._net_prev.bytes_sent +
                     cur.bytes_recv - self._net_prev.bytes_recv)
            spd   = delta / 1024; unit = "KB/s"
            if spd > 1024: spd /= 1024; unit = "MB/s"
            self._net_history.append(spd)
            self._net_prev = cur

            try: disk_pct = psutil.disk_usage("C:\\").percent
            except Exception: disk_pct = 0

            self.lbl_cpu.configure(text=f"CPU  {cpu:.0f}%",
                text_color=RED if cpu>self.settings["alert_cpu"] else (ORANGE if cpu>70 else self.MUTED))
            self.lbl_ram.configure(text=f"RAM  {ram:.0f}%",
                text_color=RED if ram>self.settings["alert_ram"] else (ORANGE if ram>70 else self.MUTED))
            self.lbl_net.configure(text=f"NET  {spd:.1f} {unit}")
            self.lbl_time.configure(text=datetime.now().strftime("%H:%M:%S"))

            updates = [
                ("cpu",  f"{cpu:.0f}%",        cpu/100,         BLUE,   self._cpu_history),
                ("ram",  f"{ram:.0f}%",         ram/100,         PURPLE, self._ram_history),
                ("disk", f"{disk_pct:.0f}%",    disk_pct/100,   ORANGE, deque([disk_pct]*40)),
                ("net",  f"{spd:.1f} {unit}",  min(1,spd/500), CYAN,   self._net_history),
            ]
            for key, txt, prog, col, hist in updates:
                lbl, bar = self._metric_cards[key]
                lbl.configure(text=txt)
                bar.set(prog)
                self._draw_canvas_graph(key, hist, col,
                    "#111111" if self.settings["theme"]=="dark" else "#e0e0e0")

            # Alertes
            alerts = []
            if cpu      > self.settings["alert_cpu"]:  alerts.append(f"⚠  CPU : {cpu:.0f}%")
            if ram      > self.settings["alert_ram"]:  alerts.append(f"⚠  RAM : {ram:.0f}%")
            if disk_pct > self.settings["alert_disk"]: alerts.append(f"⚠  Disque C: : {disk_pct:.0f}%")
            uptime_h = (datetime.now()-datetime.fromtimestamp(psutil.boot_time())).total_seconds()/3600
            if uptime_h > self.settings["alert_uptime"] and "uptime" not in self._alert_shown:
                alerts.append(f"⚠  PC allumé depuis {uptime_h:.0f}h")
                self._alert_shown.add("uptime")
                toast_notify("PC Tool — Alerte uptime",
                             f"Votre PC est allumé depuis {uptime_h:.0f}h.")

            if cpu > self.settings["alert_cpu"] and "cpu_toast" not in self._alert_shown:
                self._alert_shown.add("cpu_toast")
                toast_notify("PC Tool — Alerte CPU", f"CPU à {cpu:.0f}% — vérifiez les processus.")
            if ram > self.settings["alert_ram"] and "ram_toast" not in self._alert_shown:
                self._alert_shown.add("ram_toast")
                toast_notify("PC Tool — Alerte RAM", f"RAM à {ram:.0f}% — mémoire critique.")

            self.alert_box.configure(state="normal")
            self.alert_box.delete("0.0","end")
            if alerts:
                for a in alerts: self.alert_box.insert("end", f"  {a}\n")
                self.alert_box.configure(text_color=RED)
            else:
                self.alert_box.insert("end","  ✅  Aucune alerte — PC en bonne santé\n")
                self.alert_box.configure(text_color=GREEN)
            self.alert_box.configure(state="disabled")

        except Exception:
            pass  # Ne jamais planter la boucle tick

        rate_ms = max(500, self.settings.get("refresh_rate", 2) * 1000)
        self.after(rate_ms, self._tick)


# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()