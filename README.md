# Smart File Organizer

A Python utility that automatically organizes files into category-based folders based on their file extensions. Supports both CLI and GUI interfaces.

## Features

### File Categories
- **Audio**: `.mp3`, `.wav`
- **Video**: `.mp4`, `.mkv`
- **Images**: `.jpg`, `.png`, `.jpeg`
- **Documents**: `.pdf`, `.docx`, `.txt`
- **Others**: Any unclassified files

### Core Functionality
- Automatic file sorting by extension
- Reverse sorting (restore files to original location)
- Watch mode for continuous monitoring
- Recursive folder processing
- Duplicate file handling (automatic renaming)
- Activity logging to file
- GUI and CLI interfaces

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI

```bash
python ui/app.py
```

The GUI includes:
- **Mode Selection**: Manual Sort or Watch Mode
- **Folder Selection**: Source and Destination folders with browse buttons
- **Options**:
  - Recursive (include subfolders)
  - Log to activity_log.txt
  - Handle duplicates (rename if exists)
- **Category Selection**: Checkboxes for each file category
- **Action Buttons**: Sort Now and Restore Files
- **Activity Log**: Real-time display of operations

### CLI

```bash
# Basic usage (default folders)
python main.py

# Custom source and destination
python main.py -s ./my_files -d ./organized

# Watch mode (continuous monitoring)
python main.py -m watch

# Recursive with specific categories
python main.py --recursive --categories Audio Video

# With logging
python main.py --log
```

#### CLI Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--source` | `-s` | Source folder path |
| `--destination` | `-d` | Destination folder path |
| `--mode` | `-m` | `sort` (default) or `watch` |
| `--recursive` | `-r` | Include subfolders |
| `--categories` | | Filter by categories (e.g., `Audio Video`) |
| `--log` | | Enable logging to activity_log.txt |

## File Types Configuration

Edit `config.py` to add or modify file extensions:

```python
FILE_TYPES = {
    "Audio": [".mp3", ".wav"],
    "Video": [".mp4", ".mkv"],
    "Images": [".jpg", ".png", ".jpeg"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Others": [],
}
```

## License

MIT License
