**This app will NOT `perform` any ingest or import, but it should be used to prep digital assets and metadata (identifiers, Handles, filenames, etc.) for subsequent operations.**

  
## Features of this app include:  
  
  - a processing mode selector: `Alma` or `CollectionBuilder`,  
  - object file selection via...  
    - a system file picker pop-up, or  
    - ability to read a list of digital object filenames from a `CSV` file,  
      - coupled with a "fuzzy" network file search utility, and
      - automatic update of the `CSV` with unique IDs, Handles, and revised file names/paths,
  - an optional derivative (thumbnails, small images, etc.) creation utility,
  - an `Azure Blob Storage` output selector for digital objects and derivatives,   
  - automatic naming and transport of files to `Azure` storage if needed, and
  - a follow-up instructions/scripts generator to assist in subsequent ingest or import operations.

