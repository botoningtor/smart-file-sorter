# Smart File Sorter

A lightweight, robust, and zero-dependency Python script that automatically organizes files in a specified directory into categorized folders based on their extensions. Perfect for cleaning up your cluttered `Downloads` or `Desktop` folders.

## Features

- **Dynamic Configuration**: Keeps extensions mapped to folders in an external `conf.json` file. Modify it without changing the source code.
- **Safety First (`--dry-run`)**: Test the sorting process in simulation mode to see what happens before any files are actually moved.
- **Smart Name Conflict Resolution**: If a file with the same name already exists in the destination folder, it will automatically append an incremented suffix (e.g., `file_1.txt`, `file_2.txt`) instead of overwriting your data.
- **Detailed Analytics**: Outputs comprehensive operational logs and a summary of files moved per category at the end of execution.
- **Clean & Maintained**: Compliant with PEP 8 standards, fully typed, and verified against modern linters (Pylint and Ruff).

## Requirements

- Python 3.6 or higher
- No external libraries required (uses built-in modules only)

## Installation

Clone this repository or download the source files directly:

```bash
git clone https://github.com
cd smart-file-sorter
```

## Usage

Run the script by passing the full path of the target directory as an argument:

```bash
python sort.py "C:\Users\Username\Downloads"
```

### Modes and Options

#### 1. Simulation Mode (Recommended for first run)
Use the `--dry-run` flag to safely preview the sorting process without moving any files:

```bash
python sort.py "D:\TargetFolder" --dry-run
```

#### 2. Help Menu
View the built-in manual and description of arguments:

```bash
python sort.py --help
```

## Configuration (`conf.json`)

On the very first run, the script automatically generates a default `conf.json` file in its root directory. You can easily customize it to add your own extensions or modify the target folder names.

Example structure:

```json
{
    ".zip": "Archives",
    ".pdf": "Documents",
    ".jpg": "Images",
    ".mp4": "Video",
    ".py": "Web"
}
```

*Note: Unrecognized extensions will automatically be moved to a folder named after their capitalized extension (e.g., `.xyz` goes to `XYZ`). Files without any extension will go to `No_Extension`.*

## Logging

A detailed log file named `sort_log.txt` is automatically created and updated directly inside the target directory during every real execution. It tracks every action taken, as well as any errors encountered (like locked or system-protected files).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
