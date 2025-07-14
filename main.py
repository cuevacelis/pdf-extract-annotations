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
from src.analyzers.annotation_analyzer import AnnotationAnalyzer
from src.utils.file_utils import ensure_directory_exists, load_json, file_exists

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
    print("3. Analyze annotations")
    print("4. Process all (extract text, annotations and analyze)")
    print("5. Settings")
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


def analyze_annotations(annotations_path=None):
    """
    Analyze annotations from a JSON file.

    Args:
        annotations_path (str, optional): Path to the annotations JSON file.
                                         If None, the user will be prompted.
    """
    print("\n--- ANNOTATION ANALYSIS ---")

    if annotations_path is None:
        # Try to find annotation files
        annotation_dir = "data/output/annotations"
        if os.path.isdir(annotation_dir):
            annotation_files = [
                f for f in os.listdir(annotation_dir) if f.endswith(".json")
            ]

            if annotation_files:
                print("Available annotation files:")
                for i, file in enumerate(annotation_files, 1):
                    print(f"{i}. {file}")

                try:
                    choice = int(
                        input(
                            "\nSelect a file number (or 0 to enter a different path): "
                        )
                    )
                    if 1 <= choice <= len(annotation_files):
                        annotations_path = (
                            f"{annotation_dir}/{annotation_files[choice-1]}"
                        )
                    else:
                        annotations_path = input(
                            "Enter the path to the annotations JSON file: "
                        )
                except ValueError:
                    annotations_path = input(
                        "Enter the path to the annotations JSON file: "
                    )
            else:
                annotations_path = input(
                    "Enter the path to the annotations JSON file: "
                )
        else:
            annotations_path = input("Enter the path to the annotations JSON file: ")

    # Verify that the file exists
    if not file_exists(annotations_path):
        print(f"Error: The file {annotations_path} does not exist")
        return

    # Load annotations
    print(f"\nLoading annotations from {annotations_path}...")
    try:
        data = load_json(annotations_path)
        annotations = data.get("annotations", [])

        if not annotations:
            print("No annotations found in the file.")
            input("\nPress Enter to continue...")
            return

        print(f"Loaded {len(annotations)} annotations.")

        # Analyze annotations
        analyzer = AnnotationAnalyzer(annotations)

        # Generate report
        output_dir = "data/output/reports"
        report_path = analyzer.generate_report(output_dir)

        print(f"\nReport generated in directory: {report_path}")

        # Display some statistics
        statistics = analyzer.get_statistics()
        print("\nMain statistics:")
        print(f"- Total annotations: {statistics['total_annotations']}")
        print(f"- Pages with annotations: {statistics['pages_with_annotations']}")
        print(f"- Most common annotation type: {statistics['most_common_type']}")

        # Display highlighted texts
        highlighted_texts = analyzer.extract_highlighted_texts()
        if highlighted_texts:
            print(f"\nFound {len(highlighted_texts)} highlighted texts.")
            print("First 3 highlighted texts:")
            for i, item in enumerate(highlighted_texts[:3], 1):
                print(f"{i}. Page {item['page']}: \"{item['text']}\"")

    except Exception as e:
        print(f"Error analyzing annotations: {e}")

    input("\nPress Enter to continue...")


def process_all():
    """Process a PDF file: extract text, annotations, and analyze."""
    print("\n--- COMPLETE PDF PROCESSING ---")
    
    pdf_path = get_pdf_path()

    # Verify that the file exists
    if not file_exists(pdf_path):
        print(f"Error: The file {pdf_path} does not exist")
        return

    # 1. Extract text
    print("\nStep 1: Extracting text...")
    extract_text(pdf_path)

    # 2. Extract annotations
    print("\nStep 2: Extracting annotations...")
    annotations_path = extract_annotations(pdf_path)

    # 3. Analyze annotations
    if annotations_path:
        print("\nStep 3: Analyzing annotations...")
        analyze_annotations(annotations_path)

    print("\nComplete processing finished.")
    input("\nPress Enter to continue...")


def get_pdf_path():
    """Get PDF path from available files or user input."""
    if os.path.isdir(DEFAULT_INPUT_DIR):
        pdf_files = [f for f in os.listdir(DEFAULT_INPUT_DIR) if f.endswith('.pdf')]
        
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
                choice = int(input("\nSelect a file number (or 0 to enter a different path): "))
                if 1 <= choice <= len(pdf_files):
                    return f"{DEFAULT_INPUT_DIR}/{pdf_files[choice-1]}"
            except ValueError:
                pass
    
    return input("Enter the path to the PDF file: ")

def settings():
    """Configure application settings."""
    global DEFAULT_INPUT_DIR
    print("\n--- SETTINGS ---")
    print(f"Current input directory: {DEFAULT_INPUT_DIR}")
    new_dir = input(f"Enter new input directory (or press Enter to keep '{DEFAULT_INPUT_DIR}'): ")
    if new_dir.strip():
        DEFAULT_INPUT_DIR = new_dir.strip()
        print(f"Input directory updated to: {DEFAULT_INPUT_DIR}")
    input("\nPress Enter to continue...")


def main():
    """Main function to run the PDF Extract tool."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PDF Extract Tool")
    parser.add_argument("--text", help="Extract text from the specified PDF file")
    parser.add_argument(
        "--annotations", help="Extract annotations from the specified PDF file"
    )
    parser.add_argument(
        "--analyze", help="Analyze annotations from the specified JSON file"
    )
    parser.add_argument("--all", help="Process the specified PDF file completely")
    parser.add_argument(
        "pdf", nargs="?", help="PDF file to process (optional)"
    )

    args = parser.parse_args()
    
    # If a PDF file is provided as a positional argument, use it
    if args.pdf and os.path.isfile(args.pdf) and args.pdf.lower().endswith('.pdf'):
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
    elif args.analyze:
        analyze_annotations(args.analyze)
        return
    elif args.all:
        # Set the PDF path and process all
        pdf_path = args.all
        if file_exists(pdf_path):
            # 1. Extract text
            extract_text(pdf_path)

            # 2. Extract annotations
            annotations_path = extract_annotations(pdf_path)

            # 3. Analyze annotations
            if annotations_path:
                analyze_annotations(annotations_path)
        else:
            print(f"Error: The file {pdf_path} does not exist")
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

        choice = input("Enter your choice (0-5): ")

        if choice == "1":
            extract_text()
        elif choice == "2":
            extract_annotations()
        elif choice == "3":
            analyze_annotations()
        elif choice == "4":
            process_all()
        elif choice == "5":
            settings()
        elif choice == "0":
            print("\nExiting PDF Extract Tool. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
