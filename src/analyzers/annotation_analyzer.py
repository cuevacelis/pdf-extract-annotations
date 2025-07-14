#!/usr/bin/env python3
"""
Script for advanced analysis of annotations in PDF files
"""

from src.extractors.annotation_extractor import PDFAnnotationExtractor
import json
from collections import defaultdict
import os
from datetime import datetime


class AnnotationAnalyzer:
    """Class for analyzing annotations extracted from a PDF."""

    def __init__(self, annotations):
        """
        Initialize the analyzer with a list of annotations.

        Args:
            annotations (List[Dict]): List of extracted annotations
        """
        self.annotations = annotations
        self.by_page = self._group_by_page()
        self.by_type = self._group_by_type()
        self.by_author = self._group_by_author()

    def _group_by_page(self):
        """Group annotations by page number."""
        result = defaultdict(list)
        for annotation in self.annotations:
            result[annotation["page"]].append(annotation)
        return dict(result)

    def _group_by_type(self):
        """Group annotations by type."""
        result = defaultdict(list)
        for annotation in self.annotations:
            result[annotation["type"]].append(annotation)
        return dict(result)

    def _group_by_author(self):
        """Group annotations by author."""
        result = defaultdict(list)
        for annotation in self.annotations:
            result[annotation["author"]].append(annotation)
        return dict(result)

    def get_statistics(self):
        """
        Generate statistics about the annotations.

        Returns:
            Dict: Statistics of the annotations
        """
        statistics = {
            "total_annotations": len(self.annotations),
            "pages_with_annotations": len(self.by_page),
            "annotation_types": {
                type_: len(annotations) for type_, annotations in self.by_type.items()
            },
            "authors": {
                author: len(annotations)
                for author, annotations in self.by_author.items()
            },
            "page_with_most_annotations": (
                max(self.by_page.items(), key=lambda x: len(x[1]), default=(0, []))[0]
                if self.by_page
                else None
            ),
            "most_common_type": (
                max(self.by_type.items(), key=lambda x: len(x[1]), default=(None, []))[
                    0
                ]
                if self.by_type
                else None
            ),
        }
        return statistics

    def extract_highlighted_texts(self):
        """
        Extract all highlighted texts.

        Returns:
            List[Dict]: List of highlighted texts with metadata
        """
        results = []

        # Get highlight type annotations
        highlights = self.by_type.get("Highlight", [])

        for highlight in highlights:
            if "highlighted_text" in highlight and highlight["highlighted_text"]:
                results.append(
                    {
                        "page": highlight["page"],
                        "text": highlight["highlighted_text"],
                        "author": highlight["author"],
                        "comment": highlight["content"],
                    }
                )

        return results

    def generate_report(self, output_path="data/output/reports"):
        """
        Generate a complete report of the annotations.

        Args:
            output_path (str): Directory where to save the report

        Returns:
            str: Path to the report directory
        """
        # Create directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Save statistics
        with open(f"{output_path}/statistics.json", "w", encoding="utf-8") as f:
            json.dump(self.get_statistics(), f, indent=2, ensure_ascii=False)

        # Save highlighted texts
        with open(f"{output_path}/highlighted_texts.json", "w", encoding="utf-8") as f:
            json.dump(self.extract_highlighted_texts(), f, indent=2, ensure_ascii=False)

        # Save annotations by page
        with open(
            f"{output_path}/annotations_by_page.json", "w", encoding="utf-8"
        ) as f:
            json.dump(
                {str(k): v for k, v in self.by_page.items()},
                f,
                indent=2,
                ensure_ascii=False,
            )

        # Generate text report
        with open(f"{output_path}/report.txt", "w", encoding="utf-8") as f:
            f.write(f"ANNOTATION REPORT\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(
                f"File: {os.path.basename(self.annotations[0]['source_file']) if self.annotations else 'Unknown'}\n\n"
            )

            # Write statistics
            statistics = self.get_statistics()
            f.write(f"GENERAL STATISTICS\n")
            f.write(f"Total annotations: {statistics['total_annotations']}\n")
            f.write(f"Pages with annotations: {statistics['pages_with_annotations']}\n")
            f.write(
                f"Page with most annotations: {statistics['page_with_most_annotations']}\n"
            )
            f.write(
                f"Most common annotation type: {statistics['most_common_type']}\n\n"
            )

            # Write annotation types
            f.write(f"ANNOTATION TYPES\n")
            for type_, count in statistics["annotation_types"].items():
                f.write(f"- {type_}: {count}\n")
            f.write("\n")

            # Write authors
            f.write(f"AUTHORS\n")
            for author, count in statistics["authors"].items():
                f.write(f"- {author}: {count} annotations\n")
            f.write("\n")

            # Write highlighted texts
            highlighted_texts = self.extract_highlighted_texts()
            if highlighted_texts:
                f.write(f"HIGHLIGHTED TEXTS ({len(highlighted_texts)})\n")
                for i, item in enumerate(highlighted_texts, 1):
                    f.write(f"{i}. Page {item['page']}: \"{item['text']}\"\n")
                    if item["comment"]:
                        f.write(f"   Comment: {item['comment']}\n")
                    f.write("\n")

        return output_path


def main():
    # Path to the PDF file
    pdf_path = "data/input/Campus CEPU - Docente - Casos de Prueba v1.0.pdf"

    # Extract annotations
    extractor = PDFAnnotationExtractor(pdf_path)
    annotations = extractor.extract_annotations()

    if not annotations:
        print("No annotations found in the PDF.")
        return

    print(f"Found {len(annotations)} annotations in the PDF.")

    # Analyze annotations
    analyzer = AnnotationAnalyzer(annotations)

    # Generate report
    report_path = analyzer.generate_report()
    print(f"Report generated in directory: {report_path}")

    # Show some statistics
    statistics = analyzer.get_statistics()
    print("\nMain statistics:")
    print(f"- Total annotations: {statistics['total_annotations']}")
    print(f"- Pages with annotations: {statistics['pages_with_annotations']}")
    print(f"- Most common annotation type: {statistics['most_common_type']}")

    # Show highlighted texts
    highlighted_texts = analyzer.extract_highlighted_texts()
    if highlighted_texts:
        print(f"\nFound {len(highlighted_texts)} highlighted texts.")
        print("First 3 highlighted texts:")
        for i, item in enumerate(highlighted_texts[:3], 1):
            print(f"{i}. Page {item['page']}: \"{item['text']}\"")


if __name__ == "__main__":
    main()
