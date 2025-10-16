"""
Settings View for Manage Digital Ingest Application

This module contains the SettingsView class for displaying and managing
application settings and configurations.
"""

import flet as ft
from views.base_view import BaseView
import json
import os


class SettingsView(BaseView):
    """
    Settings view class for configuration management.
    """
    
    def load_persistent_settings(self):
        """Load settings from persistent.json"""
        try:
            persistent_path = os.path.join("_data", "persistent.json")
            if os.path.exists(persistent_path):
                with open(persistent_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
        except Exception as e:
            self.logger.warning(f"Failed to load persistent settings: {e}")
        return {}
    
    def save_persistent_settings(self, settings):
        """Save settings to persistent.json"""
        try:
            persistent_path = os.path.join("_data", "persistent.json")
            # Ensure the _data directory exists
            os.makedirs("_data", exist_ok=True)
            
            # Load existing data to preserve other settings
            existing_data = {}
            if os.path.exists(persistent_path):
                try:
                    with open(persistent_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception:
                    self.logger.warning("Failed to read existing persistent data")
            
            # Update with new settings
            existing_data.update(settings)
            
            # Write back to file
            with open(persistent_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
            
            self.logger.info(f"Saved persistent settings: {settings}")
        except Exception as e:
            self.logger.error(f"Failed to save persistent settings: {e}")
    
    def render(self) -> ft.Column:
        """
        Render the settings view content.
        
        Returns:
            ft.Column: The settings page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # Read data from JSON files
        with open("_data/modes.json", "r", encoding="utf-8") as file:
            modes_data = json.load(file)
            mode_options = modes_data.get("options", [])
        
        with open("_data/azure_blobs.json", "r", encoding="utf-8") as file:
            azure_blob_options = json.load(file)
        
        with open("_data/cb_collections.json", "r", encoding="utf-8") as file:
            cb_collection_options = json.load(file)
        
        # File selector options (hardcoded as requested)
        file_selector_options = ["FilePicker", "Google Sheet", "CSV"]
        
        # Log all available options
        self.logger.info(f"Available mode options: {mode_options}")
        self.logger.info(f"Available file selector options: {file_selector_options}")
        self.logger.info(f"Available storage options: {azure_blob_options}")
        self.logger.info(f"Available collection options: {cb_collection_options}")
        
        # Load persistent settings
        persistent_settings = self.load_persistent_settings()
        
        # Get current selections from session or fall back to persistent settings
        current_mode = self.page.session.get("selected_mode") or persistent_settings.get("selected_mode")
        current_file_option = self.page.session.get("selected_file_option") or persistent_settings.get("selected_file_option")
        current_storage = self.page.session.get("selected_storage") or persistent_settings.get("selected_storage")
        current_collection = self.page.session.get("selected_collection") or persistent_settings.get("selected_collection")
        
        # Store in session if loaded from persistent
        if current_mode:
            self.page.session.set("selected_mode", current_mode)
        if current_file_option:
            self.page.session.set("selected_file_option", current_file_option)
        if current_storage:
            self.page.session.set("selected_storage", current_storage)
        if current_collection:
            self.page.session.set("selected_collection", current_collection)
        
        # Log current session selections if they exist
        if current_mode:
            self.logger.info(f"Current mode selection: {current_mode}")
        if current_file_option:
            self.logger.info(f"Current file option selection: {current_file_option}")
        if current_storage:
            self.logger.info(f"Current storage selection: {current_storage}")
        if current_collection:
            self.logger.info(f"Current collection selection: {current_collection}")
        
        # Calculate collection enabled state
        is_collection_enabled = current_mode == "CollectionBuilder"
        self.logger.info(f"CB Collection Selector enabled: {is_collection_enabled}")
        
        # Create the collection dropdown reference
        collection_dropdown = ft.Dropdown(
            label="Select Target CBCollection",
            value=current_collection if current_collection else "",
            options=[ft.dropdown.Option(collection) for collection in cb_collection_options],
            width=300,
            disabled=not is_collection_enabled
        )
        
        # Create the collection container reference
        collection_settings_container = ft.Container(
            content=ft.Column([
                # ft.Text("CB Collection Selector", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
                collection_dropdown
            ]),
            padding=ft.padding.all(8),
            border=ft.border.all(1, colors['border']),
            border_radius=10,
            margin=ft.margin.symmetric(vertical=4),
            bgcolor=colors['container_bg'],
            opacity=1.0 if is_collection_enabled else 0.5
        )
        
        # Dropdown change handlers
        def on_mode_change(e):
            self.page.session.set("selected_mode", e.control.value)
            self.save_persistent_settings({"selected_mode": e.control.value})
            self.logger.info(f"Mode selected: {e.control.value}")
            self.log_all_current_selections()
            
            # Update collection selector state based on new mode
            new_is_enabled = e.control.value == "CollectionBuilder"
            collection_dropdown.disabled = not new_is_enabled
            collection_settings_container.opacity = 1.0 if new_is_enabled else 0.5
            self.page.update()
        
        def on_collection_change(e):
            self.page.session.set("selected_collection", e.control.value)
            self.save_persistent_settings({"selected_collection": e.control.value})
            self.logger.info(f"Collection selected: {e.control.value}")
            self.log_all_current_selections()
        
        # Set the collection dropdown's change handler
        collection_dropdown.on_change = on_collection_change
        
        def on_file_selector_change(e):
            self.page.session.set("selected_file_option", e.control.value)
            self.save_persistent_settings({"selected_file_option": e.control.value})
            self.logger.info(f"File option selected: {e.control.value}")
            self.log_all_current_selections()
        
        def on_storage_change(e):
            self.page.session.set("selected_storage", e.control.value)
            self.save_persistent_settings({"selected_storage": e.control.value})
            self.logger.info(f"Storage selected: {e.control.value}")
            self.log_all_current_selections()
        
        # Theme selector handler
        def on_theme_change(e):
            """Handle theme mode changes"""
            theme_value = e.control.value
            if theme_value == "Light":
                self.page.theme_mode = ft.ThemeMode.LIGHT
            elif theme_value == "Dark":
                self.page.theme_mode = ft.ThemeMode.DARK
            
            self.page.update()
            self.save_persistent_settings({"selected_theme": theme_value})
            self.logger.info(f"Theme changed to: {theme_value}")
            self.page.session.set("selected_theme", theme_value)
        
        # Get current theme for selector - check persistent settings first
        current_theme = persistent_settings.get("selected_theme", "Light")
        # Override with current page theme if different
        if self.page.theme_mode == ft.ThemeMode.DARK:
            current_theme = "Dark"
        elif self.page.theme_mode == ft.ThemeMode.LIGHT:
            current_theme = "Light"
        
        # Theme selector container
        theme_settings_container = ft.Container(
            content=ft.Row([
                ft.Icon(
                    name=ft.Icons.PALETTE_OUTLINED,
                    size=20,
                    color=colors['container_text']
                ),
                ft.Text("Theme:", size=16, weight=ft.FontWeight.BOLD, color=colors['container_text']),
                ft.Dropdown(
                    label="Select Theme",
                    value=current_theme,
                    options=[
                        ft.dropdown.Option("Light"),
                        ft.dropdown.Option("Dark")
                    ],
                    on_change=on_theme_change,
                    width=150
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            padding=ft.padding.all(8),
            border=ft.border.all(1, colors['border']),
            border_radius=10,
            margin=ft.margin.symmetric(vertical=4),
            bgcolor=colors['container_bg']
        )
        
        # Create containers with dropdowns
        mode_settings_container = ft.Container(
            content=ft.Column([
                # ft.Text("Mode Selector", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
                ft.Dropdown(
                    label="Select the Processing Mode",
                    value=current_mode if current_mode else "",
                    options=[ft.dropdown.Option(mode) for mode in mode_options],
                    on_change=on_mode_change,
                    width=300
                )
            ]),
            padding=ft.padding.all(8),
            border=ft.border.all(1, colors['border']),
            border_radius=10,
            margin=ft.margin.symmetric(vertical=4),
            bgcolor=colors['container_bg']
        )
        
        file_selector_settings_container = ft.Container(
            content=ft.Column([
                # ft.Text("File Selector Options", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
                ft.Dropdown(
                    label="Choose a File Selection Option",
                    value=current_file_option if current_file_option else "",
                    options=[ft.dropdown.Option(option) for option in file_selector_options],
                    on_change=on_file_selector_change,
                    width=300
                )
            ]),
            padding=ft.padding.all(8),
            border=ft.border.all(1, colors['border']),
            border_radius=10,
            margin=ft.margin.symmetric(vertical=4),
            bgcolor=colors['container_bg']
        )
        
        storage_settings_container = ft.Container(
            content=ft.Column([
                # ft.Text("Object Storage Selector", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
                ft.Dropdown(
                    label="Select Azure Storage",
                    value=current_storage if current_storage else "",
                    options=[ft.dropdown.Option(storage) for storage in azure_blob_options],
                    on_change=on_storage_change,
                    width=300
                )
            ]),
            padding=ft.padding.all(8),
            border=ft.border.all(1, colors['border']),
            border_radius=10,
            margin=ft.margin.symmetric(vertical=4),
            bgcolor=colors['container_bg']
        )
        
        return ft.Column([
            *self.create_page_header("Settings Page", include_log_button=False),
            mode_settings_container,
            file_selector_settings_container,
            storage_settings_container,
            collection_settings_container,
            ft.Divider(height=15, color=colors['divider']),
            theme_settings_container
        ], alignment="start", spacing=0)
    
    def log_all_current_selections(self):
        """Log all current selections in one summary"""
        selections = {
            "mode": self.page.session.get("selected_mode"),
            "file_option": self.page.session.get("selected_file_option"),
            "storage": self.page.session.get("selected_storage"),
            "collection": self.page.session.get("selected_collection")
        }
        self.logger.info(f"Current selections summary: {selections}")