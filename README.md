# Smart File Organizer

> A powerful and flexible Python utility that automatically organizes files into category-based folders based on file extensions. Features both a modern GUI and a comprehensive CLI.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Graphical User Interface (GUI)](#graphical-user-interface-gui)
  - [Command Line Interface (CLI)](#command-line-interface-cli)
- [Supported File Types](#supported-file-types)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Release](#release)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Smart File Organizer simplifies file management by automatically sorting files into organized category folders. Whether you need to tidy up a cluttered downloads folder or maintain an organized archive, this tool handles the work for you.

**Key benefits:**
- Save time with automatic file organization
- Keep your workspace clean and structured
- Support for 40+ file formats across 5 categories
- Flexible deployment via GUI or CLI
- Real-time folder monitoring with Watch Mode

---

## Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| **Automatic Sorting** | Organizes files by extension into category folders |
| **Watch Mode** | Continuously monitors folders for new files |
| **Reverse Sorting** | Restores organized files back to original locations |
| **Recursive Processing** | Option to include subfolders in sorting |
| **Duplicate Handling** | Automatic renaming when files already exist |
| **Activity Logging** | Records all operations to a log file |

### User Interfaces

- **GUI Mode**: Modern dark-themed interface with real-time activity log
- **CLI Mode**: Full-featured command-line interface with flexible options

### Extensibility

- Easily customizable file type mappings via `config.py`
- Add new categories or extend existing ones without code changes

---

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Steps

1. Clone or download the repository:

```bash
git clone https://github.com/yourusername/smart-file-organizer.git
cd smart-file-organizer
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Build Executable (Optional)

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller smartsorter.spec
```

The executable will be available in the `dist/` folder.

---

## Quick Start

### GUI Mode

```bash
python ui/app.py
```

1. Select **Source Folder** (files to organize)
2. Select **Destination Folder** (where organized files go)
3. Choose categories to include
4. Click **Sort Now** to begin

### CLI Mode

```bash
python main.py -s ./source -d ./destination
```

---

## Usage

### Graphical User Interface (GUI)

Launch the GUI with:

```bash
python ui/app.py
```

#### Interface Components

| Component | Description |
|-----------|-------------|
| **Mode Selection** | Choose between Manual Sort or Watch Mode |
| **Source Folder** | Browse and select the folder containing files to organize |
| **Destination Folder** | Browse and select where organized folders will be created |
| **Options Panel** | Configure recursive processing, logging, and duplicate handling |
| **Category Selection** | Toggle which file categories to process |
| **Activity Log** | Real-time display of sorting operations |

#### GUI Options

- **Recursive**: Include files from subfolders
- **Log Activity**: Save operations to `activity_log.txt`
- **Handle Duplicates**: Automatically rename files if destination exists

---

### Command Line Interface (CLI)

#### Basic Usage

```bash
# Sort with default settings
python main.py

# Specify source and destination folders
python main.py -s /path/to/source -d /path/to/destination

# Watch mode for continuous monitoring
python main.py -m watch -s /path/to/source -d /path/to/destination
```

#### Advanced Options

```bash
# Recursive sorting with specific categories
python main.py -s ./files -d ./organized --recursive --categories Audio Video Images

# Enable logging
python main.py -s ./files -d ./organized --log

# Reverse sort (restore files to original location)
python main.py -m reverse -s ./organized -d ./restored

# Combine multiple options
python main.py -s ./downloads -d ./organized -m watch --recursive --log
```

#### CLI Arguments Reference

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--source` | `-s` | Current directory | Source folder path containing files to sort |
| `--destination` | `-d` | `./sorted` | Destination folder path for organized files |
| `--mode` | `-m` | `sort` | Operation mode: `sort`, `watch`, or `reverse` |
| `--recursive` | `-r` | `False` | Include subfolders in processing |
| `--categories` | | All | Space-separated list of categories to process |
| `--log` | | `False` | Enable logging to `activity_log.txt` |
| `--help` | `-h` | | Show help message and exit |

---

## Supported File Types

The organizer supports the following file categories and extensions:

| Category | File Extensions |
|----------|-----------------|
| **Audio** | `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`, `.m4a`, `.aiff` |
| **Video** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.3gp` |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.svg`, `.webp`, `.ico`, `.raw`, `.heic` |
| **Documents** | `.pdf`, `.doc`, `.docx`, `.txt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.odt`, `.ods`, `.odp`, `.rtf`, `.csv`, `.md`, `.epub` |
| **Archives** | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2` |
| **Others** | All other file types |

---

## Configuration

File type mappings can be customized by editing `config.py`:

```python
FILE_TYPES = {
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff"],
    "Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".ico", ".raw", ".heic"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp", ".rtf", ".csv", ".md", ".epub"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Others": [],
}
```

**Configuration Notes:**

- Extensions are case-insensitive (`.JPG` and `.jpg` are treated the same)
- Always include the leading dot when adding extensions
- The "Others" category captures any files not matching other categories
- New categories will automatically appear as folders in the destination directory

---

## Project Structure

```
smart-file-organizer/
├── config.py           # File type configuration
├── main.py             # CLI entry point
├── sorter.py           # Core sorting logic
├── requirements.txt    # Python dependencies
├── smartsorter.spec    # PyInstaller configuration
├── README.md           # Project documentation
├── LICENSE             # MIT License
├── ui/
│   └── app.py          # GUI application (Tkinter)
├── build/              # PyInstaller build directory
└── dist/               # PyInstaller output
```

### File Descriptions

| File | Description |
|------|-------------|
| `config.py` | Defines file extension to category mappings |
| `sorter.py` | Core logic for sorting, moving, watching, and reversing files |
| `main.py` | Command-line interface and argument parsing |
| `ui/app.py` | Graphical user interface built with Tkinter |

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---
## Release
[Download Latest Release](https://github.com/Favour-OE/smart-file-organizer/releases)

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support

If you encounter any issues or have questions:

- Open an issue on [GitHub Issues](https://github.com/Favour-OE/smart-file-organizer/issues)
- Check the documentation in this README
- Review the inline code comments for implementation details
