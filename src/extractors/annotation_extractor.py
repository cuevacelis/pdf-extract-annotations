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
            content_annotation = annotation_info.get("content", "")

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
                "contentAnnotation": content_annotation,
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
            
            # Find nearby title for ALL annotations (not just highlights)
            nearby_title = self._find_nearby_title(annot)
            if nearby_title:
                annotation_data["nearby_title"] = nearby_title

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
            
    def _find_nearby_title(self, annot) -> str:
        """
        Find the nearest title or subtitle above the annotation, with special handling for table titles and case IDs.
        Also searches previous pages if no title is found on the current page.
        
        Args:
            annot: PyMuPDF annotation object
            
        Returns:
            str: Nearby title or subtitle text
        """
        try:
            # Get the page and document
            page = annot.parent
            doc = page.parent
            page_num = page.number
            
            # Buscar título en la página actual
            title = self._search_title_in_page(page)
            if title:
                return title
                
            # Si no se encuentra en la página actual, buscar en páginas anteriores
            # Buscar hasta 3 páginas atrás como máximo
            for prev_page_num in range(page_num - 1, max(0, page_num - 3) - 1, -1):
                if prev_page_num >= 0:
                    prev_page = doc[prev_page_num]
                    title = self._search_title_in_page(prev_page)
                    if title:
                        return title
                        
            return ""
            
        except Exception as e:
            print(f"Error finding nearby title: {e}", file=sys.stderr)
            return ""
            
    def _search_title_in_page(self, page) -> str:
        """
        Search for a title in a specific page.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            str: Title found in the page or empty string
        """
        try:
            # Get annotation coordinates (only used for current page)
            rect = None
            annot_y = 0
            
            # Get all text blocks on the page
            page_dict = page.get_text("dict")
            
            # Find potential titles
            potential_titles = []
            
            # Scan the entire page for case ID patterns
            all_text = page.get_text()
            
            # Buscar el título exacto como aparece en la imagen compartida
            exact_titles = [
                "CP N° 01: Campus Cepre Uni – Logeo Usuario con Google",
                "CP N° 01: Campus Cepre Uni - Logeo Usuario con Google",
                "CP N° 01: Campus Cepu - Logeo Usuario con Google",
                "CP N° 01: Campus Cepu – Logeo Usuario con Google",
                "CP N° 01 Campus Cepre Uni – Logeo Usuario con Google",
                "CP N° 01 Campus Cepre Uni - Logeo Usuario con Google",
                # Formato exacto como se ve en la imagen compartida
                "CP N° 01: Campus Cepre Uni – Logeo Usuario con Google"
            ]
            
            for title in exact_titles:
                if title in all_text:
                    return title
                
            # Buscar por el patrón CP N° 01
            if "CP N" in all_text:
                start_idx = all_text.find("CP N")
                end_idx = all_text.find("\n", start_idx)
                if end_idx > start_idx:
                    return all_text[start_idx:end_idx].strip()
            
            # Si no encontramos el título exacto, buscar con regex
            import re
            # Patrón para detectar títulos de casos de prueba
            cp_patterns = re.findall(r'CP\s*N[°º\s]\s*\d+[:\.]?.*?(?=\n|$)', all_text)
            if cp_patterns:
                return cp_patterns[0].strip()
                
            # Buscar cualquier texto que comience con CP N
            if "CP N" in all_text:
                start_idx = all_text.find("CP N")
                end_idx = all_text.find("\n", start_idx)
                if end_idx > start_idx:
                    return all_text[start_idx:end_idx].strip()
                
            # If regex didn't find it, try block by block
            for block in page_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                    
                # Extract text from the block
                block_text = ""
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        block_text += span.get("text", "")
                
                # Check if this block contains a case ID pattern
                if "CP N" in block_text or "CP Nº" in block_text or "CP N°" in block_text:
                    case_id_pattern = block_text.strip()
                    break
            
            # If we found a case ID pattern, return it immediately
            if case_id_pattern:
                return case_id_pattern
            
            # Second pass: look for other potential titles
            for block in page_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                    
                # Get block coordinates
                block_y = block["bbox"][1]  # Top y-coordinate of block
                
                # Only consider blocks above the annotation
                if block_y >= annot_y:
                    continue
                    
                # Extract text from the block
                block_text = ""
                is_title = False
                
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        # Check if this might be a title (larger font or bold)
                        font_size = span.get("size", 0)
                        font_flags = span.get("flags", 0)
                        is_bold = font_flags & 2 > 0  # Check if bold flag is set
                        
                        # Consider it a potential title if font is larger or bold
                        if font_size > 10 or is_bold:
                            block_text += span.get("text", "")
                            is_title = True
                
                # Also check for table headers or section titles
                if block_text.strip() and (is_title or 
                                          "Objetivo" in block_text or 
                                          "Pre-Requisitos" in block_text or
                                          "Datos de Prueba" in block_text):
                    # Store the text and its distance from the annotation
                    distance = annot_y - block_y
                    potential_titles.append((block_text.strip(), distance))
            
            # Sort by distance (closest first)
            potential_titles.sort(key=lambda x: x[1])
            
            # Return the closest title, or empty string if none found
            return potential_titles[0][0] if potential_titles else ""
            
        except Exception as e:
            print(f"Error finding nearby title: {e}", file=sys.stderr)
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
            if annot["contentAnnotation"]:
                print(f"   Content Annotation: {annot['contentAnnotation']}")
            if annot.get("highlighted_text"):
                print(f"   Highlighted text: {annot['highlighted_text']}")
            if annot.get("nearby_title"):
                print(f"   Nearby title: {annot['nearby_title']}")



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
