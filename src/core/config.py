# -*- coding: utf-8 -*-
"""
Unified Configuration Management for EasyCut

Centralizes all application configuration with:
- JSON persistence
- Type safety
- Default values
- Hot-reload support
- Validation

Usage:
    config = ConfigManager()
    output_dir = config.get("output_folder")
    config.set("dark_mode", True)
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union
from datetime import datetime

from .exceptions import ConfigException
from .logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    Centralized configuration manager for EasyCut
    
    Handles all configuration loading, saving, validation, and defaults.
    Supports nested keys using dot notation: "theme.dark_mode"
    """
    
    # Default configuration structure
    DEFAULTS = {
        # UI Settings
        "dark_mode": True,
        "language": "en",
        "window_width": 1000,
        "window_height": 700,
        
        # Download Settings
        "output_folder": str(Path.home() / "Downloads"),
        "download_quality": "best",
        "auto_download": False,
        "fallback_quality": "720p",
        
        # Audio Settings
        "audio_format": "mp3",
        "audio_bitrate": "192",
        
        # Auth Settings
        "save_credentials": True,
        
        # Advanced Settings
        "log_level": "INFO",
        "use_ffmpeg": True,
        "proxy": None,
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ConfigManager
        
        Args:
            config_path: Path to config.json (auto-detected if None)
        """
        # Determine config path
        if config_path is None:
            app_data = Path.home() / ".easycut"
            app_data.mkdir(parents=True, exist_ok=True)
            config_path = app_data / "config.json"
        
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_or_create()
    
    def _load_or_create(self) -> None:
        """Load config from file or create with defaults"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"Config loaded from {self.config_path}")
            else:
                self._config = self.DEFAULTS.copy()
                self._save()
                logger.info(f"Config created at {self.config_path}")
        
        except Exception as e:
            logger.error(f"Failed to load config: {e}", exc_info=True)
            self._config = self.DEFAULTS.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Config key (supports dot notation for nested keys)
            default: Default value if key not found
        
        Returns:
            Configuration value
        
        Example:
            output = config.get("output_folder")
            quality = config.get("download.quality", "best")
        """
        try:
            # Handle nested keys with dot notation
            if "." in key:
                parts = key.split(".")
                value = self._config
                for part in parts:
                    value = value[part]
                return value
            else:
                return self._config.get(key, default)
        
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value
        
        Args:
            key: Config key (supports dot notation)
            value: Value to set
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle nested keys
            if "." in key:
                parts = key.split(".")
                target = self._config
                
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                
                target[parts[-1]] = value
            else:
                self._config[key] = value
            
            self._save()
            logger.debug(f"Config set: {key} = {value}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration"""
        return self._config.copy()
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self._config = self.DEFAULTS.copy()
            self._save()
            logger.info("Config reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to reset config: {e}")
            return False
    
    def _save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigException(
                f"Failed to save config: {e}",
                code="CONFIG_SAVE_ERROR",
                context={"path": str(self.config_path)}
            )
    
    def validate(self, key: str, value_type: Type) -> bool:
        """
        Validate configuration value type
        
        Args:
            key: Config key
            value_type: Expected type
        
        Returns:
            True if valid
        """
        value = self.get(key)
        return isinstance(value, value_type) if value else True
    
    def __repr__(self):
        return f"ConfigManager(path={self.config_path})"
