"""
Exit View for Manage Digital Ingest Application

This module contains the ExitView class for handling application termination.
"""

import flet as ft
from views.base_view import BaseView


class ExitView(BaseView):
    """
    Exit view class for application termination.
    """
    
    def render(self) -> ft.Column:
        """
        Render the exit view content.
        
        Returns:
            ft.Column: The exit page layout
        """
        self.on_view_enter()
        
        return ft.Column([
            ft.Text("Exit Page"),
            ft.ElevatedButton("Exit App", on_click=lambda e: self.page.window_close())
        ], alignment="center")