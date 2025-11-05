# Deployment Guide: Splitting to Separate Repositories

This document provides instructions for deploying the split applications to their intended separate repositories.

## Overview

The applications in this repository have been split into two independent projects:

1. **Alma Edition** → Deploy to: `Digital-Grinnell/manage-digital-ingest-flet-Alma`
2. **CollectionBuilder Edition** → Deploy to: `Digital-Grinnell/manage-digital-ingest-flet-CollectionBuilder`

## Deployment Steps

### 1. Create Target Repositories

On GitHub, create two new repositories:

- `Digital-Grinnell/manage-digital-ingest-flet-Alma`
- `Digital-Grinnell/manage-digital-ingest-flet-CollectionBuilder`

### 2. Deploy Alma Edition

```bash
# From the root of this repository
cd manage-digital-ingest-flet-Alma

# Initialize as a new git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Alma Edition split from unified app"

# Add the remote repository
git remote add origin https://github.com/Digital-Grinnell/manage-digital-ingest-flet-Alma.git

# Push to the new repository
git branch -M main
git push -u origin main
```

### 3. Deploy CollectionBuilder Edition

```bash
# Return to the root of this repository
cd ..
cd manage-digital-ingest-flet-CollectionBuilder

# Initialize as a new git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: CollectionBuilder Edition split from unified app"

# Add the remote repository
git remote add origin https://github.com/Digital-Grinnell/manage-digital-ingest-flet-CollectionBuilder.git

# Push to the new repository
git branch -M main
git push -u origin main
```

## Post-Deployment Checklist

### For Each Repository

- [ ] Update repository description on GitHub
- [ ] Add appropriate topics/tags
- [ ] Configure repository settings (issues, wiki, etc.)
- [ ] Add LICENSE file if not already present
- [ ] Update README with repository-specific links
- [ ] Configure branch protection rules
- [ ] Set up CI/CD if needed

### Alma Repository Specific

- [ ] Verify Alma-specific documentation is present
- [ ] Check that ALMA-COMPOUND-HANDLING.md is included
- [ ] Ensure AWS S3 script generation documentation is clear
- [ ] Add Alma-specific examples or sample files

### CollectionBuilder Repository Specific

- [ ] Verify CollectionBuilder-specific documentation is present
- [ ] Check that PARENT-CHILD-CHANGES.md is included
- [ ] Ensure Azure Blob Storage documentation is clear
- [ ] Add CollectionBuilder-specific examples or sample files

## Repository Structure

Each deployed repository should have:

```
manage-digital-ingest-flet-Alma/  or  manage-digital-ingest-flet-CollectionBuilder/
├── README.md                     # Application-specific README
├── app.py                         # Main application file
├── logger.py                      # Logging configuration
├── utils.py                       # Utility functions
├── thumbnail.py                   # Thumbnail generation
├── python-requirements.txt        # Python dependencies
├── run.sh                         # Startup script
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── views/                         # View modules
│   ├── __init__.py
│   ├── base_view.py
│   ├── home_view.py
│   ├── about_view.py
│   ├── settings_view.py
│   ├── exit_view.py
│   ├── file_selector_view.py
│   ├── derivatives_view.py
│   ├── storage_view.py
│   ├── instructions_view.py
│   ├── update_csv_view.py
│   ├── log_view.py
│   └── log_overlay.py
├── _data/                         # Configuration and data files
│   ├── modes.json                 # Mode configuration (single mode)
│   ├── config.json                # Application configuration
│   ├── azure_blobs.json           # Azure storage configuration
│   ├── cb_collections.json        # CollectionBuilder collections (CB only)
│   ├── file_sources.json          # File source configuration
│   ├── persistent.json            # Persistent settings
│   ├── home.md                    # Home page content
│   ├── picker.md                  # File picker instructions
│   └── verified_CSV_headings_*.csv # Verified CSV column headings
├── assets/                        # Application assets
│   ├── Primary_Libraries.png      # Logo
│   └── update-csv-icon.png        # Icons
└── storage/                       # Runtime storage (ignored by git)
    ├── data/                      # Persistent data
    └── temp/                      # Temporary files
```

## Documentation Updates

### Update Links in README Files

After deployment, update any references to the repository location:

**In Alma Edition README:**
```markdown
## Repository
https://github.com/Digital-Grinnell/manage-digital-ingest-flet-Alma
```

**In CollectionBuilder Edition README:**
```markdown
## Repository
https://github.com/Digital-Grinnell/manage-digital-ingest-flet-CollectionBuilder
```

### Cross-Reference Between Apps

Add a note in each README referencing the other application:

**In Alma README:**
```markdown
## Related Projects
For CollectionBuilder workflows, see [manage-digital-ingest-flet-CollectionBuilder](https://github.com/Digital-Grinnell/manage-digital-ingest-flet-CollectionBuilder)
```

**In CollectionBuilder README:**
```markdown
## Related Projects
For Alma Digital workflows, see [manage-digital-ingest-flet-Alma](https://github.com/Digital-Grinnell/manage-digital-ingest-flet-Alma)
```

## Versioning

Both applications can now be versioned independently:

### Suggested Initial Versions

- **Alma Edition**: Start at `v2.0.0` (major change from unified app)
- **CollectionBuilder Edition**: Start at `v2.0.0` (major change from unified app)

### Semantic Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API/workflow changes
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

## Release Process

For each application, create a release on GitHub:

1. Create a git tag: `git tag -a v2.0.0 -m "Initial release: Alma Edition"`
2. Push the tag: `git push origin v2.0.0`
3. Create a GitHub release from the tag
4. Add release notes describing the split and features

## Maintenance

### Bug Fixes

If a bug is found that affects both applications:
1. Fix in both repositories independently
2. Ensure fixes are tested in each context
3. Release patches for both (can be different versions)

### Feature Development

Features can now be developed independently:
- Alma-specific features only in the Alma repository
- CollectionBuilder-specific features only in the CollectionBuilder repository

### Shared Code Updates

If utility functions or shared code needs updates:
1. Update in both repositories
2. Consider creating a shared library if significant overlap continues
3. Document any divergence in the repositories

## Testing After Deployment

For each deployed application:

1. **Clone the new repository**
   ```bash
   git clone https://github.com/Digital-Grinnell/manage-digital-ingest-flet-Alma.git
   cd manage-digital-ingest-flet-Alma
   ```

2. **Test installation**
   ```bash
   ./run.sh
   ```

3. **Verify key features**
   - Home page displays correctly
   - Settings show the correct mode
   - File selector works
   - Derivative generation functions
   - CSV update operates correctly
   - Storage/upload features work

4. **Check documentation**
   - README renders correctly on GitHub
   - All links work
   - Examples are clear

## Rollback Plan

If issues are discovered after deployment:

1. Keep this unified repository as a backup
2. Can re-split or adjust the deployment
3. Original commit history is preserved in this repository

## Future Considerations

### Packaging

Consider packaging each application for distribution:
- PyPI package
- Standalone executable (using PyInstaller or similar)
- Docker container
- Conda package

### CI/CD

Set up automated testing and deployment:
- GitHub Actions for automated tests
- Automated releases on tag push
- Automated Docker image builds

### Documentation Site

Consider creating a documentation site:
- GitHub Pages for each repository
- MkDocs or Sphinx for comprehensive docs
- API documentation if extending the apps

## Questions and Support

If you encounter issues during deployment:

1. Check this deployment guide
2. Review the README-SPLIT-APPS.md in this repository
3. Check individual application READMEs
4. Contact the development team

---

**Last Updated**: November 2025  
**Source Repository**: `McFateM/manage-digital-ingest-flet-oo`  
**Target Repositories**: 
- `Digital-Grinnell/manage-digital-ingest-flet-Alma`
- `Digital-Grinnell/manage-digital-ingest-flet-CollectionBuilder`
