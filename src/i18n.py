# -*- coding: utf-8 -*-
"""
Internationalization (i18n) System for EasyCut
Professional Application with Full Multi-Language Support
Supports: English (Default), Portuguese

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
License: MIT

This module provides complete translation management for the EasyCut application,
enabling seamless language switching between English and Portuguese with 150+ strings.
All translations are organized by functional category for easy maintenance.
"""

TRANSLATIONS = {
    "en": {
        # Application Titles and Headers
        "app_title": "EasyCut - YouTube Video Downloader",
        "version": "1.0.0",
        
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
        "tab_live": "Live Stream",
        "tab_audio": "Audio",
        "tab_history": "History",
        "tab_about": "About",

        # Header Actions
        "header_theme": "Theme",
        "header_login": "YouTube Login",
        "header_open_folder": "Open Folder",

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
        "download_start_time": "Start Time (MM:SS)",
        "download_end_time": "End Time (MM:SS)",
        "download_until_time": "Until Time (MM:SS)",
        "download_quality": "Quality/Format",
        "download_quality_best": "Best Quality",
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
        
        # Live Stream Recording
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
        
        # Audio Conversion
        "audio_url": "YouTube URL",
        "audio_format": "Audio Format",
        "audio_format_mp3": "MP3",
        "audio_format_wav": "WAV",
        "audio_format_m4a": "M4A",
        "audio_format_opus": "OPUS",
        "audio_bitrate": "Bitrate",
        "audio_bitrate_128": "128 kbps",
        "audio_bitrate_192": "192 kbps",
        "audio_bitrate_256": "256 kbps",
        "audio_bitrate_320": "320 kbps",
        "audio_convert": "Convert",
        "audio_success": "Audio conversion completed!",
        "audio_error": "Audio conversion failed.",
        
        # Download History
        "history_title": "Download History",
        "history_update": "Update",
        "history_clear": "Clear History",
        "history_date": "Date",
        "history_filename": "Filename",
        "history_status": "Status",
        "history_url": "URL",
        "history_empty": "No downloads yet",
        
        # About Application
        "about_tab_about": "About",
        "about_tab_credits": "Credits",
        "about_tab_features": "Features",
        "about_subtitle": "Professional YouTube Downloader & Audio Converter",
        "about_section_info": "Application Info",
        "about_section_links": "Connect & Support",
        "about_section_features": "Features",
        "about_section_tech": "Technologies & Credits",
        "about_section_thanks": "Special Thanks",
        "about_footer": "Made with Python | MIT License | © 2026 Deko Costa",
        "about_link_github": "GitHub Repository",
        "about_link_coffee": "Buy Me a Coffee",
        "about_link_livepix": "Livepix Donate",
        "about_description": "EasyCut is a simple and secure YouTube video downloader with support for batch downloads and audio extraction.",
        "about_author": "Author: Deko Costa",
        "about_version_info": "Version 1.0.0 - Professional Edition",
        "about_github": "GitHub: https://github.com/dekouninter/EasyCut",
        "about_support": "Support: buymeacoffee.com/dekocosta | livepix.gg/dekocosta",
        "about_license": "License: MIT",
        "about_credits_libs": "Libraries: yt-dlp, FFmpeg, keyring",
        "about_credits_tools": "Tools: Python, Tkinter",
        "about_tech_text": "Core: Python, Tkinter, yt-dlp, FFmpeg, keyring",
        "about_thanks_text": "Thanks to the open-source community and creators.",
        "about_features_list": [
            "Single and batch video downloads",
            "Secure credential storage with keyring",
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
    },
    
    "pt": {
        # Títulos e cabeçalhos
        "app_title": "EasyCut - Baixador de Vídeos YouTube",
        "version": "1.0.0",
        
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
        "tab_live": "Transmissão Ao Vivo",
        "tab_audio": "Áudio",
        "tab_history": "Histórico",
        "tab_about": "Sobre",

        # Acoes do cabecalho
        "header_theme": "Tema",
        "header_login": "Login YouTube",
        "header_open_folder": "Abrir pasta",

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
        "download_start_time": "Tempo de Início (MM:SS)",
        "download_end_time": "Tempo Final (MM:SS)",
        "download_until_time": "Até o Tempo (MM:SS)",
        "download_quality": "Qualidade/Formato",
        "download_quality_best": "Melhor Qualidade",
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
        
        # Áudio
        "audio_url": "URL do YouTube",
        "audio_format": "Formato de Áudio",
        "audio_format_mp3": "MP3",
        "audio_format_wav": "WAV",
        "audio_format_m4a": "M4A",
        "audio_format_opus": "OPUS",
        "audio_bitrate": "Taxa de Bits",
        "audio_bitrate_128": "128 kbps",
        "audio_bitrate_192": "192 kbps",
        "audio_bitrate_256": "256 kbps",
        "audio_bitrate_320": "320 kbps",
        "audio_convert": "Converter",
        "audio_success": "Conversão de áudio concluída!",
        "audio_error": "Falha na conversão de áudio.",
        
        # Histórico
        "history_title": "Histórico de Downloads",
        "history_update": "Atualizar",
        "history_clear": "Limpar Histórico",
        "history_date": "Data",
        "history_filename": "Nome do Arquivo",
        "history_status": "Status",
        "history_url": "URL",
        "history_empty": "Nenhum download ainda",
        
        # Sobre
        "about_tab_about": "Sobre",
        "about_tab_credits": "Créditos",
        "about_tab_features": "Recursos",
        "about_subtitle": "Downloader profissional do YouTube e conversor de audio",
        "about_section_info": "Informacoes do aplicativo",
        "about_section_links": "Conectar e apoiar",
        "about_section_features": "Recursos",
        "about_section_tech": "Tecnologias e creditos",
        "about_section_thanks": "Agradecimentos",
        "about_footer": "Feito com Python | Licenca MIT | © 2026 Deko Costa",
        "about_link_github": "Repositorio GitHub",
        "about_link_coffee": "Buy Me a Coffee",
        "about_link_livepix": "Doar via Livepix",
        "about_description": "EasyCut é um simples e seguro baixador de vídeos YouTube com suporte a downloads em lote e extração de áudio.",
        "about_author": "Autor: Equipe EasyCut",
        "about_version_info": "Versão 1.0.0",
        "about_github": "GitHub: https://github.com/easycut",
        "about_license": "Licença: MIT",
        "about_credits_libs": "Bibliotecas: yt-dlp, FFmpeg, keyring",
        "about_credits_tools": "Ferramentas: Python, Tkinter",
        "about_tech_text": "Base: Python, Tkinter, yt-dlp, FFmpeg, keyring",
        "about_thanks_text": "Obrigado a comunidade open-source e criadores.",
        "about_features_list": [
            "Download de vídeos único e em lote",
            "Armazenamento seguro de credenciais com keyring",
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
        "log_checking_ffmpeg": "Verificando instalação do FFmpeg...",
        "log_ffmpeg_found": "FFmpeg encontrado.",
        "log_ffmpeg_not_found": "FFmpeg não encontrado. Conversão de áudio pode não funcionar.",
        "log_downloading": "Baixando vídeo de",
        "log_verifying_url": "Verificando URL...",
        "log_video_info": "Informações do vídeo obtidas com sucesso",
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
    
    def get_language(self):
        """Get currently active language code
        
        Returns:
            str: Current language ('en' or 'pt')
        """
        return self.language
    
    def get_available_languages(self):
        """Get list of all available languages
        
        Returns:
            list: Available language codes
        """
        return list(TRANSLATIONS.keys())
    
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
