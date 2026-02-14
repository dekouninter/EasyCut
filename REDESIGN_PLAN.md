# 🎨 EasyCut — Complete UI Redesign Plan

**Created:** 2026-02-13  
**Author:** Deko Costa  
**Priority:** Appearance > Functionality  
**Status:** Implementation Complete (P0–P5 done, P6 in progress)

---

## 📋 Table of Contents

1. [Design Decisions Summary](#design-decisions-summary)
2. [Phase 0 — Cleanup & Foundation](#phase-0--cleanup--foundation)
3. [Phase 1 — New Design System](#phase-1--new-design-system)
4. [Phase 2 — Core Layout](#phase-2--core-layout)
5. [Phase 3 — Component Library](#phase-3--component-library)
6. [Phase 4 — Sections Rebuild](#phase-4--sections-rebuild)
7. [Phase 5 — New Features](#phase-5--new-features)
8. [Phase 6 — Polish & QA](#phase-6--polish--qa)
9. [Technical Notes](#technical-notes)

---

## 🎯 Design Decisions Summary

| Decision | Choice |
|----------|--------|
| **Design Language** | Clean Minimal (Linear/Notion style) |
| **Accent Color** | `#4A90D9` (Steel Blue) — replaces coral `#f85451` |
| **Dark Background** | `#1E1E1E` (VS Code Dark) — replaces navy `#0A0E27` |
| **Light Background** | `#FFFFFF` (keep white) |
| **Navigation** | Sidebar left, expandable/collapsible (VS Code style) |
| **Header** | Complete header redesigned (logo + title + controls) |
| **Buttons** | Outline as default, Filled for CTAs only |
| **Cards** | Elevated with simulated shadow |
| **Inputs** | Outlined with visible border, accent on focus |
| **History** | Treeview/Table (sortable columns) |
| **Log** | Collapsible panel (VS Code terminal style) |
| **Progress** | Inline progress bar with %, speed, ETA |
| **Scrollbars** | Custom rounded, thin, accent on hover |
| **Window Size** | 1000×700 (min 800×500) |
| **Theme** | Dark + Light with toggle (default: dark) |
| **Font** | Inter Display / Segoe UI fallback (keep) |
| **Login** | Banner + Popup (keep, restyle) |
| **Audio Tab** | DELETE — improve audio options inside Download |
| **About Tab** | Simplified (version, credits, links only) |
| **Donation** | Floating button redesigned (blue outline style) |
| **Dead Code** | Adapt existing screens/factories to new design |

### New Features to Add
- Keyboard shortcuts (Ctrl+V paste URL, Ctrl+D download, Ctrl+T theme)
- Toast notifications (replace ModernAlert)
- Context menu on history items (right-click)
- Drag & Drop URLs into app

---

## 🧹 Phase 0 — Cleanup & Foundation

> Remove dead code, unify systems, prepare clean base for redesign.

### 0.1 — Delete Audio Tab Code ✅
- [x] Remove `create_audio_tab()` method from `easycut.py` (if still exists)
- [x] Remove `AudioScreen` from `ui/screens/audio_screen.py`
- [x] Remove audio screen import from `ui/screens/__init__.py`
- [x] Remove "Audio" tab from sidebar navigation
- [x] Remove `tab_audio` translation keys from `i18n.py`

### 0.2 — Unify Theme Systems (3 → 1) ✅
- [x] Audit all imports of `ui_enhanced.Theme` — list every file
- [x] Audit all imports of `design_system.ModernTheme`/`DesignTokens` — list every file
- [x] Audit all imports of `theme/theme_manager.ThemeManager` — list every file
- [x] Create single `src/theme.py` (or rewrite `design_system.py`) as THE one theme source
- [x] Migrate all `ui_enhanced.Theme` usage → new unified theme
- [x] Migrate all `DesignTokens` usage → new unified theme
- [x] Delete `theme/theme_manager.py`
- [x] Remove `Theme` class from `ui_enhanced.py` (keep ConfigManager, LogWidget, etc.)
- [x] Update all imports across codebase

### 0.3 — Remove Hardcoded Colors ✅
- [x] Replace `#FF0000` in live stream status → use theme.error
- [x] Replace `#FF9800` in live stream offline → use theme.warning
- [x] Replace `#10B981` in history success → use theme.success
- [x] Replace `#EF4444` in history error → use theme.error
- [x] Replace `#F59E0B` in history pending → use theme.warning
- [x] Replace `#3B82F6` in history default → use theme.info
- [x] Replace `#4CAF50` / `#45a049` in donation → use theme.accent
- [x] Replace `#FF6B6B` / `#E63946` in donation button → use theme.accent
- [x] Replace all `"Arial"` in donation_system.py → use LOADED_FONT_FAMILY
- [x] Replace all `"Segoe UI"` hardcoded → use LOADED_FONT_FAMILY or theme font

### 0.4 — Fix Known Bugs ✅
- [x] Fix `ModernAlert` dark_mode bug: pass `dark_mode` parameter to `DesignTokens()`
- [x] Fix `ModernTabHeader` dark_mode bug: same issue
- [x] Fix `apply_theme()` called twice in `__init__`
- [x] Fix canvas scroll — bind `<Configure>` to update scrollregion on window resize

### 0.5 — Remove color_extractor.py Integration ✅
- [x] Remove icon color extraction from design_system.py (no longer needed)
- [x] Delete `color_extractor.py` (we're using fixed blue now)
- [x] Update imports

---

## 🎨 Phase 1 — New Design System

> Build the complete design token system with all colors, fonts, spacing.

### 1.1 — Color Palette

#### Dark Theme
```
bg_primary:     #1E1E1E    (main background — VS Code style)
bg_secondary:   #252526    (sidebar, secondary panels)
bg_tertiary:    #2D2D2D    (cards, elevated surfaces)
bg_elevated:    #333333    (hover states, modals)
bg_hover:       #3C3C3C    (hover highlight)

fg_primary:     #E4E4E4    (main text)
fg_secondary:   #A0A0A0    (secondary text, labels)
fg_tertiary:    #6A6A6A    (placeholders, disabled)
fg_disabled:    #4A4A4A    (disabled elements)

accent_primary: #4A90D9    (Steel Blue — buttons, links, focus)
accent_hover:   #5BA0E9    (accent hover state)
accent_pressed: #3A80C9    (accent pressed state)
accent_muted:   #4A90D920  (accent at 12% opacity for backgrounds)

success:        #4CAF50    (green)
success_bg:     #1B3A1F    (muted green bg)
warning:        #FFA726    (amber)
warning_bg:     #3E2E1A    (muted amber bg)
error:          #EF5350    (red)
error_bg:       #3A1F1F    (muted red bg)
info:           #42A5F5    (light blue)
info_bg:        #1A2E3E    (muted blue bg)

border:         #3C3C3C    (default borders)
border_focus:   #4A90D9    (focus ring = accent)
border_hover:   #505050    (hover borders)

shadow:         #00000040  (card shadow — 25% black)
```

#### Light Theme
```
bg_primary:     #FFFFFF    (main background)
bg_secondary:   #F5F5F5    (sidebar, secondary panels)
bg_tertiary:    #FAFAFA    (cards)
bg_elevated:    #FFFFFF    (modals)
bg_hover:       #EEEEEE    (hover highlight)

fg_primary:     #1A1A1A    (main text)
fg_secondary:   #555555    (secondary text)
fg_tertiary:    #888888    (placeholders, disabled)
fg_disabled:    #BBBBBB    (disabled)

accent_primary: #4A90D9    (Steel Blue — same in both themes)
accent_hover:   #3A80C9    (darker on hover for light)
accent_pressed: #2A70B9    (darker on press)
accent_muted:   #4A90D915  (accent at 8% opacity)

success:        #2E7D32    (dark green for contrast)
success_bg:     #E8F5E9
warning:        #E65100    (dark amber)
warning_bg:     #FFF3E0
error:          #C62828    (dark red)
error_bg:       #FFEBEE
info:           #1565C0    (dark blue)
info_bg:        #E3F2FD

border:         #E0E0E0
border_focus:   #4A90D9
border_hover:   #CCCCCC

shadow:         #00000015  (lighter shadow for light theme)
```

### 1.2 — Typography Scale
```python
FONT_FAMILY = LOADED_FONT_FAMILY  # "Inter Display" or "Segoe UI"

SIZE_HERO    = 32    # App title only
SIZE_H1      = 24    # Section headers
SIZE_H2      = 18    # Card titles
SIZE_H3      = 15    # Subsection titles
SIZE_BODY    = 13    # Default body text, buttons, inputs
SIZE_CAPTION = 11    # Captions, timestamps, secondary info
SIZE_TINY    = 9     # Badges, version numbers

WEIGHT_BOLD     = "bold"
WEIGHT_SEMIBOLD = "bold"  # Tkinter only has normal/bold
WEIGHT_NORMAL   = "normal"
```

### 1.3 — Spacing Scale (4px grid)
```python
SPACE_XXS = 2     # Micro gaps
SPACE_XS  = 4     # Icon padding, tight spacing
SPACE_SM  = 8     # Between inline elements
SPACE_MD  = 12    # Card internal padding, between rows
SPACE_LG  = 16    # Section gaps, sidebar padding
SPACE_XL  = 24    # Between major sections
SPACE_XXL = 32    # Page margins
```

### 1.4 — Shadow System (simulated)
Cards use a double-frame technique:
```
┌── Outer Frame (bg=shadow_color, padding=1) ──┐
│ ┌── Inner Frame (bg=bg_tertiary, content) ──┐ │
│ │                                            │ │
│ │   Card Content Here                        │ │
│ │                                            │ │
│ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```
Shadow simulated via offset: 2px right, 2px bottom darker frame behind the card.

### 1.5 — Implementation ✅
- [x] Rewrite `design_system.py` with new palette above
- [x] Remove ColorPalette.DARK / ColorPalette.LIGHT old colors
- [x] Update Typography constants
- [x] Update Spacing constants
- [x] Create `ElevatedCard` class with shadow simulation (via ModernCard with border)
- [x] Create shadow utility function
- [x] Export single `theme` object with `.colors`, `.fonts`, `.spacing`
- [x] All token access via `theme.colors.bg_primary`, `theme.fonts.body`, etc.

---

## 📐 Phase 2 — Core Layout

> Build the main window structure: sidebar + header + content area.

### 2.1 — Window Setup ✅
- [x] Change default geometry to `1000x700`
- [x] Change minsize to `800x500`
- [x] Update window title: "EasyCut"
- [x] Keep icon loading from `main.py`

### 2.2 — Main Layout Structure
```
┌───────────────────────────────────────────────────────┐
│ Header (45px) — Logo + Title + Controls              │
├──────────┬────────────────────────────────────────────┤
│          │                                            │
│ Sidebar  │  Content Area                              │
│ (200px   │  (fills remaining space)                   │
│  or 50px │                                            │
│  when    │  ┌─ Active Section ─────────────────────┐  │
│  clpsed) │  │                                      │  │
│          │  │  (Download / Batch / Live /           │  │
│ ┌──────┐ │  │   History / About)                   │  │
│ │ Nav  │ │  │                                      │  │
│ │ Items│ │  └──────────────────────────────────────┘  │
│ │      │ │                                            │
│ │      │ │  ┌─ Collapsible Log Panel ──────────────┐  │
│ ├──────┤ │  │ (hidden by default, toggle to show)  │  │
│ │Footer│ │  └──────────────────────────────────────┘  │
│ └──────┘ │                                            │
├──────────┴────────────────────────────────────────────┤
│ Status Bar (optional, 24px)                           │
└───────────────────────────────────────────────────────┘
```

### 2.3 — Header Bar (45px) ✅
- [x] Create redesigned header frame
- [x] Left: App icon (24×24) + "EasyCut" title (SIZE_H2, bold)
- [x] Center: (empty, or breadcrumb of current section)
- [x] Right group: Theme toggle button (outline, icon only) + Language selector (compact combobox) + Login button/status
- [x] Bottom border: 1px `border` color
- [x] Login banner (when not logged in): slim bar under header with warning icon + text + Login button

### 2.4 — Sidebar ✅
- [x] Create sidebar frame — left side, full height below header
- [x] Width: 200px expanded, 50px collapsed
- [x] Toggle button at top of sidebar (hamburger ☰ or chevron ◀/▶)
- [x] Nav items (top-aligned):
  ```
  ⬇️  Download      (or icon: download arrow)
  📦  Batch         (or icon: layers/stack)
  🔴  Live          (or icon: radio/broadcast)
  📜  History       (or icon: clock/history)
  ℹ️  About         (or icon: info circle)
  ```
- [x] Each nav item: icon (20px) + label (SIZE_BODY) + hover highlight (bg_hover)
- [x] Active item: accent_primary left border (3px) + accent_muted background
- [x] Collapsed mode: only icons, tooltip on hover
- [x] Footer section (bottom-aligned):
  - Version badge ("v1.0.0", SIZE_TINY)
  - Select Folder button (outline, compact)
  - Open Folder button (outline, compact)

### 2.5 — Content Area ✅
- [x] Right side of sidebar, fills remaining space
- [x] Padding: SPACE_XL (24px)
- [x] Scrollable when content exceeds viewport
- [x] Content changes based on active sidebar item
- [x] Smooth transition between sections (or instant swap)

### 2.6 — Collapsible Log Panel ✅
- [x] Bottom of content area, above status bar
- [x] Toggle button: "▼ Log" / "▲ Log" or keyboard shortcut
- [x] Default: collapsed (0px height)
- [x] Expanded: 200px height, resizable drag handle
- [x] Monospace font for log output
- [x] Auto-scroll to bottom
- [x] Clear log button
- [x] Color-coded lines: info=fg_secondary, warning=warning, error=error

---

## 🧩 Phase 3 — Component Library

> Redesign every reusable component to match new design system.

### 3.1 — ModernButton Redesign ✅
- [x] **Outline variant** (default): transparent bg, `accent_primary` text + border 1.5px, rounded
  - Hover: `accent_muted` bg
  - Pressed: `accent_pressed` text + border
- [x] **Filled variant** (CTA only): `accent_primary` bg, white text, no visible border
  - Hover: `accent_hover` bg
  - Pressed: `accent_pressed` bg
- [x] **Ghost variant**: no border, no bg, `accent_primary` text only
  - Hover: `accent_muted` bg
- [x] **Danger variant**: same as outline but with `error` color
  - Hover: `error_bg` background
- [x] Icon support: emoji left of text (SIZE_BODY)
- [x] Size variants: `sm` (h=28, text=11), `md` (h=34, text=13), `lg` (h=40, text=15)
- [x] Disabled state: `fg_disabled` text, no hover

### 3.2 — ElevatedCard Redesign ✅
- [x] Background: `bg_tertiary`
- [x] Shadow: simulated via outer frame with `shadow` color offset 2px (implemented as 1px border)
- [x] Border radius: simulated via padding (Tkinter limitation)
- [x] Padding: SPACE_MD (12px) all sides
- [x] Optional title: SIZE_H3, bold, fg_primary
- [x] Optional subtitle: SIZE_CAPTION, fg_secondary
- [x] Hover state (optional): slightly lighter bg

### 3.3 — Input Fields Redesign
- [ ] **Entry**: border 1.5px `border`, bg `bg_secondary`, fg `fg_primary`
  - Focus: border `accent_primary`, subtle glow (thicker border or color bg)
  - Placeholder text: `fg_tertiary` (simulated via bind/unbind)
  - Error state: border `error`, error message below
  - Height: 34px (SIZE_BODY font + padding)
- [ ] **Text (multi-line)**: same styling, with scrollbar
- [ ] **Combobox**: same border style, dropdown matches theme

### 3.4 — Radiobuttons & Checkboxes
- [ ] Custom styled via ttk (remove emoji prefixes from options)
- [ ] Use accent_primary for selected state indicator
- [ ] Clean text labels (SIZE_BODY)
- [ ] Grid layout: consistent columns

### 3.5 — Toast Notifications (NEW) ✅
- [x] Replace ModernAlert with toast system
- [x] Toast appears top-right of content area
- [x] Auto-dismiss after 4 seconds (configurable)
- [x] Manual dismiss via ✕ button
- [x] Variants: success (green left bar), warning (amber), error (red), info (blue)
- [x] Slide-in animation (via `after()` + geometry changes)
- [x] Stack multiple toasts vertically
- [x] Icon + title + message layout

### 3.6 — Progress Bar (NEW)
- [ ] Inline in download card
- [ ] Blue accent fill, gray track
- [ ] Rounded ends
- [ ] Labels: percentage (left), speed + ETA (right)
- [ ] Indeterminate mode: animated blue stripe
- [ ] Height: 6px bar + labels above

### 3.7 — Custom Scrollbar
- [ ] Width: 6px (8px on hover)
- [ ] Track: transparent (or bg_secondary)
- [ ] Thumb: `border_hover` color, rounded ends
- [ ] Thumb hover: `accent_primary`
- [ ] Thumb pressed: `accent_pressed`
- [ ] Smooth appearance transition

### 3.8 — Treeview (for History)
- [ ] Custom styled ttk.Treeview
- [ ] Headers: bg_secondary, fg_secondary, SIZE_CAPTION, bold
- [ ] Rows: alternating bg_primary / bg_secondary (zebra striping)
- [ ] Selected row: accent_muted background + accent_primary text
- [ ] Hover row: bg_hover
- [ ] Columns: Status icon | Filename | Format | Date | Size
- [ ] Sortable by clicking column headers
- [ ] Right-click context menu

### 3.9 — Context Menu (NEW)
- [ ] Custom styled `tk.Menu` (tearoff=0)
- [ ] Options for history items: "Re-download", "Copy URL", "Open file", "Delete"
- [ ] Accent highlight on hover
- [ ] Keyboard accessible

### 3.10 — Tooltip
- [ ] Redesign ModernTooltip: bg `bg_elevated`, border 1px `border`, shadow
- [ ] Font: SIZE_CAPTION
- [ ] Delay: 500ms before show
- [ ] Arrow pointing to source element (optional)

---

## 📑 Phase 4 — Sections Rebuild

> Rebuild every section/tab with new components and layout.

### 4.1 — Download Section ✅
- [x] Section header: "Download" (SIZE_H1, bold)
- [x] **URL Card** (ElevatedCard):
  - Row: URL input (outlined, expands) + "Verify" button (outline, sm)
  - Drag & Drop area: dashed border, "Drop URL here" text, icon
- [x] **Video Info Card** (appears after verify):
  - Thumbnail placeholder (if available)
  - Title (SIZE_H3, bold, truncated)
  - Duration, channel, format info (SIZE_CAPTION, fg_secondary)
- [x] **Download Options Card**:
  - **Mode** section: Radio group — Full Video | Time Range | Until Time
  - **Time inputs** (shown when Time Range / Until Time selected):
    - Start time + End time entries (outlined, compact)
    - Help text (SIZE_CAPTION, fg_tertiary)
  - **Quality** section: Radio group — Best | 1080p | 720p | 480p
  - **Audio Format** section (improved integration):
    - Toggle: "Download as audio only" (checkbox)
    - When checked, show: Format dropdown (MP3/WAV/M4A/OPUS) + Bitrate dropdown (128/192/256/320)
    - When unchecked, hide audio options
- [x] **Action Row**:
  - "Download" button (filled, lg) — primary CTA
  - "Stop" button (danger outline, lg) — shown during download
  - "Clear" button (ghost, sm) — clears form
- [x] **Progress** (shown during download):
  - Progress bar with %, speed, ETA
  - Current file label

### 4.2 — Batch Section ✅
- [x] Section header: "Batch Download" (SIZE_H1, bold)
- [x] **URL List Card** (ElevatedCard):
  - Multi-line Text widget (outlined, h=15)
  - Placeholder: "Paste URLs here, one per line..."
  - Row: "Paste from Clipboard" (outline, sm) + "Clear All" (ghost, sm) + count label ("3 URLs")
- [x] **Options Card** (shared quality/format with Download):
  - Quality radio group
  - Audio-only toggle + format/bitrate
- [x] **Action Row**:
  - "Download All" (filled, lg) + "Stop All" (danger outline, lg)
- [x] **Progress**:
  - Overall: "Downloading 3/10 URLs"
  - Current file progress bar
  - Per-URL status list (compact)

### 4.3 — Live Section ✅
- [x] Section header: "Live Recording" (SIZE_H1, bold)
- [x] **URL Card** (ElevatedCard):
  - URL input + "Check" button (outline, sm)
- [x] **Stream Info Card** (after check):
  - Status indicator: ● Live (green) / ● Offline (gray) / ● Error (red)
  - Stream title, duration
- [x] **Recording Options Card**:
  - Mode: Continuous | Duration limit | Schedule
  - Duration inputs (HH:MM:SS entries) — shown for Duration mode
  - Quality: Best / 1080p / 720p / Audio Only
- [x] **Action Row**:
  - "Start Recording" (filled, lg) + "Stop" (danger outline, lg)
- [x] **Progress**:
  - Recording indicator: ● REC + elapsed time
  - File size counter

### 4.4 — History Section ✅
- [x] Section header: "Download History" (SIZE_H1, bold)
- [x] **Action Row** (above table):
  - "Refresh" (outline, sm) + "Clear History" (danger outline, sm) + search/filter input
- [x] **History Table** (Treeview):
  - Columns: Status | Filename | Format | Date | Size
  - Status: ✓ (green), ✗ (red), ⏳ (amber) — icons not text
  - Sortable columns (click header)
  - Zebra striping
  - Right-click context menu: Re-download | Copy URL | Open file | Open folder | Delete
- [x] **Empty state**: centered icon + "No downloads yet" text

### 4.5 — About Section ✅
- [x] Section header: "About EasyCut" (SIZE_H1, bold)
- [x] **Info Card** (single card):
  - App icon (48×48) + "EasyCut" (SIZE_H2) + version
  - Author: "Deko Costa"
  - License: "GPL-3.0"
  - Links: GitHub repo, Issues, Discussions (as ghost buttons)
- [ ] **Support Card**:
  - Donation links (Buy Me a Coffee, Livepix) as outline buttons
- [ ] **Credits Card** (collapsible):
  - Libraries: yt-dlp, FFmpeg, Keyring, Pillow
  - Design: Inter font, Feather icons

### 4.6 — Login Banner & Popup ✅
- [x] Redesign login banner: slim bar (32px) with info icon + message + "Login" button (outline, sm)
- [x] Banner matches new theme (bg_secondary, border bottom)
- [x] Redesign LoginPopup:
  - Clean modal with new card style
  - Outlined inputs for email/password
  - "Login" filled button + "Cancel" ghost button
  - "Remember me" checkbox
  - Proper focus order (Tab key navigation)

### 4.7 — Donation Button Redesign
- [ ] Restyle floating button: outline blue style
- [ ] Use LOADED_FONT_FAMILY instead of Arial
- [ ] Use theme colors instead of hardcoded Material colors
- [ ] Redesign DonationWindow: new card style, blue accent buttons
- [ ] Position: bottom-right of content area, above log panel

---

## ⚡ Phase 5 — New Features

### 5.1 — Keyboard Shortcuts ✅
- [x] `Ctrl+V` — Paste URL into active input field
- [x] `Ctrl+D` — Start download (if URL is filled)
- [x] `Ctrl+T` — Toggle dark/light theme
- [x] `Ctrl+L` — Toggle log panel visibility
- [x] `Ctrl+O` — Open downloads folder
- [x] `Ctrl+1/2/3/4/5` — Switch to section 1-5
- [x] `Escape` — Cancel current download / Close dialog
- [x] Display shortcuts in tooltip or About section
- [x] Bind at root level, check for conflicts

### 5.2 — Toast Notification System ✅
- [x] Create `ToastManager` class
- [x] Toast types: success, warning, error, info
- [x] Auto-dismiss with configurable duration
- [x] Stack multiple toasts
- [x] Replace all `messagebox` calls with toasts (except confirmations)
- [x] Replace all `ModernAlert` usage with toasts
- [x] Slide-in/fade animation using `after()` callbacks

### 5.3 — Context Menu (History)
- [ ] Right-click on history row → shows menu
- [ ] Options: Re-download, Copy URL, Open file, Open folder, Delete entry
- [ ] Keyboard: Select row + Menu key
- [ ] Disabled options when not applicable (e.g., Open file if file deleted)

### 5.4 — Drag & Drop URLs
- [ ] Bind `<Drop>` event on Download/Batch sections
- [ ] Visual indicator: dashed border highlight when dragging over
- [ ] Parse dropped text for valid URLs
- [ ] Auto-fill URL entry (Download) or append to text (Batch)
- [ ] Note: Native Tkinter doesn't support DnD — may need `tkinterdnd2` package
  - [ ] Add `tkinterdnd2` to requirements.txt if used
  - [ ] Fallback: disable DnD gracefully if package not available

### 5.5 — Inline Progress System
- [ ] Create `ProgressTracker` class
- [ ] Parse yt-dlp output for percentage, speed, ETA
- [ ] Update progress bar in real-time via `root.after()`
- [ ] Show: [█████████░░░░░░] 65% — 2.4 MB/s — ETA: 00:32
- [ ] Indeterminate state for "processing" phases
- [ ] Per-file progress for batch downloads

---

## ✨ Phase 6 — Polish & QA

### 6.1 — Theme Consistency Audit ✅
- [x] Verify EVERY widget uses theme tokens (no hardcoded colors)
- [x] Test dark theme: all text readable, no invisible elements
- [x] Test light theme: all text readable, proper contrast
- [x] Check all states: normal, hover, focus, pressed, disabled
- [x] Check all entry fields: cursor visible, selection colors correct

### 6.2 — Responsive Layout
- [ ] Test at minimum size (800×500) — no overlapping, no cut-off
- [ ] Test at large size (1920×1080) — content doesn't stretch absurdly
- [ ] Sidebar collapse works at small sizes
- [ ] Content area scrolls properly
- [ ] Canvas scrollregion updates on resize (`<Configure>` bind)

### 6.3 — Font Consistency ✅
- [x] Every text element uses LOADED_FONT_FAMILY
- [x] No "Arial" or "Segoe UI" hardcoded anywhere
- [x] Typography scale consistently applied (no random sizes)
- [x] Test with Inter Display missing (fallback works)

### 6.4 — Accessibility
- [ ] Tab order logical (Tab key navigates sensibly)
- [ ] Focus indicators visible (accent border on focused elements)
- [ ] All buttons keyboard-accessible (Enter/Space to activate)
- [ ] Color contrast ratio ≥ 4.5:1 for all text
- [ ] Tooltips on icon-only buttons

### 6.5 — i18n Completeness
- [ ] ALL visible text uses translator (no hardcoded EN or PT strings)
- [ ] Add missing translation keys for new features
- [ ] Test full app in Portuguese — no English leaking through
- [ ] Test full app in English — clean, natural phrasing

### 6.6 — Performance
- [ ] Startup time < 2 seconds
- [ ] Theme toggle < 300ms (full UI rebuild)
- [ ] Language switch < 300ms
- [ ] Sidebar collapse/expand < 100ms
- [ ] No memory leaks during long sessions
- [ ] Profile with `cProfile` if needed

### 6.7 — Documentation Update
- [ ] Update ARCHITECTURE.md with new layout (sidebar, no audio tab)
- [ ] Update TECHNICAL.md with new components
- [ ] Update README.md with new screenshots
- [ ] Update QUICKSTART.md if workflow changed
- [ ] Update REFACTORING_SUMMARY.md with Phase status

### 6.8 — Git & Release
- [ ] Commit after each phase (atomic, tested commits)
- [ ] Push to GitHub after each phase
- [ ] Tag v2.0.0 when redesign is complete
- [ ] Update version in setup.py, __init__.py, About section

---

## 🔧 Technical Notes

### Shadow Simulation in Tkinter

Tkinter has no `box-shadow`. Simulate with layered frames:

```python
class ElevatedCard(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=theme.colors.shadow)
        
        # Shadow offset (2px right, 2px down)
        self.shadow = tk.Frame(self, bg=theme.colors.shadow, width=2, height=2)
        self.shadow.place(relx=1.0, rely=1.0, anchor="se")
        
        # Main card on top
        self.card = tk.Frame(self, bg=theme.colors.bg_tertiary, padx=12, pady=12)
        self.card.pack(padx=(0, 2), pady=(0, 2))
```

Alternative: Use `relief="groove"` or `relief="ridge"` with subtle border colors.

### Collapsible Log Panel

```python
class CollapsiblePanel(tk.Frame):
    def __init__(self, parent):
        self.expanded = False
        self.content_height = 200
        
    def toggle(self):
        if self.expanded:
            self.content.pack_forget()
        else:
            self.content.pack(fill=tk.BOTH, expand=True)
        self.expanded = not self.expanded
```

### Sidebar State Management

```python
class Sidebar(tk.Frame):
    EXPANDED_WIDTH = 200
    COLLAPSED_WIDTH = 50
    
    def __init__(self, parent):
        self.is_expanded = True
        self.nav_items = []
        
    def toggle(self):
        self.is_expanded = not self.is_expanded
        target_width = self.EXPANDED_WIDTH if self.is_expanded else self.COLLAPSED_WIDTH
        self.configure(width=target_width)
        self._update_labels()  # Show/hide text labels
```

### Drag & Drop

```python
# If tkinterdnd2 available:
try:
    from tkinterdnd2 import DND_TEXT, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# Fallback: Just use Ctrl+V paste
```

### Progress Parsing from yt-dlp

```python
def parse_progress(line: str) -> dict:
    """Parse yt-dlp output for progress info."""
    # [download]  45.2% of 120.5MiB at 2.3MiB/s ETA 00:32
    match = re.search(r'(\d+\.?\d*)%.*?(\d+\.?\d*\w+/s).*?ETA\s+(\S+)', line)
    if match:
        return {
            "percent": float(match.group(1)),
            "speed": match.group(2),
            "eta": match.group(3)
        }
    return None
```

---

## 📊 Estimated Effort

| Phase | Files Changed | New Files | Est. Lines Changed | Priority |
|-------|--------------|-----------|-------------------|----------|
| Phase 0 | ~10 | 0 | ~500 deleted, ~200 modified | ★★★★★ |
| Phase 1 | 2-3 | 0 | ~600 rewritten | ★★★★★ |
| Phase 2 | 1-2 | 1-2 | ~800 new | ★★★★★ |
| Phase 3 | 3-4 | 2-3 | ~1,200 rewritten | ★★★★☆ |
| Phase 4 | 1-2 | 0 | ~1,500 rewritten | ★★★★☆ |
| Phase 5 | 3-5 | 2-3 | ~600 new | ★★★☆☆ |
| Phase 6 | ~15 | 0 | ~300 modified | ★★★★☆ |

**Total estimated:** ~5,000+ lines of changes across ~25 files.

---

**Let's build something beautiful.** 🎨
