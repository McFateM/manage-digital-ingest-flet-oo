"""
Instructions View for Manage Digital Ingest Application

This module contains the InstructionsView class for displaying follow-up instructions
and scripts based on the current mode.
"""

import flet as ft
from views.base_view import BaseView


class InstructionsView(BaseView):
    """
    Instructions view class for displaying mode-specific instructions and scripts.
    """
    
    def __init__(self, page: ft.Page):
        """Initialize the instructions view."""
        super().__init__(page)
    
    def get_alma_instructions(self) -> list:
        """
        Get instructions for Alma mode.
        
        Returns:
            list: List of instruction controls
        """
        colors = self.get_theme_colors()
        
        return [
            ft.Text("Alma Workflow Instructions", 
                   size=20, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Container(height=10),
            
            ft.Text("1. Upload to Alma Digital Repository", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Text("• Navigate to your Alma digital repository", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Upload the thumbnail derivatives from the TN/ directory", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Thumbnails are sized at 200x200 pixels with .jpg.clientThumb suffix", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            
            ft.Text("2. Metadata Assignment", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Text("• Link thumbnails to their corresponding master files", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Verify all metadata fields are complete", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            
            ft.Text("3. Quality Check", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Text("• Review thumbnail rendering in Alma", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Ensure all files are properly linked", 
                   size=14, color=colors['secondary_text']),
        ]
    
    def get_collectionbuilder_instructions(self) -> list:
        """
        Get instructions for CollectionBuilder mode.
        
        Returns:
            list: List of instruction controls
        """
        colors = self.get_theme_colors()
        
        return [
            ft.Text("CollectionBuilder Workflow Instructions", 
                   size=20, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Container(height=10),
            
            ft.Text("1. Organize Derivative Files", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Text("• TN/ directory contains thumbnails (400x400 pixels)", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• SMALL/ directory contains small images (800x800 pixels)", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Both use _TN.jpg and _SMALL.jpg suffixes respectively", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            
            ft.Text("2. Upload to Repository", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Text("• Upload TN/ directory to /objects/thumbnails/", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Upload SMALL/ directory to /objects/small/", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Original files go to /objects/ directory", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            
            ft.Text("3. Update Metadata CSV", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Text("• Add filenames to the 'filename' column", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Ensure objectid values match your filenames", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Add format, title, and other required metadata", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            
            ft.Text("4. Build and Deploy", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Text("• Run 'rake generate_derivatives' if needed", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Run 'rake deploy' to build and publish", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• Verify site displays correctly", 
                   size=14, color=colors['secondary_text']),
        ]
    
    def get_no_mode_instructions(self) -> list:
        """
        Get instructions when no mode is selected.
        
        Returns:
            list: List of instruction controls
        """
        colors = self.get_theme_colors()
        
        return [
            ft.Text("No Mode Selected", 
                   size=20, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Container(height=10),
            ft.Text("Please select a mode in the Settings page to view mode-specific instructions.", 
                   size=14, color=colors['secondary_text']),
            ft.Container(height=10),
            ft.Text("Available Modes:", 
                   size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
            ft.Text("• Alma - For Alma Digital Repository workflows", 
                   size=14, color=colors['secondary_text']),
            ft.Text("• CollectionBuilder - For CollectionBuilder static site workflows", 
                   size=14, color=colors['secondary_text']),
        ]
    
    def render(self) -> ft.Column:
        """
        Render the instructions view content.
        
        Returns:
            ft.Column: The instructions page layout
        """
        self.on_view_enter()
        
        # Get theme-appropriate colors
        colors = self.get_theme_colors()
        
        # Get current mode from session
        current_mode = self.page.session.get("selected_mode")
        
        # Get temp directory info
        temp_dir = self.page.session.get("temp_directory")
        temp_objs_dir = self.page.session.get("temp_objs_directory")
        temp_tn_dir = self.page.session.get("temp_tn_directory")
        temp_small_dir = self.page.session.get("temp_small_directory")
        
        # Build file paths section
        file_paths_controls = []
        if temp_dir:
            file_paths_controls.extend([
                ft.Text("Current Session Directories:", 
                       size=16, weight=ft.FontWeight.BOLD, color=colors['primary_text']),
                ft.Container(height=5),
                ft.Text(f"Base: {temp_dir}", 
                       size=12, color=colors['secondary_text'], selectable=True),
                ft.Text(f"OBJS/: {temp_objs_dir}", 
                       size=12, color=colors['secondary_text'], selectable=True),
                ft.Text(f"TN/: {temp_tn_dir}", 
                       size=12, color=colors['secondary_text'], selectable=True),
                ft.Text(f"SMALL/: {temp_small_dir}", 
                       size=12, color=colors['secondary_text'], selectable=True),
                ft.Container(height=15),
            ])
        
        # Get mode-specific instructions
        if current_mode == "Alma":
            instruction_controls = self.get_alma_instructions()
        elif current_mode == "CollectionBuilder":
            instruction_controls = self.get_collectionbuilder_instructions()
        else:
            instruction_controls = self.get_no_mode_instructions()
        
        # Build the layout
        return ft.Column([
            ft.Row([
                ft.Text("Follow-Up Instructions", size=24, weight=ft.FontWeight.BOLD),
                self.create_log_button("Show Logs", ft.Icons.LIST_ALT)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=15, color=colors['divider']),
            
            # Current mode indicator
            ft.Container(
                content=ft.Column([
                    ft.Text(f"Current Mode: {current_mode or 'None'}", 
                           size=16, weight=ft.FontWeight.BOLD, color=colors['container_text']),
                ], spacing=5),
                padding=ft.padding.all(10),
                border=ft.border.all(1, colors['border']),
                border_radius=10,
                bgcolor=colors['container_bg'],
                margin=ft.margin.symmetric(vertical=5)
            ),
            
            ft.Container(height=10),
            
            # File paths section (if available)
            *file_paths_controls,
            
            # Instructions container
            ft.Container(
                content=ft.Column(
                    instruction_controls,
                    spacing=5,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.all(15),
                border=ft.border.all(1, colors['border']),
                border_radius=10,
                bgcolor=colors['container_bg'],
                expand=True
            ),
            
        ], alignment="start", expand=True, spacing=0, scroll=ft.ScrollMode.AUTO)
