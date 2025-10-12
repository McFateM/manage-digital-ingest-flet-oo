import flet as ft
import logging
import utils
import json
from logger import SnackBarHandler

# --- LOGGER SETUP ------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("flet_app")
_snack_handler = SnackBarHandler()
_snack_handler.setLevel(logging.INFO)
logger.addHandler(_snack_handler)
# File logging: write messages to mdi.log in the repo root
_file_handler = logging.FileHandler("mdi.log")
_file_handler.setLevel(logging.INFO)
_file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_file_handler.setFormatter(_file_formatter)
logger.addHandler(_file_handler)

# Write an initial log entry
logger.info("Logger initialized - writing to mdi.log and SnackBarHandler attached")

# --- UNIVERSAL FUNCTIONS ------------------------------------------------------

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

# Home view with markdown content
# -----------------------------------------------------------------------
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

    # Read markdown content from a file
    with open("_data/about.md", "r", encoding="utf-8") as file:
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


    # return ft.Column([
    #     ft.Text("About this app."),
    #     ft.Row([
    #         # ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "About SnackBar!")),
    #         ft.VerticalDivider(opacity=0),
    #         ft.ElevatedButton("Log INFO", on_click=_log_info),
    #         ft.ElevatedButton("Log WARNING", on_click=_log_warn),
    #         ft.ElevatedButton("Log ERROR", on_click=_log_error),
    #     ], alignment=ft.MainAxisAlignment.CENTER)
    # ], alignment="center")

def exit_view(page):
    logger.info("Loaded Exit page")
    return ft.Column([
        ft.Text("Exit Page"),
        ft.ElevatedButton("Exit App", on_click=lambda e: page.window_close())
    ], alignment="center")

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
    file_selector_options = ["FilePicker", "Google Sheet"]
    
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
    
    # Ensure CB Collection is disabled when mode is not CollectionBuilder
    is_collection_enabled = current_mode == "CollectionBuilder"
    
    if current_mode:
        logger.info(f"Current mode selection: {current_mode}")
    if current_file_option:
        logger.info(f"Current file option selection: {current_file_option}")
    if current_storage:
        logger.info(f"Current storage selection: {current_storage}")
    if current_collection:
        logger.info(f"Current collection selection: {current_collection}")
    
    logger.info(f"CB Collection Selector enabled: {is_collection_enabled}")
    
    # Dropdown change handlers
    def on_mode_change(e):
        page.session.set("selected_mode", e.control.value)
        logger.info(f"Mode selected: {e.control.value}")
        log_all_current_selections()
        # Refresh the page to update container states
        page.go("/settings")
    
    def on_file_selector_change(e):
        page.session.set("selected_file_option", e.control.value)
        logger.info(f"File option selected: {e.control.value}")
        log_all_current_selections()
    
    def on_storage_change(e):
        page.session.set("selected_storage", e.control.value)
        logger.info(f"Storage selected: {e.control.value}")
        log_all_current_selections()
    
    def on_collection_change(e):
        page.session.set("selected_collection", e.control.value)
        logger.info(f"Collection selected: {e.control.value}")
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
    theme_container = ft.Container(
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
    mode_container = ft.Container(
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
    
    file_selector_container = ft.Container(
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
    
    storage_container = ft.Container(
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
    
    collection_container = ft.Container(
        content=ft.Column([
            ft.Text("CB Collection Selector", size=18, weight=ft.FontWeight.BOLD, color=colors['container_text']),
            ft.Dropdown(
                label="Select Collection",
                value=current_collection,
                options=[ft.dropdown.Option(collection) for collection in cb_collection_options],
                on_change=on_collection_change,
                width=300,
                disabled=not is_collection_enabled
            )
        ]),
        padding=ft.padding.all(10),
        border=ft.border.all(1, colors['border']),
        border_radius=10,
        margin=ft.margin.symmetric(vertical=5),
        disabled=not is_collection_enabled,
        bgcolor=colors['container_bg']
    )
    
    return ft.Column([
        ft.Text("Settings Page", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=20, color=colors['divider']),
        theme_container,
        mode_container,
        file_selector_container,
        storage_container,
        collection_container,
        ft.Divider(height=20, color=colors['divider'])
    ], alignment="center", scroll=ft.ScrollMode.AUTO, expand=True)

def picker_view(page):
    logger.info("Loaded Picker page")
    return ft.Column([
        ft.Text("Picker Page")
    ], alignment="center")

def sheet_view(page):
    logger.info("Loaded Sheet page")
    return ft.Column([
        ft.Text("Sheet Page")
    ], alignment="center")

def fuzzy_search_view(page):
    logger.info("Loaded Fuzzy Search page")
    return ft.Column([
        ft.Text("Fuzzy Search Page")
    ], alignment="center")

def derivatives_view(page):
    logger.info("Loaded Derivatives page")
    return ft.Column([
        ft.Text("Derivatives Page")
    ], alignment="center")

def storage_view(page):
    logger.info("Loaded Storage page")
    return ft.Column([
        ft.Text("Storage Page")
    ], alignment="center")

VIEWS = {
    "/": home_view,
    "/about": about_view,
    "/exit": exit_view,
    "/settings": settings_view,
    "/picker": picker_view,
    "/sheet": sheet_view,
    "/fuzzy_search": fuzzy_search_view,
    "/derivatives": derivatives_view,
    "/storage": storage_view,
}

def build_appbar(page):
    return ft.AppBar(
        title=ft.Text("MDI"),
        actions=[
            ft.IconButton(ft.Icons.HOME, tooltip="Home", on_click=lambda e: page.go("/")),
            ft.IconButton(ft.Icons.INFO, tooltip="About", on_click=lambda e: page.go("/about")),
            ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda e: page.go("/settings")),
            ft.IconButton(ft.Icons.FILE_OPEN, tooltip="Select Files for Ingest", on_click=lambda e: page.go("/picker")),
            ft.IconButton(ft.Icons.GRID_ON_SHARP, tooltip="Show Files from a Google Sheet or CSV", on_click=lambda e: page.go("/sheet")),
            ft.IconButton(ft.Icons.IMAGE_SEARCH, tooltip="Fuzzy Search for Selected Files", on_click=lambda e: page.go("/fuzzy_search")),
            ft.IconButton(ft.Icons.PHOTO_SIZE_SELECT_LARGE_SHARP, tooltip="Create Derivatives from Selected Files", on_click=lambda e: page.go("/derivatives")),
            ft.IconButton(ft.Icons.STORAGE, tooltip="Engage Azure Storage", on_click=lambda e: page.go("/storage")),
            ft.IconButton(ft.Icons.EXIT_TO_APP, tooltip="Exit", on_click=lambda e: page.go("/exit"))
        ]
    )

def route_change(e):
    page = e.page
    route = e.route
    page.appbar = build_appbar(page)
    page.controls.clear( )
    logger.info(f"Route changed to: {route}")
    view_func = VIEWS.get(route, home_view)
    page.add(view_func(page))

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
