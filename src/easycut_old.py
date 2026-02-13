# -*- coding: utf-8 -*-
"""
EasyCut - YouTube Video Downloader and Audio Converter
Aplicativo desktop em Tkinter para baixar videos do YouTube e converter audio

Autor: Deko Costa
GitHub: https://github.com/dekouninter/EasyCut
Versão: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
import re
import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import urllib.parse

# Importar módulos locais
sys.path.insert(0, os.path.dirname(__file__))
from i18n import translator as t, Translator
from ui_enhanced import Theme, ConfigManager, LogWidget, StatusBar, LoginPopup, LanguageSelector, LoginPopup
from donation_system import DonationButton

# Importar bibliotecas externas (podem não estar instaladas)
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


class EasyCutApp:
    """Aplicação principal do EasyCut"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(t("app_title"))
        self.root.geometry("1000x700")
        
        # Configurações
        self.config_manager = ConfigManager()
        self.load_config()
        
        # Tema
        self.theme = Theme(dark_mode=self.dark_mode)
        
        # Tradutor
        self.translator = Translator(self.language)
        
        # Estado de login
        self.logged_in = False
        self.current_email = ""
        self.check_saved_credentials()
        
        # Threading
        self.download_thread = None
        self.is_downloading = False
        
        # Diretório de saída
        self.output_dir = Path(self.config_manager.get("output_folder", "downloads"))
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Construir UI
        self.setup_ui()
        self.log_app("Aplicativo iniciado com sucesso")
    
    def load_config(self):
        """Carrega configurações do arquivo"""
        config = self.config_manager.load()
        self.dark_mode = config.get("dark_mode", True)
        self.language = config.get("language", "pt")
    
    def setup_logging(self):
        """Configura logging da aplicação"""
        log_file = Path("config") / "app.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_saved_credentials(self):
        """Verifica se há credenciais salvas"""
        if not KEYRING_AVAILABLE:
            return
        
        try:
            password = keyring.get_password("easycut", "email")
            if password:
                email = keyring.get_password("easycut", "user_email")
                if email:
                    self.logged_in = True
                    self.current_email = email
        except Exception as e:
            self.logger.warning(f"Erro ao verificar credenciais: {e}")
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Aplicar tema ttk
        self.theme.get_ttk_style()
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Menu
        self.create_menu()
        
        # Barra de status superior
        top_status = ttk.Frame(main_frame)
        top_status.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(top_status, text=f"Status: {self.get_login_status()}").pack(side=tk.LEFT)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Criar abas
        self.create_login_tab()
        self.create_download_tab()
        self.create_batch_tab()
        self.create_audio_tab()
        self.create_history_tab()
        self.create_about_tab()
        
        # Barra de status inferior
        self.status_bar = StatusBar(main_frame, theme=self.theme)
        self.status_bar.pack(fill=tk.X)
        self.status_bar.set_login_status(self.logged_in, self.current_email)
        
        # Botão flutuante de doações
        donation_btn = DonationButton(self.root)
        donation_btn.create_floating_button(main_frame)
    
    def create_menu(self):
        """Cria barra de menu"""
        menubar = tk.Menu(self.root, bg=self.theme.get("bg"), fg=self.theme.get("fg"))
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_file"), menu=file_menu)
        file_menu.add_command(label=t("menu_open_folder"), command=self.open_output_folder)
        file_menu.add_command(label=t("menu_refresh"), command=self.refresh_ui)
        file_menu.add_separator()
        file_menu.add_command(label=t("menu_exit"), command=self.root.quit)
        
        # Menu Visualizar
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_view"), menu=view_menu)
        view_menu.add_command(label=t("menu_theme"), command=self.toggle_theme)
        
        # Menu Idioma
        lang_selector = LanguageSelector(default=self.language)
        lang_menu = lang_selector.create_menu(menubar, self.change_language)
        menubar.add_cascade(label=t("menu_language"), menu=lang_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_help"), menu=help_menu)
        help_menu.add_command(label=t("menu_donations"), command=self.show_donations)
        help_menu.add_command(label=t("menu_about"), command=self.show_about)
    
    def create_login_tab(self):
        """Cria aba de login"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=t("tab_login"))
        
        # Frame principal com padding
        main_frame = ttk.Frame(frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text=t("login_title"), font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Status de login
        self.login_status_label = ttk.Label(main_frame, text=self.get_login_status(), font=("Arial", 11))
        self.login_status_label.pack(pady=10)
        
        # Frame de campos
        fields_frame = ttk.LabelFrame(main_frame, text=t("login_status"), padding=15)
        fields_frame.pack(fill=tk.X, pady=10)
        
        # Email
        ttk.Label(fields_frame, text=t("login_email")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.login_email_entry = ttk.Entry(fields_frame, width=40)
        self.login_email_entry.grid(row=0, column=1, sticky=tk.EW, padx=10)
        
        # Senha
        ttk.Label(fields_frame, text=t("login_password")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.login_password_entry = ttk.Entry(fields_frame, width=40, show="*")
        self.login_password_entry.grid(row=1, column=1, sticky=tk.EW, padx=10)
        
        # Lembrar credenciais
        self.login_remember_var = tk.BooleanVar()
        ttk.Checkbutton(fields_frame, text=t("login_remember"), variable=self.login_remember_var).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=10
        )
        
        fields_frame.columnconfigure(1, weight=1)
        
        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(button_frame, text=t("login_btn"), command=self.do_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t("login_popup"), command=self.open_login_popup).pack(side=tk.LEFT, padx=5)
        
        if self.logged_in:
            ttk.Button(button_frame, text=t("login_logout"), command=self.do_logout).pack(side=tk.LEFT, padx=5)
    
    def create_download_tab(self):
        """Cria aba de download"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=t("tab_download"))
        
        main_frame = ttk.Frame(frame, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL do video
        url_frame = ttk.LabelFrame(main_frame, text=t("download_url"), padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.download_url_entry = ttk.Entry(url_frame, width=60)
        self.download_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(url_frame, text=t("download_verify"), command=self.verify_video).pack(side=tk.LEFT, padx=5)
        
        # Informações do vídeo
        info_frame = ttk.LabelFrame(main_frame, text="Info do Vídeo", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"{t('download_title')}:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.download_title_label = ttk.Label(info_frame, text="-", foreground="gray")
        self.download_title_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text=f"{t('download_duration')}:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.download_duration_label = ttk.Label(info_frame, text="-", foreground="gray")
        self.download_duration_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Modo de download
        mode_frame = ttk.LabelFrame(main_frame, text=t("download_mode"), padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.download_mode_var = tk.StringVar(value="full")
        ttk.Radiobutton(mode_frame, text=t("download_mode_full"), variable=self.download_mode_var, value="full", 
                       command=self.update_download_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text=t("download_mode_range"), variable=self.download_mode_var, value="range",
                       command=self.update_download_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text=t("download_mode_until"), variable=self.download_mode_var, value="until",
                       command=self.update_download_mode).pack(anchor=tk.W)
        
        # Frame para parâmetros de tempo
        self.time_params_frame = ttk.Frame(mode_frame)
        self.time_params_frame.pack(fill=tk.X, pady=10)
        
        # Qualidade
        quality_frame = ttk.LabelFrame(main_frame, text=t("download_quality"), padding=10)
        quality_frame.pack(fill=tk.X, pady=5)
        
        self.download_quality_var = tk.StringVar(value="best")
        ttk.Radiobutton(quality_frame, text=t("download_quality_best"), variable=self.download_quality_var, 
                       value="best").pack(anchor=tk.W)
        ttk.Radiobutton(quality_frame, text=t("download_quality_mp4"), variable=self.download_quality_var,
                       value="mp4").pack(anchor=tk.W)
        ttk.Radiobutton(quality_frame, text=t("download_quality_audio"), variable=self.download_quality_var,
                       value="audio").pack(anchor=tk.W)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.download_log = LogWidget(log_frame, theme=self.theme, height=8, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.download_log.yview)
        self.download_log.config(yscrollcommand=scrollbar.set)
        self.download_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text=t("download_btn"), command=self.start_download).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t("download_stop"), command=self.stop_download).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t("download_clear_log"), command=lambda: self.download_log.clear()).pack(side=tk.LEFT, padx=5)
    
    def create_batch_tab(self):
        """Cria aba de lote (batch)"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=t("tab_batch"))
        
        main_frame = ttk.Frame(frame, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Batch Download", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame de URLs
        urls_frame = ttk.LabelFrame(main_frame, text=t("batch_urls"), padding=10)
        urls_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(urls_frame, orient=tk.VERTICAL)
        self.batch_text = tk.Text(urls_frame, height=10, width=80, yscrollcommand=scrollbar.set)
        self.batch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.batch_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text=t("batch_download_all"), command=self.start_batch_download).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t("batch_paste"), command=self.batch_paste).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t("batch_clear"), command=lambda: self.batch_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        # Log do batch
        log_frame = ttk.LabelFrame(main_frame, text="Log do Lote", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.batch_log = LogWidget(log_frame, theme=self.theme, height=8, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.batch_log.yview)
        self.batch_log.config(yscrollcommand=scrollbar.set)
        self.batch_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_audio_tab(self):
        """Cria aba de áudio"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=t("tab_audio"))
        
        main_frame = ttk.Frame(frame, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL
        url_frame = ttk.LabelFrame(main_frame, text=t("audio_url"), padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.audio_url_entry = ttk.Entry(url_frame, width=60)
        self.audio_url_entry.pack(fill=tk.X)
        
        # Formato
        format_frame = ttk.LabelFrame(main_frame, text=t("audio_format"), padding=10)
        format_frame.pack(fill=tk.X, pady=5)
        
        self.audio_format_var = tk.StringVar(value="mp3")
        formats = [
            ("MP3", "mp3"),
            ("WAV", "wav"),
            ("M4A", "m4a"),
            ("OPUS", "opus")
        ]
        for text, value in formats:
            ttk.Radiobutton(format_frame, text=text, variable=self.audio_format_var, value=value).pack(anchor=tk.W)
        
        # Bitrate
        bitrate_frame = ttk.LabelFrame(main_frame, text=t("audio_bitrate"), padding=10)
        bitrate_frame.pack(fill=tk.X, pady=5)
        
        self.audio_bitrate_var = tk.StringVar(value="320")
        bitrates = ["128", "192", "256", "320"]
        for bitrate in bitrates:
            ttk.Radiobutton(bitrate_frame, text=f"{bitrate} kbps", variable=self.audio_bitrate_var, 
                           value=bitrate).pack(anchor=tk.W)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.audio_log = LogWidget(log_frame, theme=self.theme, height=10, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.audio_log.yview)
        self.audio_log.config(yscrollcommand=scrollbar.set)
        self.audio_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão de conversão
        ttk.Button(main_frame, text=t("audio_convert"), command=self.start_audio_conversion).pack(pady=10)
    
    def create_history_tab(self):
        """Cria aba de histórico"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=t("tab_history"))
        
        main_frame = ttk.Frame(frame, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text=t("history_update"), command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t("history_clear"), command=self.clear_history).pack(side=tk.LEFT, padx=5)
        
        # Árvore de histórico
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = (t("history_date"), t("history_filename"), t("history_status"))
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, height=15, show="tree headings")
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=250)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.config(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_history()
    
    def create_about_tab(self):
        """Cria aba sobre"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=t("tab_about"))
        
        # Sub-notebook
        about_notebook = ttk.Notebook(frame)
        about_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba Sobre
        about_frame = ttk.Frame(about_notebook, padding=20)
        about_notebook.add(about_frame, text=t("about_tab_about"))
        
        ttk.Label(about_frame, text=t("app_title"), font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(about_frame, text=t("about_description"), wraplength=500, justify=tk.CENTER).pack(pady=10)
        ttk.Label(about_frame, text=t("about_version_info")).pack(pady=5)
        ttk.Label(about_frame, text=t("about_github")).pack(pady=5)
        ttk.Label(about_frame, text=t("about_license")).pack(pady=5)
        
        # Aba Créditos
        credits_frame = ttk.Frame(about_notebook, padding=20)
        about_notebook.add(credits_frame, text=t("about_tab_credits"))
        
        ttk.Label(credits_frame, text=t("about_author"), font=("Arial", 11, "bold")).pack(pady=5)
        ttk.Label(credits_frame, text=t("about_credits_libs")).pack(pady=5)
        ttk.Label(credits_frame, text=t("about_credits_tools")).pack(pady=5)
        
        # Aba Recursos
        features_frame = ttk.Frame(about_notebook, padding=20)
        about_notebook.add(features_frame, text=t("about_tab_features"))
        
        ttk.Label(features_frame, text="Recursos do EasyCut:", font=("Arial", 11, "bold")).pack(pady=5, anchor=tk.W)
        
        features_text = tk.Text(features_frame, height=15, width=60, state=tk.DISABLED)
        features_text.pack(fill=tk.BOTH, expand=True)
        
        features_text.config(state=tk.NORMAL)
        for feature in t("about_features_list"):
            features_text.insert(tk.END, f"• {feature}\n")
        features_text.config(state=tk.DISABLED)
    
    def update_download_mode(self):
        """Atualiza opções de tempo baseado no modo"""
        # Limpar frame
        for widget in self.time_params_frame.winfo_children():
            widget.destroy()
        
        mode = self.download_mode_var.get()
        
        if mode == "range":
            ttk.Label(self.time_params_frame, text=t("download_start_time")).pack(side=tk.LEFT, padx=5)
            self.start_time_entry = ttk.Entry(self.time_params_frame, width=10)
            self.start_time_entry.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(self.time_params_frame, text=t("download_end_time")).pack(side=tk.LEFT, padx=5)
            self.end_time_entry = ttk.Entry(self.time_params_frame, width=10)
            self.end_time_entry.pack(side=tk.LEFT, padx=5)
        
        elif mode == "until":
            ttk.Label(self.time_params_frame, text=t("download_until_time")).pack(side=tk.LEFT, padx=5)
            self.until_time_entry = ttk.Entry(self.time_params_frame, width=10)
            self.until_time_entry.pack(side=tk.LEFT, padx=5)
    
    def verify_video(self):
        """Verifica informações do vídeo"""
        url = self.download_url_entry.get().strip()
        
        if not url:
            messagebox.showwarning(t("msg_warning"), t("download_invalid_url"))
            return
        
        if not self.is_valid_youtube_url(url):
            messagebox.showerror(t("msg_error"), t("download_invalid_url"))
            return
        
        self.download_log.add_log(t("log_verifying_url"))
        
        # Thread para verificação
        thread = threading.Thread(target=self._verify_video_thread, args=(url,), daemon=True)
        thread.start()
    
    def _verify_video_thread(self, url):
        """Thread para verificar vídeo"""
        if not YT_DLP_AVAILABLE:
            self.download_log.add_log("yt-dlp não instalado", "ERROR")
            return
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Desconhecido')
                duration = info.get('duration', 0)
                is_live = info.get('is_live', False)
                
                # Atualizar labels
                self.download_title_label.config(text=title[:50])
                
                mins, secs = divmod(duration, 60)
                self.download_duration_label.config(text=f"{int(mins)}:{int(secs):02d}")
                
                self.download_log.add_log(t("log_video_info"))
        
        except Exception as e:
            self.download_log.add_log(f"Erro: {str(e)}", "ERROR")
    
    def start_download(self):
        """Inicia download"""
        url = self.download_url_entry.get().strip()
        
        if not url:
            messagebox.showwarning(t("msg_warning"), t("download_invalid_url"))
            return
        
        if not self.is_valid_youtube_url(url):
            messagebox.showerror(t("msg_error"), t("download_invalid_url"))
            return
        
        self.is_downloading = True
        self.download_log.add_log(f"{t('log_downloading')} {url}")
        
        # Preparar opções
        quality = self.download_quality_var.get()
        mode = self.download_mode_var.get()
        
        # Thread para download
        self.download_thread = threading.Thread(
            target=self._download_thread,
            args=(url, quality, mode),
            daemon=True
        )
        self.download_thread.start()
    
    def _download_thread(self, url, quality, mode):
        """Thread para download"""
        if not YT_DLP_AVAILABLE:
            self.download_log.add_log("yt-dlp não instalado", "ERROR")
            return
        
        try:
            output_template = str(self.output_dir / "%(title)s.%(ext)s")
            
            ydl_opts = {
                'format': self._get_format_string(quality),
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
            }
            
            # Aplicar modo de download
            if mode == "range" and hasattr(self, 'start_time_entry'):
                start = self.start_time_entry.get().strip()
                end = self.end_time_entry.get().strip()
                
                if not self.validate_time_format(start) or not self.validate_time_format(end):
                    self.download_log.add_log(t("download_invalid_time"), "ERROR")
                    self.is_downloading = False
                    return
                
                start_sec = self.time_to_seconds(start)
                end_sec = self.time_to_seconds(end)
                
                if end_sec <= start_sec:
                    self.download_log.add_log(t("download_range_error"), "ERROR")
                    self.is_downloading = False
                    return
                
                ydl_opts['postprocessor_args'] = ['-ss', start, '-to', end]
                self.download_log.add_log(f"Download de {start} a {end}")
            
            elif mode == "until" and hasattr(self, 'until_time_entry'):
                until = self.until_time_entry.get().strip()
                
                if not self.validate_time_format(until):
                    self.download_log.add_log(t("download_invalid_time"), "ERROR")
                    self.is_downloading = False
                    return
                
                ydl_opts['postprocessor_args'] = ['-to', until]
                self.download_log.add_log(f"Download até {until}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Adicionar ao histórico
                entry = {
                    "date": datetime.now().isoformat(),
                    "filename": info.get('title', 'unknown'),
                    "status": "success",
                    "url": url
                }
                self.config_manager.add_to_history(entry)
                
                self.download_log.add_log(t("download_success"), "INFO")
                self.refresh_history()
        
        except Exception as e:
            self.download_log.add_log(f"{t('download_error')}: {str(e)}", "ERROR")
        
        finally:
            self.is_downloading = False
    
    def stop_download(self):
        """Para o download"""
        self.is_downloading = False
        self.download_log.add_log("Download cancelado", "INFO")
    
    def start_batch_download(self):
        """Inicia download em lote"""
        urls_text = self.batch_text.get(1.0, tk.END).strip()
        
        if not urls_text:
            messagebox.showwarning(t("msg_warning"), t("batch_empty"))
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            messagebox.showwarning(t("msg_warning"), t("batch_empty"))
            return
        
        self.batch_log.add_log(f"{t('batch_progress')}: {len(urls)} URLs", "INFO")
        
        thread = threading.Thread(target=self._batch_download_thread, args=(urls,), daemon=True)
        thread.start()
    
    def _batch_download_thread(self, urls):
        """Thread para download em lote"""
        success_count = 0
        error_count = 0
        
        for i, url in enumerate(urls, 1):
            if not self.is_valid_youtube_url(url):
                self.batch_log.add_log(f"[{i}/{len(urls)}] URL inválida: {url}", "WARNING")
                error_count += 1
                continue
            
            self.batch_log.add_log(f"[{i}/{len(urls)}] Baixando: {url}", "INFO")
            
            try:
                output_template = str(self.output_dir / "%(title)s.%(ext)s")
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': output_template,
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": info.get('title', 'unknown'),
                        "status": "success",
                        "url": url
                    }
                    self.config_manager.add_to_history(entry)
                    success_count += 1
                    self.batch_log.add_log(f"✓ Concluído", "INFO")
            
            except Exception as e:
                self.batch_log.add_log(f"✗ Erro: {str(e)}", "ERROR")
                error_count += 1
        
        self.batch_log.add_log(f"Lote concluído: {success_count} sucesso, {error_count} erros", "INFO")
        self.refresh_history()
    
    def batch_paste(self):
        """Cola URLs da área de transferência"""
        try:
            clipboard_data = self.root.clipboard_get()
            self.batch_text.insert(tk.END, clipboard_data)
        except Exception as e:
            messagebox.showerror(t("msg_error"), f"Erro ao colar: {e}")
    
    def start_audio_conversion(self):
        """Inicia conversão de áudio"""
        url = self.audio_url_entry.get().strip()
        
        if not url:
            messagebox.showwarning(t("msg_warning"), t("download_invalid_url"))
            return
        
        if not self.is_valid_youtube_url(url):
            messagebox.showerror(t("msg_error"), t("download_invalid_url"))
            return
        
        fmt = self.audio_format_var.get()
        bitrate = self.audio_bitrate_var.get()
        
        self.audio_log.add_log(f"Convertendo áudio para {fmt} ({bitrate}kbps)")
        
        thread = threading.Thread(
            target=self._audio_conversion_thread,
            args=(url, fmt, bitrate),
            daemon=True
        )
        thread.start()
    
    def _audio_conversion_thread(self, url, fmt, bitrate):
        """Thread para conversão de áudio"""
        if not YT_DLP_AVAILABLE:
            self.audio_log.add_log("yt-dlp não instalado", "ERROR")
            return
        
        try:
            output_template = str(self.output_dir / "%(title)s.%(ext)s")
            
            format_map = {
                'mp3': 'bestaudio/best',
                'wav': 'bestaudio/best',
                'm4a': 'bestaudio/best',
                'opus': 'bestaudio/best'
            }
            
            postprocessor_args = [
                '-acodec', 'libmp3lame' if fmt == 'mp3' else fmt,
                '-ab', f'{bitrate}k'
            ]
            
            ydl_opts = {
                'format': format_map.get(fmt, 'bestaudio/best'),
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': fmt,
                    'preferredquality': bitrate,
                    'nopostprocessor': False,
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.audio_log.add_log(t("audio_success"), "INFO")
                
                entry = {
                    "date": datetime.now().isoformat(),
                    "filename": f"{info.get('title', 'unknown')}.{fmt}",
                    "status": "success",
                    "url": url
                }
                self.config_manager.add_to_history(entry)
                self.refresh_history()
        
        except Exception as e:
            self.audio_log.add_log(f"{t('audio_error')}: {str(e)}", "ERROR")
    
    def refresh_history(self):
        """Atualiza histórico de downloads"""
        # Limpar árvore
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Carregar histórico
        history = self.config_manager.load_history()
        
        if not history:
            self.history_tree.insert("", tk.END, values=(t("history_empty"), "-", "-"))
            return
        
        # Adicionar itens (ordenado por data decrescente)
        for item in reversed(history):
            date_obj = datetime.fromisoformat(item.get("date", ""))
            date_str = date_obj.strftime("%d/%m/%Y %H:%M")
            filename = item.get("filename", "unknown")
            status = item.get("status", "unknown")
            
            self.history_tree.insert("", tk.END, values=(date_str, filename, status))
    
    def clear_history(self):
        """Limpa histórico"""
        if messagebox.askyesno(t("msg_confirm"), "Limpar todo o histórico?"):
            self.config_manager.save_history([])
            self.refresh_history()
            messagebox.showinfo(t("msg_success"), "Histórico limpo")
    
    def toggle_theme(self):
        """Alterna tema"""
        self.dark_mode = self.theme.toggle()
        self.config_manager.set("dark_mode", self.dark_mode)
        messagebox.showinfo(t("msg_info"), "Tema alterado. Reinicie a aplicação para aplicar as mudanças completamente.")
    
    def change_language(self, language):
        """Muda idioma"""
        self.translator.set_language(language)
        self.config_manager.set("language", language)
        messagebox.showinfo(t("msg_info"), "Idioma alterado. Reinicie a aplicação para aplicar as mudanças.")
    
    def open_output_folder(self):
        """Abre pasta de saída"""
        try:
            import subprocess
            subprocess.Popen(f'explorer "{self.output_dir}"')
        except Exception as e:
            messagebox.showerror(t("msg_error"), f"Erro ao abrir pasta: {e}")
    
    def refresh_ui(self):
        """Atualiza UI"""
        self.status_bar.set_status("Atualizado")
        self.refresh_history()
    
    def show_donations(self):
        """Mostra janela de doações"""
        messagebox.showinfo(t("donation_title"), t("donation_description"))
    
    def show_about(self):
        """Mostra informações sobre"""
        self.notebook.select(self.notebook.tabs()[-1])
    
    def do_login(self):
        """Realiza login"""
        email = self.login_email_entry.get().strip()
        password = self.login_password_entry.get()
        remember = self.login_remember_var.get()
        
        if not email or not password:
            messagebox.showwarning(t("msg_warning"), t("login_validation_error"))
            return
        
        if not self.is_valid_email(email):
            messagebox.showerror(t("msg_error"), t("login_validation_error"))
            return
        
        # Validação simplificada (em produção, seria com servidor real)
        self.logged_in = True
        self.current_email = email
        
        if remember and KEYRING_AVAILABLE:
            try:
                keyring.set_password("easycut", "user_email", email)
                keyring.set_password("easycut", "password", password)
            except Exception as e:
                self.logger.warning(f"Erro ao salvar credenciais: {e}")
        
        self.login_status_label.config(text=self.get_login_status())
        self.status_bar.set_login_status(True, email)
        messagebox.showinfo(t("msg_success"), t("login_success"))
    
    def open_login_popup(self):
        """Abre popup de login"""
        popup = LoginPopup(self.root, callback=self.do_login)
        popup.show()
    
    def do_logout(self):
        """Realiza logout"""
        if messagebox.askyesno(t("msg_confirm"), "Desconectar?"):
            self.logged_in = False
            self.current_email = ""
            
            if KEYRING_AVAILABLE:
                try:
                    keyring.delete_password("easycut", "user_email")
                    keyring.delete_password("easycut", "password")
                except Exception:
                    pass
            
            self.login_status_label.config(text=self.get_login_status())
            self.status_bar.set_login_status(False)
            messagebox.showinfo(t("msg_success"), t("login_logout_success"))
    
    def get_login_status(self):
        """Retorna status de login formatado"""
        if self.logged_in:
            return f"{t('status_logged_in')} {self.current_email}"
        return t("status_not_logged_in")
    
    def log_app(self, message):
        """Log da aplicação"""
        self.logger.info(message)
    
    @staticmethod
    def is_valid_youtube_url(url):
        """Valida URL do YouTube"""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        return re.match(youtube_regex, url) is not None
    
    @staticmethod
    def is_valid_email(email):
        """Valida formato de email"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    @staticmethod
    def validate_time_format(time_str):
        """Valida formato MM:SS"""
        if not time_str:
            return False
        parts = time_str.split(':')
        if len(parts) != 2:
            return False
        try:
            mm, ss = int(parts[0]), int(parts[1])
            return 0 <= mm < 999 and 0 <= ss < 60
        except ValueError:
            return False
    
    @staticmethod
    def time_to_seconds(time_str):
        """Converte MM:SS para segundos"""
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    
    @staticmethod
    def _get_format_string(quality):
        """Retorna string de formato para yt-dlp"""
        formats = {
            'best': 'bestvideo+bestaudio/best',
            'mp4': 'best[ext=mp4]/best',
            'audio': 'bestaudio/best'
        }
        return formats.get(quality, 'best')


def main():
    """Função principal"""
    root = tk.Tk()
    app = EasyCutApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
