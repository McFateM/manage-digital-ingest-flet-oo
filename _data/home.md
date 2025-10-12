**This app will NOT `perform` any ingest or import, but it should be used to prep digital assets and metadata (filenames, etc.) for subsequent operations.**

  
## Features of this app include:  
  
  - a processing mode selector: `Alma` or `CollectionBuilder`,  
  - object file selection via...  
    - a system file picker pop-up, or  
    - ability to read a list of digital object filenames from a `Google Sheet` or `CSV` file,  
      - coupled with a "fuzzy" network file search utility, and
      - automatic update of `Google Sheet` or `CSV` with revised file names and paths,
  - an optional derivative (thumbnails, small images, etc.) creation utility,
  - an `Azure Blob Storage` output selector for digital objects and derivatives, and  
  - automatic naming and transport of files to `Azure` storage.

