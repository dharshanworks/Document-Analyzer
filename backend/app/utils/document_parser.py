"""Document parsing: PDF, DOCX, TXT, and image OCR extraction with layout preservation."""

import base64
import io
import os
import re
from typing import Dict, Tuple

import PyPDF2
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract

# Set Tesseract path for Render (Linux)
_tesseract_path = '/usr/bin/tesseract'
if os.path.exists(_tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = _tesseract_path


class DocumentParser:
    @staticmethod
    def extract_from_base64(file_base64: str, file_type: str) -> str:
        try:
            file_bytes = base64.b64decode(file_base64)
        except Exception as e:
            raise ValueError(f"Invalid base64 encoding: {e}")

        file_type = file_type.lower().strip()

        if file_type == "pdf":
            return DocumentParser._from_pdf(file_bytes)
        elif file_type == "docx":
            return DocumentParser._from_docx(file_bytes)
        elif file_type in ("txt", "text"):
            return DocumentParser._from_text(file_bytes)
        elif file_type in ("image", "jpg", "jpeg", "png", "gif", "bmp"):
            return DocumentParser._from_image(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _from_pdf(file_bytes: bytes) -> str:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text() or ""
            text += f"\n{'='*60}\n"
            text += f"  PAGE {page_num + 1} OF {len(pdf_reader.pages)}\n"
            text += f"{'='*60}\n\n"
            text += DocumentParser._detect_pdf_structure(page_text)
        return text.strip()

    @staticmethod
    def _detect_pdf_structure(page_text: str) -> str:
        lines = page_text.split('\n')
        result = []
        in_table = False
        table_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_table:
                    result.append(DocumentParser._format_table(table_lines))
                    table_lines = []
                    in_table = False
                result.append("")
                continue

            if '|' in stripped and stripped.count('|') >= 2:
                in_table = True
                table_lines.append(stripped)
                continue

            if in_table:
                result.append(DocumentParser._format_table(table_lines))
                table_lines = []
                in_table = False

            if stripped.isupper() and len(stripped) < 80 and len(stripped.split()) <= 10:
                result.append(f"\n## {stripped}\n")
            elif re.match(r'^\d+\.\s+[A-Z]', stripped) and len(stripped.split()) <= 8:
                result.append(f"\n### {stripped}\n")
            elif re.match(r'^[\-\*\u2022]\s+', stripped):
                result.append(f"  - {stripped.lstrip('-*• ').strip()}")
            else:
                result.append(stripped)

        if table_lines:
            result.append(DocumentParser._format_table(table_lines))

        return '\n'.join(result)

    @staticmethod
    def _format_table(table_lines: list) -> str:
        if not table_lines:
            return ""
        return "\n[TABLE]\n" + "\n".join(table_lines) + "\n[/TABLE]\n"

    @staticmethod
    def _from_docx(file_bytes: bytes) -> str:
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)
        text = ""

        for paragraph in doc.paragraphs:
            if not paragraph.text.strip():
                text += "\n"
                continue

            style_name = paragraph.style.name.lower() if paragraph.style else ""
            alignment = paragraph.alignment

            if 'heading 1' in style_name:
                text += f"\n{'='*60}\n"
                text += f"  {paragraph.text}\n"
                text += f"{'='*60}\n\n"
            elif 'heading 2' in style_name:
                text += f"\n## {paragraph.text}\n\n"
            elif 'heading 3' in style_name:
                text += f"\n### {paragraph.text}\n\n"
            elif 'list' in style_name:
                text += f"  - {paragraph.text}\n"
            elif paragraph.runs and any(run.bold for run in paragraph.runs if run.text.strip()):
                text += f"\n**{paragraph.text}**\n\n"
            elif alignment == WD_ALIGN_PARAGRAPH.CENTER:
                text += f"\n[centered] {paragraph.text}\n\n"
            else:
                text += paragraph.text + "\n"

        if doc.tables:
            text += f"\n{'─'*60}\n"
            text += "  TABLES\n"
            text += f"{'─'*60}\n\n"
            for table_idx, table in enumerate(doc.tables):
                text += f"[Table {table_idx + 1}]\n"
                for row_idx, row in enumerate(table.rows):
                    cells = [cell.text.strip() for cell in row.cells]
                    if any(cells):
                        text += " | ".join(cells) + "\n"
                text += "\n"

        return text.strip()

    @staticmethod
    def _from_text(file_bytes: bytes) -> str:
        return file_bytes.decode('utf-8', errors='ignore').strip()

    @staticmethod
    def _from_image(file_bytes: bytes) -> str:
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            raise RuntimeError("Tesseract OCR is not installed.")
        image = Image.open(io.BytesIO(file_bytes))
        image = DocumentParser._preprocess_image(image)
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        return DocumentParser._reconstruct_layout(ocr_data)

    @staticmethod
    def _preprocess_image(image: Image.Image) -> Image.Image:
        if image.mode != 'L':
            image = image.convert('L')

        image = image.point(lambda x: 0 if x < 128 else 255, '1')

        image = image.filter(ImageFilter.MedianFilter(size=3))

        scale_factor = max(1, 2000 / max(image.size))
        if scale_factor > 1:
            new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
            image = image.resize(new_size, Image.LANCZOS)

        return image

    @staticmethod
    def _reconstruct_layout(ocr_data: dict) -> str:
        lines = {}
        for i, word in enumerate(ocr_data['text']):
            if word.strip():
                line_num = ocr_data['line_num'][i]
                block_num = ocr_data['block_num'][i]
                key = (block_num, line_num)
                if key not in lines:
                    lines[key] = []
                lines[key].append(word)

        result = []
        for key in sorted(lines.keys()):
            line_text = ' '.join(lines[key])
            if len(line_text) < 60 and line_text.isupper():
                result.append(f"\n## {line_text}\n")
            else:
                result.append(line_text)

        return '\n'.join(result).strip()

    @staticmethod
    def get_metadata(file_bytes: bytes, file_type: str) -> Dict:
        metadata = {"file_type": file_type, "size_bytes": len(file_bytes)}

        if file_type == "pdf":
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                metadata["page_count"] = len(pdf_reader.pages)
                meta = pdf_reader.metadata
                if meta:
                    metadata["title"] = meta.get('/Title', '')
                    metadata["author"] = meta.get('/Author', '')
                    metadata["creator"] = meta.get('/Creator', '')
                    metadata["producer"] = meta.get('/Producer', '')
            except Exception:
                pass
        elif file_type == "docx":
            try:
                doc = Document(io.BytesIO(file_bytes))
                metadata["paragraph_count"] = len(doc.paragraphs)
                metadata["table_count"] = len(doc.tables)
                props = doc.core_properties
                metadata["title"] = props.title or ''
                metadata["author"] = props.author or ''
                metadata["created"] = str(props.created) if props.created else ''
                metadata["modified"] = str(props.modified) if props.modified else ''
            except Exception:
                pass
        elif file_type in ("image", "jpg", "jpeg", "png", "gif", "bmp"):
            try:
                img = Image.open(io.BytesIO(file_bytes))
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["format"] = img.format
                metadata["mode"] = img.mode
            except Exception:
                pass

        return metadata

    @staticmethod
    def validate_base64(file_base64: str) -> bool:
        try:
            file_bytes = bytes(file_base64, 'utf-8') if isinstance(file_base64, str) else file_base64
            return base64.b64encode(base64.b64decode(file_bytes)) == file_bytes
        except Exception:
            return False


def extract_text(file_base64: str, file_type: str) -> Tuple[str, bool]:
    try:
        text = DocumentParser.extract_from_base64(file_base64, file_type)
        return text, True
    except Exception as e:
        return str(e), False
