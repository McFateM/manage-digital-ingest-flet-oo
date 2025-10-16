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

        # Generate session report as plain text (markdown breaks with complex data)
        session_data_found = False
        session_lines = []
        session_lines.append(ft.Text("Current Session Data:", size=18, weight=ft.FontWeight.BOLD, color=colors['primary_text']))
        session_lines.append(ft.Container(height=10))

        # Get all session keys and values
        for key in self.page.session.get_keys():
            value = self.page.session.get(key)
            # Don't truncate - show full values
            value_str = str(value)
            session_lines.append(
                ft.Column([
                    ft.Text(f"{key}:", size=14, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                    ft.Text(value_str, size=12, color=colors['code_text'], selectable=True),
                    ft.Container(height=5),
                ], spacing=2)
            )
            session_data_found = True
        
        if not session_data_found:
            session_lines.append(ft.Text("No session data found!", italic=True, color=colors['secondary_text']))
        
        session_lines.append(ft.Container(height=10))
        session_lines.append(ft.Divider(color=colors['divider']))
        session_lines.append(ft.Text("This report shows all key-value pairs stored in page.session.", 
                                     size=11, italic=True, color=colors['secondary_text']))

        # Create a column with all session data
        session_widget = ft.Column(session_lines, spacing=0, scroll=ft.ScrollMode.AUTO)  

        # Read config from _data/config.json
        config = utils.read_config()

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=4,
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=8),
                ft.Image(
                    src='assets/Primary_Libraries.png',  # Grinnell College Libraries logo
                    fit=ft.ImageFit.CONTAIN,
                    width=400,
                ),
                ft.Text(f"🚀 powered by Flet {config['flet_version']} and Python version {config['python_version']} 🐍", 
                       color=colors['secondary_text']),
                ft.Text("Manage Digital Ingest: a Flet Multi-Page App", 
                       size=24, weight=ft.FontWeight.BOLD),
                ft.Text("A Flet Python app for managing Grinnell College ingest of digital objects to Alma or CollectionBuilder",
                       size=14, color=colors['secondary_text']),
                ft.Divider(height=15, color=colors['divider']),
                ft.Container(
                    content=session_widget,
                    padding=10,
                    width=800,
                    height=400,  # Set explicit height for scrolling
                    bgcolor=colors['container_bg'],
                    border=ft.border.all(1, colors['border']),
                    border_radius=8,
                ),
                ft.Divider(height=15, color=colors['divider']),
                ft.Row([
                    ft.ElevatedButton("Log INFO", on_click=_log_info),
                    ft.ElevatedButton("Log WARNING", on_click=_log_warn),
                    ft.ElevatedButton("Log ERROR", on_click=_log_error),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=20),
            ],
        )