"""
Storage view for Azure storage operations.
"""
import os
import json
import flet as ft
from azure.storage.blob import BlobServiceClient

import utils
from .base_view import BaseView


class StorageView(BaseView):
    
    def __init__(self, page: ft.Page):
        """Initialize the storage view."""
        super().__init__(page)
        self.upload_progress = ft.ProgressBar(width=400, visible=False)
        self.upload_status = ft.Text("", visible=False)
    
    def get_azure_base_url(self):
        """Get the Azure base URL from persistent settings."""
        try:
            with open("_data/persistent.json", "r", encoding="utf-8") as f:
                persistent_data = json.load(f)
            return persistent_data.get("azure_base_url", "")
        except Exception as e:
            self.logger.error(f"Failed to read Azure base URL: {e}")
            return ""
    
    def generate_upload_script(self, e):
        """Generate Alma S3 upload script and display it with copy buttons."""
        try:
            # Get the temp directory from session
            temp_dir = self.page.session.get("temp_directory")
            if not temp_dir:
                self.show_snack("No temporary directory found. Please select files first.", is_error=True)
                return
            
            # Get the temp CSV filename from session
            temp_csv_filename = self.page.session.get("temp_csv_filename")
            
            # Generate the script
            script_content = utils.generate_alma_s3_script(temp_dir, temp_csv_filename)
            
            # Save script to temp directory
            script_path = os.path.join(temp_dir, "upload_to_alma.sh")
            try:
                with open(script_path, "w") as f:
                    f.write(script_content)
                os.chmod(script_path, 0o755)  # Make executable
                self.logger.info(f"Generated upload script: {script_path}")
            except Exception as ex:
                self.logger.error(f"Failed to save script: {ex}")
                self.show_snack(f"Failed to save script: {ex}", is_error=True)
                return
            
            # Parse script into commands (lines starting with 'aws')
            lines = script_content.split('\n')
            commands = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('aws '):
                    commands.append(stripped)
            
            # Create display with copy buttons
            colors = self.get_theme_colors()
            
            command_controls = []
            for idx, cmd in enumerate(commands, 1):
                command_controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    cmd,
                                    size=11,
                                    font_family="Courier New",
                                    color=colors['code_text'],
                                    selectable=True
                                ),
                                expand=True,
                                padding=10,
                                bgcolor=colors['markdown_bg'],
                                border_radius=4,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.COPY,
                                tooltip=f"Copy command {idx}",
                                on_click=lambda e, command=cmd: self.copy_to_clipboard(e, command)
                            )
                        ], spacing=5),
                        margin=ft.margin.only(bottom=10)
                    )
                )
            
            # Create dialog to show the script
            dialog = ft.AlertDialog(
                title=ft.Text("Alma S3 Upload Script Generated", weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            f"Script saved to: {script_path}",
                            size=12,
                            color=ft.Colors.GREEN_700,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Divider(),
                        ft.Text(
                            "AWS Commands:",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=colors['primary_text']
                        ),
                        ft.Text(
                            "Click the copy button to copy each command to clipboard",
                            size=11,
                            italic=True,
                            color=colors['secondary_text']
                        ),
                        ft.Container(height=10),
                        ft.Column(
                            command_controls,
                            scroll=ft.ScrollMode.AUTO,
                            height=300
                        ),
                    ], spacing=5),
                    width=700,
                ),
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self.close_dialog(dialog))
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
            
        except Exception as ex:
            self.logger.error(f"Error generating upload script: {ex}")
            self.show_snack(f"Error: {ex}", is_error=True)
    
    def copy_to_clipboard(self, e, text):
        """Copy text to clipboard."""
        self.page.set_clipboard(text)
        self.show_snack("✓ Copied to clipboard", is_error=False)
    
    def close_dialog(self, dialog):
        """Close the dialog."""
        dialog.open = False
        self.page.update()
    
    def upload_files_to_azure(self, e):
        """Upload files from temporary /OBJS directory to Azure Blob storage."""
        try:
            # Get the Azure base URL
            azure_base_url = self.get_azure_base_url()
            if not azure_base_url:
                self.upload_status.value = "❌ Azure base URL not configured"
                self.upload_status.color = ft.Colors.RED
                self.upload_status.visible = True
                self.page.update()
                return
            
            # Get the temp directory from session
            temp_dir = self.page.session.get("temp_directory")
            if not temp_dir:
                self.upload_status.value = "❌ No temporary directory found. Please select files first."
                self.upload_status.color = ft.Colors.RED
                self.upload_status.visible = True
                self.page.update()
                return
            
            # Check for OBJS directory
            objs_dir = os.path.join(temp_dir, "OBJS")
            if not os.path.exists(objs_dir):
                self.upload_status.value = f"❌ No OBJS directory found in {temp_dir}"
                self.upload_status.color = ft.Colors.RED
                self.upload_status.visible = True
                self.page.update()
                return
            
            # Show progress bar
            self.upload_progress.visible = True
            self.upload_status.value = "🔄 Initializing Azure connection..."
            self.upload_status.color = ft.Colors.BLUE
            self.upload_status.visible = True
            self.page.update()
            
            # Initialize Azure Blob Service Client using connection string
            try:
                # Get connection string from environment variable
                connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                
                if not connection_string:
                    self.upload_status.value = "❌ Azure Storage connection string not configured"
                    self.upload_status.value += "\n\n💡 Please set AZURE_STORAGE_CONNECTION_STRING in .env file"
                    self.upload_status.color = ft.Colors.RED
                    self.upload_progress.visible = False
                    self.logger.error("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
                    self.page.update()
                    return
                
                # Create BlobServiceClient from connection string
                blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                
            except Exception as e:
                error_msg = str(e)
                self.upload_status.value = f"❌ Failed to connect to Azure Storage"
                self.upload_status.value += f"\n\nError: {error_msg}"
                self.upload_status.value += "\n\n💡 Please check your AZURE_STORAGE_CONNECTION_STRING in .env file"
                self.upload_status.color = ft.Colors.RED
                self.upload_progress.visible = False
                self.logger.error(f"Azure Storage connection failed: {error_msg}")
                self.page.update()
                return
            
            # Get list of files to upload
            files_to_upload = []
            for root, dirs, files in os.walk(objs_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create relative path for blob name
                    relative_path = os.path.relpath(file_path, objs_dir)
                    files_to_upload.append((file_path, relative_path))
            
            if not files_to_upload:
                self.upload_status.value = "⚠️ No files found in OBJS directory"
                self.upload_status.color = ft.Colors.ORANGE
                self.upload_progress.visible = False
                self.page.update()
                return
            
            # Upload files
            uploaded_count = 0
            total_files = len(files_to_upload)
            
            for i, (local_path, blob_name) in enumerate(files_to_upload):
                try:
                    self.upload_status.value = f"🔄 Uploading {blob_name} ({i+1}/{total_files})"
                    self.upload_progress.value = i / total_files
                    self.page.update()
                    
                    # Determine container based on file path
                    if "thumbs/" in blob_name or "/TN/" in local_path:
                        container_name = "thumbs"
                        # Remove 'thumbs/' prefix if present
                        blob_path = blob_name.replace("thumbs/", "")
                    elif "smalls/" in blob_name or "/SMALL/" in local_path:
                        container_name = "smalls"
                        # Remove 'smalls/' prefix if present
                        blob_path = blob_name.replace("smalls/", "")
                    else:
                        container_name = "objs"
                        # Remove 'objs/' prefix if present
                        blob_path = blob_name.replace("objs/", "")
                    
                    # Create blob client
                    blob_client = blob_service_client.get_blob_client(
                        container=container_name, 
                        blob=blob_path
                    )
                    
                    # Check if blob already exists
                    if blob_client.exists():
                        self.logger.info(f"Blob '{blob_path}' already exists in container '{container_name}'. Skipping.")
                        uploaded_count += 1  # Count as uploaded (already there)
                    else:
                        # Upload the file
                        with open(local_path, "rb") as data:
                            blob_client.upload_blob(data)
                        self.logger.info(f"Successfully uploaded '{blob_path}' to container '{container_name}'")
                        uploaded_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to upload {blob_name}: {e}")
                    continue
            
            # Update final status
            self.upload_progress.value = 1.0
            if uploaded_count == total_files:
                self.upload_status.value = f"✅ Successfully uploaded {uploaded_count} files to Azure"
                self.upload_status.color = ft.Colors.GREEN
            else:
                self.upload_status.value = f"⚠️ Uploaded {uploaded_count} of {total_files} files (some may have been skipped)"
                self.upload_status.color = ft.Colors.ORANGE
            
            self.page.update()
            
        except Exception as e:
            self.logger.error(f"Upload process failed: {e}")
            self.upload_status.value = f"❌ Upload failed: {str(e)}"
            self.upload_status.color = ft.Colors.RED
            self.upload_progress.visible = False
            self.page.update()
    
    def render(self) -> ft.Column:
        """
        Render the storage page content based on selected mode.
        
        Returns:
            ft.Column: The storage page content
        """
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # Get selected mode
        try:
            with open("_data/persistent.json", "r", encoding="utf-8") as f:
                persistent_data = json.load(f)
            selected_mode = persistent_data.get("selected_mode", "Alma")
        except Exception as e:
            self.logger.error(f"Failed to read selected mode: {e}")
            selected_mode = "Alma"
        
        if selected_mode == "Alma":
            # For Alma mode, show markdown content and upload script button
            alma_content = utils.read_markdown("_data/alma_storage.md")
            
            return ft.Column(
                controls=[
                    *self.create_page_header("Storage", include_log_button=True),
                    # Add button for generating upload script
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "Alma AWS S3 Upload",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=colors['primary_text']
                            ),
                            ft.Text(
                                "Generate a bash script to upload files to Alma's AWS S3 storage",
                                size=13,
                                color=colors['secondary_text']
                            ),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    text="Generate Upload Script",
                                    icon=ft.Icons.TERMINAL,
                                    on_click=self.generate_upload_script,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.GREEN_700
                                    )
                                ),
                                margin=ft.margin.only(top=10, bottom=5)
                            ),
                        ], spacing=5),
                        bgcolor=colors['container_bg'],
                        border=ft.border.all(1, colors['border']),
                        border_radius=8,
                        padding=20,
                        margin=ft.margin.only(top=10, bottom=10)
                    ),
                    # Markdown instructions
                    ft.Container(
                        content=ft.Markdown(
                            alma_content,
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            on_tap_link=lambda e: self.page.launch_url(e.data),
                            md_style_sheet=self.get_markdown_style()
                        ),
                        bgcolor=colors['container_bg'],
                        border=ft.border.all(1, colors['border']),
                        border_radius=8,
                        padding=20,
                        margin=ft.margin.only(top=10)
                    )
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            )
        else:
            # For Storage and CollectionBuilder modes, show Azure upload controls
            azure_url = self.get_azure_base_url()
            
            upload_button = ft.ElevatedButton(
                text="Upload Files to Azure",
                icon=ft.Icons.CLOUD_UPLOAD,
                on_click=self.upload_files_to_azure,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE
                )
            )
            
            upload_controls = ft.Column(
                controls=[
                    ft.Text(
                        "Azure Storage Upload",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=colors['primary_text']
                    ),
                    ft.Divider(height=1, color=colors['divider']),
                    ft.Text(
                        f"Azure Base URL: {azure_url or 'Not configured'}",
                        size=14,
                        color=colors['secondary_text']
                    ),
                    ft.Text(
                        "This will upload files from the temporary /OBJS directory to Azure Blob storage.",
                        size=14,
                        color=colors['secondary_text']
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "📋 Prerequisites:",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=colors['primary_text']
                            ),
                            ft.Text(
                                "• Files must be selected first (via File Selector page)",
                                size=12,
                                color=colors['secondary_text']
                            ),
                            ft.Text(
                                "• Azure Storage connection string must be configured in .env file",
                                size=12,
                                color=colors['secondary_text']
                            ),
                            ft.Text(
                                "  AZURE_STORAGE_CONNECTION_STRING=\"...\"",
                                size=11,
                                color=colors['code_text'],
                                font_family="monospace"
                            ),
                        ], spacing=4),
                        bgcolor=colors['markdown_bg'],
                        border=ft.border.all(1, colors['border']),
                        border_radius=4,
                        padding=10,
                        margin=ft.margin.only(top=10, bottom=10)
                    ),
                    ft.Container(
                        content=upload_button,
                        margin=ft.margin.only(top=20, bottom=10)
                    ),
                    self.upload_progress,
                    self.upload_status
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.START
            )
            
            return ft.Column(
                controls=[
                    *self.create_page_header("Storage", include_log_button=True),
                    ft.Container(
                        content=upload_controls,
                        bgcolor=colors['container_bg'],
                        border=ft.border.all(1, colors['border']),
                        border_radius=8,
                        padding=20,
                        margin=ft.margin.only(top=10)
                    )
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            )