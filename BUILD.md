# 🔨 Building EasyCut

This document explains how to build standalone executables of EasyCut with embedded OAuth credentials.

## 📋 Overview

EasyCut uses a **source-clean** approach for distribution:

- **Source code on GitHub**: No credentials - clean and secure
- **Released executables**: Contain embedded OAuth credentials for zero-setup user experience

This approach gives us:
- ✅ Security: No credentials exposed in public repository
- ✅ Convenience: Users download and run immediately
- ✅ Professionalism: GitHub security scanning happy
- ✅ Control: You manage the OAuth project quota

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install PyInstaller
pip install pyinstaller

# Verify installation
pyinstaller --version
```

### Build Steps

1. **Ensure `build_config.json` exists** with your OAuth credentials:

```json
{
  "oauth_credentials": {
    "installed": {
      "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
      "project_id": "your-project-id",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_secret": "YOUR_CLIENT_SECRET",
      "redirect_uris": ["http://localhost"]
    }
  },
  "app_version": "1.2.1",
  "app_name": "EasyCut"
}
```

2. **Run the build script**:

```bash
python scripts/build.py
```

3. **Find your executable**:

```
dist/EasyCut.exe
```

That's it! 🎉

---

## 📦 What the Build Script Does

The `scripts/build.py` script automates the entire packaging process:

### Step 1: Validation
- Checks PyInstaller is installed
- Validates `build_config.json` exists and is valid

### Step 2: Prepare Build Directory
- Creates temporary `build_temp/` folder
- Copies all source files
- Copies assets and config directories

### Step 3: Embed Credentials
- Creates modified version of `oauth_manager.py`
- Embeds OAuth credentials as `_EMBEDDED_CREDENTIALS` constant
- Modifies `__init__` to use embedded credentials by default

### Runtime OAuth Files (Generated at First Login)
- `config/youtube_token.pickle` — OAuth token cache
- `config/yt_cookies.txt` — Cookies used by yt-dlp for authenticated downloads

### Step 4: Run PyInstaller
- Compiles Python code to executable
- Bundles all dependencies
- Includes assets and config files
- Creates single-file executable

### Step 5: Cleanup
- Removes temporary build directory
- Removes PyInstaller build artifacts
- Keeps only final executable in `dist/`

---

## 🔐 Security Considerations

### Safe Files (Committed to Git)
- ✅ `scripts/build.py` - Build script (no secrets)
- ✅ `config/credentials_template.json` - Empty template
- ✅ `src/oauth_manager.py` - Loads credentials from file
- ✅ `.gitignore` - Protects secret files

### Secret Files (NOT Committed)
- ⛔ `build_config.json` - **Contains OAuth credentials!**
- ⛔ `config/youtube_token.pickle` - OAuth token cache
- ⛔ `config/yt_cookies.txt` - Cookies for authenticated yt-dlp downloads
- ⛔ `build_temp/` - Temporary build files
- ⛔ `dist/` - Final executable (has embedded credentials)
- ⛔ `*.spec` - PyInstaller spec files

### Important Notes

1. **Never commit `build_config.json`** - It's in `.gitignore` for a reason!

2. **Distribute only via GitHub Releases** - Don't commit executables to repository

3. **OAuth Desktop App context**: While OAuth Desktop App credentials are considered "less secret" by design (they're meant for installed applications), we still protect them to:
   - Prevent quota abuse on your Google Cloud project
   - Maintain professional security practices
   - Avoid GitHub security warnings

4. **Users can't abuse credentials** - OAuth requires user consent, so embedded credentials can't access anyone's YouTube without authorization

---

## 🎯 Distribution Workflow

### For Maintainers

1. **Development**:
   ```bash
   # Use credentials.json during development
   cp config/credentials_template.json config/credentials.json
   # Edit with your dev credentials
   python main.py  # Test locally
   ```

2. **Building Release**:
   ```bash
   # Ensure build_config.json has production credentials
   python build.py
   # Creates dist/EasyCut.exe
   ```

3. **Create GitHub Release**:
   - Go to GitHub → Releases → New Release
   - Tag: `v1.2.1`
   - Upload: `dist/EasyCut.exe`
   - Write release notes
   - Publish

### For End Users

1. **Download** latest release from GitHub
2. **Run** `EasyCut.exe`
3. **Click** "Sync with YouTube"
4. **Authorize** in browser
5. **Done!** - No Python, no setup, no credentials needed

---

## 🛠️ Advanced Configuration

### Custom Build Options

Edit `scripts/build.py` to customize:

```python
# Change application icon
"--icon", "assets/my_icon.ico"

# Add more hidden imports
"--hidden-import", "my_module"

# Change executable name
"--name", "MyCustomName"

# Console mode (for debugging)
# Remove "--windowed" line
```

### Build for Multiple Platforms

PyInstaller creates executables for the platform you build on:

- **Windows**: `EasyCut.exe`
- **Mac**: `EasyCut.app`
- **Linux**: `EasyCut`

Run `build.py` on each platform to create native executables.

---

## 🐛 Troubleshooting

### "PyInstaller not found"

```bash
pip install pyinstaller
# Or with pipx:
pipx install pyinstaller
```

### "build_config.json not found"

Create it with your OAuth credentials:

```bash
cp config/credentials_template.json build_config.json
# Then edit build_config.json with real credentials
```

### "Module not found" errors in executable

Add hidden imports to `scripts/build.py`:

```python
"--hidden-import", "missing_module_name"
```

### Executable is too large

PyInstaller bundles entire Python runtime. Normal sizes:
- **50-100 MB**: Expected for tkinter + yt-dlp application
- **>200 MB**: Check if unnecessary packages included

Optimize with:
```python
"--exclude-module", "unnecessary_module"
```

### Antivirus false positives

Common with PyInstaller executables. Solutions:
- Sign the executable with code signing certificate
- Submit to antivirus vendors as false positive
- Distribute via GitHub Releases (trusted source)

---

## 📝 Maintenance Checklist

Before each release:

- [ ] Update version in `build_config.json`
- [ ] Update version in `src/easycut.py`
- [ ] Update version in `src/i18n.py` (`TRANSLATIONS['en']['version']` and `['pt']['version']`)
- [ ] Update About tab version in `src/easycut.py` (Application Info card)
- [ ] Test locally with `python main.py`
- [ ] Run `python scripts/build.py`
- [ ] Test executable on clean Windows machine
- [ ] Create GitHub Release with executable
- [ ] Update release notes
- [ ] Announce on README

---

## 🤝 Contributing

If you're a developer wanting to contribute:

1. **Clone repository**
2. **Create `config/credentials.json`** with your own OAuth credentials (see [OAUTH_SETUP.md](OAUTH_SETUP.md))
3. **Develop and test** with `python main.py`
4. **Submit PR** with code changes (never commit credentials!)

Maintainers will build and release executables separately.

---

## 📚 Related Documentation

- [OAUTH_SETUP.md](OAUTH_SETUP.md) - How to create OAuth credentials
- [README.md](README.md) - Main documentation

---

## ❓ FAQ

**Q: Why not just embed credentials in source code?**  
A: GitHub secret scanning blocks it, and it's unprofessional security practice.

**Q: Why not make users create their own credentials?**  
A: Terrible UX - 90% of users will give up during Google Cloud Console setup.

**Q: Can people extract credentials from the .exe?**  
A: Technically yes, but OAuth requires user consent anyway. The real risk is quota abuse, which we accept for UX.

**Q: Should I distribute the .exe file in Git?**  
A: No! Use GitHub Releases. Don't commit large binaries to Git repository.

**Q: How do I update OAuth credentials?**  
A: Edit `build_config.json`, rebuild with `python scripts/build.py`, create new GitHub Release.

---

**Made with ❤️ for EasyCut**
