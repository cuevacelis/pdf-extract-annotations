#!/usr/bin/env python3
"""
Script to extract complete text from PDF files
"""

import fitz  # PyMuPDF
import argparse
import sys
from pathlib import Path


def extract_text_from_pdf(pdf_path, by_page=False, include_numbers=True):
    """
    Extracts the complete text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file
        by_page (bool): If True, returns a dictionary with text by page
        include_numbers (bool): If True, includes page numbers in the output

    Returns:
        Union[str, Dict[int, str]]: Complete text or dictionary of texts by page
    """
    try:
        # Open the PDF document
        document = fitz.open(pdf_path)

        if by_page:
            # Extract text by page
            result = {}
            for page_num in range(len(document)):
                page = document[page_num]
                text = page.get_text()

                if include_numbers:
                    # Add page number at the beginning
                    text = f"=== PAGE {page_num + 1} ===\n\n{text}"

                result[page_num + 1] = text

            return result
        else:
            # Extract all text as a single string
            complete_text = ""

            for page_num in range(len(document)):
                page = document[page_num]
                text = page.get_text()

                if include_numbers:
                    # Add page number at the beginning
                    text = f"=== PAGE {page_num + 1} ===\n\n{text}"

                complete_text += text + "\n\n"

            return complete_text

    except Exception as e:
        print(f"Error extracting text from PDF: {e}", file=sys.stderr)
        return "" if not by_page else {}


def save_text(text, output_path):
    """
    Saves the extracted text to a file.

    Args:
        text (Union[str, Dict]): Extracted text or dictionary of texts
        output_path (str): Path of the output file
    """
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            if isinstance(text, dict):
                # If it's a dictionary (text by page)
                for page_num, content in sorted(text.items()):
                    file.write(content)
                    file.write("\n\n")
            else:
                # If it's a string (complete text)
                file.write(text)

        print(f"Text saved to: {output_path}")

    except Exception as e:
        print(f"Error saving the text: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Extract complete text from a PDF file"
    )
    parser.add_argument("pdf_file", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Path of the output file (TXT)")
    parser.add_argument(
        "-p",
        "--by_page",
        action="store_true",
        help="Extract text separated by pages",
    )
    parser.add_argument(
        "-n",
        "--no_numbers",
        action="store_true",
        help="Do not include page numbers in the output",
    )

    args = parser.parse_args()

    # Verify that the file exists
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"Error: The file {args.pdf_file} does not exist", file=sys.stderr)
        sys.exit(1)

    # Extract text
    text = extract_text_from_pdf(
        args.pdf_file, by_page=args.by_page, include_numbers=not args.no_numbers
    )

    # Determine output path
    output_path = args.output if args.output else f"{pdf_path.stem}_text.txt"

    # Save text
    save_text(text, output_path)


if __name__ == "__main__":
    main()
