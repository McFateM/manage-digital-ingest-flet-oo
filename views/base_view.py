"""
Base View Class for Manage Digital Ingest Application

This module contains the base class that all view classes inherit from,
providing common functionality and structure.
"""

import flet as ft
from abc import ABC, abstractmethod
from logger import SnackBarHandler
import logging

class BaseView(ABC):
    """
    Abstract base class for all application views.
    
    Provides common functionality including theme management,
    logging, and session handling.
    """
    
    def __init__(self, page: ft.Page):
        """
        Initialize the base view.
        
        Args:
            page (ft.Page): The Flet page object
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_theme_colors(self):
        """Get theme-appropriate colors based on current theme mode"""
        # Detect if we're in dark mode
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        
        if is_dark:
            return {
                'primary_text': ft.Colors.WHITE,
                'secondary_text': ft.Colors.GREY_300,
                'divider': ft.Colors.RED_300,  # Slightly lighter red for dark mode
                'border': ft.Colors.GREY_600,
                'markdown_bg': ft.Colors.PURPLE_900,
                'markdown_text': ft.Colors.WHITE,
                'code_text': ft.Colors.ORANGE_300,
                'container_bg': ft.Colors.GREY_900,  # Darker background for better contrast
                'container_text': ft.Colors.WHITE,   # Explicit white text for containers
                'container_label': ft.Colors.GREY_300,  # Light grey for labels/subtitles
                'error': ft.Colors.RED_400  # Slightly lighter red for better visibility in dark mode
            }
        else:
            return {
                'primary_text': ft.Colors.BLACK,
                'secondary_text': ft.Colors.GREY_600,
                'divider': ft.Colors.RED_400,
                'border': ft.Colors.GREY_400,
                'markdown_bg': ft.Colors.PURPLE_50,
                'markdown_text': ft.Colors.BLACK,
                'code_text': ft.Colors.ORANGE_400,
                'container_bg': ft.Colors.GREY_100,  # Light theme container background
                'container_text': ft.Colors.BLACK,   # Explicit black text for containers
                'container_label': ft.Colors.GREY_700,  # Dark grey for labels/subtitles
                'error': ft.Colors.RED_600  # Darker red for better visibility in light mode
            }
    
    def create_log_button(self, text="Show Logs", icon=ft.Icons.LIST_ALT):
        """Create a button that opens the log overlay"""
        from views.log_overlay import LogOverlay
        log_overlay = LogOverlay(self.page)
        
        return ft.ElevatedButton(
            text=text,
            icon=icon,
            on_click=lambda e: log_overlay.show()
        )
    
    @abstractmethod
    def render(self) -> ft.Column:
        """
        Render the view content.
        
        Returns:
            ft.Column: The view's UI content
        """
        pass
    
    def on_view_enter(self):
        """Called when the view is entered/loaded"""
        self.logger.info(f"Loaded {self.__class__.__name__}")
    
    def on_view_exit(self):
        """Called when the view is exited"""
        pass