"""
Build Script for EasyCut
Creates standalone executable with embedded OAuth credentials

Usage:
    python scripts/build.py
    
Output:
    dist/EasyCut.exe - Standalone Windows executable
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path


class BuildError(Exception):
    """Custom exception for build errors"""
    pass


def load_build_config() -> dict:
    """Load OAuth credentials from build_config.json"""
    config_file = Path("build_config.json")
    
    if not config_file.exists():
        raise BuildError(
            "build_config.json not found!\n"
            "This file contains the OAuth credentials for packaged releases.\n"
            "Please create it with your Google OAuth credentials."
        )
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'oauth_credentials' not in config:
            raise BuildError("build_config.json missing 'oauth_credentials' key")
        
        return config
    
    except json.JSONDecodeError as e:
        raise BuildError(f"Invalid JSON in build_config.json: {e}")


def create_packaged_oauth_manager(credentials: dict, temp_dir: Path) -> Path:
    """Create a version of oauth_manager.py with embedded credentials"""
    src_file = Path("src/oauth_manager.py")
    
    if not src_file.exists():
        raise BuildError(f"Source file not found: {src_file}")
    
    # Read original file
    with open(src_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create credentials constant string
    credentials_json = json.dumps(credentials, indent=4)
    embedded_const = f"\n# Embedded credentials for packaged release\n_EMBEDDED_CREDENTIALS = {credentials_json}\n"
    
    # Insert after imports
    import_end = content.find('class OAuthError')
    if import_end == -1:
        raise BuildError("Could not find insertion point in oauth_manager.py")
    
    modified_content = content[:import_end] + embedded_const + content[import_end:]
    
    # Modify __init__ to use embedded credentials by default
    modified_content = modified_content.replace(
        "self._credentials_data = credentials_data",
        "self._credentials_data = credentials_data or _EMBEDDED_CREDENTIALS"
    )
    
    # Write to temp directory
    temp_file = temp_dir / "oauth_manager.py"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    return temp_file


def prepare_build_directory() -> Path:
    """Prepare temporary build directory"""
    temp_dir = Path("build_temp")
    
    # Clean if exists
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    temp_dir.mkdir()
    
    # Copy all necessary files
    src_dir = Path("src")
    for file in src_dir.glob("*.py"):
        if file.name != "oauth_manager.py":  # We'll create special version
            shutil.copy(file, temp_dir / file.name)
    
    # Copy other necessary directories
    for dir_name in ["assets", "config"]:
        src = Path(dir_name)
        if src.exists():
            dst = temp_dir / dir_name
            shutil.copytree(src, dst)
    
    # Copy main.py
    if Path("main.py").exists():
        shutil.copy("main.py", temp_dir / "main.py")
    
    return temp_dir


def run_pyinstaller(temp_dir: Path, app_name: str, version: str):
    """Run PyInstaller to create executable"""
    
    # PyInstaller command
    icon_path = Path("assets/headerapp_icon.ico")
    
    cmd = [
        "pyinstaller",
        "--name", app_name,
        "--onefile",  # Single executable
        "--windowed",  # No console window
    ]
    
    # Add icon if exists
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    
    cmd.extend([
        "--add-data", f"{temp_dir}/assets;assets",
        "--add-data", f"{temp_dir}/config;config",
        "--hidden-import", "google_auth_oauthlib",
        "--hidden-import", "google.auth.transport.requests",
        "--hidden-import", "google.oauth2.credentials",
        "--hidden-import", "PIL",
        "--hidden-import", "yt_dlp",
        f"{temp_dir}/main.py"
    ])
    
    print("\n" + "="*60)
    print(f"Building {app_name} v{version}")
    print("="*60)
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n✅ Build successful!")
        print(f"Executable created: dist/{app_name}.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed!")
        print(e.stderr)
        raise BuildError(f"PyInstaller failed: {e}")


def check_dependencies():
    """Check if required tools are installed"""
    try:
        result = subprocess.run(
            ["pyinstaller", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ PyInstaller found: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise BuildError(
            "PyInstaller not found!\n"
            "Install it with: pip install pyinstaller"
        )


def main():
    """Main build process"""
    print("EasyCut Build Script")
    print("=" * 60)
    
    try:
        # 1. Check dependencies
        print("\n[1/6] Checking dependencies...")
        check_dependencies()
        
        # 2. Load build configuration
        print("\n[2/6] Loading build configuration...")
        config = load_build_config()
        oauth_creds = config['oauth_credentials']
        app_name = config.get('app_name', 'EasyCut')
        version = config.get('app_version', '1.3.0')
        print(f"✓ Building {app_name} v{version}")
        
        # 3. Prepare build directory
        print("\n[3/6] Preparing build directory...")
        temp_dir = prepare_build_directory()
        print(f"✓ Created temporary directory: {temp_dir}")
        
        # 4. Create packaged oauth_manager
        print("\n[4/6] Embedding OAuth credentials...")
        packaged_oauth = create_packaged_oauth_manager(oauth_creds, temp_dir)
        print(f"✓ Created packaged oauth_manager.py")
        
        # 5. Run PyInstaller
        print("\n[5/6] Running PyInstaller...")
        run_pyinstaller(temp_dir, app_name, version)
        
        # 6. Cleanup
        print("\n[6/6] Cleaning up...")
        shutil.rmtree(temp_dir)
        if Path("build").exists():
            shutil.rmtree("build")
        print("✓ Cleanup complete")
        
        print("\n" + "="*60)
        print("✅ BUILD COMPLETE!")
        print("="*60)
        print(f"\nExecutable: dist/{app_name}.exe")
        print(f"Size: {(Path('dist') / f'{app_name}.exe').stat().st_size / 1024 / 1024:.1f} MB")
        print("\nYou can now distribute this executable.")
        print("Users do NOT need to install Python or create OAuth credentials.")
        
    except BuildError as e:
        print(f"\n❌ BUILD FAILED: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
