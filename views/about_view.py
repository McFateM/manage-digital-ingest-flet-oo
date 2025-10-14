"""
About View for Manage Digital Ingest Application

This module contains the AboutView class for displaying application information
and session data.
"""

import flet as ft
from views.base_view import BaseView
import utils
import logging


class AboutView(BaseView):
    """
    About view class for displaying application information and demo logging.
    """
    
    def render(self) -> ft.Column:
        """
        Render the about view content.
        
        Returns:
            ft.Column: The about page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # Demo buttons to exercise the SnackBar logger at different levels
        def _log_info(e):
            self.logger.info("Demo INFO from About page")

        def _log_warn(e):
            self.logger.warning("Demo WARNING from About page")

        def _log_error(e):
            self.logger.error("Demo ERROR from About page")

        # Generate session report
        session_data_found = False
        session_report = "## Current Session Data:\n\n"

        # Get all session keys and values
        for key in self.page.session.get_keys():
            session_report += f"**{key}**: `{self.page.session.get(key)}`\n\n"
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
                ft.Row([
                    ft.ElevatedButton("Log INFO", on_click=_log_info),
                    ft.ElevatedButton("Log WARNING", on_click=_log_warn),
                    ft.ElevatedButton("Log ERROR", on_click=_log_error),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=15, color=colors['divider']),
                ft.Container(
                    height=60,
                    content=ft.Markdown("**Thanks for choosing Flet!**"),
                ),
            ],
        )