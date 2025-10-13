import flet as ft
import logging
import utils
import json
import os
import shutil
import tempfile
from subprocess import call
from logger import SnackBarHandler
from thumbnail import generate_thumbnail

# Optional imports for CSV processing
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

# Simple thumbnail generation function to replace missing thumbnail module
def generate_pdf_thumbnail(input_path, output_path, options):
    """
    Generate a thumbnail using ImageMagick convert command
    """
    try:
        width = options.get('width', 400)
        height = options.get('height', 400)
        quality = options.get('quality', 85)
        
        # Create the command
        cmd = f'magick convert "{input_path}" -resize {width}x{height} -quality {quality} "{output_path}"'
        
        # Execute the command
        return_code = call(cmd, shell=True)
        
        if return_code == 0:
            return True
        else:
            logging.error(f"Failed to generate thumbnail with command: {cmd}")
            return False
            
    except Exception as e:
        logging.error(f"Exception in generate_pdf_thumbnail: {str(e)}")
        return False

# --- LOGGER SETUP ------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
_snack_handler = SnackBarHandler()
_snack_handler.setLevel(logging.INFO)
logger.addHandler(_snack_handler)
# File logging: write messages to mdi.log in the repo root
_file_handler = logging.FileHandler("mdi.log")
_file_handler.setLevel(logging.INFO)
_file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_file_handler.setFormatter(_file_formatter)
logger.addHandler(_file_handler)

# Write an initial log entry
logger.info("Logger initialized - writing to mdi.log and SnackBarHandler attached")

# --- UNIVERSAL FUNCTIONS ------------------------------------------------------

# -------------------------------------------------------------------------------
# get_theme_colors()
# Purpose: Returns theme-appropriate color scheme based on current theme mode
# Parameters: page - Flet page object containing theme mode information
# Returns: Dictionary of color constants for UI theming
# -------------------------------------------------------------------------------
def get_theme_colors(page):
    """Get theme-appropriate colors based on current theme mode"""
    # Detect if we're in dark mode
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    
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
            'container_label': ft.Colors.GREY_300  # Light grey for labels/subtitles
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
            'container_label': ft.Colors.GREY_700  # Dark grey for labels/subtitles
        }

# --- ROUTE HANDLERS ------------------------------------------------------------

# -------------------------------------------------------------------------------
# home_view()
# Purpose: Renders the main home page with markdown content and app branding
# Parameters: page - Flet page object for rendering and theme management
# Returns: ft.Column containing the complete home page layout
# -------------------------------------------------------------------------------
def home_view(page):
    logger.info("Loaded Home page")

    # Get theme-appropriate colors
    colors = get_theme_colors(page)

    # Read markdown content from a file
    with open("_data/home.md", "r", encoding="utf-8") as file:
        markdown_text = file.read( )
    
    # Create a Markdown widget with the content
    md_widget = ft.Markdown(markdown_text, 
        md_style_sheet=ft.MarkdownStyleSheet(
            blockquote_text_style=ft.TextStyle(bgcolor=colors['markdown_bg'], color=colors['markdown_text'], size=16, weight=ft.FontWeight.BOLD),
            p_text_style=ft.TextStyle(color=colors['primary_text'], size=16, weight=ft.FontWeight.NORMAL),
            code_text_style=ft.TextStyle(color=colors['code_text'], size=16, weight=ft.FontWeight.BOLD),
        )
    )  

    # Read config from _data/config.json
    config = utils.read_config( )

    x = ft.Column(
        scroll = ft.ScrollMode.AUTO,
        spacing = 5,
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        controls = [
            ft.Container(
                height = 10,
            ),
            ft.Image(
                src = 'logo_for_subsplus.png',  # Updated to Grinnell College Libraries logo
                fit = ft.ImageFit.CONTAIN,
                width = 400,
                # height = 300
            ),
            ft.Text(f"🚀 powered by Flet {config['flet_version']} and Python version {config['python_version']} 🐍",color = colors['secondary_text']),
            ft.Text("Manage Digital Ingest: a Flet Multi-Page App", size=35),
            ft.Markdown("A Flet Python app for managing Grinnell College ingest of digital objects to Alma or CollectionBuilder"),
            ft.Divider(height=20, color=colors['divider']),
            md_widget,
            # ft.FilledButton("Go to Counter", on_click=data.go("/counter/test/0")),
            ft.Divider(height=20, color=colors['divider']),
            ft.Container(
                height = 80,
                content = ft.Markdown("**Thanks for choosing Flet!**"),
            ),
        ],
    )

    # page.session.set("last_status", "At Home page")

    return x


# -------------------------------------------------------------------------------
# about_view()
# Purpose: Renders the about page with markdown content and demo logging buttons
# Parameters: page - Flet page object for rendering and theme management
# Returns: ft.Column containing the about page layout with demo controls
# -------------------------------------------------------------------------------
def about_view(page):
    logger.info("Loaded About page")
    
    # Get theme-appropriate colors
    colors = get_theme_colors(page)
    
    # Demo buttons to exercise the SnackBar logger at different levels
    def _log_info(e):
        logger.info("Demo INFO from About page")

    def _log_warn(e):
        logger.warning("Demo WARNING from About page")

    def _log_error(e):
        logger.error("Demo ERROR from About page")

    # Generate session report
    session_data_found = False
    session_report = "## Current Session Data:\n\n"

    # Get all session keys and values
    for key in page.session.get_keys( ):
        session_report += f"**{key}**: `{page.session.get(key)}`\n\n"
        session_data_found = True
    
    if not session_data_found:
        session_report += "No session data found!\n\n"
    
    session_report += "---\n\n"
    session_report += "*This report shows all key-value pairs stored in `page.session`.*"

    # Create a Markdown widget with the session report
    md_widget = ft.Markdown(session_report, 
        md_style_sheet=ft.MarkdownStyleSheet(
            blockquote_text_style=ft.TextStyle(bgcolor=colors['markdown_bg'], color=colors['markdown_text'], size=16, weight=ft.FontWeight.BOLD),
            p_text_style=ft.TextStyle(color=colors['primary_text'], size=16, weight=ft.FontWeight.NORMAL),
            code_text_style=ft.TextStyle(color=colors['code_text'], size=16, weight=ft.FontWeight.BOLD),
        )
    )  

    # Read config from _data/config.json
    config = utils.read_config( )

    x = ft.Column(
        scroll = ft.ScrollMode.AUTO,
        spacing = 5,
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        controls = [
            ft.Container(
                height = 10,
            ),
            ft.Image(
                src = 'logo_for_subsplus.png',  # Updated to Grinnell College Libraries logo
                fit = ft.ImageFit.CONTAIN,
                width = 400,
                # height = 300
            ),
            ft.Text(f"🚀 powered by Flet {config['flet_version']} and Python version {config['python_version']} 🐍",color = colors['secondary_text']),
            ft.Text("Manage Digital Ingest: a Flet Multi-Page App", size=35),
            ft.Markdown("A Flet Python app for managing Grinnell College ingest of digital objects to Alma or CollectionBuilder"),
            ft.Divider(height=20, color=colors['divider']),
            md_widget,
            # ft.FilledButton("Go to Counter", on_click=data.go("/counter/test/0")),
            ft.Divider(height=20, color=colors['divider']),
            ft.Row([
                ft.ElevatedButton("Log INFO", on_click=_log_info),
                ft.ElevatedButton("Log WARNING", on_click=_log_warn),
                ft.ElevatedButton("Log ERROR", on_click=_log_error),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=20, color=colors['divider']),
            ft.Container(
                height = 80,
                content = ft.Markdown("**Thanks for choosing Flet!**"),
            ),
        ],
    )

    # page.session.set("last_status", "At Home page")

    return x

# -------------------------------------------------------------------------------
# exit_view()
# Purpose: Renders the exit page with application termination functionality
# Parameters: page - Flet page object for window control
# Returns: ft.Column containing exit page layout with close button
# -------------------------------------------------------------------------------
def exit_view(page):
    logger.info("Loaded Exit page")
    return ft.Column([
        ft.Text("Exit Page"),
        ft.ElevatedButton("Exit App", on_click=lambda e: page.window_close())
    ], alignment="center")

# -------------------------------------------------------------------------------
# settings_view()
# Purpose: Renders the settings page with configuration dropdowns and containers
# Parameters: page - Flet page object for session management and theme handling
# Returns: ft.Column containing settings page with theme and selector containers
# -------------------------------------------------------------------------------
def settings_view(page):
    logger.info("Loaded Settings page")
    
    # Get theme-appropriate colors
    colors = get_theme_colors(page)
    
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
    logger.info(f"Available mode options: {mode_options}")
    logger.info(f"Available file selector options: {file_selector_options}")
    logger.info(f"Available storage options: {azure_blob_options}")
    logger.info(f"Available collection options: {cb_collection_options}")
    
    # Log current session selections if they exist
    current_mode = page.session.get("selected_mode")
    current_file_option = page.session.get("selected_file_option")
    current_storage = page.session.get("selected_storage")
    current_collection = page.session.get("selected_collection")
    
    if current_mode:
        logger.info(f"Current mode selection: {current_mode}")
    if current_file_option:
        logger.info(f"Current file option selection: {current_file_option}")
    if current_storage:
        logger.info(f"Current storage selection: {current_storage}")
    if current_collection:
        logger.info(f"Current collection selection: {current_collection}")
    
    # Calculate collection enabled state
    is_collection_enabled = current_mode == "CollectionBuilder"
    logger.info(f"CB Collection Selector enabled: {is_collection_enabled}")
    
    # Create the collection dropdown reference
    collection_dropdown = ft.Dropdown(
        label="Select Collection",
        value=current_collection,
        options=[ft.dropdown.Option(collection) for collection in cb_collection_options],
        width=300,
        disabled=not is_collection_enabled
    )
    
    # Create the collection container reference
    collection_settings_container = ft.Container(
        content=ft.Column([
            ft.Text("CB Collection Selector", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
            collection_dropdown
        ]),
        padding=ft.padding.all(10),
        border=ft.border.all(1, colors['border']),
        border_radius=10,
        margin=ft.margin.symmetric(vertical=5),
        bgcolor=colors['container_bg'],
        opacity=1.0 if is_collection_enabled else 0.5
    )
    
    # Dropdown change handlers
    def on_mode_change(e):
        page.session.set("selected_mode", e.control.value)
        logger.info(f"Mode selected: {e.control.value}")
        log_all_current_selections()
        
        # Update collection selector state based on new mode
        new_is_enabled = e.control.value == "CollectionBuilder"
        collection_dropdown.disabled = not new_is_enabled
        collection_settings_container.opacity = 1.0 if new_is_enabled else 0.5
        page.update()
    
    def on_collection_change(e):
        page.session.set("selected_collection", e.control.value)
        logger.info(f"Collection selected: {e.control.value}")
        log_all_current_selections()
    
    # Set the collection dropdown's change handler
    collection_dropdown.on_change = on_collection_change
    
    def on_file_selector_change(e):
        page.session.set("selected_file_option", e.control.value)
        logger.info(f"File option selected: {e.control.value}")
        log_all_current_selections()
    
    def on_storage_change(e):
        page.session.set("selected_storage", e.control.value)
        logger.info(f"Storage selected: {e.control.value}")
        log_all_current_selections()
    
    def log_all_current_selections():
        """Log all current selections in one summary"""
        selections = {
            "mode": page.session.get("selected_mode"),
            "file_option": page.session.get("selected_file_option"),
            "storage": page.session.get("selected_storage"),
            "collection": page.session.get("selected_collection")
        }
        logger.info(f"Current selections summary: {selections}")
    
    # Theme selector handler
    def on_theme_change(e):
        """Handle theme mode changes"""
        theme_value = e.control.value
        if theme_value == "Light":
            page.theme_mode = ft.ThemeMode.LIGHT
        elif theme_value == "Dark":
            page.theme_mode = ft.ThemeMode.DARK
        
        page.update()
        logger.info(f"Theme changed to: {theme_value}")
        page.session.set("selected_theme", theme_value)
    
    # Get current theme for selector
    current_theme = "Light"  # Default to Light
    if page.theme_mode == ft.ThemeMode.DARK:
        current_theme = "Dark"
    
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
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        padding=ft.padding.all(10),
        border=ft.border.all(1, colors['border']),
        border_radius=10,
        margin=ft.margin.symmetric(vertical=5),
        bgcolor=colors['container_bg']
    )
    
    # Create containers with dropdowns
    mode_settings_container = ft.Container(
        content=ft.Column([
            ft.Text("Mode Selector", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
            ft.Dropdown(
                label="Select Mode",
                value=current_mode,
                options=[ft.dropdown.Option(mode) for mode in mode_options],
                on_change=on_mode_change,
                width=300
            )
        ]),
        padding=ft.padding.all(10),
        border=ft.border.all(1, colors['border']),
        border_radius=10,
        margin=ft.margin.symmetric(vertical=5),
        bgcolor=colors['container_bg']
    )
    
    file_selector_settings_container = ft.Container(
        content=ft.Column([
            ft.Text("File Selector Options", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
            ft.Dropdown(
                label="Select File Option",
                value=current_file_option,
                options=[ft.dropdown.Option(option) for option in file_selector_options],
                on_change=on_file_selector_change,
                width=300
            )
        ]),
        padding=ft.padding.all(10),
        border=ft.border.all(1, colors['border']),
        border_radius=10,
        margin=ft.margin.symmetric(vertical=5),
        bgcolor=colors['container_bg']
    )
    
    storage_settings_container = ft.Container(
        content=ft.Column([
            ft.Text("Object Storage Selector", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
            ft.Dropdown(
                label="Select Storage",
                value=current_storage,
                options=[ft.dropdown.Option(storage) for storage in azure_blob_options],
                on_change=on_storage_change,
                width=300
            )
        ]),
        padding=ft.padding.all(10),
        border=ft.border.all(1, colors['border']),
        border_radius=10,
        margin=ft.margin.symmetric(vertical=5),
        bgcolor=colors['container_bg']
    )
    
    return ft.Column([
        ft.Text("Settings Page", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=20, color=colors['divider']),
        theme_settings_container,
        mode_settings_container,
        file_selector_settings_container,
        storage_settings_container,
        collection_settings_container,
        ft.Divider(height=20, color=colors['divider'])
    ], alignment="center", scroll=ft.ScrollMode.AUTO, expand=True)

# -------------------------------------------------------------------------------
# file_selector_view()
# Purpose: Renders file selection interface with different paths for FilePicker, 
#          Google Sheets, and CSV options based on user settings
# Parameters: page - Flet page object for session and overlay management
# Returns: ft.Column containing file selector interface specific to chosen method
# -------------------------------------------------------------------------------
def file_selector_view(page):
    logger.info("File Selector page")
    
    # Get the current file selector option from session
    current_file_option = page.session.get("selected_file_option")
    
    # Get theme-appropriate colors
    colors = get_theme_colors(page)
    
    # Default content if no option is selected
    if not current_file_option:
        return ft.Column([
            ft.Text("File Selector Page", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Text("Please select a file option in Settings first.", 
                   size=16, color=colors['secondary_text']),
            ft.ElevatedButton("Go to Settings", 
                            on_click=lambda e: page.go("/settings"))
        ], alignment="center")
    
    # Different execution paths based on selected option
    if current_file_option == "FilePicker":
        logger.info("Executing FilePicker path")
        
        # Get selected files from session
        selected_files = page.session.get("selected_files")
        if selected_files is None:
            selected_files = []
        
        # Get temporary files from session (space-free copies)
        temp_files = page.session.get("temp_files")
        if temp_files is None:
            temp_files = []
        
        def sanitize_filename(filename):
            """Replace spaces with underscores and remove other problematic characters"""
            # Replace spaces with underscores
            sanitized = filename.replace(' ', '_')
            # Remove or replace other problematic characters if needed
            # For now, just handle spaces as requested
            return sanitized
        
        def copy_files_to_temp_directory(file_paths):
            """Copy selected files to temporary directory with sanitized names"""
            try:
                # Create a temporary directory in the storage/temp folder
                temp_base_dir = os.path.join(os.getcwd(), "storage", "temp")
                os.makedirs(temp_base_dir, exist_ok=True)
                
                # Create a unique subdirectory for this session
                temp_dir = tempfile.mkdtemp(dir=temp_base_dir, prefix="mdi_files_")
                logger.info(f"Created temporary directory: {temp_dir}")
                
                temp_file_paths = []
                temp_file_info = []
                
                for original_path in file_paths:
                    try:
                        # Get the original filename
                        original_filename = os.path.basename(original_path)
                        
                        # Sanitize the filename (replace spaces with underscores)
                        sanitized_filename = sanitize_filename(original_filename)
                        
                        # Create the destination path
                        temp_file_path = os.path.join(temp_dir, sanitized_filename)
                        
                        # Copy the file
                        shutil.copy2(original_path, temp_file_path)
                        
                        # Store the paths
                        temp_file_paths.append(temp_file_path)
                        temp_file_info.append({
                            'original_path': original_path,
                            'original_filename': original_filename,
                            'temp_path': temp_file_path,
                            'sanitized_filename': sanitized_filename
                        })
                        
                        logger.info(f"Copied '{original_filename}' to '{sanitized_filename}' in temp directory")
                        
                    except Exception as e:
                        logger.error(f"Failed to copy file {original_path}: {str(e)}")
                        continue
                
                # Store in session
                page.session.set("temp_directory", temp_dir)
                page.session.set("temp_files", temp_file_paths)
                page.session.set("temp_file_info", temp_file_info)
                
                logger.info(f"Successfully copied {len(temp_file_paths)} files to temporary directory")
                return temp_file_paths, temp_file_info
                
            except Exception as e:
                logger.error(f"Failed to create temporary directory or copy files: {str(e)}")
                return [], []
        
        def clear_temp_directory():
            """Clear the temporary directory and session data"""
            temp_dir = page.session.get("temp_directory")
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleared temporary directory: {temp_dir}")
                except Exception as e:
                    logger.error(f"Failed to clear temporary directory: {str(e)}")
            
            # Clear session data
            page.session.set("temp_directory", None)
            page.session.set("temp_files", [])
            page.session.set("temp_file_info", [])
        
        # FilePicker configuration for images and PDFs
        def on_file_picker_result(e: ft.FilePickerResultEvent):
            if e.files:
                # Store original file paths in session
                file_paths = [file.path for file in e.files if file.path]
                page.session.set("selected_files", file_paths)
                logger.info(f"Selected {len(file_paths)} files: {file_paths}")
                
                # Store the directory of the first selected file for future FilePicker operations
                if file_paths:
                    last_directory = os.path.dirname(file_paths[0])
                    page.session.set("last_file_directory", last_directory)
                    logger.info(f"Stored last directory: {last_directory}")
                
                # Copy files to temporary directory with sanitized names
                temp_file_paths, temp_file_info = copy_files_to_temp_directory(file_paths)
                
                # Refresh the page to show selected files
                page.go("/file_selector")
            else:
                logger.info("No files selected")
        
        # Create FilePicker with image and PDF filters
        file_picker = ft.FilePicker(
            on_result=on_file_picker_result
        )
        page.overlay.append(file_picker)
        
        def open_file_picker(e):
            # Get the last used directory from session
            last_directory = page.session.get("last_file_directory")
            
            if last_directory and os.path.exists(last_directory):
                logger.info(f"Using last directory as initial path: {last_directory}")
                file_picker.pick_files(
                    dialog_title="Select Image and/or PDF Files",
                    allow_multiple=True,
                    allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "pdf"],
                    initial_directory=last_directory
                )
            else:
                logger.info("No previous directory stored, using default")
                file_picker.pick_files(
                    dialog_title="Select Image and/or PDF Files",
                    allow_multiple=True,
                    allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "pdf"]
                )
        
        def on_clear_selection(e):
            """Clear both original selection and temporary files"""
            clear_temp_directory()
            page.session.set("selected_files", [])
            page.go("/file_selector")
        
        # Build the file list display
        file_list_controls = []
        if selected_files:
            # Get temp file info for display
            temp_file_info = page.session.get("temp_file_info")
            if temp_file_info is None:
                temp_file_info = []
            
            file_list_controls.append(
                ft.Text(f"Selected {len(selected_files)} files:", 
                       size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text'])
            )
            
            # Show temporary directory info
            temp_dir = page.session.get("temp_directory")
            if temp_dir:
                file_list_controls.append(
                    ft.Text(f"Temporary directory: {temp_dir}", 
                           size=12, color=colors['secondary_text'])
                )
                file_list_controls.append(ft.Container(height=5))
            
            # Display file information
            for i, info in enumerate(temp_file_info, 1):
                original_name = info.get('original_filename', 'Unknown')
                sanitized_name = info.get('sanitized_filename', 'Unknown')
                
                if original_name != sanitized_name:
                    file_list_controls.append(
                        ft.Text(f"{i}. {original_name} → {sanitized_name}", 
                               size=14, color=colors['secondary_text'])
                    )
                else:
                    file_list_controls.append(
                        ft.Text(f"{i}. {original_name}", 
                               size=14, color=colors['secondary_text'])
                    )
            
            file_list_controls.append(ft.Container(height=10))
            file_list_controls.append(
                ft.ElevatedButton("Clear Selection", on_click=on_clear_selection)
            )
        else:
            file_list_controls.append(
                ft.Text("No files selected yet...", 
                       size=14, color=colors['secondary_text'])
            )
        
        return ft.Column([
            ft.Text("File Selector - FilePicker", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Text("Select image and PDF files from your local file system", 
                   size=16, color=colors['primary_text']),
            ft.Text("Files are automatically copied to a temporary directory with space-free names", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            ft.ElevatedButton("Open File Picker", 
                            on_click=open_file_picker),
            ft.Container(height=20),
            *file_list_controls
        ], alignment="center")
    
    elif current_file_option == "Google Sheet":
        logger.info("Executing Google Sheet path")
        return ft.Column([
            ft.Text("File Selector - Google Sheet", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Text("Import file list from a Google Sheet", 
                   size=16, color=colors['primary_text']),
            ft.Container(height=10),
            ft.TextField(
                label="Google Sheet URL",
                hint_text="https://docs.google.com/spreadsheets/d/...",
                width=400
            ),
            ft.Container(height=10),
            ft.ElevatedButton("Connect to Google Sheet", 
                            on_click=lambda e: logger.info("Google Sheet connection button clicked")),
            ft.Container(height=20),
            ft.Text("Sheet data will be displayed here...", 
                   size=14, color=colors['secondary_text'])
        ], alignment="center")
    
    elif current_file_option == "CSV":
        logger.info("Executing CSV path")
        
        # Get selected CSV file from session
        selected_csv_file = page.session.get("selected_csv_file")
        selected_column = page.session.get("selected_csv_column")
        csv_columns = page.session.get("csv_columns")
        
        # Debug session data
        logger.info(f"CSV view - selected_csv_file: {selected_csv_file}")
        logger.info(f"CSV view - selected_column: {selected_column}")
        logger.info(f"CSV view - csv_columns: {csv_columns}")
        logger.info(f"CSV view - csv_columns type: {type(csv_columns)}")
        
        def read_csv_file(file_path):
            """Read CSV/Excel file and extract column headers"""
            try:
                if not PANDAS_AVAILABLE:
                    return None, "pandas library not available. Install with: pip install pandas openpyxl"
                
                # Determine file type and read accordingly
                if file_path.lower().endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.lower().endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                elif file_path.lower().endswith('.numbers'):
                    # Numbers files require special handling
                    logger.warning("Numbers files require manual conversion to CSV or Excel format")
                    return None, "Numbers files are not directly supported. Please export to CSV or Excel format."
                else:
                    return None, f"Unsupported file format: {file_path}"
                
                # Get column names
                columns = list(df.columns)
                logger.info(f"Found {len(columns)} columns in CSV file: {columns}")
                
                return columns, None
                
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {str(e)}")
                return None, f"Error reading file: {str(e)}"
        
        # CSV FilePicker configuration
        def on_csv_file_picker_result(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                # Store the selected file
                file_path = e.files[0].path
                page.session.set("selected_csv_file", file_path)
                logger.info(f"Selected CSV file: {file_path}")
                
                # Store the directory for future FilePicker operations
                last_directory = os.path.dirname(file_path)
                page.session.set("last_file_directory", last_directory)
                logger.info(f"Stored last directory: {last_directory}")
                
                # Read the file and get columns
                columns, error = read_csv_file(file_path)
                logger.info(f"read_csv_file returned: columns={columns}, error={error}")
                
                if columns:
                    page.session.set("csv_columns", columns)
                    page.session.set("csv_read_error", None)
                    logger.info(f"Successfully read {len(columns)} columns from file: {columns}")
                else:
                    page.session.set("csv_columns", None)
                    page.session.set("csv_read_error", error)
                    logger.error(f"Failed to read CSV file: {error}")
                
                # Clear any previous column selection and selected files
                page.session.set("selected_csv_column", None)
                page.session.set("selected_files", [])  # Clear any previously extracted filenames
                logger.info("Cleared previous column selection and selected_files list")
                
                # Update the display dynamically instead of navigating
                logger.info("Updating CSV display dynamically")
                update_csv_display()
            else:
                logger.info("No CSV file selected")
        
        def reload_csv_file():
            """Reload the currently selected CSV file"""
            current_csv_file = page.session.get("selected_csv_file")
            if current_csv_file:
                logger.info(f"Reloading CSV file: {current_csv_file}")
                columns, error = read_csv_file(current_csv_file)
                if columns:
                    page.session.set("csv_columns", columns)
                    page.session.set("csv_read_error", None)
                    logger.info(f"Successfully reloaded {len(columns)} columns from file")
                else:
                    page.session.set("csv_columns", None)
                    page.session.set("csv_read_error", error)
                    logger.error(f"Failed to reload CSV file: {error}")
                
                # Update the display dynamically instead of navigating
                update_csv_display()
        
        # Create CSV FilePicker
        csv_file_picker = ft.FilePicker(
            on_result=on_csv_file_picker_result
        )
        page.overlay.append(csv_file_picker)
        
        def open_csv_file_picker(e):
            # Get the last used directory from session
            last_directory = page.session.get("last_file_directory")
            
            if last_directory and os.path.exists(last_directory):
                logger.info(f"Using last directory as initial path for CSV picker: {last_directory}")
                csv_file_picker.pick_files(
                    dialog_title="Select CSV, Excel, or Numbers File",
                    allow_multiple=False,
                    allowed_extensions=["csv", "xlsx", "xls", "numbers"],
                    initial_directory=last_directory
                )
            else:
                logger.info("No previous directory stored for CSV picker, using default")
                csv_file_picker.pick_files(
                    dialog_title="Select CSV, Excel, or Numbers File",
                    allow_multiple=False,
                    allowed_extensions=["csv", "xlsx", "xls", "numbers"]
                )
        
        def on_clear_csv_selection(e):
            """Clear CSV file selection and related data"""
            page.session.set("selected_csv_file", None)
            page.session.set("csv_columns", None)
            page.session.set("selected_csv_column", None)
            page.session.set("csv_read_error", None)
            page.session.set("selected_files", [])  # Clear the extracted filenames
            logger.info("Cleared CSV selection and selected_files list")
            # Update display dynamically instead of navigating
            update_csv_display()
        
        def on_column_selection_change(e):
            """Handle column selection for filename processing"""
            selected_col = e.control.value
            page.session.set("selected_csv_column", selected_col)
            logger.info(f"Selected column for filename processing: {selected_col}")
            
            # Extract filenames from the selected column and add to selected_files
            if selected_col:
                current_csv_file = page.session.get("selected_csv_file")
                if current_csv_file:
                    try:
                        # Read the CSV file again to get the data
                        import pandas as pd
                        
                        file_ext = os.path.splitext(current_csv_file)[1].lower()
                        logger.info(f"Reading CSV file to extract column data: {current_csv_file}")
                        
                        if file_ext == '.csv':
                            df = pd.read_csv(current_csv_file)
                        elif file_ext in ['.xlsx', '.xls']:
                            df = pd.read_excel(current_csv_file)
                        elif file_ext == '.numbers':
                            df = pd.read_excel(current_csv_file)
                        else:
                            raise ValueError(f"Unsupported file format: {file_ext}")
                        
                        # Extract non-empty values from the selected column
                        if selected_col in df.columns:
                            # Get non-null, non-empty values and convert to strings
                            column_values = df[selected_col].dropna().astype(str).str.strip()
                            # Filter out empty strings after stripping
                            non_empty_values = column_values[column_values != ''].tolist()
                            
                            logger.info(f"Extracted {len(non_empty_values)} non-empty values from column '{selected_col}'")
                            logger.info(f"Filenames from CSV column: {non_empty_values}")
                            
                            # Add to selected_files session list
                            page.session.set("selected_files", non_empty_values)
                            logger.info(f"Added {len(non_empty_values)} filenames to selected_files list")
                            
                        else:
                            logger.error(f"Column '{selected_col}' not found in CSV file")
                            page.session.set("selected_files", [])
                            
                    except ImportError:
                        logger.error("Pandas library not available for reading CSV data")
                        page.session.set("selected_files", [])
                    except Exception as ex:
                        logger.error(f"Error extracting data from column '{selected_col}': {str(ex)}")
                        page.session.set("selected_files", [])
            else:
                # Clear selected files if no column is selected
                page.session.set("selected_files", [])
            
            # Update display to show selection status
            update_csv_display()
        
        # Build the CSV file display as a reference we can update
        csv_file_display = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        
        def update_csv_display():
            """Update the CSV file display with current session data"""
            # Get fresh session data
            current_csv_file = page.session.get("selected_csv_file")
            current_csv_columns = page.session.get("csv_columns")
            current_selected_column = page.session.get("selected_csv_column")
            current_csv_error = page.session.get("csv_read_error")
            
            logger.info(f"update_csv_display - file: {current_csv_file}")
            logger.info(f"update_csv_display - columns: {current_csv_columns}")
            logger.info(f"update_csv_display - error: {current_csv_error}")
            
            # Clear current display
            csv_file_display.controls.clear()
            
            if current_csv_file:
                filename = os.path.basename(current_csv_file)
                csv_file_display.controls.extend([
                    ft.Text("Selected file:", size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                    ft.Text(f"📄 {filename}", size=14, color=colors['secondary_text']),
                    ft.Text(f"Path: {current_csv_file}", size=12, color=colors['secondary_text']),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton("Clear Selection", on_click=on_clear_csv_selection),
                        ft.ElevatedButton("Reload File", on_click=lambda e: reload_csv_file())
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20, color=colors['divider'])
                ])
                
                # Check for read errors
                if current_csv_error:
                    logger.info("update_csv_display - Showing error message")
                    csv_file_display.controls.extend([
                        ft.Text("❌ Error reading file:", size=14, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                        ft.Text(current_csv_error, size=12, color=colors['secondary_text']),
                        ft.Divider(height=10, color=colors['divider'])
                    ])
                
                # Display columns if available
                elif current_csv_columns and len(current_csv_columns) > 0:
                    logger.info("update_csv_display - Showing columns")
                    csv_file_display.controls.extend([
                        ft.Text(f"Found {len(current_csv_columns)} columns:", size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                        ft.Container(height=5)
                    ])
                    
                    # Show column names in a more compact format if there are many columns
                    if len(current_csv_columns) > 10:
                        # For many columns, show them in a compact scrollable list
                        column_list = ft.Column([
                            ft.Text(f"{i}. {col}", size=12, color=colors['secondary_text'])
                            for i, col in enumerate(current_csv_columns, 1)
                        ], spacing=2, scroll=ft.ScrollMode.AUTO, height=150)
                        
                        csv_file_display.controls.append(
                            ft.Container(
                                content=column_list,
                                border=ft.border.all(1, colors['secondary_text']),
                                border_radius=5,
                                padding=10
                            )
                        )
                    else:
                        # For fewer columns, show them normally
                        for i, col in enumerate(current_csv_columns, 1):
                            csv_file_display.controls.append(
                                ft.Text(f"{i}. {col}", size=12, color=colors['secondary_text'])
                            )
                    
                    csv_file_display.controls.extend([
                        ft.Container(height=15),
                        ft.Text("Select column containing filenames:", size=14, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                        ft.Dropdown(
                            label="Choose filename column",
                            value=current_selected_column,
                            options=[ft.dropdown.Option(col) for col in current_csv_columns],
                            on_change=on_column_selection_change,
                            width=300
                        ),
                        ft.Container(height=10)
                    ])
                    
                    # Show selection status
                    if current_selected_column:
                        # Get the current selected_files
                        selected_files = page.session.get("selected_files")
                        if selected_files is None:
                            selected_files = []
                        file_count = len(selected_files) if selected_files else 0
                        
                        csv_file_display.controls.extend([
                            ft.Text(f"✅ Selected column: {current_selected_column}", 
                                   size=14, color=colors['primary_text']),
                            ft.Text(f"📁 Extracted {file_count} filenames from this column", 
                                   size=12, color=colors['secondary_text']),
                            ft.Text("These filenames will be used for fuzzy matching and processing.", 
                                   size=12, color=colors['secondary_text'])
                        ])
                        
                        # Show the extracted filenames if available
                        if selected_files and len(selected_files) > 0:
                            csv_file_display.controls.extend([
                                ft.Container(height=10),
                                ft.Text("Extracted filenames:", size=12, weight=ft.FontWeight.BOLD, color=colors['primary_text'])
                            ])
                            
                            # Show filenames in a scrollable container
                            filename_list = ft.Column([
                                ft.Text(f"{i+1}. {filename}", size=11, color=colors['secondary_text'])
                                for i, filename in enumerate(selected_files)
                            ], spacing=2, scroll=ft.ScrollMode.AUTO, height=min(200, len(selected_files) * 20 + 20))
                            
                            csv_file_display.controls.append(
                                ft.Container(
                                    content=filename_list,
                                    border=ft.border.all(1, colors['secondary_text']),
                                    border_radius=5,
                                    padding=10,
                                    margin=ft.margin.symmetric(vertical=5)
                                )
                            )
                    else:
                        csv_file_display.controls.append(
                            ft.Text("⚠️ Please select a column to continue with file processing.", 
                                   size=12, color=colors['secondary_text'])
                        )
                else:
                    # No columns found and no error
                    logger.info("update_csv_display - No columns and no error")
                    csv_file_display.controls.extend([
                        ft.Text("⚠️ No columns detected in file", size=14, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                        ft.Text("The file might be empty or in an unsupported format.", size=12, color=colors['secondary_text']),
                        ft.Container(height=10)
                    ])
            else:
                logger.info("update_csv_display - No file selected")
                csv_file_display.controls.append(
                    ft.Text("No file selected yet...", 
                           size=14, color=colors['secondary_text'])
                )
            
            page.update()
        
        # Initialize the display
        update_csv_display()
        
        return ft.Column([
            ft.Text("File Selector - CSV", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=colors['divider']),
            ft.Text("Select a CSV, Excel, or Numbers file for processing", 
                   size=16, color=colors['primary_text']),
            ft.Text("Supported formats: .csv, .xlsx, .xls, .numbers", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            ft.ElevatedButton("Select File", 
                            on_click=open_csv_file_picker),
            ft.Divider(height=20, color=colors['divider']),
            ft.Container(
                content=csv_file_display,
                height=400,  # Set a fixed height for the scrollable area
                expand=True
            ),
            ft.Divider(height=20, color=colors['divider']),
            ft.Text("Note: The selected column will be used for fuzzy search matching against available files.", 
                   size=12, color=colors['secondary_text'])
        ], alignment="center", scroll=ft.ScrollMode.AUTO)
    
    else:
        # Fallback for unknown options
        logger.warning(f"Unknown file selector option: {current_file_option}")
        return ft.Column([
            ft.Text("File Selector Page", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Text(f"Unknown option: {current_file_option}", 
                   size=16, color=colors['secondary_text']),
            ft.ElevatedButton("Go to Settings", 
                            on_click=lambda e: page.go("/settings"))
        ], alignment="center")

# -------------------------------------------------------------------------------
# derivatives_view()
# Purpose: Renders the derivatives creation page for processing selected files
# Parameters: page - Flet page object for rendering
# Returns: ft.Column containing derivatives page layout with processing functionality
# -------------------------------------------------------------------------------
def derivatives_view(page):
    logger.info("Derivatives Creation page")
    
    # Get theme-appropriate colors
    colors = get_theme_colors(page)
    
    # Get current mode and files from session
    current_mode = page.session.get("selected_mode")
    selected_files = page.session.get("selected_files")
    if selected_files is None:
        selected_files = []
    
    # Use temporary files (space-free copies) for processing
    temp_files = page.session.get("temp_files")
    if temp_files is None:
        temp_files = []
    
    # Use temp files for processing if available, otherwise fall back to original files
    processing_files = temp_files if temp_files else selected_files
    total_files = len(processing_files)
    
    # Create UI components
    status_text = ft.Text("Ready to create derivatives", size=16, color=colors['primary_text'])
    progress_bar = ft.ProgressBar(width=400, value=0)
    results_column = ft.Column([], scroll=ft.ScrollMode.AUTO, height=300)
    
    def create_derivatives_for_files():
        """Process all selected files and create derivatives"""
        
        def create_single_derivative(file_path, mode, derivative_type='thumbnail'):
            """Create a single derivative for a file based on mode and type"""
            try:
                # Check for spaces in the file path
                if any(char.isspace() for char in file_path):
                    error_msg = f"File path '{file_path}' contains spaces! This should not happen with temp files."
                    logger.error(error_msg)
                    return False, error_msg
                
                # Parse file path components
                dirname, basename = os.path.split(file_path)
                root, ext = os.path.splitext(basename)
                
                logger.info(f"Processing file: {file_path}")
                logger.info(f"Directory: {dirname}, Basename: {basename}, Root: {root}, Extension: {ext}")
                
                if mode == 'Alma':
                    # Alma mode - create thumbnail only with _TN.jpg extension
                    derivative_path = os.path.join(dirname, f"{root}_TN.jpg")
                    logger.info(f"Alma derivative path: {derivative_path}")
                    
                    # Define options for Alma thumbnails
                    options = {
                        'trim': False,
                        'height': 200,
                        'width': 200,
                        'quality': 85,
                        'type': 'thumbnail'
                    }
                    
                    # Process based on file type
                    if ext.lower() in ['.tiff', '.tif', '.jpg', '.jpeg', '.png']:
                        success = generate_thumbnail(file_path, derivative_path, options)
                        if success:
                            logger.info(f"Created Alma thumbnail: {derivative_path}")
                            return True, derivative_path
                        else:
                            error_msg = f"Failed to create Alma thumbnail: {derivative_path}"
                            logger.error(error_msg)
                            return False, error_msg
                    elif ext.lower() == '.pdf':
                        cmd = f'magick convert "{file_path}[0]" "{derivative_path}"'
                        return_code = call(cmd, shell=True)
                        if return_code == 0:
                            logger.info(f"Created Alma PDF thumbnail: {derivative_path}")
                            return True, derivative_path
                        else:
                            error_msg = f"Failed to create PDF thumbnail with command: {cmd}"
                            logger.error(error_msg)
                            return False, error_msg
                    else:
                        error_msg = f"Unsupported file type for Alma: {ext}"
                        logger.error(error_msg)
                        return False, error_msg
                
                elif mode == 'CollectionBuilder':
                    # CollectionBuilder mode - create thumbnail or small
                    if derivative_type == 'thumbnail':
                        derivative_path = os.path.join(dirname, f"{root}_TN.jpg")
                        logger.info(f"CollectionBuilder thumbnail path: {derivative_path}")
                        options = {
                            'trim': False,
                            'height': 400,
                            'width': 400,
                            'quality': 85,
                            'type': 'thumbnail'
                        }
                    elif derivative_type == 'small':
                        derivative_path = os.path.join(dirname, f"{root}_SMALL.jpg")
                        logger.info(f"CollectionBuilder small path: {derivative_path}")
                        options = {
                            'trim': False,
                            'height': 800,
                            'width': 800,
                            'quality': 85,
                            'type': 'thumbnail'
                        }
                    else:
                        error_msg = f"Unknown derivative type for CollectionBuilder: {derivative_type}"
                        logger.error(error_msg)
                        return False, error_msg
                    
                    # Process based on file type
                    if ext.lower() in ['.tiff', '.tif', '.jpg', '.jpeg', '.png']:
                        success = generate_thumbnail(file_path, derivative_path, options)
                        if success:
                            logger.info(f"Created CollectionBuilder {derivative_type}: {derivative_path}")
                            return True, derivative_path
                        else:
                            error_msg = f"Failed to create CollectionBuilder {derivative_type}: {derivative_path}"
                            logger.error(error_msg)
                            return False, error_msg
                    elif ext.lower() == '.pdf':
                        cmd = f'magick convert "{file_path}[0]" "{derivative_path}"'
                        return_code = call(cmd, shell=True)
                        if return_code == 0:
                            logger.info(f"Created CollectionBuilder {derivative_type} from PDF: {derivative_path}")
                            return True, derivative_path
                        else:
                            error_msg = f"Failed to create PDF {derivative_type} with command: {cmd}"
                            logger.error(error_msg)
                            return False, error_msg
                    else:
                        error_msg = f"Unsupported file type for CollectionBuilder: {ext}"
                        logger.error(error_msg)
                        return False, error_msg
                else:
                    error_msg = f"Unsupported mode: {mode}"
                    logger.error(error_msg)
                    return False, error_msg
                    
            except Exception as e:
                error_msg = f"Exception in create_single_derivative: {str(e)}"
                logger.error(error_msg)
                return False, error_msg
        
        # Main processing logic
        if not current_mode:
            status_text.value = "❌ No mode selected. Please go to Settings first."
            status_text.color = colors['primary_text']
            page.update()
            return
            
        if not processing_files:
            status_text.value = "❌ No files selected. Please go to File Selector first."
            status_text.color = colors['primary_text']
            page.update()
            return
        
        # Check if we're using temp files and log the difference
        if temp_files:
            logger.info(f"Starting derivative creation for {total_files} files in {current_mode} mode using temporary space-free copies")
        else:
            logger.info(f"Starting derivative creation for {total_files} files in {current_mode} mode using original files")
            
        status_text.value = f"🔄 Processing {total_files} files in {current_mode} mode..."
        status_text.color = colors['primary_text']
        page.update()
        
        processed_count = 0
        success_count = 0
        error_count = 0
        
        for index, file_path in enumerate(processing_files):
            try:
                # Get display name (show original filename if using temp files)
                if temp_files and index < len(selected_files):
                    display_name = os.path.basename(selected_files[index])
                else:
                    display_name = os.path.basename(file_path)
                
                logger.info(f"Processing file {index + 1}/{total_files}: {file_path}")
                
                # Update progress
                progress_bar.value = index / total_files
                status_text.value = f"🔄 Processing file {index + 1}/{total_files}: {display_name}"
                page.update()
                
                # Create derivatives based on mode
                if current_mode == "CollectionBuilder":
                    # Create thumbnail
                    thumbnail_success, thumbnail_result = create_single_derivative(file_path, current_mode, 'thumbnail')
                    
                    # Create small derivative
                    small_success, small_result = create_single_derivative(file_path, current_mode, 'small')
                    
                    # Log results
                    if thumbnail_success and small_success:
                        result_text = f"✅ {display_name} - Created thumbnail and small derivatives"
                        success_count += 1
                        logger.info(f"Successfully created derivatives for {file_path}")
                    else:
                        result_text = f"❌ {display_name} - Failed to create derivatives"
                        if not thumbnail_success:
                            logger.error(f"Thumbnail failed: {thumbnail_result}")
                        if not small_success:
                            logger.error(f"Small derivative failed: {small_result}")
                        error_count += 1
                        
                elif current_mode == "Alma":
                    # Create thumbnail only for Alma
                    thumbnail_success, thumbnail_result = create_single_derivative(file_path, current_mode, 'thumbnail')
                    
                    if thumbnail_success:
                        result_text = f"✅ {display_name} - Created thumbnail derivative"
                        success_count += 1
                        logger.info(f"Successfully created thumbnail for {file_path}")
                    else:
                        result_text = f"❌ {display_name} - Failed to create thumbnail"
                        logger.error(f"Thumbnail failed: {thumbnail_result}")
                        error_count += 1
                else:
                    result_text = f"❌ {display_name} - Unsupported mode: {current_mode}"
                    error_count += 1
                    logger.error(f"Unsupported mode {current_mode} for file {file_path}")
                
                # Add result to UI
                results_column.controls.append(
                    ft.Text(result_text, size=12, color=colors['primary_text'])
                )
                
                processed_count += 1
                
            except Exception as e:
                error_count += 1
                error_text = f"❌ {display_name} - Error: {str(e)}"
                results_column.controls.append(
                    ft.Text(error_text, size=12, color=colors['primary_text'])
                )
                logger.error(f"Exception processing {file_path}: {str(e)}")
            
            # Update progress
            progress_bar.value = (index + 1) / total_files
            page.update()
        
        # Final status update
        progress_bar.value = 1.0
        
        # For Alma mode, rename all _TN.jpg files to .jpg.clientThumb after processing
        if current_mode == "Alma" and success_count > 0:
            status_text.value = f"🔄 Renaming Alma thumbnails to .jpg.clientThumb format..."
            page.update()
            
            # Get the temporary directory where files are stored
            temp_dir = page.session.get("temp_directory")
            if temp_dir and os.path.exists(temp_dir):
                try:
                    # Find all _TN.jpg files in the temp directory
                    tn_files = []
                    for filename in os.listdir(temp_dir):
                        if filename.endswith("_TN.jpg"):
                            tn_files.append(filename)
                    
                    renamed_count = 0
                    for tn_filename in tn_files:
                        try:
                            # Create old and new paths
                            old_path = os.path.join(temp_dir, tn_filename)
                            # Replace _TN.jpg with .jpg.clientThumb
                            new_filename = tn_filename.replace("_TN.jpg", ".jpg.clientThumb")
                            new_path = os.path.join(temp_dir, new_filename)
                            
                            # Rename the file
                            os.rename(old_path, new_path)
                            renamed_count += 1
                            logger.info(f"Renamed {tn_filename} to {new_filename}")
                            
                        except Exception as e:
                            logger.error(f"Failed to rename {tn_filename}: {str(e)}")
                    
                    logger.info(f"Alma mode: Renamed {renamed_count} thumbnail files to .jpg.clientThumb format")
                    
                except Exception as e:
                    logger.error(f"Error during Alma thumbnail renaming: {str(e)}")
        
        status_text.value = f"✅ Completed! Processed: {processed_count}, Success: {success_count}, Errors: {error_count}"
        logger.info(f"Derivative creation completed. Processed: {processed_count}, Success: {success_count}, Errors: {error_count}")
        page.update()
    
    def on_create_derivatives_click(e):
        """Handle the create derivatives button click"""
        create_derivatives_for_files()
    
    def on_clear_results_click(e):
        """Clear the results display"""
        results_column.controls.clear()
        progress_bar.value = 0
        status_text.value = "Ready to create derivatives"
        page.update()
        logger.info("Results cleared")
    
    # Prepare status information controls
    status_info_controls = [
        ft.Text(f"Current Mode: {current_mode or 'None selected'}", 
               size=16, weight=ft.FontWeight.BOLD, color=colors['container_text']),
        ft.Text(f"Selected Files: {total_files}", 
               size=16, weight=ft.FontWeight.BOLD, color=colors['container_text'])
    ]
    
    # Add temp files information if available
    if temp_files:
        status_info_controls.append(
            ft.Text("✅ Using temporary space-free copies for processing", 
                   size=14, color=colors['container_text'])
        )
    else:
        status_info_controls.append(
            ft.Text("⚠️ Using original files (may have spaces in names)", 
                   size=14, color=colors['container_text'])
        )
    
    status_info_controls.extend([
        ft.Text("Derivative Types:", size=14, weight=ft.FontWeight.BOLD, color=colors['container_text']),
        ft.Text("• CollectionBuilder: _TN.jpg + _SMALL.jpg derivatives", 
               size=12, color=colors['container_text']),
        ft.Text("• Alma: .jpg.clientThumb derivative (renamed after creation)", 
               size=12, color=colors['container_text'])
    ])
    
    # Create the UI layout
    return ft.Column([
        ft.Text("Derivatives Creation", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=20, color=colors['divider']),
        
        # Status information
        ft.Container(
            content=ft.Column(status_info_controls),
            padding=ft.padding.all(15),
            border=ft.border.all(1, colors['border']),
            border_radius=10,
            bgcolor=colors['container_bg'],
            margin=ft.margin.symmetric(vertical=10)
        ),
        
        # Control buttons
        ft.Row([
            ft.ElevatedButton(
                "Create Derivatives",
                on_click=on_create_derivatives_click,
                disabled=(not current_mode or total_files == 0)
            ),
            ft.ElevatedButton(
                "Clear Results",
                on_click=on_clear_results_click
            )
        ], alignment=ft.MainAxisAlignment.CENTER),
        
        ft.Divider(height=10, color=colors['divider']),
        
        # Progress and status
        status_text,
        progress_bar,
        
        ft.Divider(height=10, color=colors['divider']),
        
        # Results display
        ft.Container(
            content=ft.Column([
                ft.Text("Processing Results:", size=16, weight=ft.FontWeight.BOLD, color=colors['container_text']),
                results_column
            ]),
            padding=ft.padding.all(15),
            border=ft.border.all(1, colors['border']),
            border_radius=10,
            bgcolor=colors['container_bg'],
            height=350,
            expand=True
        )
        
    ], alignment="center", scroll=ft.ScrollMode.AUTO, expand=True)

# -------------------------------------------------------------------------------
# storage_view()
# Purpose: Renders the Azure storage interface page for cloud storage operations
# Parameters: page - Flet page object for rendering
# Returns: ft.Column containing storage page layout (placeholder)
# -------------------------------------------------------------------------------
def storage_view(page):
    logger.info("Azure Storage page")
    return ft.Column([
        ft.Text("Storage Page")
    ], alignment="center")

VIEWS = {
    "/": home_view,
    "/about": about_view,
    "/exit": exit_view,
    "/settings": settings_view,
    "/file_selector": file_selector_view,
    "/derivatives": derivatives_view,
    "/storage": storage_view,
}

# -------------------------------------------------------------------------------
# build_appbar()
# Purpose: Constructs the application navigation bar with icon buttons for all pages
# Parameters: page - Flet page object for navigation routing
# Returns: ft.AppBar containing navigation icons and routing handlers
# -------------------------------------------------------------------------------
def build_appbar(page):
    return ft.AppBar(
        title=ft.Text("MDI"),
        actions=[
            ft.IconButton(ft.Icons.HOME, tooltip="Home", on_click=lambda e: page.go("/")),
            ft.IconButton(ft.Icons.INFO, tooltip="About", on_click=lambda e: page.go("/about")),
            ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda e: page.go("/settings")),
            ft.IconButton(ft.Icons.FILE_OPEN, tooltip="Select Files for Ingest", on_click=lambda e: page.go("/file_selector")),
            ft.IconButton(ft.Icons.PHOTO_SIZE_SELECT_LARGE_SHARP, tooltip="Create Derivatives from Selected Files", on_click=lambda e: page.go("/derivatives")),
            ft.IconButton(ft.Icons.STORAGE, tooltip="Engage Azure Storage", on_click=lambda e: page.go("/storage")),
            ft.IconButton(ft.Icons.EXIT_TO_APP, tooltip="Exit", on_click=lambda e: page.go("/exit"))
        ]
    )

# -------------------------------------------------------------------------------
# route_change()
# Purpose: Handles page navigation and route changes, sets up appbar and divider
# Parameters: e - Flet event object containing page and route information
# Returns: None (modifies page controls directly)
# -------------------------------------------------------------------------------
def route_change(e):
    page = e.page
    route = e.route
    page.appbar = build_appbar(page)
    page.controls.clear()
    logger.info(f"Route changed to: {route}")
    
    # Get theme-appropriate colors for the divider
    colors = get_theme_colors(page)
    
    # Add consistent divider below appbar
    page.add(ft.Divider(height=2, color=colors['divider']))
    
    view_func = VIEWS.get(route, home_view)
    page.add(view_func(page))

# -------------------------------------------------------------------------------
# main()
# Purpose: Application entry point - initializes page settings, logging, and routing
# Parameters: page - Flet page object for application configuration
# Returns: None (configures page and starts application)
# -------------------------------------------------------------------------------
def main(page: ft.Page):
    page.title = "Manage Digital Ingest: a Flet Multi-Page App"
    
    # Set window dimensions - increase height by 100 pixels from typical default
    page.window.height = 700  # Default is typically 600, so adding 100
    page.window.min_height = 500
    
    # Set default theme mode to Light
    page.theme_mode = ft.ThemeMode.LIGHT

    # Initialize a default SnackBar so the SnackBarHandler has a target
    page.snack_bar = ft.SnackBar(content=ft.Text(""))

    # Store the logger in the page session for other modules to use
    page.session.set("logger", logger)

    # Also give the snack handler the page reference
    _snack_handler.set_page(page)

    page.on_route_change = route_change
    page.go(page.route or "/") # Load initial route


if __name__ == "__main__":
    ft.app(target=main)
