"""Script for automatically sorting files into category folders based on extensions."""

import argparse
import sys
import logging
import json
from pathlib import Path
import shutil
from collections import defaultdict

# Default configuration to fall back on or create
DEFAULT_FILE_TYPE_MAP = {
    # Archives
    ".7z": "Archives", ".zip": "Archives", ".rar": "Archives",
    # Documents
    ".docx": "Documents", ".pdf": "Documents", ".txt": "Documents",
    # Images
    ".gif": "Images", ".jfif": "Images", ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".webp": "Images",
    # Video
    ".mp4": "Video", ".mp3": "Video",
    # Programs
    ".exe": "Programs", ".msi": "Programs",
    # Web & Code
    ".htm": "Web", ".py": "Web", ".torrent": "Web",
    # System
    ".ini": "System", ".log": "System", ".save": "System"
}


def load_file_type_map() -> dict:
    """Load extension mapping from conf.json or create it if missing."""
    config_path = Path(__file__).parent / "conf.json"
    
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            # If JSON is corrupted, log error and fallback to defaults
            print(f"Warning: Failed to parse 'conf.json' ({e}). Using defaults.")
            return DEFAULT_FILE_TYPE_MAP
    else:
        # Create default conf.json if it doesn't exist
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_FILE_TYPE_MAP, f, indent=4, ensure_ascii=False)
        except OSError as e:
            print(f"Warning: Could not create default 'conf.json' ({e}).")
        return DEFAULT_FILE_TYPE_MAP


def setup_args() -> argparse.Namespace:
    """Configure command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Automated script to sort files into category folders."
    )
    parser.add_argument(
        'path',
        type=str,
        help="Full path to the directory that needs sorting"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Simulation mode: show changes without moving any files"
    )
    return parser.parse_args()


def setup_logging(folder: Path) -> Path:
    """Configure logging to file and standard output."""
    log_file = folder / "sort_log.txt"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return log_file


def get_target_folder_name(item: Path, file_type_map: dict) -> str:
    """Determine the destination folder name based on the file extension."""
    ext = item.suffix.lower()
    if not ext:
        return 'No_Extension'
    if ext in file_type_map:
        return file_type_map[ext]
    return ext[1:].upper()


def resolve_name_conflict(target_dir: Path, file_name: str) -> Path:
    """Resolve file name conflicts by appending an incremented suffix (e.g., file_1.txt)."""
    target_path = target_dir / file_name
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1

    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = target_dir / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def process_file(item: Path, folder: Path, log_file: Path, dry_run: bool, stats: dict, file_type_map: dict) -> None:
    """Process and move a single file to its destination category folder."""
    if item == log_file:
        return

    target_folder_name = get_target_folder_name(item, file_type_map)
    target_dir = folder / target_folder_name

    # 1. Create target directory
    if not dry_run:
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logging.error("Failed to create directory %s: %s", target_folder_name, e)
            stats["errors"] += 1
            return

    # 2. Resolve name conflicts if the file already exists
    target_path = resolve_name_conflict(target_dir, item.name)
    was_conflict = target_path.name != item.name

    # 3. Move the file
    if dry_run:
        conflict_msg = " [NAME CONFLICT -> will be renamed]" if was_conflict else ""
        logging.info("[DRY-RUN] Will move: %s -> %s%s", item.name, target_folder_name, conflict_msg)
        stats["categories"][target_folder_name] += 1
        stats["moved"] += 1
    else:
        try:
            shutil.move(str(item), str(target_path))
            if was_conflict:
                logging.info("Moved with rename: %s -> %s/%s", item.name, target_folder_name, target_path.name)
            else:
                logging.info("Successfully moved: %s -> %s", item.name, target_folder_name)
            stats["categories"][target_folder_name] += 1
            stats["moved"] += 1
        except PermissionError:
            logging.error("Permission denied: File %s is locked by another process", item.name)
            stats["errors"] += 1
        except OSError as e:
            logging.error("Error moving file %s: %s", item.name, e)
            stats["errors"] += 1


def print_statistics(stats: dict, log_file: Path, dry_run: bool) -> None:
    """Display final execution statistics."""
    logging.info("--- Sorting Completed %s ---", "(DRY-RUN SIMULATION)" if dry_run else "")
    logging.info("Total files moved: %s", stats["moved"])
    
    if stats["categories"]:
        logging.info("Statistics by category:")
        for cat, count in sorted(stats["categories"].items()):
            logging.info("  - %s: %s file(s)", cat, count)
            
    logging.info("Errors encountered: %s", stats["errors"])
    if not dry_run:
        logging.info("Log file saved at: %s", log_file)


def main() -> None:
    """Application entry point."""
    args = setup_args()
    clean_path = args.path.strip('"\'')
    folder = Path(clean_path)

    if not folder.exists() or not folder.is_dir():
        print(f"Error: Path '{clean_path}' not found or is not a directory.")
        sys.exit(1)

    log_file = setup_logging(folder)
    
    # Dynamic configuration loading
    file_type_map = load_file_type_map()
    
    if args.dry_run:
        logging.info("=== RUNNING IN DRY-RUN MODE ===")
    logging.info("--- Starting sorting for directory: %s ---", folder)

    # Initialize statistics dictionary
    stats = {
        "moved": 0,
        "errors": 0,
        "categories": defaultdict(int)
    }

    try:
        # Convert to list to avoid modifying the iterator while moving files
        items = list(folder.iterdir())
        for item in items:
            if item.is_file():
                process_file(item, folder, log_file, args.dry_run, stats, file_type_map)
                
    except OSError as main_error:
        logging.critical("Critical file system error: %s", main_error, exc_info=True)
    except Exception as main_error:  # pylint: disable=broad-exception-caught
        logging.critical("Unexpected critical error: %s", main_error, exc_info=True)

    print_statistics(stats, log_file, args.dry_run)


if __name__ == "__main__":
    main()
