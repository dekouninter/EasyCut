# EasyCut Product Roadmap

**Project**: EasyCut - YouTube Downloader  
**Current Status**: v1.2.1 (Audit Release)  
**Planning Period**: 2026  
**Last Updated**: February 15, 2026

## Purpose

This roadmap defines **realistic feature development** for a YouTube downloader. No AI, no marketplaces, no enterprise features — just pragmatic improvements to core functionality.

## Related Docs
- [REFACTORING_PLAN.md](REFACTORING_PLAN.md) — Bug fixes and code cleanup (actual issues)

---

## Vision

**Simple, reliable YouTube downloads** with OAuth authentication, quality presets, and batch processing.

---

## Current Status (February 2026)

### ✅ What Works
- Single video downloads (Best, 1080p, 720p, MP4 presets)
- Audio conversion (MP3, WAV, M4A, OPUS) with 4 bitrate options
- Time range downloads (start/end time with yt-dlp download_sections)
- Batch downloads (paste multiple URLs, max 3 concurrent)
- Playlist downloads (full playlist with noplaylist toggle)
- Channel downloads (last 10 videos via playlistend)
- Live stream recording
- OAuth 2.0 authentication (Google)
- Download history with search/filter and clear button
- Structured logging (RotatingFileHandler, 5MB, 3 backups)
- Graceful shutdown with active download detection
- Light/Dark theme
- Multi-language (EN, PT — 200+ strings)

### 🐛 Known Bugs
- Download cancellation: stop button sets flag but can't cancel in-progress yt-dlp downloads
- Browser cookie UI exists but overridden by OAuth banner (dead code)
- Some UI updates from threads lack `root.after()` scheduling

---

## Q1 2026 (Feb - Apr) — Stabilization

**Goal**: Fix critical bugs, complete Google verification, publish v1.0

### Critical Fixes
- [x] Fix output folder persistence bug (`output_folder` → `output_dir`)
- [x] Normalize version strings to single source (1.2.1 everywhere)
- [x] Wire audio format UI to yt-dlp postprocessors
- [x] Wire time range UI to yt-dlp download_sections
- [x] Fix license references (MIT → GPL-3.0 in 6 files)
- [x] Fix duplicate `create_login_banner` method (rename first to `create_browser_auth_banner`)
- [x] Fix `self.current_lang` crash on app close (→ `self.language`)
- [x] Remove duplicate "Clear History" button
- [x] Fix donation_system.py `tokens` NameError in except blocks
- [ ] OAuth browser auto-close after 3 seconds

### OAuth & Publishing
- [x] Google Cloud project created
- [x] OAuth consent screen configured
- [x] Credentials obtained
- [x] Test users added
- [x] Record verification video
- [x] Submit to Google for verification
- [ ] Publish to Google OAuth (remove "testing" mode) wainting 4-6 weeks for verification

### Documentation
- [x] Update README with actual features
- [x] Remove claims of unimplemented features
- [x] OAuth setup guide for developers
- [x] Fix README Known Limitations (remove fixed items)
- [x] Fix CREDITS FFmpeg description (is now used for audio)
- [ ] User troubleshooting guide (common errors)

**Deliverable**: **v1.2.1 Release** — Stable, audited, documented

---

## Q2 2026 (May - Jul) — Format Selection & Metadata

**Goal**: Smart format selection, metadata display, thumbnails

### Format & Quality Intelligence
- [x] **Smart format selection**
  - List all available formats (video + audio combinations) after metadata fetch
  - Best quality as default
  - Automatic fallback: if best unavailable, download second-best
  - Show format details: codec, bitrate, resolution, FPS, size
  - Categorized display: Video+Audio, Video Only, Audio Only sections
- [x] **Batch quality selector**
  - Dropdown for standard quality presets (Best, 1080p, 720p, 480p, Audio)
  - Fallback to lower quality if preset unavailable (checkbox)
  - Applies to all URLs in batch, overrides main quality

### Metadata & Thumbnails
- [x] **Pre-download metadata display**
  - Fetch using `extract_info(download=False)`
  - Show: title, duration, uploader, view count, upload date
  - Display in download dialog with formatted values (M/K views, DD/MM/YYYY)
- [x] **Thumbnail integration**
  - Show thumbnail in download tab (160x90 preview)
  - Loaded via urllib + PIL on verify
  - [x] Show thumbnails in history list (async loading + cache)
  - [x] Cache thumbnails in memory (`_thumbnail_cache` dict)

### Implement Core Features
- [x] **Audio conversion** (requires FFmpeg)
  - Extract audio as MP3/WAV/M4A/OPUS
  - Wire UI selectors to yt-dlp `postprocessors`
- [x] **Time range downloads**
  - Download specific segments (e.g., 1:30-3:45)
  - Wire UI inputs to yt-dlp `download_sections`
- [x] **Playlist downloads**
  - Download entire playlists
  - [x] Playlist info display: video count + total duration after verify
  - Auto-convert to batch downloader
  - [ ] Progress tracking per video (future)
- [x] **Channel downloads**
  - Download all videos from channel
  - [x] Configurable latest N videos (Spinbox 1-500, default 10)

### UX Improvements
- [x] Download queue management (pause/resume batch queue, visual status per URL, clear completed)
- [x] Better error messages: 13 yt-dlp error patterns mapped to translated user-friendly messages
- [x] History search/filter (by URL, date, quality, uploader)
- [x] "Clear History" button
- [x] Failed downloads recorded in history (status: error)
- [x] Skip duplicate detection: warn if video already downloaded (checked by video ID in history)
- [x] Batch download history entries: each video now recorded individually

**Deliverable**: **v1.5 Release** — Smart format selection + metadata

---

## Q3 2026 (Aug - Oct) — Subtitles & Archive Mode

**Goal**: Comprehensive subtitle support, archive tracking

### Subtitle Features
- [x] **Subtitle download**
  - Auto-generated subtitles (YouTube auto-generated captions)
  - Manual subtitles (creator-uploaded)
  - Both modes available (Radio: auto / manual / both)
  - Multiple language tracks via comma-separated codes
  - Format options: SRT, VTT, ASS, JSON3 (Combobox)
  - Embed in video option (FFmpegEmbedSubtitle postprocessor)
  - Available subtitles shown after verify
- [x] **Auto-translate**
  - Translate subtitles to any language via YouTube auto-translate (native yt-dlp)
  - "Translate to" checkbox + language combobox with 24 common languages
  - Custom language code entry (editable combobox)
  - Available auto-translate count shown after verify
  - No external API required — YouTube handles translation

### Archive & Duplicate Detection
- [x] **Archive mode**
  - Track downloaded video IDs via yt-dlp `download_archive` file
  - Auto-skip videos already in archive during download
  - Export/import archive (merge with deduplication)
  - Clear archive with confirmation dialog
  - Toggle on/off in Settings tab
- [x] **Archive file tracking**
  - yt-dlp native format: `provider video_id` per line
  - Persistent across sessions in `config/download_archive.txt`
  - Entry count displayed in Settings
- [x] **Skip already downloaded**
  - Automatic via yt-dlp download_archive (batch + playlist + single)
  - History-based duplicate detection (verify warning + pre-download dialog)
  - Option to skip or re-download

### Quality Profiles
- [x] **Save custom presets**
  - Save current quality/mode/audio/subtitle settings as named profile
  - Load profile restores all settings
  - Delete profiles
  - Stored in config.json under `quality_profiles`
- [x] **Per-channel defaults** (channel→quality mapping in settings, auto-apply on verify)

### Technical
- [x] Thread pool (max 3 concurrent downloads)
- [x] Graceful shutdown (finish active downloads on exit)
- [x] Structured logging (RotatingFileHandler with levels)

**Deliverable**: **v2.0 Release** — Professional downloader with archive

---

## Q4 2026 (Nov - Dec) — Live & Chapters

**Goal**: Comprehensive live streaming and chapter support

### Live Streaming Enhancements
- [x] **Live stream status check**
  - Auto-detect if URL is currently live (on verify)
  - Offer to auto-switch to Live tab when live detected
  - Show 🔴 LIVE badge in history for live recordings
- [x] **Livestream recording**
  - Full integration in Live tab
  - Record ongoing streams with auto-stop option
  - Thumbnail and video_id saved in history for live recordings
- [x] **Live segment recording**
  - Post-processing options for live: audio extraction, subtitles
  - Audio format (mp3/wav/m4a/opus) + bitrate selection
  - Subtitle download for live recordings
- [x] **Post-processing in Live**
  - All post-processing options available for live streams
  - Audio extraction, subtitles, network settings (proxy, rate limit, retries)
  - Same postprocessors as regular downloads

### YouTube Chapters & Shorts
- [x] **Chapters download**
  - Detect YouTube chapters from video metadata (shown in verify log)
  - Split video by chapters (download each chapter separately via download_sections)
  - Chapters UI card shown dynamically after verify
  - Auto-name files by chapter title
- [x] **YouTube Shorts integration**
  - Full support for downloading YouTube Shorts
  - Detect via /shorts/ URL or vertical aspect ratio + short duration
  - Same quality/format options as regular videos
  - 📱 SHORT badge shown in history

### Settings Panel
- [x] Proxy configuration (HTTP/SOCKS, saved in config)
- [x] Rate limit (speed limit with K/M suffix parsing)
- [x] Max retries (Spinbox 1-10, saved in config)
- [x] Cookie file path (browse dialog, Netscape format)
- [x] Preferred live streaming codec (VP9, H.264, AV1 — saved in config, applied in Live tab)

**Deliverable**: **v2.5 Release** — Live streaming & chapters

---

## Q1 2027 (Jan - Mar) — History & Post-Processing

**Goal**: Enhanced history management, post-processing hub

### History Transformation
- [x] **Enhanced history area**
  - Full media gallery with thumbnails, metadata (uploader, quality, duration, format)
  - Search/filter by: text search, status filter (all/success/error)
  - Sort: date (asc/desc), title (asc/desc), status
  - History count label shows filtered vs total
- [x] **Post-processing hub**
  - Right-click context menu: Copy URL, Open Folder, Re-download, Extract Audio (MP3), Delete Entry
  - Extract audio downloads bestaudio + FFmpegExtractAudio
  - Delete single entries from history
  - Re-download populates URL in download tab
- [ ] **Video upscaling**
  - Upscale 480p/720p to 1080p (optional, requires GPU or extra processing)
  - Audio enhancement: normalize, noise reduction
  - Video enhancement: denoise, stabilize (optional filters)

### Automatic Retries & Scheduling
- [x] **Automatic retries**
  - Retry failed downloads (network errors) with exponential backoff
  - Rate limit handling (exponential backoff: 2s, 4s, 8s)
  - Max retries configurable (uses Settings max_retries)
  - Only retryable errors retried (connection, timeout, 429, 5xx)
- [x] **Download scheduler**
  - Schedule downloads by time (hour:minute picker + URL)
  - Pending downloads list with status icons
  - Timer checks every 30 seconds
  - Completed/failed status tracking
  - Individual item removal

**Deliverable**: **v3.0 Release** — Professional post-processing hub

---

## 2027 — Future Ideas (No Promises)

### Maybe
- Python API (import EasyCut as library)
- Command-line interface (CLI mode)
- Linux/macOS support (Tkinter works cross-platform)
- Auto-update checker (opt-in)
- Portable mode (all files in app folder)
- Download reports (CSV export)

### Probably Not
- ❌ AI-powered subtitle translation
- ❌ Cloud storage integration (Google Drive, Dropbox)
- ❌ Mobile app
- ❌ Web version
- ❌ Enterprise SSO

**Focus**: Keep it simple, keep it working

---

## Success Metrics (Realistic)

### By v1.0 (Q1 2026)
- Zero critical bugs
- Google OAuth verified (public access)
- 100% feature documentation

### By v2.0 (Q3 2026)
- All UI features implemented
- 3+ concurrent downloads working
- <10% download failure rate (excluding deleted videos)

### By v2.5 (Q4 2026)
- 5+ languages supported
- 1000+ downloads tested successfully
- User-reported bugs addressed

---

## Dependencies & Risks

### External Dependencies
- Google OAuth API availability
- Cloud storage provider APIs
- ML/AI service providers
- Third-party c

### External
- **yt-dlp**: YouTube download engine (updates frequently)
- **Google OAuth API**: Authentication service (stable, rarely changes)
- **FFmpeg** (optional): Audio conversion / format handling

### Risks
- **yt-dlp breakage**: YouTube changes site, yt-dlp needs update
  - Mitigation: Pin yt-dlp version, test before upgrading
- **Google OAuth rejection**: App might fail verification
  - Mitigation: Follow guidelines, record compliant demo video
- **Windows-only**: Tkinter works cross-platform but code has Windows-specific calls
  - Mitigation: Abstract OS calls (e.g., `open_output_folder()`)

---

## Implementation Strategy & Suggestions

### Priority Matrix
**High Impact + Low Effort** (Implement First):
1. Smart format selection with fallback — foundational for quality control
2. Thumbnail display in history — big UX improvement
3. Skip duplicate detection — prevents user frustration
4. Subtitle download (auto + manual) — highly requested feature
5. Live stream status check — auto-routing improves UX

**High Impact + Medium Effort** (Implement Next):
1. Enhanced history with post-processing hub — transforms entire app workflow
2. Chapters download — great for educational/long-form content
3. Archive mode — essential for power users doing bulk downloads
4. YouTube Shorts integration — covers emerging format

**Medium Impact / Future**:
1. Video upscaling (requires GPU or significant processing)
2. Editor integrations (Shotcut, resolve)
3. Automatic retry with exponential backoff
4. Download scheduler with recurring jobs

### Technical Recommendations
1. **Format Selection**: Use `ydl.extract_info(url, download=False)['formats']` to build format table
2. **Fallback Logic**: Implement format priority scoring (resolution × bitrate × codec preference)
3. **Archive Tracking**: SQLite instead of JSON for better query performance with large downloads
4. **Live Streaming**: Use separate thread pool for livestream recording (can run indefinitely)
5. **Post-Processing Hub**: Leverage existing postprocessors, add UI layer in history
6. **Thumbnail Caching**: Store `~/.easycut/cache/thumbnails/{video_id}.jpg` to avoid re-fetching

### Testing Recommendations
- Test with problematic URLs: age-restricted, geo-blocked, member-only, deleted videos
- Test format fallback with artificially unavailable formats
- Test batch duplicate detection with 1000+ item history
- Test concurrent livestream + regular download handling
- Test chapter extraction with varying chapter metadata formats

### Dependencies to Add (May be Optional)
- `Pillow` (MIT) — thumbnail image processing
- `opencv-python` or `moviepy` (MIT/BSD) — video upscaling (optional, feature expansion)
- `google-cloud-translate` (Apache 2.0) — auto-translate subtitles (optional)

---

## Review Schedule

- **Monthly**: Bug triage, feature priority
- **Quarterly**: Roadmap adjustments based on usage
- **Yearly**: Major version planning

**Last Updated**: February 15, 2026 (Updated with expanded features)  
**Next Review**: March 15, 2026