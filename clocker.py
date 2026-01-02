"""
Clocker - System Time & Date Faker
A modern, elegant Windows utility for system time manipulation
"""

import customtkinter as ctk
from datetime import datetime, timedelta
import subprocess
import ctypes
import sys
import os
import json
import hashlib
import socket
import winreg
from typing import Optional
import threading
import time
import re
import random
from tkcalendar import Calendar

# ==================== CONFIGURATION ====================
APP_NAME = "Clocker"
APP_VERSION = "1.0.0"
PASSWORD_HASH = hashlib.sha256("kali2003".encode()).hexdigest()
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clocker_config.json")

# ==================== THEME CONFIGURATION ====================
COLORS = {
    "bg_dark": "#0a0a0a",
    "bg_card": "#141414",
    "bg_card_hover": "#1a1a1a",
    "bg_input": "#1e1e1e",
    "border": "#262626",
    "border_focus": "#404040",
    "text_primary": "#fafafa",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "gradient_start": "#3b82f6",
    "gradient_end": "#8b5cf6"
}

# ==================== UTILITY FUNCTIONS ====================

def is_admin() -> bool:
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the script with admin privileges"""
    if sys.platform == 'win32':
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

def set_system_datetime(year: int, month: int, day: int, hour: int, minute: int, second: int) -> tuple[bool, str]:
    """Set the Windows system date and time"""
    try:
        # Disable automatic time sync first
        subprocess.run(
            ['sc', 'stop', 'w32time'],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        subprocess.run(
            ['w32tm', '/unregister'],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Format date and time for Windows commands
        date_str = f"{month:02d}-{day:02d}-{year}"
        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        
        # Set date
        date_result = subprocess.run(
            ['cmd', '/c', 'date', date_str],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Set time
        time_result = subprocess.run(
            ['cmd', '/c', 'time', time_str],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Also use PowerShell as backup method
        ps_command = f"Set-Date -Date '{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}'"
        subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return True, "Date and time changed successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def restore_time_sync() -> tuple[bool, str]:
    """Re-enable Windows time synchronization"""
    try:
        subprocess.run(
            ['w32tm', '/register'],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        subprocess.run(
            ['sc', 'start', 'w32time'],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        subprocess.run(
            ['w32tm', '/resync', '/nowait'],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, "Time sync restored successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_computer_name() -> str:
    """Get current computer name"""
    return socket.gethostname()

def set_computer_name(new_name: str) -> tuple[bool, str]:
    """Change computer name (requires restart)"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "ComputerName", 0, winreg.REG_SZ, new_name)
        winreg.CloseKey(key)
        
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "ComputerName", 0, winreg.REG_SZ, new_name)
        winreg.CloseKey(key)
        
        return True, f"Computer name changed to '{new_name}'. Restart required."
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_timezone_info() -> str:
    """Get current timezone"""
    try:
        result = subprocess.run(
            ['tzutil', '/g'],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.stdout.strip()
    except:
        return "Unknown"

def get_available_timezones() -> list:
    """Get list of available timezones"""
    try:
        result = subprocess.run(
            ['tzutil', '/l'],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.stdout.strip().split('\n')
        timezones = [line.strip() for line in lines if line.strip() and not line.startswith('(')]
        return timezones[:50]  # Limit to 50 for performance
    except:
        return ["UTC", "Pacific Standard Time", "Eastern Standard Time", "Central Standard Time"]

def set_timezone(timezone: str) -> tuple[bool, str]:
    """Set system timezone"""
    try:
        result = subprocess.run(
            ['tzutil', '/s', timezone],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            return True, f"Timezone changed to '{timezone}'"
        return False, f"Failed to change timezone: {result.stderr}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_network_adapters() -> list:
    """Get list of network adapters with their MAC addresses"""
    adapters = []
    try:
        result = subprocess.run(
            ['getmac', '/v', '/fo', 'csv'],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        for line in lines:
            parts = line.replace('"', '').split(',')
            if len(parts) >= 3 and parts[2] != 'N/A':
                adapters.append({
                    'name': parts[0],
                    'transport': parts[1],
                    'mac': parts[2]
                })
    except:
        pass
    return adapters

def generate_random_mac() -> str:
    """Generate a random MAC address"""
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return '-'.join(map(lambda x: "%02X" % x, mac))

def set_mac_address(adapter_name: str, new_mac: str) -> tuple[bool, str]:
    """Set MAC address for a network adapter"""
    try:
        # Clean MAC address format
        new_mac_clean = new_mac.replace('-', '').replace(':', '')
        
        # Find adapter in registry
        reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
        
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        
        for i in range(100):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey_path = f"{reg_path}\\{subkey_name}"
                subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path, 0, winreg.KEY_ALL_ACCESS)
                
                try:
                    desc = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                    if adapter_name.lower() in desc.lower():
                        winreg.SetValueEx(subkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac_clean)
                        winreg.CloseKey(subkey)
                        
                        # Disable and re-enable adapter
                        subprocess.run(
                            ['netsh', 'interface', 'set', 'interface', adapter_name, 'disable'],
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        time.sleep(1)
                        subprocess.run(
                            ['netsh', 'interface', 'set', 'interface', adapter_name, 'enable'],
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        return True, f"MAC address changed to {new_mac}. Adapter restarted."
                except:
                    pass
                winreg.CloseKey(subkey)
            except:
                break
        
        winreg.CloseKey(key)
        return False, "Adapter not found in registry"
    except Exception as e:
        return False, f"Error: {str(e)}"

def reset_mac_address(adapter_name: str) -> tuple[bool, str]:
    """Reset MAC address to original"""
    try:
        reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        
        for i in range(100):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey_path = f"{reg_path}\\{subkey_name}"
                subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path, 0, winreg.KEY_ALL_ACCESS)
                
                try:
                    desc = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                    if adapter_name.lower() in desc.lower():
                        try:
                            winreg.DeleteValue(subkey, "NetworkAddress")
                        except:
                            pass
                        winreg.CloseKey(subkey)
                        
                        subprocess.run(
                            ['netsh', 'interface', 'set', 'interface', adapter_name, 'disable'],
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        time.sleep(1)
                        subprocess.run(
                            ['netsh', 'interface', 'set', 'interface', adapter_name, 'enable'],
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        return True, "MAC address reset to original."
                except:
                    pass
                winreg.CloseKey(subkey)
            except:
                break
        
        winreg.CloseKey(key)
        return False, "Adapter not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def load_config() -> dict:
    """Load saved configuration"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"original_datetime": None, "locked": True}

def save_config(config: dict):
    """Save configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

# ==================== CUSTOM WIDGETS ====================

class ModernButton(ctk.CTkButton):
    """Modern styled button with hover effects"""
    def __init__(self, master, text, command=None, variant="primary", **kwargs):
        colors = {
            "primary": (COLORS["accent"], COLORS["accent_hover"]),
            "secondary": (COLORS["bg_input"], COLORS["border"]),
            "success": (COLORS["success"], "#16a34a"),
            "danger": (COLORS["error"], "#dc2626"),
            "ghost": ("transparent", COLORS["bg_card_hover"])
        }
        
        fg_color, hover_color = colors.get(variant, colors["primary"])
        text_color = COLORS["text_primary"] if variant != "ghost" else COLORS["text_secondary"]
        
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            border_width=1 if variant == "secondary" else 0,
            border_color=COLORS["border"],
            **kwargs
        )

class ModernEntry(ctk.CTkEntry):
    """Modern styled entry field"""
    def __init__(self, master, placeholder="", **kwargs):
        super().__init__(
            master,
            placeholder_text=placeholder,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            corner_radius=8,
            height=42,
            font=ctk.CTkFont(size=14),
            border_width=1,
            **kwargs
        )

class ModernLabel(ctk.CTkLabel):
    """Modern styled label"""
    def __init__(self, master, text, variant="primary", **kwargs):
        colors = {
            "primary": COLORS["text_primary"],
            "secondary": COLORS["text_secondary"],
            "muted": COLORS["text_muted"],
            "accent": COLORS["accent"],
            "success": COLORS["success"],
            "error": COLORS["error"]
        }
        
        super().__init__(
            master,
            text=text,
            text_color=colors.get(variant, COLORS["text_primary"]),
            font=ctk.CTkFont(size=14),
            **kwargs
        )

class Card(ctk.CTkFrame):
    """Modern card container"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )

class StatusIndicator(ctk.CTkFrame):
    """Status indicator with colored dot"""
    def __init__(self, master, text, status="info"):
        super().__init__(master, fg_color="transparent")
        
        colors = {
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"],
            "info": COLORS["accent"]
        }
        
        self.dot = ctk.CTkLabel(
            self,
            text="●",
            text_color=colors.get(status, COLORS["accent"]),
            font=ctk.CTkFont(size=10)
        )
        self.dot.pack(side="left", padx=(0, 6))
        
        self.label = ModernLabel(self, text=text, variant="secondary")
        self.label.pack(side="left")
    
    def update_status(self, text: str, status: str):
        colors = {
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"],
            "info": COLORS["accent"]
        }
        self.dot.configure(text_color=colors.get(status, COLORS["accent"]))
        self.label.configure(text=text)

# ==================== LOGIN SCREEN ====================

class LoginScreen(ctk.CTkFrame):
    """Password protected login screen"""
    def __init__(self, master, on_success):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.on_success = on_success
        self.attempts = 0
        self.setup_ui()
    
    def setup_ui(self):
        # Center container
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo/Icon
        logo_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["accent"], corner_radius=16, width=64, height=64)
        logo_frame.pack(pady=(0, 24))
        logo_frame.pack_propagate(False)
        
        logo_icon = ctk.CTkLabel(
            logo_frame,
            text="🕐",
            font=ctk.CTkFont(size=28),
            text_color=COLORS["text_primary"]
        )
        logo_icon.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ctk.CTkLabel(
            center_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(pady=(0, 8))
        
        # Subtitle
        subtitle = ModernLabel(
            center_frame,
            text="System Time & Date Faker",
            variant="secondary"
        )
        subtitle.pack(pady=(0, 32))
        
        # Card
        card = Card(center_frame)
        card.pack(padx=20, pady=10, fill="x")
        
        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(padx=32, pady=32)
        
        # Lock icon
        lock_label = ctk.CTkLabel(
            card_inner,
            text="🔒",
            font=ctk.CTkFont(size=24)
        )
        lock_label.pack(pady=(0, 16))
        
        # Password label
        pwd_label = ModernLabel(card_inner, text="Enter Password", variant="muted")
        pwd_label.pack(pady=(0, 12))
        
        # Password entry
        self.password_entry = ModernEntry(card_inner, placeholder="••••••••", width=280)
        self.password_entry.configure(show="•")
        self.password_entry.pack(pady=(0, 16))
        self.password_entry.bind("<Return>", lambda e: self.verify_password())
        
        # Error message
        self.error_label = ModernLabel(card_inner, text="", variant="error")
        self.error_label.pack(pady=(0, 8))
        
        # Login button
        self.login_btn = ModernButton(
            card_inner,
            text="Unlock",
            command=self.verify_password,
            width=280
        )
        self.login_btn.pack(pady=(8, 0))
        
        # Footer
        footer = ModernLabel(
            center_frame,
            text=f"v{APP_VERSION} • Requires Administrator",
            variant="muted"
        )
        footer.pack(pady=(24, 0))
        
        # Focus password entry
        self.after(100, lambda: self.password_entry.focus())
    
    def verify_password(self):
        password = self.password_entry.get()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash == PASSWORD_HASH:
            self.on_success()
        else:
            self.attempts += 1
            self.error_label.configure(text=f"Incorrect password ({self.attempts}/5)")
            self.password_entry.delete(0, 'end')
            
            if self.attempts >= 5:
                self.error_label.configure(text="Too many attempts. Please wait...")
                self.login_btn.configure(state="disabled")
                self.after(30000, self.reset_attempts)
    
    def reset_attempts(self):
        self.attempts = 0
        self.error_label.configure(text="")
        self.login_btn.configure(state="normal")

# ==================== MAIN APPLICATION ====================

class MainApp(ctk.CTkFrame):
    """Main application interface"""
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.config = load_config()
        self.current_time_label = None
        self.running = True
        self.setup_ui()
        self.start_clock_update()
    
    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=70)
        header.pack(fill="x", padx=24, pady=(16, 0))
        header.pack_propagate(False)
        
        # Logo and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="y")
        
        logo_small = ctk.CTkLabel(
            title_frame,
            text="🕐",
            font=ctk.CTkFont(size=24)
        )
        logo_small.pack(side="left", padx=(0, 12))
        
        title = ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(side="left")
        
        # Admin status
        admin_status = StatusIndicator(
            header,
            "Administrator" if is_admin() else "Standard User",
            "success" if is_admin() else "warning"
        )
        admin_status.pack(side="right", pady=20)
        
        # Navigation tabs
        self.tab_view = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_dark"],
            segmented_button_fg_color=COLORS["bg_card"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_card"],
            segmented_button_unselected_hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["text_secondary"],
            corner_radius=12
        )
        self.tab_view.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Create tabs
        self.datetime_tab = self.tab_view.add("⏰ Date & Time")
        self.system_tab = self.tab_view.add("💻 System")
        self.network_tab = self.tab_view.add("🌐 Network")
        self.settings_tab = self.tab_view.add("⚙️ Settings")
        
        self.setup_datetime_tab()
        self.setup_system_tab()
        self.setup_network_tab()
        self.setup_settings_tab()
    
    def setup_datetime_tab(self):
        """Setup Date & Time faker tab"""
        # Main container with scroll
        container = ctk.CTkScrollableFrame(
            self.datetime_tab,
            fg_color="transparent"
        )
        container.pack(fill="both", expand=True)
        
        # Current Time Card
        current_card = Card(container)
        current_card.pack(fill="x", pady=(0, 16))
        
        current_inner = ctk.CTkFrame(current_card, fg_color="transparent")
        current_inner.pack(padx=24, pady=20, fill="x")
        
        current_title = ctk.CTkLabel(
            current_inner,
            text="Current System Time",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_muted"]
        )
        current_title.pack(anchor="w")
        
        self.current_time_label = ctk.CTkLabel(
            current_inner,
            text="Loading...",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.current_time_label.pack(anchor="w", pady=(8, 0))
        
        self.current_date_label = ctk.CTkLabel(
            current_inner,
            text="",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_secondary"]
        )
        self.current_date_label.pack(anchor="w")
        
        # Set Custom Time Card
        custom_card = Card(container)
        custom_card.pack(fill="x", pady=(0, 16))
        
        custom_inner = ctk.CTkFrame(custom_card, fg_color="transparent")
        custom_inner.pack(padx=24, pady=20, fill="x")
        
        custom_title_frame = ctk.CTkFrame(custom_inner, fg_color="transparent")
        custom_title_frame.pack(fill="x", pady=(0, 16))
        
        custom_title = ctk.CTkLabel(
            custom_title_frame,
            text="Set Custom Date & Time",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        custom_title.pack(side="left")
        
        ModernButton(
            custom_title_frame,
            text="↺ Reset",
            command=self.reset_datetime_fields,
            variant="ghost",
            width=80
        ).pack(side="right")
        
        # Calendar picker button and date display
        cal_frame = ctk.CTkFrame(custom_inner, fg_color="transparent")
        cal_frame.pack(fill="x", pady=(0, 12))
        
        ModernButton(
            cal_frame,
            text="📅 Pick Date",
            command=self.open_calendar,
            variant="secondary",
            width=120
        ).pack(side="left", padx=(0, 12))
        
        self.selected_date_label = ModernLabel(cal_frame, text="", variant="accent")
        self.selected_date_label.pack(side="left")
        
        # Date inputs row
        date_frame = ctk.CTkFrame(custom_inner, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 12))
        
        # Year
        year_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        year_frame.pack(side="left", padx=(0, 12))
        ModernLabel(year_frame, text="Year", variant="muted").pack(anchor="w")
        self.year_entry = ModernEntry(year_frame, placeholder="2026", width=100)
        self.year_entry.pack()
        self.year_entry.insert(0, str(datetime.now().year))
        
        # Month
        month_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        month_frame.pack(side="left", padx=(0, 12))
        ModernLabel(month_frame, text="Month", variant="muted").pack(anchor="w")
        self.month_entry = ModernEntry(month_frame, placeholder="01", width=80)
        self.month_entry.pack()
        self.month_entry.insert(0, str(datetime.now().month).zfill(2))
        
        # Day
        day_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        day_frame.pack(side="left", padx=(0, 12))
        ModernLabel(day_frame, text="Day", variant="muted").pack(anchor="w")
        self.day_entry = ModernEntry(day_frame, placeholder="15", width=80)
        self.day_entry.pack()
        self.day_entry.insert(0, str(datetime.now().day).zfill(2))
        
        # Time inputs row
        time_frame = ctk.CTkFrame(custom_inner, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 16))
        
        # Hour
        hour_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        hour_frame.pack(side="left", padx=(0, 12))
        ModernLabel(hour_frame, text="Hour", variant="muted").pack(anchor="w")
        self.hour_entry = ModernEntry(hour_frame, placeholder="12", width=80)
        self.hour_entry.pack()
        self.hour_entry.insert(0, str(datetime.now().hour).zfill(2))
        
        # Minute
        minute_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        minute_frame.pack(side="left", padx=(0, 12))
        ModernLabel(minute_frame, text="Minute", variant="muted").pack(anchor="w")
        self.minute_entry = ModernEntry(minute_frame, placeholder="30", width=80)
        self.minute_entry.pack()
        self.minute_entry.insert(0, str(datetime.now().minute).zfill(2))
        
        # Second
        second_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        second_frame.pack(side="left", padx=(0, 12))
        ModernLabel(second_frame, text="Second", variant="muted").pack(anchor="w")
        self.second_entry = ModernEntry(second_frame, placeholder="00", width=80)
        self.second_entry.pack()
        self.second_entry.insert(0, str(datetime.now().second).zfill(2))
        
        # Quick presets
        presets_title = ModernLabel(custom_inner, text="Quick Presets", variant="muted")
        presets_title.pack(anchor="w", pady=(8, 8))
        
        presets_frame = ctk.CTkFrame(custom_inner, fg_color="transparent")
        presets_frame.pack(fill="x", pady=(0, 16))
        
        presets = [
            ("+1 Day", lambda: self.apply_offset(days=1)),
            ("-1 Day", lambda: self.apply_offset(days=-1)),
            ("+1 Week", lambda: self.apply_offset(weeks=1)),
            ("+1 Month", lambda: self.apply_offset(days=30)),
            ("+1 Year", lambda: self.apply_offset(days=365)),
            ("-1 Year", lambda: self.apply_offset(days=-365)),
        ]
        
        for text, cmd in presets:
            btn = ModernButton(presets_frame, text=text, command=cmd, variant="secondary", width=100)
            btn.pack(side="left", padx=(0, 8))
        
        # Action buttons
        action_frame = ctk.CTkFrame(custom_inner, fg_color="transparent")
        action_frame.pack(fill="x", pady=(8, 0))
        
        self.apply_btn = ModernButton(
            action_frame,
            text="✓ Apply Changes",
            command=self.apply_datetime,
            variant="primary",
            width=160
        )
        self.apply_btn.pack(side="left", padx=(0, 12))
        
        self.restore_btn = ModernButton(
            action_frame,
            text="↻ Sync with Internet",
            command=self.restore_datetime,
            variant="secondary",
            width=160
        )
        self.restore_btn.pack(side="left")
        
        # Status message
        self.datetime_status = StatusIndicator(custom_inner, "Ready", "info")
        self.datetime_status.pack(anchor="w", pady=(16, 0))
        
        # Warning card
        warning_card = Card(container)
        warning_card.pack(fill="x")
        
        warning_inner = ctk.CTkFrame(warning_card, fg_color="transparent")
        warning_inner.pack(padx=24, pady=16, fill="x")
        
        warning_icon = ctk.CTkLabel(
            warning_inner,
            text="⚠️",
            font=ctk.CTkFont(size=18)
        )
        warning_icon.pack(side="left", padx=(0, 12))
        
        warning_text = ModernLabel(
            warning_inner,
            text="Changing system time may affect scheduled tasks, certificates, and time-sensitive applications.",
            variant="muted"
        )
        warning_text.pack(side="left", fill="x", expand=True)
    
    def setup_system_tab(self):
        """Setup System faker tab"""
        container = ctk.CTkScrollableFrame(self.system_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Computer Name Card
        name_card = Card(container)
        name_card.pack(fill="x", pady=(0, 16))
        
        name_inner = ctk.CTkFrame(name_card, fg_color="transparent")
        name_inner.pack(padx=24, pady=20, fill="x")
        
        name_title_frame = ctk.CTkFrame(name_inner, fg_color="transparent")
        name_title_frame.pack(fill="x", pady=(0, 4))
        
        name_title = ctk.CTkLabel(
            name_title_frame,
            text="Computer Name",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        name_title.pack(side="left")
        
        ModernButton(
            name_title_frame,
            text="↺ Reset",
            command=self.reset_computer_name,
            variant="ghost",
            width=80
        ).pack(side="right")
        
        self.original_computer_name = get_computer_name()
        current_name = ModernLabel(
            name_inner,
            text=f"Current: {get_computer_name()}",
            variant="secondary"
        )
        current_name.pack(anchor="w", pady=(0, 12))
        
        name_input_frame = ctk.CTkFrame(name_inner, fg_color="transparent")
        name_input_frame.pack(fill="x")
        
        self.computer_name_entry = ModernEntry(name_input_frame, placeholder="New computer name", width=300)
        self.computer_name_entry.pack(side="left", padx=(0, 12))
        
        ModernButton(
            name_input_frame,
            text="Change Name",
            command=self.change_computer_name,
            variant="secondary"
        ).pack(side="left")
        
        self.name_status = ModernLabel(name_inner, text="", variant="muted")
        self.name_status.pack(anchor="w", pady=(12, 0))
        
        # Timezone Card
        tz_card = Card(container)
        tz_card.pack(fill="x", pady=(0, 16))
        
        tz_inner = ctk.CTkFrame(tz_card, fg_color="transparent")
        tz_inner.pack(padx=24, pady=20, fill="x")
        
        tz_title_frame = ctk.CTkFrame(tz_inner, fg_color="transparent")
        tz_title_frame.pack(fill="x", pady=(0, 4))
        
        tz_title = ctk.CTkLabel(
            tz_title_frame,
            text="Timezone",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        tz_title.pack(side="left")
        
        ModernButton(
            tz_title_frame,
            text="↺ Reset",
            command=self.reset_timezone,
            variant="ghost",
            width=80
        ).pack(side="right")
        
        self.original_timezone = get_timezone_info()
        self.current_tz_label = ModernLabel(
            tz_inner,
            text=f"Current: {get_timezone_info()}",
            variant="secondary"
        )
        self.current_tz_label.pack(anchor="w", pady=(0, 12))
        
        tz_input_frame = ctk.CTkFrame(tz_inner, fg_color="transparent")
        tz_input_frame.pack(fill="x")
        
        timezones = get_available_timezones()
        self.timezone_combo = ctk.CTkComboBox(
            tz_input_frame,
            values=timezones,
            width=300,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["text_primary"]
        )
        self.timezone_combo.pack(side="left", padx=(0, 12))
        self.timezone_combo.set(get_timezone_info())
        
        ModernButton(
            tz_input_frame,
            text="Set Timezone",
            command=self.change_timezone,
            variant="secondary"
        ).pack(side="left")
        
        self.tz_status = ModernLabel(tz_inner, text="", variant="muted")
        self.tz_status.pack(anchor="w", pady=(12, 0))
    
    def setup_network_tab(self):
        """Setup Network info tab"""
        container = ctk.CTkScrollableFrame(self.network_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Network Info Card
        net_card = Card(container)
        net_card.pack(fill="x", pady=(0, 16))
        
        net_inner = ctk.CTkFrame(net_card, fg_color="transparent")
        net_inner.pack(padx=24, pady=20, fill="x")
        
        net_title = ctk.CTkLabel(
            net_inner,
            text="Network Information",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        net_title.pack(anchor="w", pady=(0, 16))
        
        # Get network info
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "Unknown"
        
        info_items = [
            ("Hostname", hostname),
            ("Local IP", local_ip),
            ("Timezone", get_timezone_info()),
        ]
        
        for label, value in info_items:
            item_frame = ctk.CTkFrame(net_inner, fg_color="transparent")
            item_frame.pack(fill="x", pady=4)
            
            ModernLabel(item_frame, text=label, variant="muted", width=120, anchor="w").pack(side="left")
            ModernLabel(item_frame, text=value, variant="primary").pack(side="left")
        
        # MAC Address Card
        mac_card = Card(container)
        mac_card.pack(fill="x", pady=(0, 16))
        
        mac_inner = ctk.CTkFrame(mac_card, fg_color="transparent")
        mac_inner.pack(padx=24, pady=20, fill="x")
        
        mac_title_frame = ctk.CTkFrame(mac_inner, fg_color="transparent")
        mac_title_frame.pack(fill="x", pady=(0, 12))
        
        mac_title = ctk.CTkLabel(
            mac_title_frame,
            text="MAC Address Spoofer",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        mac_title.pack(side="left")
        
        ModernButton(
            mac_title_frame,
            text="↺ Reset MAC",
            command=self.reset_mac,
            variant="ghost",
            width=100
        ).pack(side="right")
        
        # Adapter selection
        adapter_frame = ctk.CTkFrame(mac_inner, fg_color="transparent")
        adapter_frame.pack(fill="x", pady=(0, 12))
        
        ModernLabel(adapter_frame, text="Network Adapter", variant="muted").pack(anchor="w")
        
        adapters = get_network_adapters()
        adapter_names = [a['name'] for a in adapters] if adapters else ["No adapters found"]
        
        self.adapter_combo = ctk.CTkComboBox(
            adapter_frame,
            values=adapter_names,
            width=400,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["text_primary"],
            command=self.on_adapter_select
        )
        self.adapter_combo.pack(anchor="w", pady=(4, 0))
        
        # Current MAC display
        self.current_mac_label = ModernLabel(mac_inner, text="Current MAC: --", variant="secondary")
        self.current_mac_label.pack(anchor="w", pady=(8, 12))
        
        # Update current MAC display
        if adapters:
            self.adapter_combo.set(adapters[0]['name'])
            self.current_mac_label.configure(text=f"Current MAC: {adapters[0]['mac']}")
        
        # New MAC input
        new_mac_frame = ctk.CTkFrame(mac_inner, fg_color="transparent")
        new_mac_frame.pack(fill="x", pady=(0, 12))
        
        ModernLabel(new_mac_frame, text="New MAC Address", variant="muted").pack(anchor="w")
        
        mac_input_row = ctk.CTkFrame(new_mac_frame, fg_color="transparent")
        mac_input_row.pack(fill="x", pady=(4, 0))
        
        self.mac_entry = ModernEntry(mac_input_row, placeholder="XX-XX-XX-XX-XX-XX", width=200)
        self.mac_entry.pack(side="left", padx=(0, 12))
        
        ModernButton(
            mac_input_row,
            text="🎲 Random",
            command=self.generate_random_mac,
            variant="secondary",
            width=100
        ).pack(side="left", padx=(0, 12))
        
        ModernButton(
            mac_input_row,
            text="Apply MAC",
            command=self.apply_mac,
            variant="primary",
            width=100
        ).pack(side="left")
        
        self.mac_status = ModernLabel(mac_inner, text="", variant="muted")
        self.mac_status.pack(anchor="w", pady=(8, 0))
        
        # DNS Card
        dns_card = Card(container)
        dns_card.pack(fill="x", pady=(0, 16))
        
        dns_inner = ctk.CTkFrame(dns_card, fg_color="transparent")
        dns_inner.pack(padx=24, pady=20, fill="x")
        
        dns_title = ctk.CTkLabel(
            dns_inner,
            text="DNS Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        dns_title.pack(anchor="w", pady=(0, 8))
        
        dns_note = ModernLabel(
            dns_inner,
            text="DNS manipulation requires manual network adapter configuration.",
            variant="muted"
        )
        dns_note.pack(anchor="w")
    
    def setup_settings_tab(self):
        """Setup Settings tab"""
        container = ctk.CTkScrollableFrame(self.settings_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # About Card
        about_card = Card(container)
        about_card.pack(fill="x", pady=(0, 16))
        
        about_inner = ctk.CTkFrame(about_card, fg_color="transparent")
        about_inner.pack(padx=24, pady=20, fill="x")
        
        about_title = ctk.CTkLabel(
            about_inner,
            text="About Clocker",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        about_title.pack(anchor="w", pady=(0, 12))
        
        about_info = [
            ("Version", APP_VERSION),
            ("Platform", "Windows"),
            ("Developer", "Clocker Team"),
        ]
        
        for label, value in about_info:
            item_frame = ctk.CTkFrame(about_inner, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            ModernLabel(item_frame, text=f"{label}:", variant="muted", width=100, anchor="w").pack(side="left")
            ModernLabel(item_frame, text=value, variant="secondary").pack(side="left")
        
        # Admin Card
        admin_card = Card(container)
        admin_card.pack(fill="x", pady=(0, 16))
        
        admin_inner = ctk.CTkFrame(admin_card, fg_color="transparent")
        admin_inner.pack(padx=24, pady=20, fill="x")
        
        admin_title = ctk.CTkLabel(
            admin_inner,
            text="Administrator Privileges",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        admin_title.pack(anchor="w", pady=(0, 8))
        
        if is_admin():
            StatusIndicator(admin_inner, "Running with administrator privileges", "success").pack(anchor="w")
        else:
            StatusIndicator(admin_inner, "Running without administrator privileges", "warning").pack(anchor="w", pady=(0, 12))
            ModernButton(
                admin_inner,
                text="Restart as Administrator",
                command=run_as_admin,
                variant="primary"
            ).pack(anchor="w")
        
        # Lock App Card
        lock_card = Card(container)
        lock_card.pack(fill="x")
        
        lock_inner = ctk.CTkFrame(lock_card, fg_color="transparent")
        lock_inner.pack(padx=24, pady=20, fill="x")
        
        lock_title = ctk.CTkLabel(
            lock_inner,
            text="Security",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lock_title.pack(anchor="w", pady=(0, 12))
        
        ModernButton(
            lock_inner,
            text="🔒 Lock Application",
            command=self.lock_app,
            variant="danger"
        ).pack(anchor="w")
    
    def apply_offset(self, days=0, weeks=0):
        """Apply time offset to current entries"""
        try:
            current = datetime.now() + timedelta(days=days, weeks=weeks)
            self.year_entry.delete(0, 'end')
            self.year_entry.insert(0, str(current.year))
            self.month_entry.delete(0, 'end')
            self.month_entry.insert(0, str(current.month).zfill(2))
            self.day_entry.delete(0, 'end')
            self.day_entry.insert(0, str(current.day).zfill(2))
            self.hour_entry.delete(0, 'end')
            self.hour_entry.insert(0, str(current.hour).zfill(2))
            self.minute_entry.delete(0, 'end')
            self.minute_entry.insert(0, str(current.minute).zfill(2))
            self.second_entry.delete(0, 'end')
            self.second_entry.insert(0, str(current.second).zfill(2))
        except Exception as e:
            self.datetime_status.update_status(f"Error: {str(e)}", "error")
    
    def apply_datetime(self):
        """Apply the custom date and time"""
        if not is_admin():
            self.datetime_status.update_status("Administrator privileges required!", "error")
            return
        
        try:
            year = int(self.year_entry.get())
            month = int(self.month_entry.get())
            day = int(self.day_entry.get())
            hour = int(self.hour_entry.get())
            minute = int(self.minute_entry.get())
            second = int(self.second_entry.get())
            
            # Validate
            datetime(year, month, day, hour, minute, second)
            
            success, message = set_system_datetime(year, month, day, hour, minute, second)
            
            if success:
                self.datetime_status.update_status(message, "success")
            else:
                self.datetime_status.update_status(message, "error")
                
        except ValueError as e:
            self.datetime_status.update_status(f"Invalid date/time: {str(e)}", "error")
    
    def restore_datetime(self):
        """Restore time sync with internet"""
        if not is_admin():
            self.datetime_status.update_status("Administrator privileges required!", "error")
            return
        
        success, message = restore_time_sync()
        if success:
            self.datetime_status.update_status(message, "success")
        else:
            self.datetime_status.update_status(message, "error")
    
    def change_computer_name(self):
        """Change computer name"""
        new_name = self.computer_name_entry.get().strip()
        if not new_name:
            self.name_status.configure(text="Please enter a name", text_color=COLORS["error"])
            return
        
        if not is_admin():
            self.name_status.configure(text="Administrator privileges required!", text_color=COLORS["error"])
            return
        
        success, message = set_computer_name(new_name)
        color = COLORS["success"] if success else COLORS["error"]
        self.name_status.configure(text=message, text_color=color)
    
    def change_timezone(self):
        """Change timezone"""
        timezone = self.timezone_combo.get()
        if not timezone:
            self.tz_status.configure(text="Please select a timezone", text_color=COLORS["error"])
            return
        
        if not is_admin():
            self.tz_status.configure(text="Administrator privileges required!", text_color=COLORS["error"])
            return
        
        success, message = set_timezone(timezone)
        color = COLORS["success"] if success else COLORS["error"]
        self.tz_status.configure(text=message, text_color=color)
        
        if success:
            self.current_tz_label.configure(text=f"Current: {timezone}")
    
    def open_calendar(self):
        """Open calendar picker dialog"""
        cal_window = ctk.CTkToplevel(self)
        cal_window.title("Select Date")
        cal_window.geometry("320x350")
        cal_window.configure(fg_color=COLORS["bg_dark"])
        cal_window.transient(self.master)
        cal_window.grab_set()
        
        # Center the window
        cal_window.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 160
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 175
        cal_window.geometry(f"+{x}+{y}")
        
        cal = Calendar(
            cal_window,
            selectmode='day',
            year=int(self.year_entry.get() or datetime.now().year),
            month=int(self.month_entry.get() or datetime.now().month),
            day=int(self.day_entry.get() or datetime.now().day),
            background=COLORS["bg_card"],
            foreground=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["text_primary"],
            normalbackground=COLORS["bg_dark"],
            normalforeground=COLORS["text_primary"],
            weekendbackground=COLORS["bg_dark"],
            weekendforeground=COLORS["text_secondary"],
            headersbackground=COLORS["bg_card"],
            headersforeground=COLORS["accent"],
            bordercolor=COLORS["border"]
        )
        cal.pack(padx=20, pady=20, fill="both", expand=True)
        
        def select_date():
            selected = cal.selection_get()
            self.year_entry.delete(0, 'end')
            self.year_entry.insert(0, str(selected.year))
            self.month_entry.delete(0, 'end')
            self.month_entry.insert(0, str(selected.month).zfill(2))
            self.day_entry.delete(0, 'end')
            self.day_entry.insert(0, str(selected.day).zfill(2))
            self.selected_date_label.configure(text=f"Selected: {selected.strftime('%B %d, %Y')}")
            cal_window.destroy()
        
        ModernButton(
            cal_window,
            text="Select Date",
            command=select_date,
            variant="primary",
            width=280
        ).pack(pady=(0, 20))
    
    def reset_datetime_fields(self):
        """Reset datetime fields to current time"""
        now = datetime.now()
        self.year_entry.delete(0, 'end')
        self.year_entry.insert(0, str(now.year))
        self.month_entry.delete(0, 'end')
        self.month_entry.insert(0, str(now.month).zfill(2))
        self.day_entry.delete(0, 'end')
        self.day_entry.insert(0, str(now.day).zfill(2))
        self.hour_entry.delete(0, 'end')
        self.hour_entry.insert(0, str(now.hour).zfill(2))
        self.minute_entry.delete(0, 'end')
        self.minute_entry.insert(0, str(now.minute).zfill(2))
        self.second_entry.delete(0, 'end')
        self.second_entry.insert(0, str(now.second).zfill(2))
        self.selected_date_label.configure(text="")
        self.datetime_status.update_status("Fields reset to current time", "info")
    
    def reset_computer_name(self):
        """Reset computer name field"""
        self.computer_name_entry.delete(0, 'end')
        self.name_status.configure(text=f"Original name: {self.original_computer_name}", text_color=COLORS["text_muted"])
    
    def reset_timezone(self):
        """Reset timezone to original"""
        self.timezone_combo.set(self.original_timezone)
        self.tz_status.configure(text=f"Reset to: {self.original_timezone}", text_color=COLORS["text_muted"])
    
    def on_adapter_select(self, adapter_name):
        """Handle adapter selection"""
        adapters = get_network_adapters()
        for adapter in adapters:
            if adapter['name'] == adapter_name:
                self.current_mac_label.configure(text=f"Current MAC: {adapter['mac']}")
                break
    
    def generate_random_mac(self):
        """Generate random MAC and fill entry"""
        mac = generate_random_mac()
        self.mac_entry.delete(0, 'end')
        self.mac_entry.insert(0, mac)
    
    def apply_mac(self):
        """Apply new MAC address"""
        if not is_admin():
            self.mac_status.configure(text="Administrator privileges required!", text_color=COLORS["error"])
            return
        
        adapter = self.adapter_combo.get()
        new_mac = self.mac_entry.get().strip()
        
        if not new_mac:
            self.mac_status.configure(text="Please enter a MAC address", text_color=COLORS["error"])
            return
        
        # Validate MAC format
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2}$|^[0-9A-Fa-f]{12}$')
        if not mac_pattern.match(new_mac):
            self.mac_status.configure(text="Invalid MAC format. Use XX-XX-XX-XX-XX-XX", text_color=COLORS["error"])
            return
        
        self.mac_status.configure(text="Applying MAC address...", text_color=COLORS["warning"])
        self.update()
        
        success, message = set_mac_address(adapter, new_mac)
        color = COLORS["success"] if success else COLORS["error"]
        self.mac_status.configure(text=message, text_color=color)
        
        if success:
            self.current_mac_label.configure(text=f"Current MAC: {new_mac}")
    
    def reset_mac(self):
        """Reset MAC address to original"""
        if not is_admin():
            self.mac_status.configure(text="Administrator privileges required!", text_color=COLORS["error"])
            return
        
        adapter = self.adapter_combo.get()
        self.mac_status.configure(text="Resetting MAC address...", text_color=COLORS["warning"])
        self.update()
        
        success, message = reset_mac_address(adapter)
        color = COLORS["success"] if success else COLORS["error"]
        self.mac_status.configure(text=message, text_color=color)
        
        if success:
            # Refresh adapter info
            self.after(2000, lambda: self.on_adapter_select(adapter))
    
    def lock_app(self):
        """Lock the application"""
        self.master.show_login()
    
    def start_clock_update(self):
        """Start updating the clock display"""
        def update():
            while self.running:
                try:
                    now = datetime.now()
                    if self.current_time_label:
                        self.current_time_label.configure(
                            text=now.strftime("%H:%M:%S")
                        )
                    if self.current_date_label:
                        self.current_date_label.configure(
                            text=now.strftime("%A, %B %d, %Y")
                        )
                except:
                    pass
                time.sleep(1)
        
        self.clock_thread = threading.Thread(target=update, daemon=True)
        self.clock_thread.start()
    
    def stop(self):
        """Stop the clock update thread"""
        self.running = False

# ==================== APPLICATION WINDOW ====================

class ClockerApp(ctk.CTk):
    """Main application window"""
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(APP_NAME)
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure background
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Set icon (if available)
        try:
            self.iconbitmap(default='')
        except:
            pass
        
        self.current_view = None
        self.show_login()
        
        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def show_login(self):
        """Show login screen"""
        if self.current_view:
            if hasattr(self.current_view, 'stop'):
                self.current_view.stop()
            self.current_view.destroy()
        
        self.current_view = LoginScreen(self, self.show_main)
        self.current_view.pack(fill="both", expand=True)
    
    def show_main(self):
        """Show main application"""
        if self.current_view:
            self.current_view.destroy()
        
        self.current_view = MainApp(self)
        self.current_view.pack(fill="both", expand=True)
    
    def on_close(self):
        """Handle window close"""
        if self.current_view and hasattr(self.current_view, 'stop'):
            self.current_view.stop()
        self.destroy()

# ==================== ENTRY POINT ====================

def main():
    # Check for admin privileges on startup
    if not is_admin():
        # Show warning but still allow running
        print("Warning: Running without administrator privileges.")
        print("Some features will be limited.")
    
    app = ClockerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
