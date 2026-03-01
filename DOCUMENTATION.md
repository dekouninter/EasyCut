# 📚 EasyCut Documentation Index

**Version**: 1.9.0  
**Last Updated**: February 2026

## ⚠️ v1.7 — resumo das mudanças
- Live tab: UI rework (verify, preview, record/stop, mark & save clips) — preview can now load the recording file to allow rewind to the start of the live broadcast.
- Player: melhorias no mpv (IPC robusto, suporte a arquivos em crescimento, comandos de seek percentuais).
- Clipper: Quick Cut (30/60/120s), download concorrente de clipes e botão de salvar rápido integrado.
- Correções críticas: bug de progresso de live (NameError), atualizações de thread-safety, placeholder → get_value() fix.
- Ambiente: deno recomendado para yt-dlp; cookies/ OAuth melhor integrados para streams com verificação de bot.

Complete documentation for users and developers.

---

## 🎯 Find What You Need

### 👤 For End Users
- **Getting Started**: [README.md](README.md) - Features, installation, requirements
- **Using EasyCut**: [QUICKSTART.md](QUICKSTART.md) - How to download, record, clip, and authenticate
- **Keyboard Shortcuts**: Ctrl+T (theme), Ctrl+L (logs), Ctrl+O (folder), Ctrl+1-8 (tabs)

### 👨‍💻 For Developers
- **Installation**: [README.md](README.md#-installation) - Setup from source
- **OAuth Setup**: [QUICKSTART.md](QUICKSTART.md#-oauth-setup-for-developers) - Configure Google credentials
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) - Code structure and design

### 📦 For Maintainers
- **Building Release**: See [QUICKSTART.md](QUICKSTART.md#-building-releases-maintainers-only) - Create standalone executables
- **Testing**: [internal/TESTING.md](internal/TESTING.md) - Test checklist and procedures

### ⚖️ Legal & Attribution
- **Privacy**: [PRIVACY.md](PRIVACY.md) - OAuth and data privacy
- **Terms**: [TERMS.md](TERMS.md) - Terms of service
- **Credits**: [CREDITS.md](CREDITS.md) - Dependencies, icons, fonts, third-party licenses

---

## 📖 Feature Documentation

### Core Features
| Feature | Status | Documentation |
|---------|--------|---------------|
| Single video download | ✅ Complete | [README.md](README.md#-download-single-videos) |
| Smart URL Router | ✅ Complete | [README.md](README.md#-download-single-videos) |
| Time range download | ✅ Complete | [QUICKSTART.md](QUICKSTART.md#download-time-range-extract-clip-from-video) |
| Audio format conversion | ✅ Complete | [QUICKSTART.md](QUICKSTART.md#download-time-range-extract-clip-from-video) |
| Batch downloads | ✅ Complete | [README.md](README.md#-batch-download-multiple-videos) |
| Live stream recording | ✅ Complete | [README.md](README.md#-record-live-streams--live-clipper) |
| Live Clipper & Preview | ✅ Complete | [README.md](README.md#-record-live-streams--live-clipper) |
| Embedded Video Player | ✅ Complete | [README.md](README.md#-record-live-streams--live-clipper) |
| Post-Processing Hub | ✅ Complete | [README.md](README.md#-post-processing-hub) |
| Channel Monitor | ✅ Complete | [README.md](README.md#-channel-monitor) |
| Following Tab | ✅ Complete | [README.md](README.md#-following-tab) |
| Download history | ✅ Complete | [README.md](README.md#-download-history) |
| OAuth authentication | ✅ Complete | [QUICKSTART.md](QUICKSTART.md#-oauth-setup-for-developers) |
| Browser auth (optional) | ✅ Complete | [QUICKSTART.md](QUICKSTART.md#-advanced-browser-authentication-optional) |
| Theme customization | ✅ Complete | [ARCHITECTURE.md](ARCHITECTURE.md#theme-system) |
| Multi-language (7 langs) | ✅ Complete | [ARCHITECTURE.md](ARCHITECTURE.md#internationalization) |
| SVG icon rendering (v1.6) | ✅ Complete | [ARCHITECTURE.md](ARCHITECTURE.md#design--theming) |
| Multi-accent color system (v1.6) | ✅ Complete | [ARCHITECTURE.md](ARCHITECTURE.md#color-palettes) |
| Gradient effects & glass-morphism (v1.6) | ✅ Complete | [ARCHITECTURE.md](ARCHITECTURE.md#color-palettes) |
| Windows Mica backdrop (v1.6) | ✅ Complete | [README.md](README.md#-premium-visual-design-v16) |
| 16 custom UI components (v1.6) | ✅ Complete | [ARCHITECTURE.md](ARCHITECTURE.md#ui-infrastructure) |

### Common Tasks
- **Download a YouTube video**: [QUICKSTART.md](QUICKSTART.md#-for-end-users) - 3 steps
- **Record a live stream**: [README.md](README.md#-record-live-streams--live-clipper) - Set mode and duration
- **Clip from live stream**: Use the embedded player seekbar to mark start/end points
- **Post-process downloads**: [README.md](README.md#-post-processing-hub) - Automatic conversion
- **Monitor channels**: [README.md](README.md#-channel-monitor) - Track new content
- **Change theme or language**: Click dropdown in header (Ctrl+T for theme)
- **Running**: [README.md](README.md#usage) — How to run the app
- **Building**: [QUICKSTART.md](QUICKSTART.md#-building-releases-maintainers-only) — Quick build instructions
- **Verification**: [README.md](README.md#4-verify-installation-optional) — check_installation.py usage

### Troubleshooting
- **OAuth Issues**: See OAuth Troubleshooting in [QUICKSTART.md](QUICKSTART.md)
- **Build Issues**: See Build Troubleshooting in [QUICKSTART.md](QUICKSTART.md#build-troubleshooting)
- **Runtime Support**: [README.md](README.md#security) — Security and validation details

---

## 📋 Planning Documents (Local Development Only)

These documents are in `.gitignore` as they contain planning information not intended for public repositories:

- **OAUTH_CHECKLIST.md** — Internal verification checklist for OAuth activation
- **REFACTORING_PLAN.md** — Internal strategic refactoring plan
- **ROADMAP.md** — Internal product roadmap and planning
- **DOCUMENTATION_UPDATES.md** — Internal change log for documentation updates

They're useful for team coordination and project management but kept locally to avoid repository clutter.

---

## 🆘 Need Help?

### I want to...

**...download and use EasyCut**
→ Download latest release from [GitHub Releases](https://github.com/dekouninter/EasyCut/releases)

**...run EasyCut from source code**
→ Follow [README.md](README.md#installation)

**...set up OAuth authentication (development)**
→ Follow [QUICKSTART.md](QUICKSTART.md#-oauth-setup-for-developers)

**...build a release executable**
→ Follow [QUICKSTART.md](QUICKSTART.md#-building-releases-maintainers-only)

**...understand the project's future**
→ Internal planning docs are maintained locally (not in the public repository)

**...contribute code improvements**
→ Start with [README.md](README.md) and open an issue with proposed changes

**...verify OAuth is properly configured**
→ Check `config/credentials_template.json` for the required format and Google Cloud Console guidance

---

## 📞 Support & Contact

- **Issues**: Report bugs on [GitHub Issues](https://github.com/dekouninter/EasyCut/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/dekouninter/EasyCut/discussions)
- **Donations**: Support development at [buymeacoffee.com/dekocosta](https://buymeacoffee.com/dekocosta)
- **Donations - Brazil**: Support development at [Livepix](https://livepix.gg/dekocosta)

---

**Made with ❤️ by Deko Costa**  
*Download videos. Record live streams. Simple, fast, secure.*

**Repository**: [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)
