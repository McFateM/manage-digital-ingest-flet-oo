"""
File Selector View for Manage Digital Ingest Application

This module contains the base FileSelectorView class and three specific implementations:
- FilePickerSelectorView: For file picker functionality
- GoogleSheetSelectorView: For Google Sheet functionality
- CSVSelectorView: For CSV file functionality
"""

import flet as ft
from views.base_view import BaseView
import os
import utils


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
    Handles file selection from CSV files with a 4-step workflow.
    """
    
    def __init__(self, page: ft.Page):
        """Initialize the CSV selector view."""
        super().__init__(page, "CSV")
        self.csv_file_display = None
        self.file_selection_container = None
        self.columns_display_container = None
        self.results_display_container = None
        self.search_container = None
    
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
            
            # Load existing data
            existing_data = {}
            if os.path.exists(persistent_path):
                try:
                    with open(persistent_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception:
                    self.logger.warning("Failed to read existing persistent data")
            
            # Update last_directory
            existing_data["last_directory"] = directory
            
            # Write back
            with open(persistent_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
            
            self.logger.info(f"Saved last directory: {directory}")
        except Exception as e:
            self.logger.error(f"Failed to save last directory: {e}")
    
    def read_csv_file(self, file_path):
        """
        Read CSV or Excel file and extract column headers.
        
        Returns:
            tuple: (columns: list, error: str)
        """
        try:
            import pandas as pd
            
            # Determine file type and read accordingly
            if file_path.lower().endswith('.csv'):
                # Try multiple encodings for CSV files
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
                df = None
                last_error = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        self.logger.info(f"Successfully read CSV with encoding: {encoding}")
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        last_error = f"Failed with encoding {encoding}"
                        continue
                
                if df is None:
                    return None, f"Could not read CSV file with any standard encoding. Last error: {last_error}"
                    
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return None, f"Unsupported file format: {file_path}"
            
            # Get column names
            columns = list(df.columns)
            self.logger.info(f"Found {len(columns)} columns in file: {columns}")
            
            return columns, None
            
        except ImportError:
            return None, "pandas library not available. Install with: pip install pandas openpyxl"
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            return None, f"Error reading file: {str(e)}"
    
    def extract_column_data(self, file_path, column_name):
        """
        Extract data from a specific column in the CSV file.
        
        Returns:
            list: Non-empty values from the column
        """
        try:
            import pandas as pd
            import os
            
            file_ext = os.path.splitext(file_path)[1].lower()
            self.logger.info(f"Reading CSV file to extract column data: {file_path}")
            
            if file_ext == '.csv':
                # Try multiple encodings for CSV files
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        self.logger.info(f"Successfully read CSV with encoding: {encoding}")
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                
                if df is None:
                    raise ValueError("Could not read CSV file with any standard encoding")
                    
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Extract non-empty values from the selected column
            if column_name in df.columns:
                # Get non-null, non-empty values and convert to strings
                column_values = df[column_name].dropna().astype(str).str.strip()
                # Filter out empty strings after stripping
                non_empty_values = column_values[column_values != ''].tolist()
                
                self.logger.info(f"Extracted {len(non_empty_values)} non-empty values from column '{column_name}'")
                return non_empty_values
            else:
                self.logger.error(f"Column '{column_name}' not found in CSV file")
                return []
                
        except ImportError:
            self.logger.error("Pandas library not available for reading CSV data")
            return []
        except Exception as ex:
            self.logger.error(f"Error extracting data from column '{column_name}': {str(ex)}")
            return []
    
    def update_csv_display(self):
        """Update the CSV file display with current session data."""
        if not self.csv_file_display:
            return
        
        colors = self.get_theme_colors()
        
        # Get session data
        current_csv_file = self.page.session.get("selected_csv_file")
        current_csv_columns = self.page.session.get("csv_columns")
        current_selected_column = self.page.session.get("selected_csv_column")
        current_csv_error = self.page.session.get("csv_read_error")
        search_directory = self.page.session.get("search_directory")
        
        # Update container visibility
        self.file_selection_container.visible = True
        self.columns_display_container.visible = bool(current_csv_file and (current_csv_columns or current_csv_error))
        self.results_display_container.visible = bool(current_selected_column)
        self.search_container.visible = bool(current_selected_column)
        
        # Clear current display
        self.csv_file_display.controls.clear()
        
        # === STEP 1: File Selection ===
        file_selection_content = ft.Column([
            ft.Text("Step 1: Select CSV File", size=18, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.ElevatedButton("Select File", icon=ft.Icons.FILE_UPLOAD, on_click=self.open_csv_file_picker),
        ], spacing=10)
        
        if current_csv_file:
            import os
            filename = os.path.basename(current_csv_file)
            file_selection_content.controls.extend([
                ft.Container(height=5),
                ft.Text(f"✅ Selected: {filename}", size=14, color=colors['primary_text']),
                ft.Text(f"Path: {current_csv_file}", size=12, color=colors['secondary_text']),
                ft.Row([
                    ft.ElevatedButton("Clear Selection", on_click=self.on_clear_csv_selection, scale=0.8),
                    ft.ElevatedButton("Reload File", on_click=self.reload_csv_file, scale=0.8)
                ], alignment=ft.MainAxisAlignment.CENTER)
            ])
        
        self.file_selection_container.content = ft.ExpansionTile(
            title=ft.Text("File Selection", weight=ft.FontWeight.BOLD),
            subtitle=ft.Text("Choose your CSV/Excel file"),
            leading=ft.Icon(ft.Icons.FILE_UPLOAD),
            initially_expanded=not bool(current_csv_file),
            controls=[file_selection_content]
        )
        
        # === STEP 2: Column Selection ===
        if current_csv_file:
            columns_content = ft.Column([], spacing=10)
            
            if current_csv_error:
                columns_content.controls.extend([
                    ft.Text("❌ Error reading file:", size=14, weight=ft.FontWeight.BOLD, color=colors['error']),
                    ft.Text(current_csv_error, size=12, color=colors['secondary_text'])
                ])
            elif current_csv_columns and len(current_csv_columns) > 0:
                columns_content.controls.extend([
                    ft.Text("Step 2: Select Column", size=18, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                    ft.Text(f"Found {len(current_csv_columns)} columns:", size=14, color=colors['primary_text']),
                    ft.Container(height=5)
                ])
                
                # Show column names
                if len(current_csv_columns) > 10:
                    column_list = ft.Column([
                        ft.Text(f"{i}. {col}", size=12, color=colors['secondary_text'])
                        for i, col in enumerate(current_csv_columns, 1)
                    ], spacing=2, scroll=ft.ScrollMode.AUTO, height=150)
                    
                    columns_content.controls.append(
                        ft.Container(
                            content=column_list,
                            border=ft.border.all(1, colors['border']),
                            border_radius=5,
                            padding=10
                        )
                    )
                else:
                    for i, col in enumerate(current_csv_columns, 1):
                        columns_content.controls.append(
                            ft.Text(f"{i}. {col}", size=12, color=colors['secondary_text'])
                        )
                
                columns_content.controls.extend([
                    ft.Container(height=10),
                    ft.Text("Select column containing filenames:", size=14, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                    ft.Dropdown(
                        label="Choose filename column",
                        value=current_selected_column if current_selected_column else "",
                        options=[ft.dropdown.Option(col) for col in current_csv_columns],
                        on_change=self.on_column_selection_change,
                        width=300
                    )
                ])
            else:
                columns_content.controls.extend([
                    ft.Text("⚠️ No columns detected in file", size=14, weight=ft.FontWeight.BOLD, color=colors['error']),
                    ft.Text("The file might be empty or in an unsupported format.", size=12, color=colors['secondary_text'])
                ])
            
            self.columns_display_container.content = ft.ExpansionTile(
                title=ft.Text("Column Selection", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text("Choose the column containing filenames"),
                leading=ft.Icon(ft.Icons.VIEW_COLUMN),
                initially_expanded=bool(current_csv_columns and not current_selected_column),
                controls=[columns_content]
            )
        
        # === STEP 3: Processing Results ===
        if current_selected_column:
            selected_files = self.page.session.get("selected_file_paths") or []
            extracted_filename_count = len(selected_files)
            
            results_content = ft.Column([
                ft.Text("Step 3: Processing Results", size=18, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                ft.Text(f"✅ Selected column: {current_selected_column}", size=14, color=colors['primary_text']),
                ft.Text(f"📁 Extracted {extracted_filename_count} filenames from this column", size=12, color=colors['secondary_text']),
            ], spacing=10)
            
            self.results_display_container.content = ft.ExpansionTile(
                title=ft.Text("Processing Results", weight=ft.FontWeight.BOLD),
                subtitle=ft.Markdown(f"{extracted_filename_count} potential filenames extracted from the `{current_selected_column}` column"),
                leading=ft.Icon(ft.Icons.CHECK_CIRCLE),
                initially_expanded=True,
                controls=[results_content]
            )
            
            # === STEP 4: Fuzzy Search ===
            # Check if files have been matched (full paths vs just filenames)
            has_full_paths = any(os.path.isabs(f) for f in selected_files if f)
            matched_file_count = len([f for f in selected_files if f and os.path.isabs(f)]) if has_full_paths else 0
            
            search_content = ft.Column([
                ft.Text("Step 4: Fuzzy Search", size=18, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                ft.Text("Match filenames to actual files in a directory:", size=14, color=colors['secondary_text']),
                ft.Container(height=5),
                ft.Text(f"Search directory: {search_directory or 'Not selected'}", 
                       size=12, color=colors['secondary_text'], italic=True),
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton(
                        "Select Search Directory",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=self.open_search_dir_picker
                    ),
                    ft.ElevatedButton(
                        "Start Fuzzy Search",
                        icon=ft.Icons.SEARCH,
                        on_click=self.do_fuzzy_search,
                        disabled=not bool(search_directory)
                    ) if selected_files else ft.Container(),
                ], spacing=10),
                ft.Container(height=10),
                ft.Text("Match filenames to actual files to prepare for subsequent processing.",
                       size=11, color=colors['secondary_text'], italic=True)
            ], spacing=5)
            
            # Add fuzzy search status indicator and matched files list
            if has_full_paths:
                search_content.controls.extend([
                    ft.Container(height=10),
                    ft.Text(f"✅ {matched_file_count} of {extracted_filename_count} files matched via fuzzy search", 
                           size=12, color=ft.Colors.GREEN_600, weight=ft.FontWeight.BOLD)
                ])
                
                # Show matched file paths
                if selected_files and len(selected_files) > 0:
                    search_content.controls.extend([
                        ft.Container(height=10),
                        ft.Text("Matched file paths:", 
                               size=12, weight=ft.FontWeight.BOLD, color=colors['primary_text'])
                    ])
                    
                    # Display matched files with full paths
                    display_items = []
                    for i, filepath in enumerate(selected_files):
                        if os.path.isabs(filepath):
                            display_text = f"{i+1}. {os.path.basename(filepath)} → {filepath}"
                        else:
                            display_text = f"{i+1}. {filepath}"
                        display_items.append(ft.Text(display_text, size=11, color=colors['secondary_text']))
                    
                    filename_list = ft.ListView(
                        display_items,
                        spacing=2, 
                        height=min(200, len(selected_files) * 20 + 20)
                    )
                    
                    search_content.controls.append(
                        ft.Container(
                            content=filename_list,
                            border=ft.border.all(1, colors['border']),
                            border_radius=5,
                            padding=10,
                            margin=ft.margin.symmetric(vertical=5)
                        )
                    )
            else:
                search_content.controls.append(
                    ft.Text("⚠️ Files not yet matched", 
                           size=12, color=ft.Colors.ORANGE_600, weight=ft.FontWeight.BOLD)
                )
            
            self.search_container.content = ft.ExpansionTile(
                title=ft.Text("Fuzzy Search", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text("Match filenames to actual files"),
                leading=ft.Icon(ft.Icons.SEARCH),
                initially_expanded=True,
                controls=[search_content]
            )
        
        # Add all containers to display
        self.csv_file_display.controls.extend([
            self.file_selection_container,
            self.columns_display_container,
            self.results_display_container,
            self.search_container
        ])
        
        self.page.update()
    
    def open_csv_file_picker(self, e):
        """Open the CSV file picker."""
        last_directory = self.load_last_directory()
        
        if last_directory and os.path.exists(last_directory):
            self.logger.info(f"Using last directory: {last_directory}")
            self.csv_file_picker.pick_files(
                dialog_title="Select CSV or Excel File",
                allow_multiple=False,
                allowed_extensions=["csv", "xlsx", "xls"],
                initial_directory=last_directory
            )
        else:
            self.csv_file_picker.pick_files(
                dialog_title="Select CSV or Excel File",
                allow_multiple=False,
                allowed_extensions=["csv", "xlsx", "xls"]
            )
    
    def on_csv_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle CSV file selection."""
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            self.page.session.set("selected_csv_file", file_path)
            self.logger.info(f"Selected CSV file: {file_path}")
            
            # Store directory
            import os
            directory = os.path.dirname(file_path)
            self.save_last_directory(directory)
            
            # Read columns
            columns, error = self.read_csv_file(file_path)
            
            if columns:
                self.page.session.set("csv_columns", columns)
                self.page.session.set("csv_read_error", None)
                self.logger.info(f"Successfully read {len(columns)} columns")
            else:
                self.page.session.set("csv_columns", None)
                self.page.session.set("csv_read_error", error)
                self.logger.error(f"Failed to read CSV: {error}")
            
            # Clear previous selections
            self.page.session.set("selected_csv_column", None)
            self.page.session.set("selected_file_paths", [])
            
            self.update_csv_display()
        else:
            self.logger.info("No CSV file selected")
    
    def on_clear_csv_selection(self, e):
        """Clear CSV selection."""
        self.page.session.set("selected_csv_file", None)
        self.page.session.set("csv_columns", None)
        self.page.session.set("selected_csv_column", None)
        self.page.session.set("csv_read_error", None)
        self.page.session.set("selected_file_paths", [])
        self.page.session.set("search_directory", None)
        self.logger.info("Cleared CSV selection")
        self.update_csv_display()
    
    def reload_csv_file(self, e):
        """Reload the current CSV file."""
        current_csv_file = self.page.session.get("selected_csv_file")
        if current_csv_file:
            self.logger.info(f"Reloading CSV file: {current_csv_file}")
            columns, error = self.read_csv_file(current_csv_file)
            
            if columns:
                self.page.session.set("csv_columns", columns)
                self.page.session.set("csv_read_error", None)
            else:
                self.page.session.set("csv_columns", None)
                self.page.session.set("csv_read_error", error)
            
            self.update_csv_display()
    
    def on_column_selection_change(self, e):
        """Handle column selection."""
        selected_col = e.control.value
        self.page.session.set("selected_csv_column", selected_col)
        self.logger.info(f"Selected column: {selected_col}")
        
        if selected_col:
            current_csv_file = self.page.session.get("selected_csv_file")
            if current_csv_file:
                # Extract data from column
                column_data = self.extract_column_data(current_csv_file, selected_col)
                self.page.session.set("selected_file_paths", column_data)
                self.logger.info(f"Extracted {len(column_data)} filenames")
        else:
            self.page.session.set("selected_file_paths", [])
        
        self.update_csv_display()
    
    def open_search_dir_picker(self, e):
        """Open directory picker for fuzzy search."""
        self.search_dir_picker.get_directory_path(
            dialog_title="Select Directory for Fuzzy Search"
        )
    
    def on_search_dir_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle search directory selection."""
        if e.path:
            self.page.session.set("search_directory", e.path)
            self.logger.info(f"Selected search directory: {e.path}")
            self.update_csv_display()
    
    def do_fuzzy_search(self, e):
        """Perform fuzzy search using utils.perform_fuzzy_search_batch."""
        search_dir = self.page.session.get("search_directory")
        selected_files = self.page.session.get("selected_file_paths") or []
        
        if not search_dir or not selected_files:
            self.logger.error("Search directory or files not available")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Please select both a search directory and ensure files are extracted from CSV"),
                bgcolor=ft.Colors.RED_400
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        self.logger.info(f"Starting fuzzy search in {search_dir} for {len(selected_files)} files")
        
        # Get theme colors
        colors = self.get_theme_colors()
        
        # Create progress display
        progress_text = ft.Text("Initializing search...", size=14, color=colors['primary_text'])
        progress_bar = ft.ProgressBar(width=400, value=0)
        cancel_button = ft.ElevatedButton(
            "Cancel Search",
            icon=ft.Icons.CANCEL,
            on_click=lambda _: self.page.session.set("cancel_search", True),
            bgcolor=ft.Colors.RED_400
        )
        
        # Create progress dialog
        progress_dialog = ft.AlertDialog(
            title=ft.Text("Fuzzy Search in Progress"),
            content=ft.Column([
                progress_text,
                progress_bar,
                ft.Container(height=10),
                cancel_button
            ], tight=True, height=150),
            modal=True
        )
        
        # Show dialog
        self.page.overlay.append(progress_dialog)
        progress_dialog.open = True
        self.page.update()
        
        # Reset cancel flag
        self.page.session.set("cancel_search", False)
        
        # Define progress callback
        def update_progress(progress):
            """Update progress bar and text"""
            try:
                files_done = int(progress * len(selected_files))
                progress_text.value = f"Search Progress: {files_done}/{len(selected_files)} files processed ({progress:.0%})"
                progress_bar.value = progress
                self.logger.info(f"Progress update: {files_done}/{len(selected_files)} files ({progress:.0%})")
                self.page.update()
            except Exception as e:
                self.logger.error(f"Error updating progress: {str(e)}")
        
        # Define cancel check
        def check_cancel():
            """Check if search should be cancelled"""
            cancel = self.page.session.get("cancel_search")
            return cancel if cancel is not None else False
        
        try:
            # Perform the fuzzy search with progress tracking and cancellation support
            results = utils.perform_fuzzy_search_batch(
                search_dir, 
                selected_files,
                threshold=90,
                progress_callback=update_progress,
                cancel_check=check_cancel
            )
            
            # Close progress dialog
            progress_dialog.open = False
            self.page.update()
            
            # If search was cancelled
            if results is None:
                self.logger.info("Fuzzy search was cancelled by user")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Search cancelled by user"),
                    bgcolor=ft.Colors.ORANGE_400
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Process results and update session with matched paths
            matched_paths = []
            matches_found = 0
            
            for filename in selected_files:
                match_path, ratio = results.get(filename, (None, 0))
                if match_path and ratio >= 90:
                    matched_paths.append(match_path)
                    matches_found += 1
                    self.logger.info(f"Found match for '{filename}': {match_path} ({ratio}% match)")
                else:
                    matched_paths.append(None)
                    self.logger.info(f"No match found for '{filename}' meeting 90% threshold")
            
            # Update session with matched paths (replaces the original filenames)
            self.page.session.set("selected_file_paths", [p for p in matched_paths if p is not None])
            
            # Log completion
            self.logger.info(f"Fuzzy search completed. Found {matches_found} matches out of {len(selected_files)} files")
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Search Complete: Found {matches_found} matches out of {len(selected_files)} files"),
                bgcolor=ft.Colors.GREEN_400
            )
            self.page.snack_bar.open = True
            
            # Refresh the display to show updated results
            self.update_csv_display()
            
        except Exception as e:
            # Close progress dialog on error
            progress_dialog.open = False
            self.page.update()
            
            error_msg = f"Error during search: {str(e)}"
            self.logger.error(f"Error during fuzzy search: {str(e)}")
            
            # Show error in snackbar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(error_msg),
                bgcolor=ft.Colors.RED_400
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def render(self) -> ft.Column:
        """
        Render the CSV selector view with 4-step workflow.
        
        Returns:
            ft.Column: The CSV page layout
        """
        self.on_view_enter()
        
        # Get theme colors
        colors = self.get_theme_colors()
        
        # Create file pickers
        self.csv_file_picker = ft.FilePicker(on_result=self.on_csv_file_picker_result)
        self.search_dir_picker = ft.FilePicker(on_result=self.on_search_dir_picker_result)
        self.page.overlay.append(self.csv_file_picker)
        self.page.overlay.append(self.search_dir_picker)
        
        # Initialize containers
        self.file_selection_container = ft.Container(visible=False)
        self.columns_display_container = ft.Container(visible=False)
        self.results_display_container = ft.Container(visible=False)
        self.search_container = ft.Container(visible=False)
        
        # Create main display
        self.csv_file_display = ft.Column([], spacing=10)
        
        # Initial update
        self.update_csv_display()
        
        return ft.Column([
            ft.Row([
                ft.Text(f"File Selector - {self.selector_type}", size=24, weight=ft.FontWeight.BOLD),
                self.create_log_button("Show Logs", ft.Icons.LIST_ALT)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=15, color=colors['divider']),
            ft.Text("Process CSV or Excel files step by step", 
                   size=16, color=colors['primary_text']),
            ft.Text("Follow the collapsible sections below to complete your file selection", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            self.csv_file_display,
        ], alignment="start", expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
