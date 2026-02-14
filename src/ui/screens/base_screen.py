# -*- coding: utf-8 -*-
"""
Base Screen Class

Provides common interface and functionality for all screen implementations.
Each screen represents one tab in the application.

Best Practices:
- Implement build() to create a UI
- Implement bind_events() to hookup user interactions
- Implement get_data() to return current state
- Use factories for consistent widget creation
- Keep logic minimal - delegate to services
"""

from abc import ABC, abstractmethod
from tkinter import ttk
from typing import Dict, Any, Optional

from design_system import DesignTokens
from ui.factories import TabFactory
from core.logger import get_logger

logger = get_logger(__name__)


class BaseScreen(ABC):
    """
    Base class for all screen implementations
    
    Each screen represents a tab in the notebook.
    Screens are responsible for UI layout and user interaction,
    delegating business logic to services.
    """
    
    def __init__(
        self,
        notebook: ttk.Notebook,
        theme: DesignTokens,
        services: Dict[str, Any] = None,
        **kwargs
    ):
        """
        Initialize screen
        
        Args:
            notebook: ttk.Notebook to add this screen to
            theme: DesignTokens for colors/fonts
            services: Dictionary of service instances
            **kwargs: Additional arguments
        """
        self.notebook = notebook
        self.theme = theme
        self.services = services or {}
        self.kwargs = kwargs
        
        # Will be populated by build()
        self.tab_data = None
        self.frame = None
        self.canvas = None
        self.content = None
        
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def build(self) -> None:
        """
        Build the screen UI
        
        Should:
        1. Create tab using TabFactory.create_scrollable_tab()
        2. Populate self.tab_data with result
        3. Add widgets to self.content
        4. Call bind_events()
        
        Example:
            def build(self):
                self.tab_data = TabFactory.create_scrollable_tab(
                    self.notebook, "My Tab", self.theme, "🎬"
                )
                self.content = self.tab_data["content"]
                
                # Add widgets...
                label = ttk.Label(self.content, text="Hello")
                label.pack()
                
                self.bind_events()
        """
        pass
    
    @abstractmethod
    def bind_events(self) -> None:
        """
        Bind user interface events
        
        Should connect user actions to handlers:
        - Button clicks
        - Entry field changes
        - Combobox selections
        - etc.
        
        Example:
            def bind_events(self):
                self.download_btn.config(command=self.on_download_click)
                self.url_entry.bind("<Return>", self.on_url_enter)
        """
        pass
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Get current screen state/data
        
        Should return all relevant data from the screen
        for saving or passing to other screens.
        
        Returns:
            Dictionary with screen data
        
        Example:
            def get_data(self):
                return {
                    "url": self.url_entry.get(),
                    "quality": self.quality_combo.get(),
                    "format": self.format_var.get()
                }
        """
        pass
    
    # Convenience methods
    
    def get_service(self, service_name: str):
        """
        Get a service by name
        
        Args:
            service_name: Key in services dictionary
        
        Returns:
            Service instance or None
        """
        return self.services.get(service_name)
    
    def create_tab_header(self, title: str, subtitle: str = None):
        """Create standard tab header"""
        return TabFactory.create_tab_header(
            self.content,
            title,
            subtitle,
            theme=self.theme
        )
    
    def create_section(self, title: str = None, **kwargs):
        """Create standard section"""
        return TabFactory.create_tab_section(
            self.content,
            title,
            self.theme,
            **kwargs
        )
    
    def create_action_row(self, actions: list, **kwargs):
        """Create action button row"""
        return TabFactory.create_action_row(
            self.content,
            actions,
            self.theme,
            **kwargs
        )
    
    def create_log(self, **kwargs):
        """Create log widget"""
        return TabFactory.create_log_display(
            self.content,
            self.theme,
            **kwargs
        )
    
    def show_message(self, message: str, title: str = "Message"):
        """Show user message"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)
    
    def show_error(self, error: str, title: str = "Error"):
        """Show error message"""
        from tkinter import messagebox
        messagebox.showerror(title, error)
    
    def show_warning(self, warning: str, title: str = "Warning"):
        """Show warning message"""
        from tkinter import messagebox
        messagebox.showwarning(title, warning)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}>"


# Example screen implementation:

class ExampleScreen(BaseScreen):
    """Example screen showing best practices"""
    
    def build(self) -> None:
        """Build the UI"""
        # Create scrollable tab
        self.tab_data = TabFactory.create_scrollable_tab(
            self.notebook,
            "Example",
            self.theme,
            "🎬"
        )
        
        self.content = self.tab_data["content"]
        
        # Add header
        TabFactory.create_tab_header(
            self.content,
            "Example Screen",
            "This is an example",
            "🎬",
            self.theme
        )
        
        # Add section
        section = self.create_section("Settings")
        
        # Add widgets
        ttk.Label(section, text="Option 1:").pack(anchor="w", pady=4)
        self.option1_entry = ttk.Entry(section)
        self.option1_entry.pack(fill="x", pady=(0, 12))
        
        # Bind events
        self.bind_events()
        
        self.logger.info("ExampleScreen built")
    
    def bind_events(self) -> None:
        """Bind events"""
        self.option1_entry.bind("<Return>", self.on_option_changed)
        self.logger.info("Events bound")
    
    def get_data(self) -> Dict[str, Any]:
        """Get screen data"""
        return {
            "option1": self.option1_entry.get()
        }
    
    def on_option_changed(self, event):
        """Handle option change"""
        data = self.get_data()
        self.logger.info(f"Data changed: {data}")
