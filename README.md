# 🕐 Clocker - Windows Date & Time Faker

A modern, elegant Windows utility for system time, date, and MAC address manipulation with a beautiful Vercel-inspired dark UI.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/AASoftIR/windows-date-faker?include_prereleases)](https://github.com/AASoftIR/windows-date-faker/releases)

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-❤️-red.svg" alt="Made with love">
</p>

---

## ✨ Features

### 🎯 Date & Time

- **Date & Time Faker** - Change system date and time to any value
- **📅 Calendar Picker** - Visual date selection with popup calendar
- **Quick Presets** - One-click: +1 Day, -1 Day, +1 Week, +1 Month, +1 Year, -1 Year
- **Time Sync Restore** - Re-enable Windows automatic time synchronization
- **Real-time Clock** - Live display of current system time

### 💻 System

- **Computer Name Changer** - Modify Windows computer name
- **Timezone Changer** - Switch between different timezones
- **↺ Reset Buttons** - Quick reset to original values on all sections

### 🌐 Network

- **MAC Address Spoofer** - Change network adapter MAC address
- **🎲 Random MAC Generator** - Generate random valid MAC addresses
- **MAC Reset** - Restore original hardware MAC address
- **Network Information** - View hostname, IP, and adapter details

### 🔒 Security

- **Password Protected** - Locked by default (password: `kali2003`)
- **Administrator Detection** - Shows current privilege level
- **One-click Lock** - Quickly lock the application

---

## 📦 Installation

### Option 1: Download Executable (Recommended)

1. Go to [**Releases**](https://github.com/AASoftIR/windows-date-faker/releases)
2. Download `Clocker.exe`
3. Double-click to run (automatically requests admin privileges)

### Option 2: Run from Source

```bash
# Clone repository
git clone https://github.com/AASoftIR/windows-date-faker.git
cd windows-date-faker

# Install dependencies
pip install -r requirements.txt

# Run (as Administrator)
python clocker.py
```

### Option 3: Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Clocker" --uac-admin clocker.py
```

---

## 🔐 Default Password

```
kali2003
```

---

## ⚡ Quick Start

1. **Launch** - Run `Clocker.exe` as Administrator
2. **Unlock** - Enter password: `kali2003`
3. **Navigate** - Use tabs: ⏰ Date & Time | 💻 System | 🌐 Network | ⚙️ Settings
4. **Modify** - Change date/time, MAC address, computer name, or timezone
5. **Apply** - Click apply buttons to make changes

---

## 🎨 Design

Modern Vercel-inspired dark theme featuring:

- 🌑 Clean dark interface (#0a0a0a)
- 📐 Smooth rounded corners
- 🎨 Color-coded status indicators
- 📱 Responsive tab-based navigation

---

## ⚠️ Important Notes

| ⚡ Requirement    | 📝 Details                                                    |
| ----------------- | ------------------------------------------------------------- |
| **Admin Rights**  | Required for all system modifications                         |
| **System Impact** | May affect scheduled tasks, certificates, time-sensitive apps |
| **Restore Time**  | Use "Sync with Internet" to restore correct time              |
| **MAC Changes**   | Requires adapter restart, may disconnect network briefly      |

---

## 🛠️ Tech Stack

- **GUI Framework:** CustomTkinter
- **Calendar:** tkcalendar
- **Build:** PyInstaller
- **Platform:** Windows 10/11

---

## 📁 Project Structure

```
windows-date-faker/
├── clocker.py          # Main application
├── requirements.txt    # Python dependencies
├── build.bat          # Build script
├── LICENSE            # MIT License
├── README.md          # Documentation
└── .gitignore         # Git ignore rules
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/AASoftIR">AASoftIR</a>
</p>
