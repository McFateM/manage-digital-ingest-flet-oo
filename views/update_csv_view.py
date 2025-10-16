"""
Update CSV View for Manage Digital Ingest Application

This module contains the UpdateCSVView class for updating CSV files with
matched filenames and metadata.
"""

import flet as ft
from views.base_view import BaseView
import os
import shutil
import pandas as pd
from datetime import datetime


class UpdateCSVView(BaseView):
    """
    Update CSV view class for modifying CSV files with matched file data.
    Only enabled when CSV file selection is active.
    """
    
    def __init__(self, page: ft.Page):
        """Initialize the update CSV view."""
        super().__init__(page)
        self.csv_data = None
        self.csv_path = None
        self.temp_csv_path = None
        self.selected_column = None
        self.data_table = None
    
    def sanitize_filename(self, filename):
        """
        Sanitize a filename by replacing spaces and special characters.
        
        Args:
            filename: The filename to sanitize
            
        Returns:
            str: Sanitized filename
        """
        import re
        # Replace spaces with underscores
        sanitized = filename.replace(' ', '_')
        # Remove or replace other problematic characters
        sanitized = re.sub(r'[^\w\-_\.]', '_', sanitized)
        return sanitized
    
    def copy_csv_to_temp(self, source_path):
        """
        Copy CSV file to temporary directory with timestamp.
        
        Args:
            source_path: Path to the source CSV file
            
        Returns:
            str: Path to the copied CSV file
        """
        try:
            # Get temp directory from session
            temp_dir = self.page.session.get("temp_directory")
            if not temp_dir:
                # Create a new temp directory if one doesn't exist
                temp_dir = os.path.join("storage", "temp", f"csv_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                os.makedirs(temp_dir, exist_ok=True)
                self.page.session.set("temp_directory", temp_dir)
            
            # Get the base filename and sanitize it
            base_name = os.path.basename(source_path)
            name, ext = os.path.splitext(base_name)
            sanitized_name = self.sanitize_filename(name)
            
            # Add timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{sanitized_name}_{timestamp}{ext}"
            
            # Create the destination path
            dest_path = os.path.join(temp_dir, new_filename)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            self.logger.info(f"Copied CSV file to: {dest_path}")
            
            return dest_path
            
        except Exception as e:
            self.logger.error(f"Error copying CSV to temp: {e}")
            return None
    
    def load_csv_data(self, csv_path):
        """
        Load CSV data into a pandas DataFrame.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try multiple encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    self.csv_data = pd.read_csv(csv_path, encoding=encoding)
                    self.csv_path = csv_path
                    self.logger.info(f"Loaded CSV with {len(self.csv_data)} rows and {len(self.csv_data.columns)} columns")
                    return True
                except UnicodeDecodeError:
                    continue
            
            self.logger.error("Failed to load CSV with any supported encoding")
            return False
            
        except Exception as e:
            self.logger.error(f"Error loading CSV: {e}")
            return False
    
    def save_csv_data(self):
        """
        Save the current CSV data back to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.csv_data is not None and self.temp_csv_path:
                self.csv_data.to_csv(self.temp_csv_path, index=False, encoding='utf-8')
                self.logger.info(f"Saved CSV data to: {self.temp_csv_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
            return False
    
    def update_cell(self, row_index, column_name, new_value):
        """
        Update a specific cell in the CSV data.
        
        Args:
            row_index: The row index (0-based)
            column_name: The column name
            new_value: The new value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.csv_data is not None:
                self.csv_data.at[row_index, column_name] = new_value
                self.logger.info(f"Updated cell [{row_index}, {column_name}] = {new_value}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating cell: {e}")
            return False
    
    def apply_matched_files(self, e):
        """
        Apply matched filenames to the CSV file.
        """
        try:
            # Get matched files from session
            selected_files = self.page.session.get("selected_file_paths") or []
            original_filenames = self.page.session.get("original_filenames") or []
            
            if not selected_files or not self.csv_data is not None:
                self.logger.warning("No matched files or CSV data available")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("No matched files available to apply"),
                    bgcolor=ft.Colors.ORANGE_600
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Get the selected column name
            column_name = self.selected_column
            if not column_name:
                self.logger.warning("No column selected for updates")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please select a column to update"),
                    bgcolor=ft.Colors.ORANGE_600
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Update the CSV with matched filenames
            updates = 0
            for i, original_name in enumerate(original_filenames):
                if i < len(selected_files) and selected_files[i]:
                    # Find the row with this original filename
                    mask = self.csv_data[column_name] == original_name
                    if mask.any():
                        row_idx = self.csv_data[mask].index[0]
                        new_filename = os.path.basename(selected_files[i])
                        self.csv_data.at[row_idx, column_name] = new_filename
                        updates += 1
            
            if updates > 0:
                self.save_csv_data()
                self.logger.info(f"Applied {updates} matched filenames to CSV")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Updated {updates} filenames in CSV"),
                    bgcolor=ft.Colors.GREEN_600
                )
                self.page.snack_bar.open = True
                self.render_data_table()
                self.page.update()
            else:
                self.logger.warning("No matching rows found to update")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("No matching rows found to update"),
                    bgcolor=ft.Colors.ORANGE_600
                )
                self.page.snack_bar.open = True
                self.page.update()
                
        except Exception as e:
            self.logger.error(f"Error applying matched files: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                bgcolor=ft.Colors.RED_600
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def render_data_table(self):
        """
        Render the CSV data as a DataTable.
        
        Returns:
            ft.Container: Container with the data table
        """
        colors = self.get_theme_colors()
        
        if self.csv_data is None:
            return ft.Container(
                content=ft.Text("No CSV data loaded", color=colors['secondary_text']),
                padding=20
            )
        
        # Limit to first 50 rows for display
        display_data = self.csv_data.head(50)
        
        # Create columns
        columns = [
            ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD, size=12))
            for col in display_data.columns
        ]
        
        # Create rows
        rows = []
        for idx, row in display_data.iterrows():
            cells = [
                ft.DataCell(ft.Text(str(val), size=11))
                for val in row
            ]
            rows.append(ft.DataRow(cells=cells))
        
        table = ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, colors['border']),
            border_radius=10,
            horizontal_lines=ft.BorderSide(1, colors['border']),
            heading_row_color=ft.Colors.GREY_200,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(f"Showing first {len(display_data)} of {len(self.csv_data)} rows",
                       size=12, italic=True, color=colors['secondary_text']),
                ft.Container(
                    content=table,
                    border=ft.border.all(1, colors['border']),
                    border_radius=10,
                    padding=10,
                )
            ], spacing=10),
            expand=True
        )
    
    def render(self) -> ft.Column:
        """
        Render the Update CSV view content.
        
        Returns:
            ft.Column: The Update CSV page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # Check if CSV mode is selected
        file_option = self.page.session.get("selected_file_option")
        
        if file_option != "CSV":
            return ft.Column([
                *self.create_page_header("Update CSV"),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.WARNING_AMBER, size=64, color=ft.Colors.ORANGE_600),
                        ft.Container(height=20),
                        ft.Text(
                            "CSV Update is only available when CSV file selection is active.",
                            size=16,
                            color=colors['primary_text'],
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "Please go to Settings and select 'CSV' as your file selector option.",
                            size=14,
                            color=colors['secondary_text'],
                            text_align=ft.TextAlign.CENTER
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            ], alignment="start", expand=True, spacing=0)
        
        # Get CSV file path from session
        original_csv_path = self.page.session.get("csv_file_path")
        
        # Check if no CSV file is selected (FilePicker was used)
        if not original_csv_path:
            return ft.Column([
                *self.create_page_header("Update CSV"),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED_600),
                        ft.Container(height=20),
                        ft.Text(
                            "No CSV file selected.",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=colors['primary_text'],
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "Please select a CSV file in the File Selector view before using Update CSV.",
                            size=14,
                            color=colors['secondary_text'],
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "Note: FilePicker mode does not provide a CSV file to update.",
                            size=12,
                            italic=True,
                            color=colors['secondary_text'],
                            text_align=ft.TextAlign.CENTER
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            ], alignment="start", expand=True, spacing=0)
        
        # Automatically load CSV if not already loaded
        if self.csv_data is None and original_csv_path:
            # Copy to temp directory
            self.temp_csv_path = self.copy_csv_to_temp(original_csv_path)
            if self.temp_csv_path:
                # Load the CSV data
                if not self.load_csv_data(self.temp_csv_path):
                    self.logger.error("Failed to load CSV file")
            else:
                self.logger.error("Failed to copy CSV to temp directory")
        
        # Column selector dropdown
        column_selector = None
        if self.csv_data is not None:
            def on_column_change(e):
                self.selected_column = e.control.value
                self.logger.info(f"Selected column for updates: {self.selected_column}")
            
            column_selector = ft.Dropdown(
                label="Column to Update",
                hint_text="Select the column containing filenames",
                options=[ft.dropdown.Option(col) for col in self.csv_data.columns],
                value=self.selected_column,
                on_change=on_column_change,
                width=300
            )
        
        # Build the UI - Status information controls
        status_info_controls = []
        
        if original_csv_path:
            status_info_controls.extend([
                ft.Text(f"Source CSV: {os.path.basename(original_csv_path)}", 
                       size=14, weight=ft.FontWeight.BOLD, color=colors['container_text']),
                ft.Text(f"Path: {original_csv_path}", 
                       size=11, color=colors['container_text'], selectable=True),
            ])
        
        if self.temp_csv_path:
            if status_info_controls:
                status_info_controls.append(ft.Container(height=10))
            status_info_controls.extend([
                ft.Text(f"Working Copy: {os.path.basename(self.temp_csv_path)}", 
                       size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600),
                ft.Text(f"Path: {self.temp_csv_path}", 
                       size=11, color=colors['container_text'], selectable=True),
            ])
        
        content = [
            *self.create_page_header("Update CSV"),
        ]
        
        # Add status info container if we have any
        if status_info_controls:
            content.append(
                ft.Container(
                    content=ft.Column(status_info_controls, spacing=2),
                    padding=ft.padding.all(10),
                    border=ft.border.all(1, colors['border']),
                    border_radius=10,
                    bgcolor=colors['container_bg'],
                    margin=ft.margin.symmetric(vertical=5)
                )
            )
        
        # Action buttons
        button_row_controls = []
        
        if self.csv_data is not None:
            if column_selector:
                button_row_controls.append(column_selector)
            
            button_row_controls.extend([
                ft.ElevatedButton(
                    "Apply Matched Files",
                    icon=ft.Icons.UPDATE,
                    on_click=self.apply_matched_files
                ),
                ft.ElevatedButton(
                    "Save CSV",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e: self.save_csv_data() and self.logger.info("CSV saved")
                ),
            ])
        
        if button_row_controls:
            content.extend([
                ft.Row(button_row_controls, spacing=10, wrap=True, alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=5),
            ])
        
        # Data table section
        if self.csv_data is not None:
            content.extend([
                ft.Text("CSV Data:", size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                ft.Container(height=5),
                self.render_data_table()
            ])
        else:
            content.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                        ft.Container(height=10),
                        ft.Text(
                            "Failed to load CSV file.",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=colors['primary_text']
                        ),
                        ft.Container(height=5),
                        ft.Text(
                            "Please check the log for details.",
                            size=12,
                            color=colors['secondary_text']
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        
        return ft.Column(content, alignment="start", expand=True, spacing=0, scroll=ft.ScrollMode.AUTO)
