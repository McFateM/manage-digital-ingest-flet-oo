"""
Obsolete Functions from utils.py

This module contains functions that are no longer used in the application
but are preserved here for reference or potential future use.

These functions were moved from utils.py on 2025-10-16.
DO NOT import this module in active code.
"""

import flet as ft
import os
import sys
import json
import utils
from subprocess import call
# from azure.storage.blob import BlobServiceClient


# close_app( ) callback function.   DOES NOT WORK!
# ----------------------------------------------------------------------
def close_app(e):
    # e.page.window.close( ) # Close the application window but only works in desktop apps
    page = e.page

    page.dialog = ft.AlertDialog(
        title=ft.Text("Close App"),
        content=ft.Text("App is shutting down. You may close this browser tab."),
    )
    page.dialog.open = True
    page.update( )
    sys.exit(0)



# Function to process the selected files
# ----------------------------------------------------------------------
def process_files(e):
    """
    This is the processing function tasked with creating image derivatives.
    It receives a list of selected files and the directory they are located in.
    """

    page = e.page
    logger = page.session.get("logger")
    page.result_text.value = "Processing..."
    page.update()

    files = e.page.session.get("selected_object_paths")
    directory = os.path.dirname(files[0]) if files else "N/A"
        
    if files:
        logger.info(f"Processing {len(files)} files from {directory}...")
        for file in files:
            logger.info(f"  - {file.name} (Path: {file.path})")

        processed = 0
        total = len(files) * 2  # Each file needs 2 derivatives

        for file in files:
            derivative = utils.create_derivative(page,
                mode=page.session.get("mode"),
                derivative_type='thumbnail',
                index=0,
                url=f"http://example.com/objs/{file.name}",
                local_storage_path=file.path,
                blob_service_client=None
            )
            processed += 1
            logger.info(f"Progress: {processed}/{total} derivatives processed ({processed/total:.0%})")
            page.result_text.value += f"\n- {derivative}"  
            page.update()

            derivative = utils.create_derivative(page,
                mode=page.session.get("mode"),
                derivative_type='small',
                index=0,
                url=f"http://example.com/objs/{file.name}",
                local_storage_path=file.path,
                blob_service_client=None
            )
            processed += 1
            logger.info(f"Progress: {processed}/{total} derivatives processed ({processed/total:.0%})")
            page.result_text.value += f"\n- {derivative}"  
            page.update()

        utils.show_message(page, f"Processed {len(files)} files from {directory}.")
                
    else:
        logger.info("No files were selected for processing.")
        utils.show_message(page, "No files were selected for processing.", is_error=True)


# Parse .json file to an ft.Column of Radio controls as "content"
# ---------------------------------------------------------------------
def parse_json_to_radio_content(fname):
    data_array = None

    try:
        with open(fname, 'r') as file:
            data_array = json.load(file)
    except FileNotFoundError:
        msg = f"Error: '{fname}' not found."
        return msg
    except json.JSONDecodeError:
        msg = f"Error: Could not decode JSON from '{fname}'. Check file format."
        return msg
    
    content=ft.Column(
        [ft.Radio(value=source, label=source) for source in data_array],
        # expand=True,
        # spacing=0
    )

    return content

# Load options from a JSON file and return as a list of Radio controls
# ----------------------------------------------------------------------
def load_radio_options_from_json(fname):
    content = parse_json_to_radio_content(fname)

    # Check if content is an ft.Column instance 
    if isinstance(content, ft.Column):
        return content.controls
    else:  # If content is not an ft.Column, print error and return error message
        print(f"Error: {content}")
        return [ft.Text(f"Error loading options from {fname}.")]


# Connect to Azure Blob Storage
# ----------------------------------------------------------------------
# Retrieve the connection string for use with the application. The storage
# connection string is stored in an environment variable on the machine
# running the application called AZURE_STORAGE_CONNECTION_STRING. If the environment
# variable is created after the application is launched in a console or with
# Visual Studio, the shell or application needs to be closed and reloaded to take the
# environment variable into account.

def connect_to_azure_blob(page):
    logger = page.session.get("logger")
    try:
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

        # Create the BlobServiceClient object
        # blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        # return blob_service_client
        return None  # Azure functionality not implemented

    except Exception as ex:
        logger.error(f"Error connecting to Azure Blob Storage: {ex}")
        return None


# upload_to_azure( ) - Just what the name says post-processing
# ----------------------------------------------------------------------------------------------
def upload_to_azure(blob_service_client, url, match, local_storage_path, transcript=False):

    try:

        if transcript:
            container_name = "transcripts"
        elif "thumbs/" in url:
            container_name = "thumbs"
        elif "smalls/" in url:
            container_name = "smalls"
        else:
            container_name = "objs"

        # Create a blob client using the local file name as the name for the blob
        if container_name:
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=match)
            if blob_client.exists():
                txt = f"Blob '{match}' already exists in Azure Storage container '{container_name}'.  Skipping this upload."
                # st.success(txt)
                # state('logger').success(txt)
                return "EXISTS"
            else:
                txt = f"Uploading '{match}' to Azure Storage container '{container_name}'"
                # st.success(txt)
                # state('logger').success(txt)

                # Upload the file
                with open(file=local_storage_path, mode="rb") as data:
                    blob_client.upload_blob(data)
                return "COPIED"

        else:
            txt = f"No container available for uploading '{match}' to Azure Storage!'"
            # st.error(txt)
            # state('logger').error(txt)
            return False

    except Exception as ex:
        # state('logger').critical(ex)
        # st.exception(ex)
        pass


# create_derivative(mode, derivative_type, index, url, local_storage_path, blob_service_client)
# ------------------------------------------------------------
def create_derivative(page, mode, derivative_type, index, url, local_storage_path, blob_service_client):
    logger = page.session.get("logger")

    # Check the mode, if invalid report that there's nothing to do.
    if mode not in ['Alma','CollectionBuilder']:
        msg = f"Invalid mode '{mode}' specified so create_derivative( ) has nothing to do. {local_storage_path} derivative creation failed."
        # show_message(page, msg, True)
        return msg

    # Check for spaces in the local_storage_path... NO spaces!
    if any(char.isspace( ) for char in local_storage_path):
        msg = f"File path '{local_storage_path}' contains one or more spaces!  Use `rename-file-paths-no-spaces.zsh to eradicate them before proceeding!"
        # show_message(page, msg, True)
        return msg

    sanitized = local_storage_path
    
    dirname, basename = os.path.split(sanitized)
    root, ext = os.path.splitext(basename)

    derivative_path = None
    derivative_url = None
    derivative_filename = None
    
    # Create clientThumb thumbnails for Alma
    if mode == 'Alma':
        # Create derivative filename with .jpg.clientThumb suffix
        derivative_filename = f"{root}.jpg.clientThumb"
        
        # Determine output directory - use TN/ subdirectory if it exists
        if dirname.endswith('OBJS'):
            # If source is in OBJS/, put derivative in parallel TN/ directory
            temp_base_dir = os.path.dirname(dirname)
            derivative_dir = os.path.join(temp_base_dir, 'TN')
        else:
            # Otherwise use the same directory as source
            derivative_dir = dirname
        
        # Ensure the derivative directory exists
        os.makedirs(derivative_dir, exist_ok=True)
        
        derivative_path = os.path.join(derivative_dir, derivative_filename)

        # Define options for Alma thumbnails
        options = {
            'trim': False,
            'height': 200,
            'width': 200,
            'quality': 85,
            'type': 'thumbnail'
        }

        # If original is an image...
        if ext.lower( ) in ['.tiff', '.tif', '.jpg', '.jpeg', '.png']:
            # generate_thumbnail(sanitized, derivative_path, options)
            # utils.show_message(page, f"Created thumbnail '{derivative_filename}' for '{basename}'")
            pass

        # If original is a PDF...
        elif ext.lower( ) == '.pdf':
            cmd = f'magick "{sanitized}"[0] "{derivative_path}"'
            return_code = call(cmd, shell=True)
            if return_code == 0:
                # utils.show_message(page, f"Created thumbnail '{derivative_filename}' for '{basename}'")
                pass
            else:
                txt = f"Sorry, ImageMagick failed to create a thumbnail for '{basename}'"
                # utils.show_message(page, txt, is_error=True)
                return False

        else:
            txt = f"Sorry, we can't create a thumbnail for '{basename}' (unsupported file type: {ext})"
            # utils.show_message(page, txt, is_error=True)
            return False

        return derivative_path

    # If creating derivative(s) for CollectionBuilder...
    if mode == 'CollectionBuilder':
        
        if derivative_type == 'thumbnail':
            col = 'image_thumb'
            # col = 'WORKSPACE3'
            options = {
                'trim': False,
                'height': 400,
                'width': 400,
                'quality': 85,
                'type': 'thumbnail'
            }
            
            derivative_filename = f"{root}_TN.jpg"
            derivative_path = dirname + '/' + derivative_filename
            derivative_url = url.replace('/objs/', '/thumbs/') + derivative_filename

        elif derivative_type == 'small':
            col = 'image_small'
            # col = 'WORKSPACE2'
            options = {
                'trim': False,
                'height': 800,
                'width': 800,
                'quality': 85,
                'type': 'thumbnail'
            }

            derivative_filename = f"{root}_SMALL.jpg"
            derivative_path = dirname + '/' + derivative_filename
            derivative_url = url.replace('/objs/', '/smalls/') + derivative_filename

        else:

            txt = f"Call to create_derivative( ) has an unknown 'derivative_type' of '{derivative_type}'."
            # utils.show_message(page, txt, is_error=True)
            return False

        # If original is an image...
        if ext.lower( ) in ['.tiff', '.tif', '.jpg', '.jpeg', '.png']:
            # generate_thumbnail(sanitized, derivative_path, options)
            # utils.show_message(page, f"Created '{derivative_type}' derivative '{derivative_path}' for '{sanitized}'")
            return derivative_path
    
        # If original is a PDF...
        elif ext.lower( ) == '.pdf':
            cmd = 'magick ' + sanitized + '[0] ' + derivative_path
            # utils.show_message(page, f"Calling '{cmd}' to create a '{derivative_type}' derivative for '{sanitized}'")
            
            return_code = call(cmd, shell=True)
            if return_code == 0:
                # utils.show_message(page, f"Created '{derivative_type}' derivative '{derivative_path}' for '{sanitized}'")
                return derivative_path
            else:
                txt = f"Sorry, we can't create a '{derivative_type}' derivative for '{sanitized}'"
                # utils.show_message(page, txt, is_error=True)
                return False

        else:
            txt = f"Sorry, we can't create a thumbnail for '{sanitized}'"
            # utils.show_message(page, txt, is_error=True)
            derivative_url = False
            return False
