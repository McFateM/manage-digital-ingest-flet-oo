# Manage Digital Ingest: a Flet Multi-Page

## Setup Command Sequence

```zsh
mkdir manage-digital-ingest-flet-mp
cd manage-digital-ingest-flet-mp
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip3 install 'flet[all]'==0.28.2
pip3 install thumbnail
pip3 freeze > python-requirements.txt
code .
```

## Prompt

Initial code here was created using Perplexity AI from the following prompt...  

```
Create a multi-page Flet app with a logger and an AppBar and SnackBar on every page. Pages will include: home, about, exit, mode, picker, sheet, derivatives, and storage.
```

## AI Result

Here’s a Python Flet app skeleton for a multi-page app with routing, a consistent AppBar, SnackBar on every page, and integrated logger. This covers eight pages: home, about, exit, mode, picker, sheet, derivatives, and storage. The AppBar with navigation actions and a logger setup are included, and a SnackBar is ready to display on all pages.

### Initial Code

```py
import flet as ft
import logging

# --- LOGGER SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flet_app")

def show_snack(page, message, color="green"):
    # Universal snack bar
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=color,
        action="OK"
    )
    page.snack_bar.open = True
    page.update()

# --- ROUTE HANDLERS ---
def home_view(page):
    logger.info("Loaded Home page")
    return ft.Column([
        ft.Text("Welcome to Home!"),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Home SnackBar!"))
    ], alignment="center")

def about_view(page):
    logger.info("Loaded About page")
    return ft.Column([
        ft.Text("About this app."),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "About SnackBar!"))
    ], alignment="center")

def exit_view(page):
    logger.info("Loaded Exit page")
    return ft.Column([
        ft.Text("Exit Page"),
        ft.ElevatedButton("Exit App", on_click=lambda e: page.window_close()),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Exit SnackBar!"))
    ], alignment="center")

def mode_view(page):
    logger.info("Loaded Mode page")
    return ft.Column([
        ft.Text("Mode Page"),
        ft.ElevatedButton("Show SnackBar", on_click=lambda e: show_snack(page, "Mode SnackBar!"))
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
    "/mode": mode_view,
    "/picker": picker_view,
    "/sheet": sheet_view,
    "/derivatives": derivatives_view,
    "/storage": storage_view,
}

def build_appbar(page):
    return ft.AppBar(
        title=ft.Text("MDI"), 
        actions=[
            ft.IconButton(ft.icons.HOME, tooltip="Home", on_click=lambda e: page.go("/")),
            ft.IconButton(ft.icons.INFO, tooltip="About", on_click=lambda e: page.go("/about")),
            ft.IconButton(ft.icons.STORAGE, tooltip="Storage", on_click=lambda e: page.go("/storage")),
            ft.IconButton(ft.icons.EXIT_TO_APP, tooltip="Exit", on_click=lambda e: page.go("/exit"))
        ]
    )

def route_change(e):
    page = e.page
    route = e.route
    page.appbar = build_appbar(page)
    page.controls.clear()
    logger.info(f"Route changed to: {route}")
    view_func = VIEWS.get(route, home_view)
    page.add(view_func(page))

def main(page: ft.Page):
    page.title = "Multi-Page Flet App"
    page.on_route_change = route_change
    page.go(page.route or "/") # Load initial route

ft.app(target=main)
```


if __name__ == "__main__":
    ft.app(target=main)
```

## Problems

This app may not run on macOS as a desktop app because Flet's FilePicker will not open due to missing/default macOS entitlements, the file picker window simply refuses to appear.  

The app will run in a browser if you specify `flet run --web`.  

Using `Flet` version 0.28.2 (rather than the current v0.28.3) may enable the FilePicker to open, but might also cause navigation problems. 

AI typically generates references to `.icons` and `.colors`, but both were recently converted to begin with uppercase letters, so `.Icons` and `.Colors` are needed.  

