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
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        return blob_service_client

    except Exception as ex:
        logger.error(f"Error connecting to Azure Blob Storage: {ex}")
        return None


# # build_azure_url( )
# # ----------------------------------------------------------------------
# def build_azure_url(target, score, match, mode='OBJ'):

#     # Special logic... if the score > 49 check the embedded numeric portion ONLY and
#     # if that's an EXACT match we will accept it as a match
#     if score > 49:
#         score = check_numeric_part(score, target, match)

#     try:

#         # Check if the match score was 90 or above, if not, skip it!
#         if score < 90:
#             txt = f"Best match for '{target}' has an insufficient match score of {score}.  It will NOT be accepted nor copied to Azure storage."
#             st.warning(txt)
#             state('logger').warning(txt)

#             return False

#         # Check for obvious mode/match errors
#         if "_TN." in match and mode != 'TN':
#             txt = f"_TN in '{match}' and mode '{mode}' is an error!"
#             st.error(txt)
#             state('logger').error(txt)

#             return False
#         elif "_JPG." in match and mode != 'JPG':
#             txt = f"_JPG in '{match}' and mode '{mode}' is an error!"
#             st.error(txt)
#             state('logger').error(txt)

#             return False
#         elif "_OBJ." in match and mode != 'OBJ':
#             txt = "_OBJ in '{match}' and mode '{mode}' is an error!"
#             st.error(txt)
#             state('logger').error(txt)
#             return False

#         # Determine the type of URL to build... OBJ, TN, JPG or TRANSCRIPT
#         if mode == 'TRANSCRIPT':
#             url = azure_base_url + "transcripts/" + match
#         elif "_TN." in match or mode == 'TN':
#             url = azure_base_url + "thumbs/" + match
#         elif "_JPG." in match or mode == 'JPG':
#             url = azure_base_url + "smalls/" + match
#         elif "_OBJ." in match or mode == 'OBJ':
#             url = azure_base_url + "objs/" + match
#         else:
#             txt = f"'{match}' and mode '{mode}' is an error!"
#             st.error(txt)
#             state('logger').error(txt)
#             return False

#         return url

#     except Exception as ex:
#         state('logger').critical(ex)
#         st.exception(ex)
#         pass


# # file_handler(index, blob_service_client, target, score, match, local_storage_path, transcript=False)
# # ---------------------------------------------------------------------------------------
# def file_handler(index, blob_service_client, target, score, match, local_storage_path, transcript=False):
    
#     url = None

#     # Build an Azure Blob URL for the object
#     if transcript:
#         url = build_azure_url(target, score, transcript, mode="TRANSCRIPT")
#         match = transcript
#     else:
#         url = build_azure_url(target, score, match)
#         if not url:
#             st.session_state['skipped'] += 1

#     result = False

#     # Upload the file to Azure Blob storage
#     if url and state('azure_blob_storage'):
#         result = upload_to_azure(blob_service_client, url, match, local_storage_path, transcript)
#         if not transcript:
#             if result == "EXISTS":
#                 st.session_state['exists'] += 1
#             elif result == "COPIED":
#                 st.session_state['copied'] += 1

#     # If result is NOT False and processing_mode is targeted, put the found filename into the worksheet dataframe
#     col = False
#     if result and state('processing_mode'):
#         if state('processing_mode') == 'CollectionBuilder':  # CollectionBuilder
#             if transcript:     
#                 col = 'object_transcript'
#             else:
#                 col = 'object_location'
#                 # col = 'WORKSPACE1'
#         # elif state('processing_mode') == 'Migration to Alma':  # Alma migration
#         #     col = 'file_name_1'
#         else:
#             txt = f"Sorry, the 'processing_mode' state of \'{st.session_state['processing_mode']}\' is not recognized"
#             st.error(txt)
#             state('logger').error(txt)
#             return False

#     if col and isinstance(st.session_state.df, pd.DataFrame):
#         row = st.session_state.df.index[index - 1]  # adjust for header row!
#         st.session_state.df.at[row, col] = url

#         # And if this is a transcript, set the 'display_template' value to 'transcript'
#         if transcript:
#             st.session_state.df.at[row, 'display_template'] = 'transcript'

#     # Thumbnail creation
#     if url and state('generate_thumb'):
#         result = create_derivative('thumbnail', index, url, local_storage_path, blob_service_client)

#     # "Small" creation
#     if url and state('generate_small'):
#         result = create_derivative('small', index, url, local_storage_path, blob_service_client)

#     return True



# # upload_to_azure( ) - Just what the name says post-processing
# # ----------------------------------------------------------------------------------------------
# def upload_to_azure(blob_service_client, url, match, local_storage_path, transcript=False):

#     try:

#         if transcript:
#             container_name = "transcripts"
#         elif "thumbs/" in url:
#             container_name = "thumbs"
#         elif "smalls/" in url:
#             container_name = "smalls"
#         else:
#             container_name = "objs"

#         # Create a blob client using the local file name as the name for the blob
#         if container_name:
#             blob_client = blob_service_client.get_blob_client(
#                 container=container_name, blob=match)
#             if blob_client.exists():
#                 txt = f"Blob '{match}' already exists in Azure Storage container '{container_name}'.  Skipping this upload."
#                 st.success(txt)
#                 state('logger').success(txt)
#                 return "EXISTS"
#             else:
#                 txt = f"Uploading '{match}' to Azure Storage container '{container_name}'"
#                 st.success(txt)
#                 state('logger').success(txt)

#                 # Upload the file
#                 with open(file=local_storage_path, mode="rb") as data:
#                     blob_client.upload_blob(data)
#                 return "COPIED"

#         else:
#             txt = f"No container available for uploading '{match}' to Azure Storage!'"
#             st.error(txt)
#             state('logger').error(txt)
#             return False

#     except Exception as ex:
#         state('logger').critical(ex)
#         st.exception(ex)
#         pass


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


# create_derivative(mode, derivative_type, index, url, local_storage_path, blob_service_client)
# ------------------------------------------------------------
def create_derivative(page, mode, derivative_type, index, url, local_storage_path, blob_service_client):
    logger = page.session.get("logger")

    # Check the mode, if invalid report that there's nothing to do.
    if mode not in ['Alma','CollectionBuilder']:
        msg = f"Invalid mode '{mode}' specified so create_derivative( ) has nothing to do. {local_storage_path} derivative creation failed."
        show_message(page, msg, True)
        return msg

    # Check for spaces in the local_storage_path... NO spaces!
    if any(char.isspace( ) for char in local_storage_path):
        msg = f"File path '{local_storage_path}' contains one or more spaces!  Use `rename-file-paths-no-spaces.zsh to eradicate them before proceeding!"
        show_message(page, msg, True)
        return msg

    sanitized = local_storage_path
    
    dirname, basename = os.path.split(sanitized)
    root, ext = os.path.splitext(basename)

    derivative_path = None
    derivative_url = None
    derivative_filename = None
    
    # Create clientThumb thumbnails for Alma
    if mode == 'Alma':
        derivative_path = f"/Users/mcfatem/OBJs"

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
            generate_thumbnail(sanitized, derivative_path, options)
            utils.show_message(page, f"Created thumbnail for '{sanitized}'")

        # If original is a PDF...
        elif ext.lower( ) == '.pdf':
            cmd = 'magick convert ' + sanitized + '[0] ' + derivative_path
            call(cmd, shell=True)
            utils.show_message(page, f"Created thumbnail for '{sanitized}'")

        else:
            txt = f"Sorry, we can't create a thumbnail for '{sanitized}'"
            utils.show_message(page, txt, is_error=True)

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
            utils.show_message(page, txt, is_error=True)
            return False

        # If original is an image...
        if ext.lower( ) in ['.tiff', '.tif', '.jpg', '.jpeg', '.png']:
            generate_thumbnail(sanitized, derivative_path, options)
            utils.show_message(page, f"Created '{derivative_type}' derivative '{derivative_path}' for '{sanitized}'")
            return derivative_path
    
        # If original is a PDF...
        elif ext.lower( ) == '.pdf':
            cmd = 'magick convert ' + sanitized + '[0] ' + derivative_path
            utils.show_message(page, f"Calling '{cmd}' to create a '{derivative_type}' derivative for '{sanitized}'")
            
            return_code = call(cmd, shell=True)
            if return_code == 0:
                utils.show_message(page, f"Created '{derivative_type}' derivative '{derivative_path}' for '{sanitized}'")
                return derivative_path
            else:
                txt = f"Sorry, we can't create a '{derivative_type}' derivative for '{sanitized}'"
                utils.show_message(page, txt, is_error=True)
                return False


        else:
            txt = f"Sorry, we can't create a thumbnail for '{sanitized}'"
            utils.show_message(page, txt, is_error=True)
            derivative_url = False
            return False

        # # Upload the file to Azure Blob storage
        # if derivative_url and state('azure_blob_storage'):
        #     result = upload_to_azure(blob_service_client, derivative_url, derivative_filename, derivative_path)

        # # Save it to the dataframe
        # if derivative_url and col and isinstance(st.session_state['df'], pd.DataFrame):
        #     df = st.session_state['df']
        #     row = df.index[index - 1]  # adjust for header row!
        #     df.at[row, col] = derivative_url
