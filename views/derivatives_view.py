"""
Derivatives View for Manage Digital Ingest Application

This module contains the DerivativesView class for creating file derivatives.
"""

import flet as ft
from views.base_view import BaseView


class DerivativesView(BaseView):
    """
    Derivatives view class for derivative creation operations.
    """
    
    def render(self) -> ft.Column:
        """
        Render the derivatives view content.
        
        Returns:
            ft.Column: The derivatives page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # Get current mode and files from session
        current_mode = self.page.session.get("selected_mode")
        selected_files = self.page.session.get("selected_files") or []
        total_files = len(selected_files)
        
        # Prepare status information controls
        status_info_controls = [
            ft.Text(f"Current Mode: {current_mode or 'None selected'}", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['container_text']),
            ft.Text(f"Selected Files: {total_files}", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['container_text'])
        ]
        
        status_info_controls.extend([
            ft.Text("Derivative Types:", size=14, weight=ft.FontWeight.BOLD, color=colors['container_text']),
            ft.Text("• CollectionBuilder: _TN.jpg + _SMALL.jpg derivatives", 
                   size=12, color=colors['container_text']),
            ft.Text("• Alma: .jpg.clientThumb derivative (renamed after creation)", 
                   size=12, color=colors['container_text'])
        ])
        
        def on_create_derivatives_click(e):
            """Handle the create derivatives button click"""
            # TODO: Implement derivative creation logic
            self.logger.info("Create derivatives functionality to be implemented")
        
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
                    on_click=lambda e: self.logger.info("Clear results clicked")
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(height=10, color=colors['divider']),
            
            ft.Text("TODO: Migrate full derivative creation functionality from original code.",
                   size=14, color=colors['secondary_text'])
            
        ], alignment="center")