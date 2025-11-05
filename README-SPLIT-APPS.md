# Manage Digital Ingest - Split Applications

This repository contains two separate applications for managing digital object ingest at Grinnell College:

1. **Manage Digital Ingest: Alma Edition** - For Alma Digital workflows
2. **Manage Digital Ingest: CollectionBuilder Edition** - For CollectionBuilder static sites

## 📁 Repository Structure

```
.
├── manage-digital-ingest-flet-Alma/          # Alma-specific application
│   ├── app.py                                 # Main Alma app
│   ├── views/                                 # Alma-specific views
│   ├── _data/                                 # Alma configuration and data
│   └── README.md                              # Alma documentation
│
├── manage-digital-ingest-flet-CollectionBuilder/  # CollectionBuilder-specific application
│   ├── app.py                                      # Main CollectionBuilder app
│   ├── views/                                      # CollectionBuilder-specific views
│   ├── _data/                                      # CollectionBuilder configuration and data
│   └── README.md                                   # CollectionBuilder documentation
│
└── README-SPLIT-APPS.md                       # This file
```

## 🎯 Which App Should I Use?

### Use the **Alma Edition** if you are:
- Ingesting digital objects into Alma Digital (institutional repository)
- Working with compound objects (parent/child relationships)
- Need to generate AWS S3 upload scripts for Alma
- Require Alma-specific metadata (collection_id, compound relationships, etc.)
- Creating thumbnails with `.clientThumb` extension for Alma

### Use the **CollectionBuilder Edition** if you are:
- Building CollectionBuilder static websites
- Managing objects for CollectionBuilder collections
- Need to upload to Azure Blob storage for CollectionBuilder
- Creating thumbnails and small images for web display
- Working with CollectionBuilder parent/child relationships

## 🚀 Getting Started

Each application is self-contained and can be run independently.

### For Alma Edition:

```bash
cd manage-digital-ingest-flet-Alma
./run.sh
```

See `manage-digital-ingest-flet-Alma/README.md` for detailed instructions.

### For CollectionBuilder Edition:

```bash
cd manage-digital-ingest-flet-CollectionBuilder
./run.sh
```

See `manage-digital-ingest-flet-CollectionBuilder/README.md` for detailed instructions.

## 🔑 Key Differences

| Feature | Alma Edition | CollectionBuilder Edition |
|---------|-------------|---------------------------|
| **Mode** | Fixed to "Alma" | Fixed to "CollectionBuilder" |
| **Collection Selector** | Not available | Required for selecting CB collection |
| **Derivatives** | TN thumbnails (200x200) with .clientThumb | TN (400x400) + SMALL (800x800) |
| **Storage** | AWS S3 script generation | Azure Blob Storage upload |
| **Compound Objects** | Full parent/child with TOC | Parent/child relationships |
| **CSV Columns** | Alma-D verified headings | GCCB project verified headings |

## 📋 Common Features

Both applications share:
- Fuzzy filename matching for CSV-to-file pairing
- File picker and CSV-based file selection
- Derivative image generation
- CSV metadata updates
- Session preservation
- Theme support (Light/Dark)
- Comprehensive logging

## 🔧 Requirements

Both applications require:
- Python 3.7 or higher
- Dependencies listed in `python-requirements.txt` (same for both apps)
- Bash shell for the `run.sh` script

## 📚 Documentation

Each application has its own comprehensive documentation:

### Alma Documentation:
- `manage-digital-ingest-flet-Alma/README.md` - Alma-specific guide
- `ALMA-COMPOUND-HANDLING.md` - Compound object processing details
- `USER.md` - General user guide (Alma workflow section)

### CollectionBuilder Documentation:
- `manage-digital-ingest-flet-CollectionBuilder/README.md` - CollectionBuilder-specific guide
- `PARENT-CHILD-CHANGES.md` - Parent/child relationship details
- `USER.md` - General user guide (CollectionBuilder workflow section)

### Shared Documentation:
- `HISTORY.md` - Development history and feature timeline
- `OO_MIGRATION.md` - Object-oriented structure migration notes

## 🏗️ Development

Both applications are built with:
- **Framework**: Flet (Python UI framework)
- **Architecture**: Object-oriented with base views
- **Storage**: Pandas DataFrames for CSV processing
- **Cloud Integration**: Azure Storage SDK / AWS CLI

## 🎓 Background

These applications were developed for Grinnell College Libraries to streamline the digital object preparation and ingest process. The split into two applications allows each to be optimized for its specific workflow without the complexity of mode switching.

## 📝 Migration Notes

This split was created from the original unified `manage-digital-ingest-flet-oo` application that supported both Alma and CollectionBuilder modes via a mode selector. The split provides:

1. **Simplified user experience** - No mode selection confusion
2. **Cleaner codebase** - Less conditional logic based on mode
3. **Focused documentation** - Each app documents only its workflow
4. **Independent deployment** - Each can be packaged and distributed separately

## 🔗 Related Repositories

For separate deployment, these applications can be extracted to:
- `Digital-Grinnell/manage-digital-ingest-flet-Alma`
- `Digital-Grinnell/manage-digital-ingest-flet-CollectionBuilder`

## 👥 Support

For questions or issues:
- Check the README in each application directory
- Review the documentation files listed above
- Contact Grinnell College Libraries Digital Team

---

**Note**: Both applications are fully functional and self-contained. Choose the one that matches your workflow and run it from its directory.
