#!/usr/bin/env python3
"""
PDF Comment and Annotation Extractor

This script extracts comments and annotations from PDF files using PyMuPDF (fitz).
It supports various annotation types including text annotations, highlights,
underlines, strikeouts, and more.
"""

import fitz  # PyMuPDF
import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class PDFAnnotationExtractor:
    """Extract comments and annotations from PDF files."""

    def __init__(self, pdf_path: str):
        """
        Initialize the extractor with a PDF file path.

        Args:
            pdf_path (str): Path to the PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def extract_annotations(self) -> List[Dict[str, Any]]:
        """
        Extract all annotations from the PDF.

        Returns:
            List[Dict[str, Any]]: List of annotation dictionaries
        """
        annotations = []

        try:
            doc = fitz.open(self.pdf_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_annotations = page.annots()

                for annot in page_annotations:
                    annotation_data = self._extract_annotation_data(annot, page_num + 1)
                    if annotation_data:
                        annotations.append(annotation_data)

            doc.close()

        except Exception as e:
            print(f"Error processing PDF: {e}", file=sys.stderr)
            return []

        return annotations

    def _extract_annotation_data(self, annot, page_num: int) -> Dict[str, Any]:
        """
        Extract data from a single annotation.

        Args:
            annot: PyMuPDF annotation object
            page_num (int): Page number (1-based)

        Returns:
            Dict[str, Any]: Annotation data dictionary
        """
        try:
            annotation_info = annot.info

            # Get annotation type
            annot_type = annot.type[1] if annot.type else "Unknown"

            # Get annotation content
            content = annotation_info.get("content", "")

            # Get annotation coordinates
            rect = annot.rect

            # Get creation and modification dates
            creation_date = annotation_info.get("creationDate", "")
            mod_date = annotation_info.get("modDate", "")

            # Get author information
            author = annotation_info.get("title", "Unknown")

            # Get subject/title
            subject = annotation_info.get("subject", "")

            # Create a dictionary of coordinates using the correct properties
            # In PyMuPDF, the Rect properties are x0, y0, x1, y1
            coordinates = {}
            try:
                coordinates = {
                    "x0": rect.x0,
                    "y0": rect.y0,
                    "x1": rect.x1,
                    "y1": rect.y1,
                }
            except AttributeError:
                # Fallback to handle different versions of PyMuPDF
                try:
                    # Try to access using indexing
                    coordinates = {
                        "x0": rect[0],
                        "y0": rect[1],
                        "x1": rect[2],
                        "y1": rect[3],
                    }
                except:
                    # If all fails, use an empty dictionary
                    coordinates = {}

            annotation_data = {
                "page": page_num,
                "type": annot_type,
                "content": content,
                "author": author,
                "subject": subject,
                "creation_date": creation_date,
                "modification_date": mod_date,
                "coordinates": coordinates,
            }

            # Extract highlighted text for text markup annotations
            if annot_type in ["Highlight", "Underline", "StrikeOut", "Squiggly"]:
                highlighted_text = self._extract_highlighted_text(annot)
                if highlighted_text:
                    annotation_data["highlighted_text"] = highlighted_text

            return annotation_data

        except Exception as e:
            print(f"Error extracting annotation data: {e}", file=sys.stderr)
            return None

    def _extract_highlighted_text(self, annot) -> str:
        """
        Extract the text that was highlighted by the annotation.

        Args:
            annot: PyMuPDF annotation object

        Returns:
            str: Highlighted text
        """
        try:
            # Get the quad points (coordinates of highlighted text)
            quad_points = annot.vertices
            if not quad_points:
                return ""

            # Get the page
            page = annot.parent

            # Extract text from the annotation area
            rect = annot.rect
            text_instances = page.get_text("dict", clip=rect)

            # Extract text from blocks
            text_content = ""
            for block in text_instances.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text_content += span.get("text", "")

            return text_content.strip()

        except Exception as e:
            print(f"Error extracting highlighted text: {e}", file=sys.stderr)
            return ""

    def save_to_json(self, annotations: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save annotations to a JSON file.

        Args:
            annotations (List[Dict[str, Any]]): List of annotations
            output_path (str): Output file path
        """
        output_data = {
            "source_file": str(self.pdf_path),
            "extraction_date": datetime.now().isoformat(),
            "total_annotations": len(annotations),
            "annotations": annotations,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

    def print_summary(self, annotations: List[Dict[str, Any]]) -> None:
        """
        Print a summary of extracted annotations.

        Args:
            annotations (List[Dict[str, Any]]): List of annotations
        """
        if not annotations:
            print("No annotations found in the PDF.")
            return

        print(f"Found {len(annotations)} annotations in {self.pdf_path.name}")
        print("-" * 50)

        # Group by type
        type_counts = {}
        for annot in annotations:
            annot_type = annot["type"]
            type_counts[annot_type] = type_counts.get(annot_type, 0) + 1

        print("Annotation types:")
        for annot_type, count in type_counts.items():
            print(f"  {annot_type}: {count}")

        print("\nDetailed annotations:")
        for i, annot in enumerate(annotations, 1):
            print(f"\n{i}. Page {annot['page']} - {annot['type']}")
            if annot["author"] != "Unknown":
                print(f"   Author: {annot['author']}")
            if annot["subject"]:
                print(f"   Subject: {annot['subject']}")
            if annot["content"]:
                print(f"   Content: {annot['content']}")
            if annot.get("highlighted_text"):
                print(f"   Highlighted text: {annot['highlighted_text']}")


def main():
    """Main function to run the PDF annotation extractor."""
    parser = argparse.ArgumentParser(
        description="Extract comments and annotations from PDF files"
    )
    parser.add_argument("pdf_file", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Output JSON file path")
    parser.add_argument(
        "-s", "--summary", action="store_true", help="Print summary to console"
    )

    args = parser.parse_args()

    try:
        extractor = PDFAnnotationExtractor(args.pdf_file)
        annotations = extractor.extract_annotations()

        if args.output:
            extractor.save_to_json(annotations, args.output)
            print(f"Annotations saved to {args.output}")

        if args.summary or not args.output:
            extractor.print_summary(annotations)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
