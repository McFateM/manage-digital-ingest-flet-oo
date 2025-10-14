"""
Main Application Class for Manage Digital Ingest Application

This module contains the main MDIApplication class that manages the application
lifecycle, routing, and UI structure.
"""

import flet as ft
import logging
from logger import SnackBarHandler
from views import (
    HomeView, AboutView, SettingsView, ExitView,
    FilePickerSelectorView, GoogleSheetSelectorView, CSVSelectorView,
    DerivativesView, StorageView, LogView
)
import utils


class MDIApplication:
    """
    Main application class for Manage Digital Ingest.
    
    Handles application initialization, routing, and UI management.
    """
    
    def __init__(self):
        """Initialize the application."""
        self.setup_logging()
        self.views = {}
        self.current_view = None
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        self.logger = logging.getLogger(__name__)
        
        # Setup snackbar handler
        self._snack_handler = SnackBarHandler()
        self._snack_handler.setLevel(logging.INFO)
        self.logger.addHandler(self._snack_handler)
        
        # File logging: write messages to mdi.log in the repo root
        _file_handler = logging.FileHandler("mdi.log")
        _file_handler.setLevel(logging.INFO)
        _file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        _file_handler.setFormatter(_file_formatter)
        self.logger.addHandler(_file_handler)
        
        # Write an initial log entry
        self.logger.info("Logger initialized - writing to mdi.log and SnackBarHandler attached")
    
    def get_file_selector_view(self, page: ft.Page):
        """
        Get the appropriate file selector view based on the selected file option.
        
        Args:
            page: The Flet page object
            
        Returns:
            The appropriate file selector view instance
        """
        # Load persistent settings to get the selected file option
        try:
            import json
            import os
            persistent_path = os.path.join("_data", "persistent.json")
            if os.path.exists(persistent_path):
                with open(persistent_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    selected_option = data.get("selected_file_option", "")
            else:
                selected_option = ""
        except Exception as e:
            self.logger.warning(f"Failed to load file option from persistent settings: {e}")
            selected_option = ""
        
        # Also check session for current selection
        session_option = page.session.get("selected_file_option")
        if session_option:
            selected_option = session_option
        
        # Return the appropriate view based on selection
        if selected_option == "FilePicker":
            return FilePickerSelectorView(page)
        elif selected_option == "Google Sheet":
            return GoogleSheetSelectorView(page)
        elif selected_option == "CSV":
            return CSVSelectorView(page)
        else:
            # Default to FilePicker if no selection
            return FilePickerSelectorView(page)
    
    def initialize_views(self, page: ft.Page):
        """Initialize all view instances."""
        self.views = {
            "/": HomeView(page),
            "/home": HomeView(page),
            "/about": AboutView(page),
            "/settings": SettingsView(page),
            "/exit": ExitView(page),
            "/file_selector": None,  # Will be dynamically created
            "/derivatives": DerivativesView(page),
            "/storage": StorageView(page),
            "/logs": LogView(page),
        }
    
    def build_appbar(self, page: ft.Page) -> ft.AppBar:
        """Build the application's app bar with navigation."""
        
        def nav_home(e):
            page.go("/")
        
        def nav_file_selector(e):
            page.go("/file_selector")
        
        def nav_derivatives(e):
            page.go("/derivatives")
        
        def nav_storage(e):
            page.go("/storage")
        
        def nav_about(e):
            page.go("/about")
        
        def nav_settings(e):
            page.go("/settings")
        
        def nav_logs(e):
            page.go("/logs")
        
        def nav_exit(e):
            page.go("/exit")
        
        return ft.AppBar(
            leading=ft.Icon(ft.Icons.PALETTE),
            leading_width=40,
            title=ft.Text("Manage Digital Ingest"),
            center_title=False,
            bgcolor=ft.Colors.BLUE_GREY_100,
            actions=[
                ft.IconButton(ft.Icons.HOME, tooltip="Home", on_click=nav_home),
                ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=nav_settings),
                ft.IconButton(ft.Icons.INFO, tooltip="About", on_click=nav_about),
                ft.IconButton(ft.Icons.LIST_ALT, tooltip="Application Log", on_click=nav_logs),
                # Vertical separator between Application Log and File Selector icons
                ft.Container(
                    width=2,
                    height=23,
                    bgcolor=ft.Colors.GREY_400,
                    margin=ft.margin.symmetric(horizontal=4)
                ),
                ft.IconButton(ft.Icons.FILE_OPEN, tooltip="File Selector", on_click=nav_file_selector),
                ft.IconButton(ft.Icons.AUTO_FIX_HIGH, tooltip="Derivatives", on_click=nav_derivatives),
                ft.IconButton(ft.Icons.CLOUD_UPLOAD, tooltip="Storage", on_click=nav_storage),
                # Vertical separator before the Exit icon
                ft.Container(
                    width=2,
                    height=23,
                    bgcolor=ft.Colors.GREY_400,
                    margin=ft.margin.symmetric(horizontal=4)
                ),
                ft.IconButton(ft.Icons.EXIT_TO_APP, tooltip="Exit", on_click=nav_exit),
            ],
        )
    
    def route_change(self, route):
        """Handle route changes."""
        self.logger.info(f"Route changed to: {route.route}")
        
        # Special handling for file_selector route - dynamically create based on settings
        if route.route == "/file_selector":
            view = self.get_file_selector_view(route.page)
            self.views["/file_selector"] = view
        else:
            # Get the view for the current route
            view = self.views.get(route.route)
        
        if view:
            self.current_view = view
            # Clear existing controls and add the new view
            route.page.controls.clear()
            route.page.controls.append(view.render())
            route.page.update()
        else:
            self.logger.warning(f"No view found for route: {route.route}")
            # Redirect to home if route not found
            route.page.go("/")
    
    def view_pop(self, view):
        """Handle view pop events."""
        self.logger.info("View popped")
        top_view = view.page.views[-1]
        view.page.views.pop()
        top_view_route = top_view.route
        view.page.go(top_view_route)
    
    def main(self, page: ft.Page):
        """Main application entry point."""
        # Configure page
        page.title = "Manage Digital Ingest: a Flet Multi-Page App"
        
        # Load persistent settings from persistent storage
        window_height = 700  # Default value
        theme_mode = "Light"  # Default theme
        try:
            with open("_data/persistent.json", "r", encoding="utf-8") as f:
                persistent_data = utils.json.load(f)
                window_height = persistent_data.get("window-height", 700)
                theme_mode = persistent_data.get("selected_theme", "Light")
        except Exception as e:
            self.logger.warning(f"Failed to load persistent settings from persistent.json: {e}")
        
        # Set window dimensions
        page.window.height = window_height
        page.window.min_height = 500
        
        # Set theme mode from persistent settings
        if theme_mode == "Dark":
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        
        # Enable page-level scrolling
        page.scroll = ft.ScrollMode.AUTO
        
        # Initialize views
        self.initialize_views(page)
        
        # Set up the app bar
        page.appbar = self.build_appbar(page)
        
        # Set up routing
        page.on_route_change = self.route_change
        page.on_view_pop = self.view_pop
        
        # Store page reference for logging handler
        self._snack_handler.page = page
        
        # Log configuration info
        config = utils.read_config()
        self.logger.info(f"Application started with Python {config['python_version']} and Flet {config['flet_version']}")
        
        # Navigate to home page
        page.go("/")


def main(page: ft.Page):
    """Entry point for the Flet application."""
    app = MDIApplication()
    app.main(page)


if __name__ == "__main__":
    ft.app(target=main)