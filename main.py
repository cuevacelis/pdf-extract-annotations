#!/usr/bin/env python3
"""
PDF Extract - Main Menu

This script provides a command-line interface to access the different
functionalities of the PDF Extract tool.
"""

import os
import sys
import argparse
from pathlib import Path

from src.extractors.text_extractor import extract_text_from_pdf, save_text
from src.extractors.annotation_extractor import PDFAnnotationExtractor
from src.utils.file_utils import ensure_directory_exists, file_exists

# Configuration
DEFAULT_INPUT_DIR = "data/input"
DEFAULT_PDF = None  # Will be set dynamically


def print_header():
    """Print the application header."""
    print("\n" + "=" * 60)
    print("PDF EXTRACT TOOL".center(60))
    print("=" * 60)


def print_menu():
    """Print the main menu options."""
    print("\nMAIN MENU:")
    print("1. Extract text from PDF")
    print("2. Extract annotations from PDF")
    print("0. Exit")
    print("-" * 60)


def extract_text(pdf_path=None):
    """
    Extract text from a PDF file.

    Args:
        pdf_path (str, optional): Path to the PDF file. If None, the user will be prompted.
    """
    print("\n--- TEXT EXTRACTION ---")

    if pdf_path is None:
        pdf_path = get_pdf_path()

    # Verify that the file exists
    if not file_exists(pdf_path):
        print(f"Error: The file {pdf_path} does not exist")
        return

    # Ask for extraction options
    by_page = input("Extract text by page? (y/n, default: n): ").lower() == "y"
    include_numbers = input("Include page numbers? (y/n, default: y): ").lower() != "n"

    # Extract text
    print(f"\nExtracting text from {pdf_path}...")
    text = extract_text_from_pdf(
        pdf_path, by_page=by_page, include_numbers=include_numbers
    )

    # Determine output path
    pdf_file = Path(pdf_path)
    output_dir = "data/output/text"
    ensure_directory_exists(output_dir)
    output_path = f"{output_dir}/{pdf_file.stem}_text.txt"

    # Save text
    save_text(text, output_path)

    print(f"Text extraction completed. Text saved to: {output_path}")
    input("\nPress Enter to continue...")


def extract_annotations(pdf_path=None):
    """
    Extract annotations from a PDF file.

    Args:
        pdf_path (str, optional): Path to the PDF file. If None, the user will be prompted.
    """
    print("\n--- ANNOTATION EXTRACTION ---")

    if pdf_path is None:
        pdf_path = get_pdf_path()

    # Verify that the file exists
    if not file_exists(pdf_path):
        print(f"Error: The file {pdf_path} does not exist")
        return

    # Extract annotations
    print(f"\nExtracting annotations from {pdf_path}...")
    extractor = PDFAnnotationExtractor(pdf_path)
    annotations = extractor.extract_annotations()

    if not annotations:
        print("No annotations found in the PDF.")
        input("\nPress Enter to continue...")
        return

    # Determine output path
    pdf_file = Path(pdf_path)
    output_dir = "data/output/annotations"
    ensure_directory_exists(output_dir)
    output_path = f"{output_dir}/{pdf_file.stem}_annotations.json"

    # Save annotations
    extractor.save_to_json(annotations, output_path)

    # Print summary
    print(f"\nAnnotations saved to: {output_path}")
    print("\nAnnotation Summary:")
    extractor.print_summary(annotations)

    input("\nPress Enter to continue...")
    return output_path


def get_pdf_path():
    """Get PDF path from available files or user input."""
    if os.path.isdir(DEFAULT_INPUT_DIR):
        pdf_files = [f for f in os.listdir(DEFAULT_INPUT_DIR) if f.endswith(".pdf")]

        if pdf_files:
            # If there's only one PDF file, use it automatically
            if len(pdf_files) == 1:
                pdf_path = f"{DEFAULT_INPUT_DIR}/{pdf_files[0]}"
                print(f"Using the only available PDF: {pdf_files[0]}")
                return pdf_path

            print("Available PDF files:")
            for i, file in enumerate(pdf_files, 1):
                print(f"{i}. {file}")

            try:
                choice = int(
                    input("\nSelect a file number (or 0 to enter a different path): ")
                )
                if 1 <= choice <= len(pdf_files):
                    return f"{DEFAULT_INPUT_DIR}/{pdf_files[choice-1]}"
            except ValueError:
                pass

    return input("Enter the path to the PDF file: ")


def main():
    """Main function to run the PDF Extract tool."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PDF Extract Tool")
    parser.add_argument("--text", help="Extract text from the specified PDF file")
    parser.add_argument(
        "--annotations", help="Extract annotations from the specified PDF file"
    )
    parser.add_argument("pdf", nargs="?", help="PDF file to process (optional)")

    args = parser.parse_args()

    # If a PDF file is provided as a positional argument, use it
    if args.pdf and os.path.isfile(args.pdf) and args.pdf.lower().endswith(".pdf"):
        # Override the default input directory with the directory of the provided PDF
        global DEFAULT_INPUT_DIR
        DEFAULT_INPUT_DIR = os.path.dirname(os.path.abspath(args.pdf))
        pdf_path = args.pdf

    # If command line arguments are provided, run the corresponding function
    if args.text:
        extract_text(args.text)
        return
    elif args.annotations:
        extract_annotations(args.annotations)
        return
    elif args.pdf:
        # If only a PDF file is provided without specific action, show menu but use the PDF
        pdf_path = args.pdf
        if not file_exists(pdf_path):
            print(f"Error: The file {pdf_path} does not exist")
            return

    # Interactive menu
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print_header()
        print_menu()

        choice = input("Enter your choice (0-2): ")

        if choice == "1":
            extract_text()
        elif choice == "2":
            extract_annotations()
        elif choice == "0":
            print("\nExiting PDF Extract Tool. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
