# Parent/Child Relationship Handling in UpdateCSV

## Overview
This document describes the parent/child relationship logic implemented in the UpdateCSV view for CollectionBuilder mode.

## Implementation Date
November 3, 2025

## Purpose
In CollectionBuilder workflows, compound objects often have parent records with multiple child records. Parent records typically don't have their own image files but need to display a representative image (usually from the first child) in collection browsing views.

## Functionality

### When It Runs
- **Mode**: CollectionBuilder only (not applied in Alma mode)
- **Timing**: Step 3.7 in the `apply_all_updates()` method, after Azure URLs are populated but before dginfo processing
- **Trigger**: Automatic when "Apply All Updates" button is clicked

### Required CSV Columns
The logic requires the following columns to be present in the CSV:
- `objectid`: Unique identifier for each record
- `parentid`: Identifier linking child records to their parent (empty for parent records)
- `image_small`: URL to the small derivative image (optional, will be populated if missing)
- `image_thumb`: URL to the thumbnail derivative image (optional, will be populated if missing)

### Logic Flow

1. **Identify Parent Records**
   - Finds all rows where `parentid` is empty or NaN
   - These are considered parent records

2. **Find Children for Each Parent**
   - For each parent, searches for child records where `parentid` matches the parent's `objectid`

3. **Copy Derivative URLs**
   - If children exist, gets the **first child** in the dataset
   - Copies `image_small` from first child to parent (if child has a value)
   - Copies `image_thumb` from first child to parent (if child has a value)

4. **Update CSV**
   - Changes are made to the in-memory DataFrame
   - Saved when `save_csv_data()` is called after all updates

### Example

#### Before Processing
| objectid | parentid | image_small | image_thumb |
|----------|----------|-------------|-------------|
| album_01 |          |             |             |
| album_01_p1 | album_01 | https://.../album_01_p1_SMALL.jpg | https://.../album_01_p1_TN.jpg |
| album_01_p2 | album_01 | https://.../album_01_p2_SMALL.jpg | https://.../album_01_p2_TN.jpg |

#### After Processing
| objectid | parentid | image_small | image_thumb |
|----------|----------|-------------|-------------|
| album_01 |          | https://.../album_01_p1_SMALL.jpg | https://.../album_01_p1_TN.jpg |
| album_01_p1 | album_01 | https://.../album_01_p1_SMALL.jpg | https://.../album_01_p1_TN.jpg |
| album_01_p2 | album_01 | https://.../album_01_p2_SMALL.jpg | https://.../album_01_p2_TN.jpg |

## Logging

The implementation includes detailed logging:
- Info messages when derivative URLs are copied to parents
- Summary count of how many parent records were updated
- Warnings if required columns (`objectid` or `parentid`) are missing
- Info message if no parent/child updates were needed

### Log Examples
```
[INFO] Processing parent/child relationships...
[INFO] Copied image_small from child to parent (objectid=album_01)
[INFO] Copied image_thumb from child to parent (objectid=album_01)
[INFO] Updated 1 parent record(s) with child derivative URLs
```

## Edge Cases Handled

1. **Missing Columns**: If `objectid` or `parentid` columns don't exist, logs a warning and skips processing
2. **Empty Parent ObjectID**: Skips parents with empty/NaN `objectid` values
3. **No Children**: If a parent has no children, no updates are made
4. **Empty Child Values**: Only copies from child if child has a non-empty value
5. **Multiple Children**: Always uses the **first child** (index order) for derivative URLs

## Code Location

- **File**: `views/update_csv_view.py`
- **Method**: `apply_all_updates()`
- **Step**: 3.7 (after collection_id processing, before dginfo processing)
- **Lines**: Approximately 368-423 (may vary with updates)

## Future Enhancements

Potential improvements for consideration:
1. Allow user to select which child to use (not always first)
2. Support for selecting "best" child based on criteria (file size, specific naming pattern)
3. Configurable behavior (enable/disable via settings)
4. Handling of multiple parent levels (grandparent/parent/child hierarchies)

## Related Documentation

- CollectionBuilder compound object documentation: https://collectionbuilder.github.io/cb-docs/docs/metadata/compound-objects/
- Azure Storage URL structure: See `views/storage_view.py` upload logic
- CSV column mapping: See File Selector view column selection
