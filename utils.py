import flet as ft
import os
import utils
from thumbnail import generate_thumbnail
from subprocess import call
# from azure.identity import DefaultAzureCredential
# from azure.storage.blob import BlobServiceClient
import json
import sys
import logging

# Simple string matching functions
# ----------------------------------------------------------------------
def calculate_string_similarity(str1, str2):
    """
    Calculate similarity between two strings using a simple approach.
    Returns a percentage (0-100) of how similar the strings are.
    """
    if str1 == str2:
        return 100
    
    # Simple substring matching approach
    if str1 in str2 or str2 in str1:
        # Calculate ratio based on length overlap
        overlap = min(len(str1), len(str2))
        total = max(len(str1), len(str2))
        return int((overlap / total) * 100)
    
    # Count common characters
    common_chars = 0
    str1_chars = list(str1)
    str2_chars = list(str2)
    
    for char in str1_chars:
        if char in str2_chars:
            common_chars += 1
            str2_chars.remove(char)
    
    # Calculate similarity based on common characters
    total_chars = max(len(str1), len(str2))
    if total_chars == 0:
        return 0
    
    return int((common_chars / total_chars) * 100)

def sanitize_filename(filename):
    """
    Sanitize a filename by replacing spaces and special characters.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: Sanitized filename with spaces replaced by underscores,
             special characters removed, and hyphens cleaned up
    """
    import re
    # Replace spaces with underscores
    sanitized = filename.replace(' ', '_')
    # Remove or replace other problematic characters (keep word chars, hyphens, underscores, dots)
    sanitized = re.sub(r'[^\w\-_\.]', '_', sanitized)
    # Clean up multiple underscores around hyphens: _-_ or -_ or _- becomes just -
    sanitized = re.sub(r'_*-_*', '-', sanitized)
    # Clean up any remaining multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized

def perform_fuzzy_search(base_path, target_filename, threshold=90):
    """
    Recursively search for files in base_path and find the best match for target_filename
    using simple string matching.
    
    Args:
        base_path (str): The directory to start searching from
        target_filename (str): The filename to match against
        threshold (int): The minimum match percentage to consider a match (0-100)
        
    Returns:
        tuple: (best_match_path, best_match_ratio) or (None, 0) if no match found
    """
    try:
        best_match_path = None
        best_match_ratio = 0
        
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                # Calculate simple string similarity ratio
                ratio = calculate_string_similarity(filename.lower(), target_filename.lower())
                
                # Update best match if this ratio is higher
                if ratio > best_match_ratio:
                    best_match_ratio = ratio
                    best_match_path = os.path.join(root, filename)
                    
                    # If we found a perfect match, we can return immediately
                    if ratio == 100:
                        return (best_match_path, ratio)
        
        # Only return the match if it meets the threshold
        if best_match_ratio >= threshold:
            return (best_match_path, best_match_ratio)
        else:
            return (None, 0)
            
    except Exception as e:
        logging.error(f"Error in fuzzy search: {str(e)}")
        return (None, 0)


def perform_fuzzy_search_batch(base_path, target_filenames, threshold=90, progress_callback=None, cancel_check=None):
    """
    Perform fuzzy search for multiple filenames sequentially with progress tracking and cancellation support.
    
    Args:
        base_path (str): The directory to start searching from
        target_filenames (list): List of filenames to match against
        threshold (int): The minimum fuzzy match ratio to consider a match (0-100)
        progress_callback (callable): Optional callback function to report progress (0.0 to 1.0)
        cancel_check (callable): Optional function that returns True if search should be cancelled
        
    Returns:
        dict: Dictionary mapping target filenames to (match_path, ratio) tuples, or None if cancelled
    """
    results = {}
    total_files = len(target_filenames)
    
    if progress_callback:
        # Start with 0% progress
        progress_callback(0)
    
    for index, filename in enumerate(target_filenames):
        # Check for cancellation
        if cancel_check and cancel_check():
            logging.info("Fuzzy search cancelled by user")
            return None
            
        logging.info(f"Searching for match to '{filename}' ({index + 1}/{total_files})")
        
        # Update progress after each file
        if progress_callback:
            progress = (index + 1) / total_files
            progress_callback(progress)
            
        match_path, ratio = perform_fuzzy_search(base_path, filename, threshold)
        results[filename] = (match_path, ratio)
        
        # Log the result
        if match_path and ratio >= threshold:
            logging.info(f"Found match for '{filename}': {match_path} ({ratio}% match)")
        else:
            logging.info(f"No match found for '{filename}' meeting {threshold}% threshold")
    
    # Only show 100% if we completed the search (not cancelled)
    if progress_callback:
        progress_callback(1.0)
        
    return results

# # Example AppBar component
# def build_app_bar( ):
#     return ft.AppBar(title=ft.Text("My App"), actions=[
#         ft.IconButton(icon=ft.Icons.MENU),
#         ]
#     )

# # Example AppBar component
# def get_app_bar(page=None):
#     if page:
#         page.appbar=ft.AppBar(
#                 title=ft.Text("Flet-X: Manage Digital Ingest"),
#                 actions=[
#                     ft.FilledButton(
#                         text="Home",
#                         # on_click=data.go(data.route_init),
#                     ),
#                     ft.VerticalDivider(opacity=0),
#                     ft.FilledButton(
#                         text="Counter",
#                         # on_click=data.go("/counter/test/0"),
#                     ),
#                     ft.VerticalDivider(opacity=0),
#                     ft.FilledButton(
#                         text="Picker",
#                         # on_click=data.go("/picker"),
#                     ),
#                     ft.VerticalDivider(opacity=0),
#                     ft.FilledButton(
#                         text="Mode",
#                         # on_click=data.go("/mode"),
#                     ),
#                     ft.VerticalDivider(opacity=0),
#                     ft.FilledButton(
#                         text="Show Data",
#                         # on_click=data.go("/show_data"),
#                     ),
#                     ft.VerticalDivider(opacity=0),
#                     ft.FilledButton(
#                         text="Exit",
#                         # on_click=data.go("/exit"),
#                     ),
#                     # One more divider for better button spacing
#                     ft.VerticalDivider(opacity=0),
#                 ],
#                 bgcolor="#121113",
#             )
#         return pageappbar





# Read config from _data/config.json and return as 'config'
# ------------------------------------------------------------------------------
def read_config(page=None):
    # Load configuration from _data/config.json
    with open('_data/config.json', 'r') as config_file:
        config = json.load(config_file) 

    # Print config values to console for debugging and store them in page.session
    print(f"Values from _data/config.json... ")
    for key, value in config.items( ):
        print(f"{key}: {value}")
        # Store config values in page session if needed
        if page:
            page.session.set(key, value)  

    return config




# Helper function to display message in the SnackBar
# ------------------------------------------------------------
def show_message(page, text, is_error=False):
    """Helper function to update and show the SnackBar."""
    logger = page.session.get("logger")
    if is_error:
        logger.error(text)
    else:
        logger.info(text)
        
    page.snack_bar.content.value = text
    page.snack_bar.bgcolor = ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600
    page.open(page.snack_bar)
    page.update( )


# Validate CSV headings against verified heading files
# ------------------------------------------------------------
def validate_csv_headings(csv_file_path, mode):
    """
    Validate CSV file headings against verified heading files based on mode.
    
    Args:
        csv_file_path: Path to the CSV file to validate
        mode: Either 'Alma' or 'CollectionBuilder'
        
    Returns:
        tuple: (is_valid: bool, unmatched_headings: list, error_message: str or None)
        - is_valid: True if all headings match (for Alma) or if file is valid (for CB)
        - unmatched_headings: List of headings that don't match verified list
        - error_message: Error message if there was a problem, None otherwise
        
    Notes:
        - For Alma mode: ALL headings in the CSV must exactly match verified headings.
          Returns unmatched headings if any are found.
        - For CollectionBuilder mode: CSV headings are checked against verified list,
          but extra headings are allowed (more permissive).
        - Order of headings does not matter, only the names.
    """
    import pandas as pd
    
    # Determine which verified headings file to use
    if mode == 'Alma':
        verified_file = os.path.join("_data", "verified_CSV_headings_for_Alma-D.csv")
    elif mode == 'CollectionBuilder':
        verified_file = os.path.join("_data", "verified_CSV_headings_for_GCCB_projects.csv")
    else:
        return (False, [], f"Invalid mode '{mode}'. Must be 'Alma' or 'CollectionBuilder'.")
    
    # Check if verified file exists
    if not os.path.exists(verified_file):
        return (False, [], f"Verified headings file not found: {verified_file}")
    
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        return (False, [], f"CSV file not found: {csv_file_path}")
    
    try:
        # Read the verified headings (first row only)
        verified_df = pd.read_csv(verified_file, nrows=0)
        verified_headings = set(verified_df.columns.tolist())
        
        # Read the CSV file headings (first row only) with multiple encodings
        csv_df = None
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
        
        for encoding in encodings:
            try:
                csv_df = pd.read_csv(csv_file_path, nrows=0, encoding=encoding)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if csv_df is None:
            return (False, [], f"Could not read CSV file with any supported encoding")
        
        csv_headings = set(csv_df.columns.tolist())
        
        # Find headings in CSV that are NOT in verified list
        unmatched_headings = list(csv_headings - verified_headings)
        
        # For Alma mode, be strict - no unmatched headings allowed
        if mode == 'Alma':
            if unmatched_headings:
                return (False, unmatched_headings, None)
            else:
                return (True, [], None)
        
        # For CollectionBuilder mode, be more permissive - just report unmatched
        # but don't fail validation (extra headings are OK)
        elif mode == 'CollectionBuilder':
            return (True, unmatched_headings, None)
            
    except Exception as e:
        return (False, [], f"Error validating CSV headings: {str(e)}")
