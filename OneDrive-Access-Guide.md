# OneDrive Access Guide for Manage Digital Ingest Application

**Date**: November 3, 2025

## Question

I'd like to have the ability to look in OneDrive for CSV files and digital object files alike. Do you know what I need for OneDrive information to be able to find and copy/read files from someone's OneDrive? Is there a link or key that a OneDrive owner can send me to provide such access?

## Answer

Yes, there are several ways to access files from OneDrive programmatically. Here's what you need:

## OneDrive Access Options

### 1. **Shared Link (Simplest for Read Access)**
OneDrive owners can share individual files or folders:
- **Shareable Link**: Right-click file/folder → Share → Copy link
- **Types**:
  - View-only link (can read/download)
  - Edit link (can modify)
  - Link with expiration date
  - Password-protected link

**What you get**: A URL like `https://1drv.ms/u/s!...` or `https://onedrive.live.com/...`

**Limitations**: 
- Need to parse the web interface or use Microsoft Graph API
- Not ideal for automated batch operations

### 2. **Microsoft Graph API (Best for Automation)**
Official Microsoft API for accessing OneDrive programmatically.

**What the owner needs to provide:**
- **App Registration** in Azure AD (they create this)
- **Client ID**: Identifies your application
- **Client Secret**: Password for your app
- **Tenant ID**: Their organization ID (if work/school account)
- **Permissions**: Read/write permissions to specific folders

**Example credentials needed:**
```env
ONEDRIVE_CLIENT_ID=abc123...
ONEDRIVE_CLIENT_SECRET=xyz789...
ONEDRIVE_TENANT_ID=contoso.onmicrosoft.com
```

**Access patterns:**
- User authenticates once via OAuth
- App gets access token
- Token allows API calls to list/read/write files

### 3. **OneDrive Sync Folder (Easiest Integration)**
If the OneDrive owner:
- Syncs their OneDrive to their local machine
- Shares that local folder path with you

**What you need**: Just a local folder path
```
/Users/username/OneDrive/SharedFiles
# or
C:\Users\Username\OneDrive\SharedFiles
```

**Your app** can then access it like any local folder - no API needed!

**Limitations**: Only works on machines with OneDrive sync enabled

### 4. **OneDrive Personal vs Business**

**OneDrive Personal (consumer accounts):**
- Uses Microsoft Account authentication
- Simpler setup
- Owner creates app registration at https://portal.azure.com

**OneDrive for Business (Microsoft 365):**
- Uses Azure AD authentication
- Requires organization admin approval for app registration
- More control over permissions

## Recommended Approach for Your App

Given your Flet app is already working with local files and Azure, I recommend:

### **Option A: OneDrive Sync + Local Access (Easiest)**
```python
# User provides path to their synced OneDrive folder
ONEDRIVE_PATH = "/Users/mcfatem/OneDrive/DigitalIngest"

# Your app treats it like any other folder
csv_files = glob.glob(f"{ONEDRIVE_PATH}/**/*.csv", recursive=True)
```

**Setup for owner:**
1. Install OneDrive app on their computer
2. Sync the folders you need access to
3. Share the local path with users of your app

### **Option B: Microsoft Graph API (Most Flexible)**
Owner provides credentials, your app accesses OneDrive directly.

**Python package:**
```bash
pip install msal msgraph-sdk
```

**Example code structure:**
```python
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential

# Authenticate
credential = ClientSecretCredential(
    tenant_id=os.getenv("ONEDRIVE_TENANT_ID"),
    client_id=os.getenv("ONEDRIVE_CLIENT_ID"),
    client_secret=os.getenv("ONEDRIVE_CLIENT_SECRET")
)

# Create client
client = GraphServiceClient(credential)

# List files
items = await client.me.drive.root.children.get()

# Download file
file_content = await client.me.drive.items[item_id].content.get()
```

### **Option C: Shared Folder URL (Manual Hybrid)**
Owner shares a OneDrive folder URL, user downloads files manually or via web interface.

## Implementation Recommendation

For your specific app, I'd suggest:

1. **Short term**: Add support for OneDrive sync folder paths
2. **Long term**: Add Microsoft Graph API integration

## Next Steps

Potential implementation options:
1. Add a OneDrive folder path option to your file selector
2. Implement Microsoft Graph API integration
3. Create documentation for setting up OneDrive access

## Additional Resources

- **Microsoft Graph API Documentation**: https://docs.microsoft.com/en-us/graph/
- **OneDrive API Reference**: https://docs.microsoft.com/en-us/onedrive/developer/
- **Azure App Registration**: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps
- **MSAL Python Library**: https://github.com/AzureAD/microsoft-authentication-library-for-python

## Contact

For questions about implementing OneDrive access in the Manage Digital Ingest application, refer to this document and the related application documentation.
