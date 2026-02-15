# 🧪 EasyCut Testing Guide

**Last Updated**: February 20, 2026  
**Version**: 1.3.0

This document tracks all manual and automated test cases for EasyCut features.  
Update this file as features are implemented.

---

## How to Use

- **[ ]** = Not tested yet
- **[x]** = Tested and passing
- **[!]** = Tested and failing (add notes)

---

## 1. Core Downloads

### 1.1 Single Video Download
- [ ] Download with "Best" quality preset
- [ ] Download with "MP4 Best" preset
- [ ] Download with "1080p" preset
- [ ] Download with "720p" preset
- [ ] Download with unavailable quality (should fallback)
- [ ] Download age-restricted video (with OAuth)
- [ ] Download private/unlisted video (with OAuth)
- [ ] Download deleted video (should show error)
- [ ] Download geo-blocked video (should show error)
- [ ] Invalid URL shows validation error
- [ ] Empty URL shows validation error
- [ ] Progress bar updates during download
- [ ] Log panel shows download progress
- [ ] Output file appears in selected folder

### 1.2 Audio Conversion
- [ ] Extract MP3 (128 kbps)
- [ ] Extract MP3 (192 kbps)
- [ ] Extract MP3 (256 kbps)
- [ ] Extract MP3 (320 kbps)
- [ ] Extract WAV
- [ ] Extract M4A
- [ ] Extract OPUS
- [ ] Audio conversion without FFmpeg installed (should warn)
- [ ] Verify audio file metadata (bitrate, codec)

### 1.3 Time Range Downloads
- [ ] Download with start time only
- [ ] Download with end time only
- [ ] Download with start + end time
- [ ] Time format HH:MM:SS works
- [ ] Time format MM:SS works
- [ ] Invalid time format shows error
- [ ] End time before start time shows error
- [ ] Time range on long video (>1 hour)
- [ ] Time range on short video (<1 minute)

### 1.4 Batch Downloads
- [ ] Paste 2 URLs, download all
- [ ] Paste 10 URLs, download all
- [ ] Paste 50 URLs, download all
- [ ] Mixed valid/invalid URLs (should skip invalid)
- [ ] Empty batch shows warning
- [ ] Stop All button during batch
- [ ] Duplicate URLs in batch (should handle)
- [ ] History updated after batch completes

### 1.5 Playlist Downloads
- [ ] Download full playlist
- [ ] Download playlist with 50+ videos
- [ ] Private playlist (with OAuth)
- [ ] Empty/deleted playlist (should error)
- [ ] Progress shown during playlist download

### 1.6 Channel Downloads
- [ ] Download latest 10 videos from channel
- [ ] Channel with <10 videos
- [ ] Invalid channel URL

### 1.7 Live Stream Recording
- [ ] Record active live stream
- [ ] Check stream status (live vs offline)
- [ ] Stop recording button works
- [ ] Duration mode recording
- [ ] Quality presets (Best, 1080p, 720p, 480p)
- [ ] Record stream that ends during recording
- [ ] URL that is not a live stream (should warn)

---

## 2. Authentication

### 2.1 OAuth 2.0
- [ ] "Sync with YouTube" opens browser
- [ ] Login completes and tokens saved
- [ ] Token persists across app restarts
- [ ] Logout clears tokens and cookies
- [ ] Expired token auto-refreshes
- [ ] Download works after OAuth
- [ ] Download works without OAuth (public videos)
- [ ] Status bar shows login state

---

## 3. UI & UX

### 3.1 Theme
- [ ] Switch to Light theme (Ctrl+T)
- [ ] Switch to Dark theme (Ctrl+T)
- [ ] Theme persists after restart
- [ ] All UI elements update on theme change

### 3.2 Language
- [ ] Switch to English
- [ ] Switch to Portuguese
- [ ] Switch to Spanish
- [ ] Switch to French
- [ ] Switch to German
- [ ] Switch to Italian
- [ ] Switch to Japanese
- [ ] Language persists after restart
- [ ] All visible strings change on switch (all 7 languages)
- [ ] Donation window respects language

### 3.3 Keyboard Shortcuts
- [ ] Ctrl+1 → Download section
- [ ] Ctrl+2 → Batch section
- [ ] Ctrl+3 → Live section
- [ ] Ctrl+4 → History section
- [ ] Ctrl+5 → About section
- [ ] Ctrl+T → Toggle theme
- [ ] Ctrl+L → Toggle log panel
- [ ] Ctrl+O → Open output folder
- [ ] Escape → Close log panel

### 3.4 Sidebar Navigation
- [ ] Click each nav item switches section
- [ ] Hamburger menu collapses sidebar
- [ ] Hamburger menu expands sidebar
- [ ] Active section is highlighted
- [ ] Hover effects work

### 3.5 Settings
- [ ] Output folder selection works
- [ ] Settings persist in config.json
- [ ] Default settings created on first run

---

## 4. History

### 4.1 Download History
- [ ] Single download appears in history
- [ ] Batch downloads appear in history
- [ ] Search/filter works
- [ ] Clear History button works
- [ ] History persists after restart
- [ ] History limited to 100 entries
- [ ] History card layout renders correctly

---

## 5. Smart Format Selection (Q2 2026) — IMPLEMENTED

### 5.1 Format Listing
- [ ] Verify button fetches all available formats via `extract_info`
- [ ] Format combobox populated with categorized sections (Video+Audio, Video Only, Audio Only)
- [ ] Each format shows: format_id, resolution, fps, ext, bitrate, size
- [ ] "Auto (Best)" selected by default
- [ ] Separator lines shown between categories
- [ ] Format count shown in status label (e.g., "42 formats available")
- [ ] Top 15 video+audio, top 10 video-only, top 10 audio-only shown
- [ ] Formats sorted by resolution (highest first)

### 5.2 Format Download
- [ ] Selecting specific format uses its format_id for download
- [ ] "Auto (Best)" falls back to quality preset dropdown
- [ ] Selecting separator line returns None (uses default)
- [ ] `_get_selected_format_id()` returns correct format_id
- [ ] Download with specific format_id produces correct file
- [ ] Format selection resets when new URL is verified

### 5.3 i18n
- [ ] All format labels translated (EN, PT, ES, FR, DE, IT, JA)
- [ ] Category headers use translated text in all 7 languages

---

## 6. Metadata Display (Q2 2026) — IMPLEMENTED

### 6.1 Pre-Download Info
- [ ] Title displayed (truncated at 80 chars)
- [ ] Duration displayed as H:MM:SS or M:SS
- [ ] Uploader name displayed (truncated at 50 chars)
- [ ] View count formatted (K/M suffixes)
- [ ] Upload date formatted as DD/MM/YYYY
- [ ] Metadata labels reset to "..." before each fetch
- [ ] UI updates use `root.after(0, ...)` (thread-safe)
- [ ] Error on invalid URL shows in log, not crash
- [ ] Video info cached in `_video_info_cache` for reuse

---

## 7. Thumbnail Integration (Q2 2026) — IMPLEMENTED

### 7.1 Download Tab Thumbnail
- [ ] Thumbnail loads from video URL after verify
- [ ] Displayed at 160x90 (16:9) in thumbnail frame
- [ ] PIL LANCZOS resize applied
- [ ] Image reference kept to prevent GC (`.image = photo`)
- [ ] Graceful fallback if thumbnail URL missing
- [ ] Graceful fallback if PIL not installed
- [ ] Graceful fallback if network error on thumbnail fetch

### 7.2 Future
- [ ] History list thumbnails (not yet implemented)
- [ ] Local thumbnail cache (not yet implemented)

---

## 8. Duplicate Detection (Q2 2026) — IMPLEMENTED

### 8.1 Pre-Download Warning (Single)
- [ ] Warning shown before download if video ID found in history
- [ ] Dialog shows video title (truncated 60 chars)
- [ ] "Yes" proceeds with download
- [ ] "No" cancels download and logs "skipped (duplicate)"
- [ ] Only checks entries with `status: success`

### 8.2 Verify-Time Warning
- [ ] After verify, log shows ⚠ warning if video already in history
- [ ] Warning includes partial title

### 8.3 Batch Downloads
- [ ] Each batch video now recorded individually in history
- [ ] History entries include date, filename, status, url
- [ ] `refresh_history()` still called at end of batch

### 8.4 i18n
- [ ] `dup_title`, `dup_found`, `dup_overwrite`, `dup_skipped` keys present in all 7 languages (EN, PT, ES, FR, DE, IT, JA)

---

## 8.5 User-Friendly Error Messages — IMPLEMENTED

### 8.5.1 Error Pattern Mapping
- [ ] Private video → "This video is private. Sign in with OAuth to access it."
- [ ] Age-restricted → "Age-restricted video. Sign in with OAuth to access it."
- [ ] Unavailable/removed → "This video is unavailable or has been removed."
- [ ] Geo-blocked → "This video is not available in your country."
- [ ] Live not started → "This live stream has not started yet."
- [ ] Rate limited (429) → "Too many requests. Please wait a moment and try again."
- [ ] Network error → "Network error. Check your internet connection."
- [ ] No formats → "No downloadable formats found for this video."
- [ ] FFmpeg post-process → "Post-processing failed. Ensure FFmpeg is installed correctly."
- [ ] Copyright → "This video cannot be downloaded due to copyright restrictions."
- [ ] Members only → "This video is for channel members only."
- [ ] Premium only → "This content requires YouTube Premium."
- [ ] Browser cookies → "Browser is open! Close it first."
- [ ] Unknown error → "An unexpected error occurred. Check the logs."

### 8.5.2 Error Handling
- [ ] Errors shown in download log (not raw exception text)
- [ ] Errors translated correctly when switching between all 7 languages
- [ ] Failed downloads recorded in history (status: "error")
- [ ] Batch errors truncated to 80 chars in batch log
- [ ] Batch stops on browser cookie error (asks to close browser)

---

## 8.6 Channel Download Config — IMPLEMENTED

### 8.6.1 Channel Limit Control
- [ ] Spinbox visible below download mode radio buttons
- [ ] Default value is 10
- [ ] Min value 1, max value 500
- [ ] Channel mode uses spinbox value for `playlistend`
- [ ] Non-channel modes ignore spinbox value
- [ ] Invalid spinbox value falls back to 10

---

## 8.7 Playlist Info Display — IMPLEMENTED

### 8.7.1 Playlist Metadata
- [ ] Verify on playlist URL shows video count in log
- [ ] Total playlist duration shown in log
- [ ] Duration label shows "N videos • Xh XXm" for playlists
- [ ] Works for channel URLs too
- [ ] Non-playlist URLs show normal single video metadata

---

## 8.8 History Thumbnails — IMPLEMENTED

### 8.8.1 Thumbnail Display
- [ ] History cards show 80x45 thumbnail on the left
- [ ] Placeholder emoji "🎬" while loading
- [ ] Thumbnails load asynchronously (don't block UI)
- [ ] Thumbnails cached in memory (`_thumbnail_cache`)
- [ ] Cards without thumbnail data show no thumbnail area
- [ ] History entries now store `thumbnail` URL and `video_id`

### 8.8.2 Graceful Failures
- [ ] Missing PIL doesn't crash (placeholder stays)
- [ ] Network timeout on thumbnail doesn't crash
- [ ] Destroyed widget doesn't crash (TclError caught)

---

## 9. Subtitles (Q3 2026) — IMPLEMENTED

### 9.1 Subtitle UI
- [ ] Subtitle card visible in download tab (below audio format)
- [ ] Enable checkbox toggles subtitle download
- [ ] Type radio: Auto / Manual / Both
- [ ] Language entry accepts comma-separated codes (en, pt, es)
- [ ] Format combobox: srt, vtt, ass, json3
- [ ] Embed checkbox for FFmpegEmbedSubtitle

### 9.2 Subtitle Download
- [ ] Enable subtitles + Auto: yt-dlp uses `writeautomaticsub`
- [ ] Enable subtitles + Manual: yt-dlp uses `writesubtitles`
- [ ] Enable subtitles + Both: both flags set
- [ ] Language codes passed as `subtitleslangs` list
- [ ] Format passed as `subtitlesformat`
- [ ] Embed option adds FFmpegEmbedSubtitle postprocessor
- [ ] Embed NOT added in audio mode
- [ ] .srt file appears alongside video file
- [ ] Multiple language subs download correctly

### 9.3 Subtitle Info
- [ ] After verify, available subtitle languages shown in log
- [ ] Both manual and auto-generated subs detected
- [ ] "No subtitles available" if none found

### 9.4 Auto-Translate
- [ ] "Translate subtitles" checkbox visible in subtitle card
- [ ] "Translate to" combobox with 24 common languages
- [ ] Combobox is editable (custom language codes accepted)
- [ ] When translate enabled: target lang added to `subtitleslangs`
- [ ] When translate enabled: `writeautomaticsub` forced to True
- [ ] Verify shows "🌐 N auto-translate languages available" info
- [ ] Works with all subtitle types (auto/manual/both)
- [ ] Translate checkbox disabled when subtitles disabled
- [ ] Downloaded subtitle file is in target language

### 9.5 i18n
- [ ] All sub_* keys present in all 7 languages (EN, PT, ES, FR, DE, IT, JA) — including sub_translate_*

---

## 10. Archive Mode (Q3 2026) — IMPLEMENTED

### 10.1 Archive Toggle
- [ ] Archive enabled/disabled in Settings tab
- [ ] Setting persisted in config.json (`archive_enabled`)
- [ ] When enabled, `download_archive` path set in yt-dlp opts

### 10.2 Archive Tracking
- [ ] Downloaded video IDs written to `download_archive.txt`
- [ ] yt-dlp skips previously downloaded videos automatically
- [ ] Works in single, batch, and playlist modes
- [ ] Archive count displayed in Settings

### 10.3 Archive Management
- [ ] Export archive to user-selected file
- [ ] Import archive merges entries (no duplicates)
- [ ] Clear archive with confirmation dialog
- [ ] Count updates after import/clear

### 10.4 Quality Profiles
- [ ] Save current settings as named profile
- [ ] Load profile restores: quality, mode, audio, subtitles
- [ ] Delete profile
- [ ] Profiles persisted in config.json
- [ ] Profile combo refreshes after save/delete
- [ ] Empty profile name ignored

### 10.5 Settings Tab
- [ ] Settings tab accessible from sidebar (⚙️)
- [ ] Proxy entry saves to config
- [ ] Rate limit entry saves to config
- [ ] Max retries spinbox (1-10) saves to config
- [ ] Cookie file browser dialog works
- [ ] Save Settings button persists all values
- [ ] Settings loaded from config on app start
- [ ] Network settings applied to yt-dlp downloads
- [ ] Rate limit parsed correctly (5M = 5242880, 500K = 512000)

---

## 11. Download Queue Management (Q2 2026) — IMPLEMENTED

### 11.1 Queue UI
- [ ] Queue card visible in batch tab (below URL input)
- [ ] Queue progress label shows "X of Y completed"
- [ ] Each URL shown as row with emoji status + title
- [ ] Status updates in real-time during download

### 11.2 Queue Controls
- [ ] Start batch: all URLs added to queue as "queued"
- [ ] Queue processes URLs sequentially
- [ ] Pause button pauses queue (queued → paused)
- [ ] Resume button resumes queue (paused → queued)
- [ ] Stop All stops the entire batch
- [ ] Clear Completed removes finished items from queue

### 11.3 Queue Status Per URL
- [ ] ⏳ Queued: waiting to download
- [ ] ⬇️ Downloading: currently being downloaded
- [ ] ✅ Completed: downloaded successfully
- [ ] ❌ Failed: download error
- [ ] ⏸️ Paused: queue is paused

---

## 12. Per-Channel Quality Defaults (Q3 2026) — IMPLEMENTED

### 12.1 Settings UI
- [ ] Per-Channel Defaults card visible in Settings tab
- [ ] Channel name entry + quality combobox + Add button
- [ ] Quality options: best, 1080, 720, 480, audio
- [ ] Each saved default shown as row with Remove button

### 12.2 Channel Default Logic
- [ ] Default saved to config.json under `channel_defaults`
- [ ] On verify, uploader matched (case-insensitive partial match)
- [ ] Quality auto-set when channel default matches
- [ ] Log message confirms applied channel default
- [ ] Remove button deletes from config and refreshes UI

---

## 13. Live Stream Enhancements (Q4 2026) — IMPLEMENTED

### 13.1 Live Detection
- [ ] Verify video detects `is_live` from metadata
- [ ] Dialog offers to switch to Live tab
- [ ] Yes → Live tab URL populated + switched
- [ ] No → stays in download tab

### 13.2 History Badges
- [ ] 🔴 LIVE badge shown for live recordings in history
- [ ] 📱 SHORT badge shown for /shorts/ URLs in history
- [ ] Badges appear to the left of the date label

### 13.3 Live History Entries
- [ ] Live recordings save `is_live: true` in history
- [ ] Thumbnail and video_id saved for live recordings

---

## 14. YouTube Chapters (Q4 2026) — IMPLEMENTED

### 14.1 Chapter Detection
- [ ] Verify detects chapters from `info['chapters']`
- [ ] Log shows "X chapters found"
- [ ] Chapter list shown in log (title + timestamp)
- [ ] Chapters card appears in download tab after verify
- [ ] Chapters card hidden if no chapters

### 14.2 Chapter Download
- [ ] "Split by Chapters" checkbox available
- [ ] "Download All Chapters" button triggers split download
- [ ] Each chapter uses `download_sections` with start/end time
- [ ] Files named: `video title - chapter title.ext`
- [ ] Each chapter recorded in history separately
- [ ] Progress logged per chapter

---

## 15. YouTube Shorts (Q4 2026) — IMPLEMENTED

### 15.1 Shorts Detection
- [ ] /shorts/ URLs detected on verify
- [ ] Short duration + vertical aspect ratio also detected
- [ ] 📱 Short detected message shown in log
- [ ] Standard download flow works for Shorts
- [ ] All quality/format options apply to Shorts

---

## 16. Edge Cases & Error Handling

### 16.1 Network
- [ ] No internet connection shows error
- [ ] Slow connection doesn't crash app
- [ ] Connection lost mid-download (should error gracefully)

### 16.2 File System
- [ ] Output folder doesn't exist (should create)
- [ ] Output folder is read-only (should error)
- [ ] Disk full during download (should error)
- [ ] File already exists (should handle)
- [ ] Very long filename (should truncate)

### 16.3 App Lifecycle
- [ ] App starts successfully
- [ ] App closes gracefully (no orphan processes)
- [ ] Close during active download shows confirmation
- [ ] Config saved on close
- [ ] Logging works (check config/app.log)

---

## 17. Build & Distribution

### 17.1 PyInstaller Build
- [ ] `python scripts/build.py` runs successfully
- [ ] `dist/EasyCut.exe` is created
- [ ] .exe runs on clean Windows (no Python installed)
- [ ] OAuth credentials embedded in .exe
- [ ] Assets (fonts, icons) bundled correctly
- [ ] Config folder created on first run from .exe

### 17.2 Installation Check
- [ ] `python scripts/check_installation.py` passes all checks
- [ ] Missing dependencies reported correctly

---

## 18. Live Post-Processing (Q4 2026) — IMPLEMENTED

### 18.1 Audio Extraction in Live
- [ ] "Extract audio only" checkbox in Live tab
- [ ] Audio format combobox (mp3, wav, m4a, opus)
- [ ] Audio bitrate combobox (128, 192, 256, 320)
- [ ] When enabled: format set to bestaudio, FFmpegExtractAudio added
- [ ] Audio file produced from live recording

### 18.2 Subtitles in Live
- [ ] "Download subtitles" checkbox in Live tab
- [ ] When enabled: writeautomaticsub + writesubtitles set
- [ ] SRT files downloaded alongside live recording

### 18.3 Preferred Codec in Live
- [ ] Codec combobox in Live tab (auto, h264, vp9, av1)
- [ ] Codec setting also in Settings tab
- [ ] Setting persisted in config.json (`live_codec`)
- [ ] H.264: format includes `[vcodec^=avc]`
- [ ] VP9: format includes `[vcodec^=vp9]`
- [ ] AV1: format includes `[vcodec^=av01]`
- [ ] Auto: no codec filter applied

### 18.4 Network Settings in Live
- [ ] Proxy applied to live recordings
- [ ] Rate limit applied to live recordings
- [ ] Max retries applied to live recordings

---

## 19. Batch Quality Selector (Q2 2026) — IMPLEMENTED

### 19.1 Quality UI
- [ ] Batch Quality card visible in batch tab
- [ ] Quality preset combobox (best, 1080, 720, 480, audio)
- [ ] Fallback checkbox (enabled by default)
- [ ] Help text explains override behavior

### 19.2 Quality Logic
- [ ] Batch quality overrides main download quality
- [ ] Audio preset forces audio mode in batch
- [ ] Fallback appends broader format selector
- [ ] Fallback warning shown when quality downgraded

---

## 20. Automatic Retries (Q1 2027) — IMPLEMENTED

### 20.1 Single Download
- [ ] Network errors trigger retry (connection, timeout, 429, 5xx)
- [ ] Exponential backoff: 2s, 4s, 8s between retries
- [ ] Max retries from settings (default 3)
- [ ] Non-retryable errors fail immediately (private, unavailable, etc.)
- [ ] Retry log messages shown to user

### 20.2 Batch Download
- [ ] Same retry logic per URL in batch
- [ ] Each URL retried independently
- [ ] Retry count shown in queue log
- [ ] Cookie errors stop entire batch (not retryable)

---

## 21. Download Scheduler (Q1 2027) — IMPLEMENTED

### 21.1 Scheduler UI
- [ ] Scheduler card visible in Settings tab
- [ ] Hour spinbox (0-23) and minute spinbox (0-59)
- [ ] URL entry field
- [ ] Schedule button adds to list
- [ ] Clear All button removes all scheduled
- [ ] Status label shows count of pending downloads
- [ ] Each scheduled item shows time, URL, status emoji

### 21.2 Scheduler Logic
- [ ] Scheduled download starts at specified time
- [ ] Timer checks every 30 seconds
- [ ] Download uses current quality/mode settings
- [ ] Completed downloads saved to history
- [ ] Failed downloads logged with friendly error
- [ ] Individual items removable via ✕ button
- [ ] Timer stops when no pending items remain

### 21.3 i18n
- [ ] All scheduler_* keys present in all 7 languages (EN, PT, ES, FR, DE, IT, JA)
- [ ] All live_postprocess/codec keys present in all 7 languages
- [ ] All batch_quality_* keys present in all 7 languages
- [ ] All retry_* keys present in all 7 languages

---

## 22. Enhanced History (Q1 2027) — IMPLEMENTED

### 22.1 Sort & Filter UI
- [ ] Sort combobox in history (date_desc, date_asc, title_asc, title_desc, status)
- [ ] Status filter combobox (all, success, error)
- [ ] Sort/filter trigger instant refresh
- [ ] History count label shows "X of Y shown"

### 22.2 Sort Logic
- [ ] date_desc: newest first (default)
- [ ] date_asc: oldest first
- [ ] title_asc: alphabetical A-Z
- [ ] title_desc: alphabetical Z-A
- [ ] status: grouped by status

### 22.3 Enhanced Metadata
- [ ] Uploader shown in history cards (👤)
- [ ] Quality shown in history cards (📺)
- [ ] Duration shown in history cards (⏱)
- [ ] Format shown in history cards (📦)
- [ ] Metadata saved with download entries

### 22.4 Search Enhancement
- [ ] Search now includes: filename, URL, date, uploader, quality, format

---

## 23. Post-Processing Hub (Q1 2027) — IMPLEMENTED

### 23.1 Context Menu
- [ ] Right-click on any history card shows context menu
- [ ] Menu items: Copy URL, Open Folder, Re-download, Extract Audio, Delete
- [ ] Context menu binds to card + all children widgets

### 23.2 Post-Processing Actions
- [ ] Copy URL copies to system clipboard
- [ ] Open Output Folder opens explorer to output_dir
- [ ] Re-download populates download tab URL + switches tab
- [ ] Extract Audio (MP3): downloads bestaudio + FFmpegExtractAudio 192kbps
- [ ] Extract Audio requires FFmpeg (shows error if missing)
- [ ] Delete from History removes single entry (with confirm dialog)

### 23.3 i18n
- [ ] All pp_* keys present in all 7 languages (EN, PT, ES, FR, DE, IT, JA)
- [ ] All history_sort/filter/count keys present in all 7 languages

---

## 24. Video/Audio Enhancement via FFmpeg (Q1 2027) — IMPLEMENTED

### 24.1 Enhancement Submenu
- [ ] Right-click a **successful** history entry → "✨ Enhance..." submenu appears
- [ ] Submenu shows 4 options: Normalize Audio, Denoise Video, Stabilize Video, Upscale to 1080p
- [ ] Submenu only appears for entries with `status == "success"`

### 24.2 Normalize Audio
- [ ] Select "🔊 Normalize Audio" on a downloaded entry
- [ ] FFmpeg runs with `loudnorm` filter (EBU R128 normalization)
- [ ] Output file created as `{name}_normalized.{ext}` in output folder
- [ ] Log shows progress and completion message with file size

### 24.3 Denoise Video
- [ ] Select "🎞️ Denoise Video" on a downloaded video entry
- [ ] FFmpeg runs with `hqdn3d` filter (temporal + spatial denoising)
- [ ] Output file created as `{name}_denoised.{ext}`
- [ ] Audio stream is copied (not re-encoded)

### 24.4 Stabilize Video
- [ ] Select "📐 Stabilize Video" on a shaky video
- [ ] FFmpeg runs with `deshake` filter (motion compensation)
- [ ] Output file created as `{name}_stabilized.{ext}`
- [ ] Audio stream is copied

### 24.5 Upscale to 1080p
- [ ] Select "⬆️ Upscale to 1080p" on a lower-resolution video
- [ ] FFmpeg runs with `scale=-2:1080:flags=lanczos` filter
- [ ] Output file created as `{name}_1080p.{ext}`
- [ ] Aspect ratio is preserved (width auto-calculated)

### 24.6 Error Handling
- [ ] If FFmpeg is not installed → error dialog "FFmpeg not found"
- [ ] If source file is missing/moved → warning "File not found in output folder"
- [ ] If FFmpeg process fails → error logged with stderr details
- [ ] If output file already exists → auto-incremented name (`_normalized_1`, `_normalized_2`, etc.)

### 24.7 i18n
- [ ] Enhancement keys present in all 7 languages (EN, PT, ES, FR, DE, IT, JA): pp_enhance, pp_normalize_audio, pp_denoise_video, pp_stabilize_video, pp_upscale, pp_enhancing, pp_enhance_done, pp_enhance_error, pp_no_file

---

## Test URLs

### Standard Videos
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ   (standard video)
https://www.youtube.com/watch?v=jNQXAC9IVRw    (short video, "Me at the zoo")
https://youtu.be/dQw4w9WgXcQ                   (short URL format)
```

### YouTube Shorts
```
https://www.youtube.com/shorts/VIDEO_ID         (Shorts URL format)
```

### Videos with Chapters
```
(Use any long-form video with chapters — educational content often has them)
```

### Playlists
```
https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf  (small playlist)
```

### Live Streams
```
(Use any currently live stream URL — these change frequently)
```

### Edge Cases
```
https://www.youtube.com/watch?v=INVALID_ID      (invalid video ID)
https://not-youtube.com/video                     (non-YouTube URL)
(empty string)                                    (empty URL)
```
