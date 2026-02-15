# Scripts & Utilities

This folder contains **build scripts, installers, and utility scripts** for EasyCut development and deployment.

## Available Scripts

### Build & Setup
- **`build.py`** - PyInstaller build script (creates standalone .exe)
- **`setup.py`** - Python package setup script
- **`check_installation.py`** - Validates Python dependencies and environment

### Execution Scripts (Windows)
- **`START.bat`** - Quick launcher for EasyCut (activates venv + runs main.py)
- **`run.bat`** - Alternative execution script

## Usage

### Building Executable
```bash
python scripts/build.py
```

### Checking Installation
```bash
python scripts/check_installation.py
```

### Running from Source (Windows)
```cmd
scripts\START.bat
```

## Requirements
- Python 3.10+
- Virtual environment activated (for most scripts)
- See `requirements.txt` for Python dependencies
