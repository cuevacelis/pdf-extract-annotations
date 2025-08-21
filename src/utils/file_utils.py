#!/usr/bin/env python3
"""
Utility functions for file operations
"""

import os
from pathlib import Path


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path (str): Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path (str): Path to the file

    Returns:
        bool: True if the file exists, False otherwise
    """
    return Path(file_path).is_file()
