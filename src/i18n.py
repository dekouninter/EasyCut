# -*- coding: utf-8 -*-
"""
Internationalization (i18n) System for EasyCut
Professional Application with Full Multi-Language Support
Supports: English (Default), Portuguese

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
License: GPL-3.0

This module provides complete translation management for the EasyCut application,
enabling seamless language switching between English and Portuguese with 230+ strings.
All translations are organized by functional category for easy maintenance.
"""

TRANSLATIONS = {
    "en": {
        # Application Titles and Headers
        "app_title": "EasyCut",
        "version": "1.2.1",
        
        # Menu and Shortcuts
        "menu_file": "File",
        "menu_edit": "Edit",
        "menu_view": "View",
        "menu_help": "Help",
        "menu_open_folder": "Open Output Folder",
        "menu_settings": "Settings",
        "menu_refresh": "Refresh",
        "menu_language": "Language",
        "menu_theme": "Theme",
        "menu_theme_light": "Light",
        "menu_theme_dark": "Dark",
        "menu_donations": "Donations",
        "menu_about": "About",
        "menu_exit": "Exit",

        # Language Names
        "lang_en": "English",
        "lang_pt": "Portuguese",
        
        # Application Tabs
        "tab_login": "Login",
        "tab_download": "Download",
        "tab_batch": "Batch",
        "tab_live": "Live",
        "tab_history": "History",
        "tab_about": "About",

        # Header Actions
        "header_theme": "Theme",
        "header_login": "YouTube Login",
        "header_open_folder": "Open Folder",
        "header_select_folder": "Select Folder",
        
        # Browser Cookies
        "browser_cookies_title": "Browser Authentication",
        "browser_cookies_info": "EasyCut can use cookies from your browser or a cookies file.\n\nOption 1: Browser (requires closing browser)\nOption 2: Cookies file (works with browser open)",
        "browser_select_label": "Select Browser:",
        "browser_chrome": "Chrome",
        "browser_firefox": "Firefox",
        "browser_edge": "Edge",
        "browser_opera": "Opera",
        "browser_brave": "Brave",
        "browser_safari": "Safari",
        "browser_none": "None (No Authentication)",
        "browser_profile_label": "Profile (optional):",
        "browser_profile_placeholder": "Default, Profile 1, etc.",
        "browser_profile_auto_label": "YouTube Account:",
        "browser_profile_detecting": "Detecting accounts...",
        "browser_profile_refresh": "Refresh",
        "browser_profile_none_found": "No accounts found",
        "browser_profile_select": "Select account...",
        "browser_test_button": "Test Connection",
        "browser_test_checking": "Testing connection...",
        "browser_test_success": "✓ Connected to YouTube",
        "browser_test_success_as": "✓ Logged in as:",
        "browser_test_failed": "✗ Connection failed",
        "browser_test_no_auth": "⚠ Not authenticated",
        "browser_test_browser_open": "⚠️ Browser is open! Close it first.",
        "browser_cookies_file": "Cookies File (works with browser open)",
        "browser_cookies_file_label": "Cookies File:",
        "browser_cookies_file_button": "Select File",
        "browser_cookies_file_none": "No file selected",
        "browser_cookies_file_selected": "File: {}",
        "browser_cookies_export_help": "How to export cookies:",
        "browser_cookies_export_step1": "1. Install browser extension 'Get cookies.txt LOCALLY'",
        "browser_cookies_export_step2": "2. Go to youtube.com and click the extension",
        "browser_cookies_export_step3": "3. Click 'Export' and save the cookies.txt file",
        "browser_cookies_export_step4": "4. Select the saved file here",
        "browser_account_status": "Account Status:",
        "browser_account_none": "No account detected",
        
        # Login Tab
        "login_tab_title": "Authentication",
        "login_tab_info": "Use popup login for secure authentication\nCredentials are stored securely using OAuth tokens",
        "login_popup_btn": "Login (Popup)",
        "login_logout_btn": "Logout",
        "folder_selected": "Output folder changed to:",

        # Login Banner
        "login_banner_title": "Not connected to YouTube",
        "login_banner_note": "Login is only used by yt-dlp. Credentials are not stored.",
        "login_banner_button": "YouTube Login",
        
        # Status Messages
        "status_logged_in": "Logged in as",
        "status_not_logged_in": "Not logged in",
        "status_ready": "Ready",
        "status_downloading": "Downloading...",
        "status_processing": "Processing...",
        "status_completed": "Completed",
        "status_error": "Error",
        
        # User Authentication
        "login_title": "User Authentication",
        "login_email": "Email/Username",
        "login_password": "Password",
        "login_btn": "Login",
        "login_logout": "Logout",
        "login_popup": "Login (Popup)",
        "login_success": "Successfully logged in!",
        "login_error": "Login failed. Check your credentials.",
        "login_validation_error": "Invalid email or empty fields.",
        "login_logout_success": "Logged out successfully.",
        "login_status": "Login Status",
        "login_remember": "Remember credentials",
        
        # Download
        "download_url": "YouTube URL",
        "download_verify": "Verify",
        "download_title": "Video Title",
        "download_duration": "Duration",
        "download_is_live": "Is Live",
        "download_info": "Video Information",
        "download_mode": "Download Mode",
        "download_mode_full": "Complete Video",
        "download_mode_range": "Time Range",
        "download_mode_until": "Until Time",
        "download_mode_audio": "Audio Only",
        "download_mode_playlist": "Full Playlist",
        "download_mode_channel": "Channel Videos",
        "download_start_time": "Start Time (MM:SS)",
        "download_end_time": "End Time (MM:SS)",
        "download_until_time": "Until Time (MM:SS)",
        "download_quality": "Quality/Format",
        "audio_format": "Audio Format",
        "audio_bitrate": "Bitrate",
        "download_quality_best": "Best Quality",
        "download_subtitle": "Download videos and audio from YouTube",
        "download_quality_mp4": "MP4 (Best)",
        "download_quality_audio": "Audio Only",
        "download_btn": "Download",
        "download_stop": "Stop",
        "download_clear_log": "Clear Log",
        "download_log": "Download Log",
        "download_progress": "Downloading...",
        "download_success": "Download completed successfully!",
        "download_error": "Download failed.",
        "download_validation_error": "Invalid URL or format.",
        "download_invalid_url": "Please enter a valid YouTube URL",
        "download_invalid_time": "Invalid time format. Use MM:SS",
        "download_range_error": "End time must be greater than start time",
        "download_time_help": "Use start/end for range. Use only end for until mode.",
        "download_time_invalid": "Invalid time format. Use HH:MM:SS or MM:SS.",
        "download_time_order": "End time must be greater than start time.",
        "download_time_range": "Time Range",
        
        # Batch Download Operations
        "batch_urls": "URLs (one per line)",
        "batch_download_all": "Download All",
        "batch_paste": "Paste",
        "batch_clear": "Clear",
        "batch_progress": "Downloading batch",
        "batch_success": "Batch download completed!",
        "batch_error": "Batch download had some errors.",
        "batch_empty": "Please add at least one URL",
        "batch_log": "Batch Log",
        "batch_subtitle": "Download multiple videos at once",
        "batch_help": "Paste one URL per line. Up to 50 URLs supported.",
        "batch_stop": "Stop All",
        "live_title": "Live Stream Recorder",
        "live_url": "Live Stream URL",
        "live_check_stream": "Check Stream",
        "live_status": "Stream Status",
        "live_status_live": "🔴 LIVE NOW",
        "live_status_offline": "⏱️ OFFLINE",
        "live_status_unknown": "🔴 UNKNOWN",
        "live_status_error": "❌ ERROR",
        "live_duration": "Stream Duration",
        "live_mode": "Recording Mode",
        "live_mode_continuous": "Continuous Recording",
        "live_mode_until": "Record Until Time",
        "live_mode_duration": "Record Duration",
        "live_quality": "Quality",
        "live_quality_best": "Best Available",
        "live_quality_1080": "1080p",
        "live_quality_720": "720p",
        "live_quality_480": "480p",
        "live_log": "Recording Log",
        "live_start_recording": "Start Recording",
        "live_stop_recording": "Stop Recording",
        "live_recording_started": "Live stream recording started...",
        "live_recording_stopped": "Recording stopped by user",
        "live_recording_completed": "Recording completed successfully!",
        "live_recording_error": "Recording error occurred",
        "live_hours": "Hours",
        "live_minutes": "Minutes",
        "live_seconds": "Seconds",
        "live_subtitle": "Record live streams with customizable duration and quality",
        "live_duration_settings": "Duration Settings",

        
        # Download History
        "history_title": "Download History",
        "history_search": "Search",
        "history_update": "Update",
        "history_clear": "Clear History",
        "history_date": "Date",
        "history_filename": "Filename",
        "history_status": "Status",
        "history_url": "URL",
        "history_empty": "No downloads yet",
        "history_no_results": "No downloads match your search",
        "history_subtitle": "Track all your downloads in one place",
        "history_records": "Download Records",
        
        # About Application
        "about_tab_about": "About",
        "about_tab_credits": "Credits",
        "about_tab_features": "Features",
        "about_subtitle": "Professional YouTube Downloader & Audio Converter",
        "about_section_legal": "Legal Notice - Personal Use Only",
        "about_legal_disclaimer": (
            "FOR PERSONAL USE ONLY\n\n"
            "EasyCut is intended for downloading:\n"
            "\u2022 Your own videos uploaded to YouTube\n"
            "\u2022 Content with explicit creator permission\n"
            "\u2022 Content allowed under fair use in your jurisdiction\n\n"
            "YOU ARE RESPONSIBLE FOR:\n"
            "\u2022 Complying with YouTube's Terms of Service\n"
            "\u2022 Respecting copyright laws\n"
            "\u2022 Obtaining necessary permissions\n\n"
            "Developers are NOT responsible for copyright violations or misuse."
        ),
        "about_section_info": "Application Info",
        "about_section_links": "Connect & Support",
        "about_section_features": "Features",
        "about_section_tech": "Technologies & Credits",
        "about_section_thanks": "Special Thanks",
        "about_footer": "Made with Python | GPL-3.0 License | © 2026 Deko Costa",
        "about_link_github": "GitHub Repository",
        "about_link_coffee": "Buy Me a Coffee",
        "about_link_livepix": "Livepix Donate",
        "about_link_kofi": "Support on Ko-fi",
        "about_title": "EasyCut",
        "about_description": "EasyCut is a simple and secure YouTube video downloader with support for batch downloads and audio extraction.",
        "about_author": "Author: Deko Costa",
        "about_version_info": "Version 1.2.1 - Professional Edition",
        "about_github": "GitHub: https://github.com/dekouninter/EasyCut",
        "about_support": "Support: buymeacoffee.com/dekocosta | livepix.gg/dekocosta",
        "about_license": "License: GPL-3.0",
        "about_credits_libs": "Libraries: yt-dlp, FFmpeg, Google OAuth",        "about_credits_tools": "Tools: Python, Tkinter",
        "about_tech_text": "Core: Python, Tkinter, yt-dlp, FFmpeg, OAuth",
        "about_thanks_text": "Thanks to the open-source community and creators.",
        "about_features_list": [
            "Single and batch video downloads",
            "Secure authentication with OAuth",
            "Time range extraction",
            "Audio conversion (MP3, WAV, M4A, OPUS)",
            "Real-time logging",
            "Dark/Light theme",
            "Multi-language support (EN, PT)",
            "Download history",
        ],
        
        # Donation and Support
        "donation_title": "Support EasyCut Development",
        "donation_description": "If you enjoy EasyCut, please consider supporting the project!",
        "donation_coffee": "Buy Me a Coffee",
        "donation_livepix": "Livepix",
        "donation_open": "Open Link",
        
        # General User Messages
        "msg_warning": "Warning",
        "msg_error": "Error",
        "msg_success": "Success",
        "msg_info": "Information",
        "msg_confirm": "Confirm",
        "msg_download_active": "Downloads are in progress. Close anyway?",
        "msg_yes": "Yes",
        "msg_no": "No",
        "msg_ok": "OK",
        "msg_cancel": "Cancel",
        "msg_close": "Close",
        "msg_save": "Save",
        "msg_loading": "Loading...",
        "msg_clipboard": "Copied to clipboard",
        
        # Application Logging Messages
        "log_starting": "Starting application...",
        "log_startup_complete": "Application startup completed successfully",
        "log_checking_ffmpeg": "Checking FFmpeg installation...",
        "log_ffmpeg_found": "FFmpeg found.",
        "log_ffmpeg_not_found": "FFmpeg not found. Audio conversion may not work.",
        "log_downloading": "Downloading video from",
        "log_verifying_url": "Verifying URL...",
        "log_video_info": "Video info retrieved successfully",
        
        # Format Selection
        "format_title": "Available Formats",
        "format_select": "Select Format",
        "format_auto": "Auto (Best)",
        "format_video_audio": "Video + Audio",
        "format_video_only": "Video Only",
        "format_audio_only": "Audio Only",
        "format_resolution": "Resolution",
        "format_codec": "Codec",
        "format_fps": "FPS",
        "format_size": "Size",
        "format_bitrate": "Bitrate",
        "format_ext": "Extension",
        "format_note": "Note",
        "format_fallback": "Selected format unavailable, falling back to: {}",
        "format_fetching": "Fetching available formats...",
        "format_none": "No formats available",
        "format_count": "{} formats available",
        
        # Metadata Display
        "meta_uploader": "Uploader",
        "meta_views": "Views",
        "meta_upload_date": "Upload Date",
        "meta_description": "Description",
        "meta_fetching": "Fetching video info...",
        "meta_thumbnail": "Thumbnail",
        
        # Error Messages (user-friendly)
        "err_private": "This video is private. Sign in with OAuth to access it.",
        "err_age_restricted": "Age-restricted video. Sign in with OAuth to access it.",
        "err_unavailable": "This video is unavailable or has been removed.",
        "err_geo_blocked": "This video is not available in your country.",
        "err_live_not_started": "This live stream has not started yet.",
        "err_rate_limited": "Too many requests. Please wait a moment and try again.",
        "err_network": "Network error. Check your internet connection.",
        "err_no_formats": "No downloadable formats found for this video.",
        "err_ffmpeg_post": "Post-processing failed. Ensure FFmpeg is installed correctly.",
        "err_copyright": "This video cannot be downloaded due to copyright restrictions.",
        "err_members_only": "This video is for channel members only.",
        "err_premium_only": "This content requires YouTube Premium.",
        "err_unknown": "An unexpected error occurred. Check the logs for details.",
        
        # Channel Downloads
        "channel_limit": "Latest videos",
        "channel_limit_help": "Number of latest videos to download (1-500)",
        
        # Playlist Info
        "playlist_info": "Playlist: {} videos",
        "playlist_duration": "Total duration: {}",
        "playlist_uploader": "By: {}",
        
        # Duplicate Detection
        "dup_title": "Duplicate Detection",
        "dup_found": "This video was already downloaded:",
        "dup_skip": "Skip",
        "dup_overwrite": "Download Again",
        "dup_ask": "Video already downloaded. Download again?",
        "dup_skipped": "Skipped (already downloaded)",
        "dup_batch_skipped": "{} duplicates skipped",
        
        # Subtitles
        "sub_title": "Subtitles",
        "sub_enable": "Download Subtitles",
        "sub_auto": "Auto-generated",
        "sub_manual": "Manual (creator)",
        "sub_both": "Both",
        "sub_language": "Subtitle Language",
        "sub_format": "Subtitle Format",
        "sub_embed": "Embed in video",
        "sub_help": "Language code (e.g., en, pt, es). Comma-separated for multiple.",
        "sub_found": "Subtitles found: {}",
        "sub_none": "No subtitles available",
        
        # Settings
        "tab_settings": "Settings",
        "settings_subtitle": "Configure application preferences",
        "settings_network": "Network",
        "settings_proxy": "Proxy URL",
        "settings_proxy_help": "HTTP/SOCKS proxy (e.g., socks5://127.0.0.1:1080)",
        "settings_rate_limit": "Speed Limit",
        "settings_rate_limit_help": "Max download speed (e.g., 5M, 500K). Empty = unlimited.",
        "settings_retries": "Max Retries",
        "settings_retries_help": "Number of retry attempts for failed downloads (1-10)",
        "settings_cookies": "Cookie File",
        "settings_cookies_help": "Path to cookies.txt file (Netscape format)",
        "settings_cookies_browse": "Browse...",
        "settings_save": "Save Settings",
        "settings_saved": "Settings saved successfully!",
        "settings_download": "Download Defaults",
        "settings_archive": "Archive & Tracking",
        
        # Archive Mode
        "archive_enable": "Enable Archive Mode",
        "archive_help": "Track downloaded videos and skip duplicates automatically",
        "archive_file": "Archive File",
        "archive_count": "{} videos archived",
        "archive_skipped": "Skipped (already archived): {}",
        "archive_export": "Export Archive",
        "archive_import": "Import Archive",
        "archive_clear": "Clear Archive",
        "archive_cleared": "Archive cleared ({} entries removed)",
        
        # Quality Profiles
        "profile_title": "Quality Profiles",
        "profile_save": "Save Current as Profile",
        "profile_load": "Load Profile",
        "profile_delete": "Delete Profile",
        "profile_name": "Profile Name",
        "profile_saved": "Profile '{}' saved",
        "profile_loaded": "Profile '{}' loaded",
        "profile_deleted": "Profile '{}' deleted",
        "profile_none": "No profiles saved",
    },
    
    "pt": {
        # Títulos e cabeçalhos
        "app_title": "EasyCut",
        "version": "1.2.1",
        
        # Menu e atalhos
        "menu_file": "Arquivo",
        "menu_edit": "Editar",
        "menu_view": "Visualizar",
        "menu_help": "Ajuda",
        "menu_open_folder": "Abrir Pasta de Saída",
        "menu_settings": "Configurações",
        "menu_refresh": "Atualizar",
        "menu_language": "Idioma",
        "menu_theme": "Tema",
        "menu_theme_light": "Claro",
        "menu_theme_dark": "Escuro",
        "menu_donations": "Doações",
        "menu_about": "Sobre",
        "menu_exit": "Sair",

        # Idiomas
        "lang_en": "English",
        "lang_pt": "Portugues",
        
        # Abas
        "tab_login": "Entrar",
        "tab_download": "Download",
        "tab_batch": "Lote",
        "tab_live": "Live",
        "tab_history": "Histórico",
        "tab_about": "Sobre",

        # Acoes do cabecalho
        "header_theme": "Tema",
        "header_login": "Login YouTube",
        "header_open_folder": "Abrir pasta",
        "header_select_folder": "Selecionar pasta",
        
        # Browser Cookies
        "browser_cookies_title": "Autenticação por Navegador",
        "browser_cookies_info": "O EasyCut pode usar cookies do navegador ou arquivo de cookies.\n\nOpção 1: Navegador (requer fechar navegador)\nOpção 2: Arquivo de cookies (funciona com navegador aberto)",
        "browser_select_label": "Selecione o Navegador:",
        "browser_chrome": "Chrome",
        "browser_firefox": "Firefox",
        "browser_edge": "Edge",
        "browser_opera": "Opera",
        "browser_brave": "Brave",
        "browser_safari": "Safari",
        "browser_none": "Nenhum (Sem Autenticação)",        "browser_profile_label": "Perfil (opcional):",
        "browser_profile_placeholder": "Default, Profile 1, etc.",
        "browser_profile_auto_label": "Conta do YouTube:",
        "browser_profile_detecting": "Detectando contas...",
        "browser_profile_refresh": "Atualizar",
        "browser_profile_none_found": "Nenhuma conta encontrada",
        "browser_profile_select": "Selecione a conta...",
        "browser_test_button": "Testar Conex\u00e3o",
        "browser_test_checking": "Testando conex\u00e3o...",
        "browser_test_success": "\u2713 Conectado ao YouTube",
        "browser_test_success_as": "\u2713 Logado como:",
        "browser_test_failed": "\u2717 Falha na conex\u00e3o",
        "browser_test_no_auth": "\u26a0 N\u00e3o autenticado",
        "browser_test_browser_open": "\u26a0\ufe0f Navegador est\u00e1 aberto! Feche-o primeiro.",
        "browser_cookies_file": "Arquivo de Cookies (funciona com navegador aberto)",
        "browser_cookies_file_label": "Arquivo de Cookies:",
        "browser_cookies_file_button": "Selecionar Arquivo",
        "browser_cookies_file_none": "Nenhum arquivo selecionado",
        "browser_cookies_file_selected": "Arquivo: {}",
        "browser_cookies_export_help": "Como exportar cookies:",
        "browser_cookies_export_step1": "1. Instale a extens\u00e3o 'Get cookies.txt LOCALLY'",
        "browser_cookies_export_step2": "2. V\u00e1 para youtube.com e clique na extens\u00e3o",
        "browser_cookies_export_step3": "3. Clique em 'Export' e salve o arquivo cookies.txt",
        "browser_cookies_export_step4": "4. Selecione o arquivo salvo aqui",
        "browser_account_status": "Status da Conta:",
        "browser_account_none": "Nenhuma conta detectada",        
        # Aba de Login
        "login_tab_title": "Autenticação",
        "login_tab_info": "Use login popup para autenticação segura\nCredenciais são armazenadas com segurança via OAuth",
        "login_popup_btn": "Entrar (Popup)",
        "login_logout_btn": "Sair",
        "folder_selected": "Pasta de saída alterada para:",

        # Banner de login
        "login_banner_title": "Nao conectado ao YouTube",
        "login_banner_note": "Login usado apenas pelo yt-dlp. Credenciais nao sao armazenadas.",
        "login_banner_button": "Login YouTube",
        
        # Status
        "status_logged_in": "Conectado como",
        "status_not_logged_in": "Não conectado",
        "status_ready": "Pronto",
        "status_downloading": "Baixando...",
        "status_processing": "Processando...",
        "status_completed": "Concluído",
        "status_error": "Erro",
        
        # Login
        "login_title": "Autenticação de Usuário",
        "login_email": "Email/Usuário",
        "login_password": "Senha",
        "login_btn": "Entrar",
        "login_logout": "Sair",
        "login_popup": "Entrar (Popup)",
        "login_success": "Logado com sucesso!",
        "login_error": "Falha no login. Verifique suas credenciais.",
        "login_validation_error": "Email inválido ou campos vazios.",
        "login_logout_success": "Desconectado com sucesso.",
        "login_status": "Status de Login",
        "login_remember": "Lembrar credenciais",
        
        # Download
        "download_url": "URL do YouTube",
        "download_verify": "Verificar",
        "download_title": "Título do Vídeo",
        "download_duration": "Duração",
        "download_is_live": "É Live",
        "download_info": "Informacoes do video",
        "download_mode": "Modo de Download",
        "download_mode_full": "Vídeo Completo",
        "download_mode_range": "Intervalo de Tempo",
        "download_mode_until": "Até um Tempo",
        "download_mode_audio": "Apenas audio",
        "download_mode_playlist": "Playlist Completa",
        "download_mode_channel": "Vídeos do Canal",
        "download_start_time": "Tempo de Início (MM:SS)",
        "download_end_time": "Tempo Final (MM:SS)",
        "download_until_time": "Até o Tempo (MM:SS)",
        "download_quality": "Qualidade/Formato",
        "audio_format": "Formato de Áudio",
        "audio_bitrate": "Taxa de Bits",
        "download_quality_best": "Melhor Qualidade",
        "download_subtitle": "Baixe vídeos e áudio do YouTube",
        "download_quality_mp4": "MP4 (Melhor)",
        "download_quality_audio": "Somente Áudio",
        "download_btn": "Baixar",
        "download_stop": "Parar",
        "download_clear_log": "Limpar Log",
        "download_log": "Log do download",
        "download_progress": "Baixando...",
        "download_success": "Download concluído com sucesso!",
        "download_error": "Falha no download.",
        "download_validation_error": "URL ou formato inválido.",
        "download_invalid_url": "Digite uma URL válida do YouTube",
        "download_invalid_time": "Formato de tempo inválido. Use MM:SS",
        "download_range_error": "Tempo final deve ser maior que tempo inicial",
        "download_time_help": "Use inicio/fim para intervalo. Use apenas fim para modo ate o tempo.",
        "download_time_invalid": "Formato de tempo invalido. Use HH:MM:SS ou MM:SS.",
        "download_time_order": "O tempo final deve ser maior que o tempo inicial.",
        "download_time_range": "Intervalo de Tempo",
        
        # Lote (Batch)
        "batch_urls": "URLs (uma por linha)",
        "batch_download_all": "Baixar Tudo",
        "batch_paste": "Colar",
        "batch_clear": "Limpar",
        "batch_progress": "Baixando lote",
        "batch_success": "Download em lote concluído!",
        "batch_error": "Download em lote teve alguns erros.",
        "batch_empty": "Adicione pelo menos uma URL",
        "batch_log": "Log do lote",
        "batch_subtitle": "Baixe múltiplos vídeos de uma vez",
        "batch_help": "Cole uma URL por linha. Até 50 URLs suportadas.",
        "batch_stop": "Parar Tudo",
        
        # Transmissão Ao Vivo
        "live_title": "Gravador de Transmissão Ao Vivo",
        "live_url": "URL da Transmissão Ao Vivo",
        "live_check_stream": "Verificar Transmissão",
        "live_status": "Status da Transmissão",
        "live_status_live": "🔴 AO VIVO AGORA",
        "live_status_offline": "⏱️ OFFLINE",
        "live_status_unknown": "🔴 DESCONHECIDO",
        "live_status_error": "❌ ERRO",
        "live_duration": "Duração da Transmissão",
        "live_mode": "Modo de Gravação",
        "live_mode_continuous": "Gravação Contínua",
        "live_mode_until": "Gravar Até um Tempo",
        "live_mode_duration": "Duração da Gravação",
        "live_quality": "Qualidade",
        "live_quality_best": "Melhor Disponível",
        "live_quality_1080": "1080p",
        "live_quality_720": "720p",
        "live_quality_480": "480p",
        "live_log": "Log da gravacao",
        "live_start_recording": "Iniciar Gravação",
        "live_stop_recording": "Parar Gravação",
        "live_recording_started": "Gravação de transmissão ao vivo iniciada...",
        "live_recording_stopped": "Gravação interrompida pelo usuário",
        "live_recording_completed": "Gravação concluída com sucesso!",
        "live_recording_error": "Erro ao gravar",
        "live_hours": "Horas",
        "live_minutes": "Minutos",
        "live_seconds": "Segundos",
        "live_subtitle": "Grave transmissões ao vivo com duração e qualidade personalizáveis",
        "live_duration_settings": "Configurações de Duração",

        
        # Histórico
        "history_title": "Histórico de Downloads",
        "history_search": "Buscar",
        "history_update": "Atualizar",
        "history_clear": "Limpar Histórico",
        "history_date": "Data",
        "history_filename": "Nome do Arquivo",
        "history_status": "Status",
        "history_url": "URL",
        "history_empty": "Nenhum download ainda",
        "history_no_results": "Nenhum download encontrado",
        "history_subtitle": "Acompanhe todos os seus downloads em um só lugar",
        "history_records": "Registros de Download",
        
        # Sobre
        "about_tab_about": "Sobre",
        "about_tab_credits": "Créditos",
        "about_tab_features": "Recursos",
        "about_subtitle": "Downloader profissional do YouTube e conversor de audio",
        "about_section_legal": "Aviso Legal - Apenas Uso Pessoal",
        "about_legal_disclaimer": (
            "APENAS PARA USO PESSOAL\n\n"
            "EasyCut é destinado para baixar:\n"
            "\u2022 Seus próprios vídeos enviados ao YouTube\n"
            "\u2022 Conteúdo com permissão explícita do criador\n"
            "\u2022 Conteúdo permitido por uso justo (fair use) em sua jurisdição\n\n"
            "VOCÊ É RESPONSÁVEL POR:\n"
            "\u2022 Cumprir os Termos de Serviço do YouTube\n"
            "\u2022 Respeitar as leis de direitos autorais\n"
            "\u2022 Obter permissões necessárias\n\n"
            "Desenvolvedores NÃO são responsáveis por violações de direitos autorais ou uso indevido."
        ),
        "about_section_info": "Informacoes do aplicativo",
        "about_section_links": "Conectar e apoiar",
        "about_section_features": "Recursos",
        "about_section_tech": "Tecnologias e creditos",
        "about_section_thanks": "Agradecimentos",
        "about_footer": "Feito com Python | Licenca GPL-3.0 | © 2026 Deko Costa",
        "about_link_github": "Repositorio GitHub",
        "about_link_coffee": "Buy Me a Coffee",
        "about_link_livepix": "Doar via Livepix",
        "about_link_kofi": "Apoiar no Ko-fi",
        "about_title": "EasyCut",
        "about_description": "EasyCut é um simples e seguro baixador de vídeos YouTube com suporte a downloads em lote e extração de áudio.",
        "about_author": "Autor: Deko Costa",
        "about_version_info": "Versão 1.2.1 - Edição Profissional",
        "about_github": "GitHub: https://github.com/dekouninter/EasyCut",
        "about_license": "Licença: GPL-3.0",
        "about_support": "Apoie: buymeacoffee.com/dekocosta | livepix.gg/dekocosta",
        "about_credits_libs": "Bibliotecas: yt-dlp, FFmpeg, Google OAuth",
        "about_credits_tools": "Ferramentas: Python, Tkinter",
        "about_tech_text": "Base: Python, Tkinter, yt-dlp, FFmpeg, OAuth",
        "about_thanks_text": "Obrigado a comunidade open-source e criadores.",
        "about_features_list": [
            "Download de vídeos único e em lote",
            "Autenticação segura com OAuth",
            "Extração de intervalo de tempo",
            "Conversão de áudio (MP3, WAV, M4A, OPUS)",
            "Logs em tempo real",
            "Tema escuro/claro",
            "Suporte multi-idioma (EN, PT)",
            "Histórico de downloads",
        ],
        
        # Doações
        "donation_title": "Apoie o EasyCut",
        "donation_description": "Se você gosta do EasyCut, considere apoiar o projeto!",
        "donation_coffee": "Compre um Café",
        "donation_livepix": "Livepix",
        "donation_open": "Abrir Link",
        
        # Mensagens gerais
        "msg_warning": "Aviso",
        "msg_error": "Erro",
        "msg_success": "Sucesso",
        "msg_info": "Informação",
        "msg_confirm": "Confirmar",
        "msg_download_active": "Downloads em andamento. Fechar mesmo assim?",
        "msg_yes": "Sim",
        "msg_no": "Não",
        "msg_ok": "OK",
        "msg_cancel": "Cancelar",
        "msg_close": "Fechar",
        "msg_save": "Salvar",
        "msg_loading": "Carregando...",
        "msg_clipboard": "Copiado para a área de transferência",
        
        # Logs
        "log_starting": "Iniciando aplicativo...",
        "log_startup_complete": "Inicialização do aplicativo concluída com sucesso",
        "log_checking_ffmpeg": "Verificando instalação do FFmpeg...",
        "log_ffmpeg_found": "FFmpeg encontrado.",
        "log_ffmpeg_not_found": "FFmpeg não encontrado. Conversão de áudio pode não funcionar.",
        "log_downloading": "Baixando vídeo de",
        "log_verifying_url": "Verificando URL...",
        "log_video_info": "Informações do vídeo obtidas com sucesso",
        
        # Seleção de Formato
        "format_title": "Formatos Disponíveis",
        "format_select": "Selecionar Formato",
        "format_auto": "Automático (Melhor)",
        "format_video_audio": "Vídeo + Áudio",
        "format_video_only": "Apenas Vídeo",
        "format_audio_only": "Apenas Áudio",
        "format_resolution": "Resolução",
        "format_codec": "Codec",
        "format_fps": "FPS",
        "format_size": "Tamanho",
        "format_bitrate": "Taxa de Bits",
        "format_ext": "Extensão",
        "format_note": "Nota",
        "format_fallback": "Formato selecionado indisponível, usando: {}",
        "format_fetching": "Buscando formatos disponíveis...",
        "format_none": "Nenhum formato disponível",
        "format_count": "{} formatos disponíveis",
        
        # Exibição de Metadados
        "meta_uploader": "Autor",
        "meta_views": "Visualizações",
        "meta_upload_date": "Data de Publicação",
        "meta_description": "Descrição",
        "meta_fetching": "Buscando informações do vídeo...",
        "meta_thumbnail": "Miniatura",
        
        # Mensagens de Erro (amigáveis)
        "err_private": "Este vídeo é privado. Faça login com OAuth para acessá-lo.",
        "err_age_restricted": "Vídeo com restrição de idade. Faça login com OAuth para acessá-lo.",
        "err_unavailable": "Este vídeo não está disponível ou foi removido.",
        "err_geo_blocked": "Este vídeo não está disponível no seu país.",
        "err_live_not_started": "Esta transmissão ao vivo ainda não começou.",
        "err_rate_limited": "Muitas solicitações. Aguarde um momento e tente novamente.",
        "err_network": "Erro de rede. Verifique sua conexão com a internet.",
        "err_no_formats": "Nenhum formato disponível para download neste vídeo.",
        "err_ffmpeg_post": "Falha no pós-processamento. Verifique se o FFmpeg está instalado.",
        "err_copyright": "Este vídeo não pode ser baixado por restrições de direitos autorais.",
        "err_members_only": "Este vídeo é exclusivo para membros do canal.",
        "err_premium_only": "Este conteúdo requer YouTube Premium.",
        "err_unknown": "Ocorreu um erro inesperado. Verifique os logs para detalhes.",
        
        # Downloads de Canal
        "channel_limit": "Últimos vídeos",
        "channel_limit_help": "Número de últimos vídeos para baixar (1-500)",
        
        # Informações de Playlist
        "playlist_info": "Playlist: {} vídeos",
        "playlist_duration": "Duração total: {}",
        "playlist_uploader": "Por: {}",
        
        # Detecção de Duplicatas
        "dup_title": "Detecção de Duplicatas",
        "dup_found": "Este vídeo já foi baixado:",
        "dup_skip": "Pular",
        "dup_overwrite": "Baixar Novamente",
        "dup_ask": "Vídeo já baixado. Baixar novamente?",
        "dup_skipped": "Pulado (já baixado)",
        "dup_batch_skipped": "{} duplicatas puladas",
        
        # Legendas
        "sub_title": "Legendas",
        "sub_enable": "Baixar Legendas",
        "sub_auto": "Geradas automaticamente",
        "sub_manual": "Manuais (criador)",
        "sub_both": "Ambas",
        "sub_language": "Idioma da Legenda",
        "sub_format": "Formato da Legenda",
        "sub_embed": "Incorporar no vídeo",
        "sub_help": "Código do idioma (ex: en, pt, es). Separados por vírgula.",
        "sub_found": "Legendas encontradas: {}",
        "sub_none": "Nenhuma legenda disponível",
        
        # Configurações
        "tab_settings": "Configurações",
        "settings_subtitle": "Configurar preferências do aplicativo",
        "settings_network": "Rede",
        "settings_proxy": "URL do Proxy",
        "settings_proxy_help": "Proxy HTTP/SOCKS (ex: socks5://127.0.0.1:1080)",
        "settings_rate_limit": "Limite de Velocidade",
        "settings_rate_limit_help": "Velocidade máxima (ex: 5M, 500K). Vazio = ilimitado.",
        "settings_retries": "Máx. Tentativas",
        "settings_retries_help": "Número de tentativas para downloads falhos (1-10)",
        "settings_cookies": "Arquivo de Cookies",
        "settings_cookies_help": "Caminho para cookies.txt (formato Netscape)",
        "settings_cookies_browse": "Procurar...",
        "settings_save": "Salvar Configurações",
        "settings_saved": "Configurações salvas com sucesso!",
        "settings_download": "Padrões de Download",
        "settings_archive": "Arquivo & Rastreamento",
        
        # Modo Arquivo
        "archive_enable": "Ativar Modo Arquivo",
        "archive_help": "Rastrear vídeos baixados e pular duplicatas automaticamente",
        "archive_file": "Arquivo de Rastreamento",
        "archive_count": "{} vídeos arquivados",
        "archive_skipped": "Pulado (já arquivado): {}",
        "archive_export": "Exportar Arquivo",
        "archive_import": "Importar Arquivo",
        "archive_clear": "Limpar Arquivo",
        "archive_cleared": "Arquivo limpado ({} entradas removidas)",
        
        # Perfis de Qualidade
        "profile_title": "Perfis de Qualidade",
        "profile_save": "Salvar Atual como Perfil",
        "profile_load": "Carregar Perfil",
        "profile_delete": "Excluir Perfil",
        "profile_name": "Nome do Perfil",
        "profile_saved": "Perfil '{}' salvo",
        "profile_loaded": "Perfil '{}' carregado",
        "profile_deleted": "Perfil '{}' excluído",
        "profile_none": "Nenhum perfil salvo",
    }
}


class Translator:
    """Translation Manager for Multi-Language Support
    
    Handles dynamic language switching for the entire application
    with support for English and Portuguese translations.
    Provides hot-reload capability for seamless language changes.
    """
    
    def __init__(self, language="en"):
        self.language = language if language in TRANSLATIONS else "en"
        self.translations = TRANSLATIONS[self.language]
    
    def set_language(self, language):
        """Change active language for all UI elements
        
        Enables hot-reload language switching without restart.
        Supported languages: 'en' (English), 'pt' (Portuguese)
        
        Args:
            language (str): Language code ('en' or 'pt')
            
        Returns:
            bool: True if language was changed, False if language not found
        """
        if language in TRANSLATIONS:
            self.language = language
            self.translations = TRANSLATIONS[self.language]
            return True
        return False
    
    def get(self, key, default=""):
        """Retrieve translation string by key
        
        Args:
            key (str): Translation dictionary key
            default (str): Default value if key not found
            
        Returns:
            str: Translated string or default value
        """
        return self.translations.get(key, default)
    
    def __call__(self, key, default=""):
        """Allow using translator instance as callable function
        
        Enables convenient syntax: t("key") instead of t.get("key")
        
        Args:
            key (str): Translation key
            default (str): Default value if key not found
            
        Returns:
            str: Translated string
        """
        return self.get(key, default)


# Global Translator Instance
# Default language: English (can be changed via UI with instant hot-reload)
translator = Translator("en")
