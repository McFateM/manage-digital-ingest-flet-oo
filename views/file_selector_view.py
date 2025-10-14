"""
File Selector View for Manage Digital Ingest Application

This module contains the base FileSelectorView class and three specific implementations:
- FilePickerSelectorView: For file picker functionality
- GoogleSheetSelectorView: For Google Sheet functionality
- CSVSelectorView: For CSV file functionality
"""

import flet as ft
from views.base_view import BaseView


class FileSelectorView(BaseView):
    """
    Base file selector view class for handling file selection operations.
    This is an abstract base class that should be subclassed for specific implementations.
    """
    
    def __init__(self, page: ft.Page, selector_type: str):
        """
        Initialize the file selector view.
        
        Args:
            page: The Flet page object
            selector_type: The type of selector (e.g., "FilePicker", "Google Sheet", "CSV")
        """
        super().__init__(page)
        self.selector_type = selector_type
    
    def render(self) -> ft.Column:
        """
        Render the file selector view content.
        This base implementation should be overridden by subclasses.
        
        Returns:
            ft.Column: The file selector page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        return ft.Column([
            ft.Row([
                ft.Text(f"File Selector - {self.selector_type}", size=24, weight=ft.FontWeight.BOLD),
                self.create_log_button("Show Logs", ft.Icons.LIST_ALT)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=15),
            ft.Text(f"File selector functionality for {self.selector_type} will be implemented here.",
                   size=16, color=colors['primary_text']),
        ], alignment="center")


class FilePickerSelectorView(FileSelectorView):
    """
    File picker implementation of the file selector view.
    Handles local file system file selection.
    """
    
    def __init__(self, page: ft.Page):
        """Initialize the file picker selector view."""
        super().__init__(page, "FilePicker")
        self.selected_files = []
        self.selected_files_list = None
    
    def load_last_directory(self):
        """Load the last used directory from persistent storage."""
        try:
            import json
            import os
            persistent_path = os.path.join("_data", "persistent.json")
            if os.path.exists(persistent_path):
                with open(persistent_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    directory = data.get("last_directory")
                    if directory and os.path.exists(directory):
                        return directory
        except Exception as e:
            self.logger.warning(f"Failed to load last directory: {e}")
        return None
    
    def save_last_directory(self, directory):
        """Save the last used directory to persistent storage."""
        try:
            import json
            import os
            persistent_path = os.path.join("_data", "persistent.json")
            os.makedirs("_data", exist_ok=True)
            
            # Load existing data to preserve other settings
            existing_data = {}
            if os.path.exists(persistent_path):
                try:
                    with open(persistent_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception:
                    self.logger.warning("Failed to read existing persistent data")
            
            # Update only the last_directory field
            existing_data["last_directory"] = directory
            
            # Write back to file
            with open(persistent_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
            
            self.logger.info(f"Saved last directory: {directory}")
        except Exception as e:
            self.logger.error(f"Failed to save last directory: {e}")
    
    def render(self) -> ft.Column:
        """
        Render the file picker selector view content.
        
        Returns:
            ft.Column: The file picker page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # Load last directory
        last_dir = self.load_last_directory()
        
        # Handler for file picker result
        def on_file_picker_result(e: ft.FilePickerResultEvent):
            """Handle file picker result."""
            if e.files:
                self.selected_files = []
                file_paths = []
                
                for file in e.files:
                    self.selected_files.append(file)
                    file_paths.append(file.path)
                
                # Save the directory of the first selected file
                if file_paths:
                    import os
                    directory = os.path.dirname(file_paths[0])
                    self.save_last_directory(directory)
                    
                    # Store selected file paths in page session
                    self.page.session.set("selected_file_paths", file_paths)
                    self.logger.info(f"Selected {len(file_paths)} file(s)")
                
                # Update the UI to show selected files
                self.update_file_list()
            else:
                self.logger.info("No files selected")
        
        # Create file picker
        file_picker = ft.FilePicker(
            on_result=on_file_picker_result
        )
        
        # Add file picker to page overlay (required for FilePicker to work)
        self.page.overlay.append(file_picker)
        
        # Handler for open file picker button
        def open_file_picker(e):
            """Open the file picker dialog."""
            # Set initial directory if available
            initial_dir = last_dir if last_dir else None
            
            # Open file picker with multiple selection enabled and file type filters
            file_picker.pick_files(
                dialog_title="Select Image or PDF Files",
                allow_multiple=True,
                allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "pdf"],
                initial_directory=initial_dir
            )
        
        # Create a list view for selected files
        self.selected_files_list = ft.ListView(
            spacing=0,
            padding=2,
            height=300,
            expand=True
        )
        
        # Load previously selected files from session if available
        session_files = self.page.session.get("selected_file_paths")
        if session_files:
            self.logger.info(f"Loaded {len(session_files)} file(s) from session")
            for file_path in session_files:
                import os
                self.selected_files_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DESCRIPTION, size=14),
                        title=ft.Text(os.path.basename(file_path), size=14),
                        subtitle=ft.Text(file_path, size=11, color=colors['secondary_text']),
                        dense=True,
                        content_padding=ft.padding.symmetric(horizontal=5, vertical=0)
                        )
                    )
            self.page.update()
        
        return ft.Column([
            ft.Row([
                ft.Text(f"File Selector - {self.selector_type}", size=24, weight=ft.FontWeight.BOLD),
                self.create_log_button("Show Logs", ft.Icons.LIST_ALT)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            # ft.Container(height=8),
            ft.Divider(height=15, color=colors['divider']),
            ft.Text("Select image or PDF files from your local file system.",
                   size=16, color=colors['primary_text']),
            ft.Container(height=5),
            ft.Text(f"Last directory: {last_dir if last_dir else 'None'}", 
                   size=12, color=colors['secondary_text'], italic=True),
            ft.Container(height=8),
            ft.Row([
                ft.ElevatedButton(
                    "Open File Picker",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=open_file_picker
                ),
                ft.ElevatedButton(
                    "Clear Selection",
                    icon=ft.Icons.CLEAR,
                    on_click=lambda e: self.clear_selection()
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Container(height=8),
            ft.Text("Selected Files:", size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Container(height=5),
            ft.Container(
                content=self.selected_files_list,
                border=ft.border.all(1, colors['border']),
                border_radius=5,
                padding=2
            )
        ], alignment="start", expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
    
    def update_file_list(self):
        """Update the displayed list of selected files."""
        if self.selected_files_list:
            colors = self.get_theme_colors()
            self.selected_files_list.controls.clear()
            
            for file in self.selected_files:
                import os
                self.selected_files_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DESCRIPTION, size=14),
                        title=ft.Text(os.path.basename(file.path), size=14),
                        subtitle=ft.Text(file.path, size=11, color=colors['secondary_text']),
                        dense=True,
                        content_padding=ft.padding.symmetric(horizontal=5, vertical=0)
                    )
                )
            
            self.page.update()
    
    def clear_selection(self):
        """Clear the selected files."""
        self.selected_files = []
        self.page.session.set("selected_file_paths", [])
        if self.selected_files_list:
            self.selected_files_list.controls.clear()
        self.page.update()
        self.logger.info("Cleared file selection")


class GoogleSheetSelectorView(FileSelectorView):
    """
    Google Sheet implementation of the file selector view.
    Handles file selection from Google Sheets.
    """
    
    def __init__(self, page: ft.Page):
        """Initialize the Google Sheet selector view."""
        super().__init__(page, "Google Sheet")
    
    def render(self) -> ft.Column:
        """
        Render the Google Sheet selector view content.
        
        Returns:
            ft.Column: The Google Sheet page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # TODO: Implement Google Sheet functionality
        # This should include:
        # - Google Sheets API integration
        # - Sheet selection
        # - Data import from sheets
        
        return ft.Column([
            ft.Row([
                ft.Text(f"File Selector - {self.selector_type}", size=24, weight=ft.FontWeight.BOLD),
                self.create_log_button("Show Logs", ft.Icons.LIST_ALT)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=15),
            ft.Text("Import file list from a Google Sheet.",
                   size=16, color=colors['primary_text']),
            ft.Container(height=15),
            ft.TextField(
                label="Google Sheet URL",
                hint_text="Enter Google Sheet URL here",
                width=500
            ),
            ft.Container(height=15),
            ft.ElevatedButton(
                "Connect to Sheet",
                icon=ft.Icons.CLOUD,
                on_click=lambda e: self.logger.info("Google Sheet functionality to be implemented")
            ),
            ft.Container(height=15),
            ft.Text("Sheet data will appear here.",
                   size=14, color=colors['secondary_text'])
        ], alignment="center")


class CSVSelectorView(FileSelectorView):
    """
    CSV implementation of the file selector view.
    Handles file selection from CSV files.
    """
    
    def __init__(self, page: ft.Page):
        """Initialize the CSV selector view."""
        super().__init__(page, "CSV")
    
    def render(self) -> ft.Column:
        """
        Render the CSV selector view content.
        
        Returns:
            ft.Column: The CSV page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # TODO: Implement CSV functionality
        # This should include:
        # - CSV file picker
        # - CSV parsing
        # - Data display and validation
        
        return ft.Column([
            ft.Row([
                ft.Text(f"File Selector - {self.selector_type}", size=24, weight=ft.FontWeight.BOLD),
                self.create_log_button("Show Logs", ft.Icons.LIST_ALT)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=15),
            ft.Text("Import file list from a CSV file.",
                   size=16, color=colors['primary_text']),
            ft.Container(height=15),
            ft.ElevatedButton(
                "Select CSV File",
                icon=ft.Icons.DESCRIPTION,
                on_click=lambda e: self.logger.info("CSV functionality to be implemented")
            ),
            ft.Container(height=15),
            ft.Text("CSV data will appear here.",
                   size=14, color=colors['secondary_text'])
        ], alignment="center")
