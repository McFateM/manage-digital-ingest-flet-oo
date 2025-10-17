# User Guide: Manage Digital Ingest

A comprehensive guide for using the Manage Digital Ingest application to prepare and upload digital objects to Alma-D or CollectionBuilder.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Workflow: Alma Mode](#workflow-alma-mode)
- [Workflow: CollectionBuilder Mode](#workflow-collectionbuilder-mode)
- [View Descriptions](#view-descriptions)
- [Session Preservation](#session-preservation)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Manage Digital Ingest** is a desktop application built with Flet and Python that helps you:

- Prepare digital image collections for ingest into Alma-D or CollectionBuilder
- Match CSV metadata with corresponding image files using fuzzy search
- Generate derivative images (thumbnails and small versions)
- Update CSV files with sanitized filenames and unique identifiers
- Upload files to Alma AWS S3 storage
- Maintain session state across multiple work sessions

### Key Features

- **Dual Mode Support**: Works with both Alma-D and CollectionBuilder workflows
- **Fuzzy Filename Matching**: Automatically matches images to CSV metadata entries
- **Derivative Generation**: Creates TN (thumbnails) and SMALL versions of images
- **CSV Management**: Updates metadata with sanitized filenames and unique IDs
- **Session Preservation**: Save your work and resume later
- **AWS S3 Integration**: Generate upload scripts for Alma ingest

---

## Getting Started

### Launch the Application

```bash
flet run app.py
```

Or for web mode:
```bash
flet run --web app.py
```

### Initial Setup

1. **Select Your Mode** (Settings page)
   - Choose **Alma** for institutional repository ingest
   - Choose **CollectionBuilder** for static site collections

2. **Choose File Selection Method** (Settings page)
   - **CSV**: Select a CSV file with metadata, then match images to entries
   - **FilePicker**: Browse and select individual image files

3. **Configure Storage** (Settings page - for CollectionBuilder)
   - Select Azure Blob storage or local file system

---

## Workflow: Alma Mode

This workflow prepares digital objects for upload to Alma Digital via AWS S3.

### Step 1: Home - Review Instructions

1. Navigate to **Home** page
2. Read the Alma-specific instructions
3. Note the CSV heading requirements

### Step 2: Settings - Configure for Alma

1. Go to **Settings** page
2. Set **Mode** to `Alma`
3. Set **File Selector** to `CSV`
4. Optionally adjust theme and window height

### Step 3: File Selector - Load CSV and Images

1. Navigate to **File Selector** page
2. Click **"Select CSV File"** and choose your metadata CSV
   - CSV must have verified headings for Alma mode
   - See `_data/verified_CSV_headings_for_Alma-D.csv` for valid columns
3. Review the CSV validation status
4. Click **"Browse for Image Files"**
5. Select all image files that correspond to CSV entries
6. Click **"Run Fuzzy Search"**
   - Application matches image filenames to CSV metadata
   - Reviews matched files and their similarity scores
   - Adjust similarity threshold if needed (default: 80%)
7. Click **"Copy Matched Files to Temp"**
   - Creates temporary directory structure
   - Copies images with sanitized filenames
   - Structure: `storage/temp/file_selector_YYYYMMDD_HHMMSS_XXXXXXXX/`

### Step 4: Derivatives - Generate Thumbnails

1. Navigate to **Derivatives** page
2. Click **"Generate TN Derivatives"**
   - Creates thumbnails (200px max dimension) in `/TN` subdirectory
3. Optionally click **"Generate SMALL Derivatives"**
   - Creates small versions (800px max dimension) in `/SMALL` subdirectory
4. Review generation statistics

### Step 5: Update CSV - Apply All Updates

1. Navigate to **Update CSV** page
2. Review the "Before" CSV data display
3. Click **"Apply All Updates"** button
   - Updates existing rows with sanitized filenames
   - Appends new row for the CSV file itself
   - Generates unique `dg_<epoch>` IDs for empty `originating_system_id` cells
   - Populates `dginfo` field with temp CSV filename for all rows
4. Review "Before/After" comparison tables
5. Check the change count summary
6. Click **"Save CSV"** if additional changes needed

### Step 6: Instructions - Generate Upload Script

1. Navigate to **Instructions** page
2. Enter your Alma profile ID and import ID (if known)
3. Click **"Generate Upload Script"**
4. Script is saved to: `{temp_directory}/upload_to_alma.sh`
5. Review the displayed AWS S3 commands
6. Use copy buttons to copy commands to clipboard

### Step 7: Execute Upload

1. Open terminal and navigate to temp directory
2. Make script executable: `chmod +x upload_to_alma.sh`
3. Run script: `./upload_to_alma.sh`
4. Follow interactive prompts:
   - **Step 1**: Lists S3 bucket contents to find profile/import IDs
   - **Step 2**: Copies entire temp directory to S3 (OBJS, TN, CSV, etc.)
   - **Step 3**: Verifies upload completion
5. Return to Alma Digital Uploader to complete ingest

---

## Workflow: CollectionBuilder Mode

This workflow prepares digital objects for CollectionBuilder static sites.

### Step 1: Settings - Configure for CollectionBuilder

1. Go to **Settings** page
2. Set **Mode** to `CollectionBuilder`
3. Set **File Selector** to `CSV` or `FilePicker`
4. Set **Storage** to `Azure` or `Local`
5. Select **Collection** from dropdown

### Step 2: File Selector - Load Files

**If using CSV:**
- Follow Alma workflow steps 3.2-3.7
- CSV heading validation is more permissive

**If using FilePicker:**
1. Click **"Browse for Files"**
2. Select image files
3. Files are automatically copied to temp directory

### Step 3: Derivatives - Generate Images

1. Navigate to **Derivatives** page
2. Generate TN and/or SMALL derivatives as needed

### Step 4: Storage - Upload to Destination

1. Navigate to **Storage** page
2. For Azure: Click upload button to transfer to blob storage
3. For Local: Files remain in temp directory for manual processing

---

## View Descriptions

### Home
- Welcome page with mode-specific instructions
- Quick overview of the ingest process
- Links to relevant documentation

### Settings
- **Mode**: Alma or CollectionBuilder
- **File Selector**: CSV or FilePicker
- **Storage**: Azure or Local (CollectionBuilder only)
- **Collection**: Select target collection (CollectionBuilder only)
- **Theme**: Light or Dark mode
- **Window Height**: Adjust application window size

### File Selector
- **CSV Mode**:
  - Select and validate CSV file
  - Browse for image files
  - Run fuzzy search to match files
  - Copy matched files to temp directory
- **FilePicker Mode**:
  - Browse and select files
  - Files copied to temp automatically

### Derivatives
- Generate TN (thumbnail) derivatives
- Generate SMALL derivative images
- Shows file counts and generation status
- Lists generated files

### Update CSV
- View CSV data before changes
- **Apply All Updates** button performs:
  - Filename updates (matched files)
  - CSV row append (for the CSV itself)
  - Empty ID generation
  - dginfo field population
- Side-by-side Before/After comparison
- Change count summary
- Manual save option

### Storage
- Azure upload interface (CollectionBuilder mode)
- Generate Alma upload script (Alma mode)
- View temp directory status

### Instructions
- Mode-specific follow-up instructions
- For Alma: Generate AWS S3 upload script
- Input fields for profile/import IDs
- Copy buttons for individual commands

### Log
- Real-time application log viewer
- Filter by log level (INFO, WARNING, ERROR)
- Search functionality
- Export log to file

### About
- Application information
- Current session data viewer
- Logging test buttons
- **Session preservation** functionality

---

## Session Preservation

Save your work and resume later without losing progress.

### Saving a Session

1. Navigate to **About** page
2. Click **"Preserve Session & Protect Temp Directory"**
3. Confirmation message shows number of keys saved
4. Session data saved to: `storage/data/persistent_session.json`
5. Temporary directory marked as protected

### What Gets Preserved

- All session keys and values
- Temp directory path and protection status
- File selection data (`temp_file_info`, `csv_filenames_for_matched`)
- CSV file paths and metadata
- Mode, storage, and collection settings
- Any other session state

### Restoring a Session

- **Automatic**: Session restores on next application launch
- Temp directory remains intact (not deleted)
- All files (CSV, OBJS, TN, SMALL) available
- Continue work from where you left off

### When to Use Session Preservation

- **End of work day**: Save progress on large batch
- **Multi-day projects**: Resume work tomorrow
- **Testing**: Preserve test scenarios
- **Before app updates**: Protect work in progress
- **Interrupted workflows**: Safe recovery point

### Managing Preserved Sessions

- Session persists until manually deleted or overwritten
- To clear: Delete `storage/data/persistent_session.json`
- To update: Click preserve button again (overwrites)
- Temp directory cleanup respects protection flag

---

## Troubleshooting

### CSV Not Validating

**Problem**: CSV file rejected with heading validation error

**Solutions**:
- Check CSV against verified headings file: `_data/verified_CSV_headings_for_Alma-D.csv`
- Remove any custom/unrecognized column headers
- Ensure column names match exactly (case-sensitive)
- For CollectionBuilder: use `verified_CSV_headings_for_GCCB_projects.csv`

### Fuzzy Search Not Finding Matches

**Problem**: Images not matching to CSV entries

**Solutions**:
- Lower similarity threshold (try 70% or 60%)
- Check that CSV column contains filenames (not full paths)
- Verify image filenames somewhat resemble CSV entries
- Remove special characters from filenames
- Check for encoding issues in CSV

### Derivatives Not Generating

**Problem**: TN or SMALL images not created

**Solutions**:
- Ensure temp directory exists and has files
- Check file permissions on temp directory
- Verify image files are valid (not corrupted)
- Check log for specific error messages
- Try generating one derivative type at a time

### Upload Script Not Working

**Problem**: AWS S3 upload fails or script errors

**Solutions**:
- Verify AWS credentials are configured: `aws configure`
- Test AWS connection: `aws s3 ls`
- Check profile ID and import ID are correct
- Ensure script has execute permissions: `chmod +x upload_to_alma.sh`
- Review AWS S3 bucket permissions
- Check network connectivity

### Session Not Restoring

**Problem**: Preserved session not loading on restart

**Solutions**:
- Verify file exists: `storage/data/persistent_session.json`
- Check file is valid JSON (not corrupted)
- Review application log for restore errors
- Temp directory must still exist at saved path
- Try preserving session again

### Application Crashes or Freezes

**Problem**: App becomes unresponsive

**Solutions**:
- Check `mdi.log` for error messages
- Verify Python version compatibility (3.9+)
- Update Flet: `pip install --upgrade flet==0.28.2`
- Clear temp directories manually
- Delete `persistent_session.json` and restart fresh
- Run in web mode: `flet run --web app.py`

### macOS FilePicker Not Opening

**Problem**: File browser dialog doesn't appear on macOS

**Solutions**:
- Use CSV mode instead of FilePicker mode
- Run in web mode: `flet run --web app.py`
- Grant appropriate macOS permissions
- Check for entitlement issues in console logs

---

## File Locations

### Application Files
- Main application: `app.py`
- Configuration: `_data/config.json`
- Persistent settings: `_data/persistent.json`
- Preserved sessions: `storage/data/persistent_session.json`
- Log file: `mdi.log`

### Temporary Files
- Temp directories: `storage/temp/file_selector_YYYYMMDD_HHMMSS_XXXXXXXX/`
- Subdirectories: `OBJS/`, `TN/`, `SMALL/`
- Working CSV copy: `{temp_dir}/csv_filename_YYYYMMDD_HHMMSS.csv`
- Upload script: `{temp_dir}/upload_to_alma.sh`

### Reference Data
- Alma CSV headings: `_data/verified_CSV_headings_for_Alma-D.csv`
- CollectionBuilder headings: `_data/verified_CSV_headings_for_GCCB_projects.csv`
- Collections list: `_data/cb_collections.json`
- File sources: `_data/file_sources.json`

---

## Tips and Best Practices

### CSV Preparation
- ✅ Use consistent, descriptive filenames in CSV
- ✅ Avoid special characters in filename column
- ✅ Test with small subset before full batch
- ✅ Keep backup copy of original CSV

### File Naming
- ✅ Use underscores instead of spaces
- ✅ Keep filenames under 200 characters
- ✅ Avoid special characters: `< > : " / \ | ? *`
- ✅ Use consistent naming pattern

### Workflow Efficiency
- ✅ Generate all derivatives before uploading
- ✅ Review CSV changes before saving
- ✅ Preserve session before long operations
- ✅ Test upload with small batch first
- ✅ Keep log file open for monitoring

### Performance
- ✅ Process files in batches of 50-100
- ✅ Close unnecessary applications during processing
- ✅ Use SSD for temp directory when possible
- ✅ Ensure adequate disk space (3x image total size)

---

## Getting Help

### Log Files
Check `mdi.log` for detailed error messages and operation history.

### Session Data
View current session state in **About** page to verify data integrity.

### Support Resources
- Application repository: [GitHub](https://github.com/McFateM/manage-digital-ingest-flet-oo)
- Grinnell College Libraries: [Digital Collections](https://digital.grinnell.edu)
- Alma Documentation: Ex Libris knowledge center
- CollectionBuilder: [Official documentation](https://collectionbuilder.github.io)

---

**Last Updated**: October 2025  
**Version**: 1.0  
**Flet Version**: 0.28.2  
**Python Version**: 3.9+
