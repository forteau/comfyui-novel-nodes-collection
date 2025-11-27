# Installation Guide

## 📦 Installation Methods

### Method 1: ComfyUI Manager (Recommended)

The easiest way to install:

1. Open ComfyUI
2. Click on "Manager" button
3. Click "Install Custom Nodes"
4. Search for "Novel Nodes Collection" or "Novel Cinematic"
5. Click "Install"
6. Restart ComfyUI

### Method 2: Git Clone (Manual)

For the latest development version:

```bash
# Navigate to your ComfyUI custom_nodes directory
cd ComfyUI/custom_nodes

# Clone the repository
git clone https://github.com/YOUR_USERNAME/comfyui-novel-nodes-collection.git

# Navigate to the cloned directory
cd comfyui-novel-nodes-collection

# Install optional dependencies (if needed)
pip install -r requirements.txt

# Restart ComfyUI
```

### Method 3: Download ZIP

If you don't have git:

1. Go to the [GitHub repository](https://github.com/YOUR_USERNAME/comfyui-novel-nodes-collection)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Copy the extracted folder to `ComfyUI/custom_nodes/`
5. Rename the folder to `comfyui-novel-nodes-collection` (remove `-main` if present)
6. Restart ComfyUI

## 🔧 Optional Dependencies

The nodes work with standard Python libraries, but you can install optional dependencies for additional features:

### For File Format Support (TurnkeyNovelToImages)

```bash
# For .docx files
pip install python-docx

# For .pdf files (choose one)
pip install PyMuPDF        # Recommended
# OR
pip install pdfplumber     # Alternative

# For .epub files
pip install ebooklib

# For .rtf files
pip install striprtf

# For .html files
pip install beautifulsoup4 lxml
```

### For Enhanced Text Analysis (Optional)

```bash
# For advanced NLP features
pip install spacy nltk

# For improved scene detection
pip install sentence-transformers
```

## ✅ Verifying Installation

After installation:

1. Restart ComfyUI completely
2. Right-click in the ComfyUI canvas
3. Look for these categories:
   - `🎬 Story Tools` (Novel Cinematic Orchestrator nodes)
   - `📚 Novel to Images` (Turnkey Novel to Images nodes)

If you see these categories, installation was successful!

## 🔍 Troubleshooting

### Nodes Don't Appear

1. **Check folder location**: Ensure the folder is in `ComfyUI/custom_nodes/`
2. **Check folder name**: Should be `comfyui-novel-nodes-collection`
3. **Restart ComfyUI**: Fully close and reopen ComfyUI
4. **Check console**: Look for error messages in the ComfyUI console

### Import Errors

If you see import errors:

```bash
# Navigate to the custom nodes directory
cd ComfyUI/custom_nodes/comfyui-novel-nodes-collection

# Install dependencies
pip install -r requirements.txt
```

### File Format Not Supported

If you get errors loading certain file types:

```bash
# Install the specific dependency for that format
# See "Optional Dependencies" section above
```

### Python Version Issues

- Requires Python 3.8 or higher
- Check your Python version: `python --version`
- If using an older version, consider upgrading

## 🔄 Updating

### Via ComfyUI Manager

1. Open ComfyUI Manager
2. Click "Update All" or find this package and click "Update"
3. Restart ComfyUI

### Via Git

```bash
cd ComfyUI/custom_nodes/comfyui-novel-nodes-collection
git pull origin main
pip install -r requirements.txt  # Update dependencies if needed
```

## 🗑️ Uninstalling

### Via ComfyUI Manager

1. Open ComfyUI Manager
2. Find "Novel Nodes Collection"
3. Click "Uninstall"
4. Restart ComfyUI

### Manual Uninstall

```bash
# Simply delete the folder
cd ComfyUI/custom_nodes
rm -rf comfyui-novel-nodes-collection  # Linux/Mac
# OR
rmdir /s comfyui-novel-nodes-collection  # Windows
```

## 💡 Next Steps

After installation:

1. Check the [README.md](README.md) for usage examples
2. Review individual node documentation:
   - [Novel Cinematic Orchestrator](NovelCinematicOrchestrator/README.md)
   - [Turnkey Novel to Images](TurnkeyNovelToImages/README.md)
3. Try the example workflows
4. Join the community discussions

## 🆘 Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/YOUR_USERNAME/comfyui-novel-nodes-collection/issues)
2. Search for similar problems
3. Create a new issue with:
   - Your ComfyUI version
   - Python version
   - Operating system
   - Error messages
   - Steps to reproduce

---

Happy creating! 🎬📚
