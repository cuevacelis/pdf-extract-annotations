#!/usr/bin/env python3
"""
Utility functions for file operations
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Union


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path (str): Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)


def save_json(data: Any, file_path: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.

    Args:
        data (Any): Data to save
        file_path (str): Path to the output file
        indent (int): Indentation level for JSON formatting
    """
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json(file_path: str) -> Any:
    """
    Load data from a JSON file.

    Args:
        file_path (str): Path to the JSON file

    Returns:
        Any: Loaded data

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path (str): Path to the file

    Returns:
        bool: True if the file exists, False otherwise
    """
    return Path(file_path).is_file()


def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.

    Args:
        file_path (str): Path to the file

    Returns:
        str: File extension (without the dot)
    """
    return Path(file_path).suffix.lstrip(".")


def list_files(directory_path: str, extension: str = None) -> List[str]:
    """
    List all files in a directory, optionally filtered by extension.

    Args:
        directory_path (str): Path to the directory
        extension (str, optional): File extension to filter by (without the dot)

    Returns:
        List[str]: List of file paths
    """
    directory = Path(directory_path)
    if not directory.is_dir():
        return []

    if extension:
        return [str(f) for f in directory.glob(f"*.{extension}")]
    else:
        return [str(f) for f in directory.glob("*") if f.is_file()]


def get_filename_without_extension(file_path: str) -> str:
    """
    Get the filename without its extension.

    Args:
        file_path (str): Path to the file

    Returns:
        str: Filename without extension
    """
    return Path(file_path).stem
