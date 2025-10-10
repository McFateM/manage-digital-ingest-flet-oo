import flet as ft
import logging
import utils
from logger import SnackBarHandler

# --- LOGGER SETUP ------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
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
def show_snack(page, message, color="green"):
    # Universal snack bar
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=color,
        action="OK"
    )
    page.snack_bar.open = True
    page.update( )

# --- ROUTE HANDLERS ------------------------------------------------------------

# Home view with markdown content
# -----------------------------------------------------------------------
def home_view(page):
    logger.info("Loaded Home page")

    # Read markdown content from a file
    with open("_data/home.md", "r", encoding="utf-8") as file:
        markdown_text = file.read( )
    
    # Create a Markdown widget with the content
    md_widget = ft.Markdown(markdown_text, 
        md_style_sheet=ft.MarkdownStyleSheet(
            blockquote_text_style=ft.TextStyle(bgcolor=ft.Colors.PURPLE_50, color=ft.Colors.BLACK, size=16, weight=ft.FontWeight.BOLD),
            p_text_style=ft.TextStyle(color=ft.Colors.BLACK, size=16, weight=ft.FontWeight.NORMAL),
            code_text_style=ft.TextStyle(color=ft.Colors.ORANGE_400, size=16, weight=ft.FontWeight.BOLD),
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
            ft.Text(f"🚀 powered by Flet {config['flet_version']} and Python version {config['python_version']} 🐍",color = ft.Colors.GREY_600),
            ft.Text("Manage Digital Ingest: a Flet Multi-Page App", size=35),
            ft.Markdown("A Flet Python app for managing Grinnell College ingest of digital objects to Alma or CollectionBuilder"),
            ft.Divider(height=20, color=ft.Colors.RED_400),
            md_widget,
            # ft.FilledButton("Go to Counter", on_click=data.go("/counter/test/0")),
            ft.Divider(height=20, color=ft.Colors.RED_400),
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
            blockquote_text_style=ft.TextStyle(bgcolor=ft.Colors.PURPLE_50, color=ft.Colors.BLACK, size=16, weight=ft.FontWeight.BOLD),
            p_text_style=ft.TextStyle(color=ft.Colors.BLACK, size=16, weight=ft.FontWeight.NORMAL),
            code_text_style=ft.TextStyle(color=ft.Colors.ORANGE_400, size=16, weight=ft.FontWeight.BOLD),
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
                width = 500,
                # height = 300
            ),
            ft.Text(f"🚀 powered by Flet {config['flet_version']} and Python version {config['python_version']} 🐍",color = ft.Colors.GREY_600),
            ft.Text("Manage Digital Ingest: a Flet Multi-Page App", size=35),
            ft.Markdown("A Flet Python app for managing Grinnell College ingest of digital objects to Alma or CollectionBuilder"),
            ft.Divider(height=20, color=ft.Colors.RED_400),
            md_widget,
            # ft.FilledButton("Go to Counter", on_click=data.go("/counter/test/0")),
            ft.Divider(height=20, color=ft.Colors.RED_400),
            ft.Row([
                ft.ElevatedButton("Log INFO", on_click=_log_info),
                ft.ElevatedButton("Log WARNING", on_click=_log_warn),
                ft.ElevatedButton("Log ERROR", on_click=_log_error),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=20, color=ft.Colors.RED_400),
            ft.Container(
                height = 80,
                content = ft.Markdown("**Thanks for choosing Flet!**"),
            ),
        ],
    )

    # page.session.set("last_status", "At Home page")

    return x


    return ft.Column([
        ft.Text("About this app."),
        ft.Row([
            # ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "About SnackBar!")),
            ft.VerticalDivider(opacity=0),
            ft.ElevatedButton("Log INFO", on_click=_log_info),
            ft.ElevatedButton("Log WARNING", on_click=_log_warn),
            ft.ElevatedButton("Log ERROR", on_click=_log_error),
        ], alignment=ft.MainAxisAlignment.CENTER)
    ], alignment="center")

def exit_view(page):
    logger.info("Loaded Exit page")
    return ft.Column([
        ft.Text("Exit Page"),
        ft.ElevatedButton("Exit App", on_click=lambda e: page.window_close()),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Exit SnackBar!"))
    ], alignment="center")

def settings_view(page):
    logger.info("Loaded Settings page")
    return ft.Column([
        ft.Text("Settings Page"),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Settings SnackBar!"))
    ], alignment="center")

def picker_view(page):
    logger.info("Loaded Picker page")
    return ft.Column([
        ft.Text("Picker Page"),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Picker SnackBar!"))
    ], alignment="center")

def sheet_view(page):
    logger.info("Loaded Sheet page")
    return ft.Column([
        ft.Text("Sheet Page"),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Sheet SnackBar!"))
    ], alignment="center")

def fuzzy_search_view(page):
    logger.info("Loaded Fuzzy Search page")
    return ft.Column([
        ft.Text("Fuzzy Search Page"),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Fuzzy Search SnackBar!"))
    ], alignment="center")

def derivatives_view(page):
    logger.info("Loaded Derivatives page")
    return ft.Column([
        ft.Text("Derivatives Page"),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Derivatives SnackBar!"))
    ], alignment="center")

def storage_view(page):
    logger.info("Loaded Storage page")
    return ft.Column([
        ft.Text("Storage Page"),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Storage SnackBar!"))
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
