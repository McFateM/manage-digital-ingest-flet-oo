"""
Home View for Manage Digital Ingest Application

This module contains the HomeView class for displaying the main home page.
"""

import flet as ft
from views.base_view import BaseView
import utils


class HomeView(BaseView):
    """
    Home view class for displaying the main application page with branding and info.
    """
    
    def render(self) -> ft.Column:
        """
        Render the home view content.
        
        Returns:
            ft.Column: The home page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()

        # Read markdown content from a file
        with open("_data/home.md", "r", encoding="utf-8") as file:
            markdown_text = file.read()
        
        # Create a Markdown widget with the content
        md_widget = ft.Markdown(markdown_text, 
            md_style_sheet=ft.MarkdownStyleSheet(
                blockquote_text_style=ft.TextStyle(bgcolor=colors['markdown_bg'], color=colors['markdown_text'], size=16, weight=ft.FontWeight.BOLD),
                p_text_style=ft.TextStyle(color=colors['primary_text'], size=16, weight=ft.FontWeight.NORMAL),
                code_text_style=ft.TextStyle(color=colors['code_text'], size=16, weight=ft.FontWeight.BOLD),
            )
        )  

        # Read config from _data/config.json
        config = utils.read_config()

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=4,
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    height=8,
                ),
                ft.Image(
                    src='logo_for_subsplus.png',  # Updated to Grinnell College Libraries logo
                    fit=ft.ImageFit.CONTAIN,
                    width=400,
                    # height = 300
                ),
                ft.Text(f"🚀 powered by Flet {config['flet_version']} and Python version {config['python_version']} 🐍", color=colors['secondary_text']),
                ft.Text("Manage Digital Ingest: a Flet Multi-Page App", size=35),
                ft.Markdown("A Flet Python app for managing Grinnell College ingest of digital objects to Alma or CollectionBuilder"),
                ft.Divider(height=15, color=colors['divider']),
                md_widget,
                ft.Divider(height=15, color=colors['divider']),
                ft.Container(
                    height=60,
                    content=ft.Markdown("**Thanks for choosing Flet!**"),
                ),
            ],
        )