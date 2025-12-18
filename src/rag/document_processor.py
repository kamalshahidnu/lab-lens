#!/usr/bin/env python3
"""
Document Processor for RAG System
Handles text, PDF, and image file processing
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.utils.error_handling import ErrorHandler, safe_execute
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Try importing required libraries
PDF_LIB = None
try:
    import pdfplumber

    PDF_AVAILABLE = True
    PDF_LIB = "pdfplumber"
except ImportError:
    try:
        import PyPDF2

        PDF_AVAILABLE = True
        PDF_LIB = "PyPDF2"
    except ImportError:
        PDF_AVAILABLE = False
        PDF_LIB = None

try:
    import pytesseract
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import google.generativeai as genai

    GEMINI_VISION_AVAILABLE = True
except ImportError:
    GEMINI_VISION_AVAILABLE = False


class DocumentProcessor:
    """Process various document types (text, PDF, images) for RAG"""

    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize document processor

        Args:
          gemini_api_key: Optional API key for Gemini Vision (for image analysis)
        """
        self.error_handler = ErrorHandler(logger)
        self.gemini_api_key = gemini_api_key

        if gemini_api_key and GEMINI_VISION_AVAILABLE:
            try:
                genai.configure(api_key=gemini_api_key)
                logger.info("Gemini Vision API configured for image processing")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini Vision: {e}")

    @safe_execute("process_file", logger, ErrorHandler(logger))
    def process_file(self, file_path: str) -> Dict[str, any]:
        """
        Process a file and extract text content

        Args:
          file_path: Path to the file (text, PDF, or image)

        Returns:
          Dictionary with extracted text and metadata
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = file_path.suffix.lower()

        logger.info(f"Processing file: {file_path} (type: {file_ext})")

        result = {"file_path": str(file_path), "file_name": file_path.name, "file_type": file_ext, "text": "", "metadata": {}}

        # Process based on file type
        if file_ext == ".txt" or file_ext == ".md":
            result["text"] = self._process_text_file(file_path)
            result["metadata"]["source"] = "text_file"
        elif file_ext == ".pdf":
            result["text"] = self._process_pdf_file(file_path)
            result["metadata"]["source"] = "pdf_file"
        elif file_ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]:
            result.update(self._process_image_file(file_path))
            result["metadata"]["source"] = "image_file"
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        result["metadata"]["text_length"] = len(result["text"])
        logger.info(f"Extracted {len(result['text'])} characters from {file_path.name}")

        return result

    def _process_text_file(self, file_path: Path) -> str:
        """Extract text from a text file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            return text
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, "r", encoding="latin-1") as f:
                text = f.read()
            return text

    def _process_pdf_file(self, file_path: Path) -> str:
        """Extract text from a PDF file"""
        if not PDF_AVAILABLE:
            raise ImportError(
                "PDF processing requires PyPDF2 or pdfplumber. " "Install with: pip install PyPDF2 or pip install pdfplumber"
            )

        text_parts = []

        try:
            # Use pdfplumber if available (better text extraction)
            if PDF_LIB == "pdfplumber":
                import pdfplumber

                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
            elif PDF_LIB == "PyPDF2":
                # Fallback to PyPDF2
                import PyPDF2

                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
            else:
                raise ImportError("No PDF library available")

            full_text = "\n\n".join(text_parts)
            if not full_text.strip():
                logger.warning(f"No text extracted from PDF: {file_path}")

            return full_text

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise

    def _process_image_file(self, file_path: Path) -> Dict[str, any]:
        """
        Process an image file - extract text using OCR and optionally analyze with Gemini Vision

        Returns:
          Dictionary with 'text' (OCR) and optionally 'image_analysis' (Gemini Vision)
        """
        result = {"text": "", "metadata": {"ocr_used": False, "vision_analysis": False}}

        # Load image
        try:
            image = Image.open(file_path)
            result["metadata"]["image_size"] = image.size
            result["metadata"]["image_format"] = image.format
        except Exception as e:
            logger.error(f"Error opening image: {e}")
            raise

        # Method 1: OCR extraction
        ocr_text = None
        if OCR_AVAILABLE:
            try:
                logger.info("Extracting text using OCR...")
                ocr_text = pytesseract.image_to_string(image)
                if ocr_text.strip():
                    result["text"] = ocr_text.strip()
                    result["metadata"]["ocr_used"] = True
                    logger.info(f"OCR extracted {len(result['text'])} characters")
            except Exception as e:
                logger.warning(f"OCR failed: {e}")

        # Method 2: Gemini Vision analysis (for medical images)
        if self.gemini_api_key and GEMINI_VISION_AVAILABLE:
            try:
                logger.info("Analyzing image with Gemini Vision...")
                vision_text = self._analyze_with_gemini_vision(image, file_path)
                if vision_text:
                    if result["text"]:
                        # Combine OCR and Vision analysis
                        result["text"] = f"OCR Text:\n{result['text']}\n\nGemini Vision Analysis:\n{vision_text}"
                    else:
                        result["text"] = vision_text
                    result["metadata"]["vision_analysis"] = True
                    logger.info("Gemini Vision analysis completed")
            except Exception as e:
                logger.warning(f"Gemini Vision analysis failed: {e}")

        if not result["text"]:
            result["text"] = f"[Image file: {file_path.name} - No text extracted]"
            logger.warning(f"Could not extract text from image: {file_path}")

        return result

    def _analyze_with_gemini_vision(self, image: Image.Image, file_path: Path) -> Optional[str]:
        """Analyze image using Gemini Vision API"""
        try:
            # Configure Gemini
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            # Create prompt for medical image analysis
            prompt = """Analyze this medical image and extract all visible text, medical findings,
diagnoses, measurements, and relevant clinical information.
Provide a comprehensive description that includes:
1. Any visible text or labels
2. Medical findings or observations
3. Measurements or values shown
4. Any diagnoses or conditions visible
5. General description of the image content

Format the output in a clear, structured way suitable for a medical report."""

            # Generate response
            response = model.generate_content([prompt, image])

            if response and response.text:
                return response.text.strip()

            return None

        except Exception as e:
            logger.error(f"Gemini Vision analysis error: {e}")
            return None

    def process_text(self, text: str, source_name: str = "user_input") -> Dict[str, any]:
        """
        Process raw text input

        Args:
          text: Raw text content
          source_name: Name/identifier for the source

        Returns:
          Dictionary with text and metadata
        """
        return {
            "text": text,
            "file_path": None,
            "file_name": source_name,
            "file_type": ".txt",
            "metadata": {"source": "raw_text", "text_length": len(text)},
        }

    def process_multiple_files(self, file_paths: List[str]) -> List[Dict[str, any]]:
        """
        Process multiple files

        Args:
          file_paths: List of file paths to process

        Returns:
          List of processed document dictionaries
        """
        results = []
        errors = []

        for file_path in file_paths:
            try:
                result = self.process_file(file_path)
                # Verify that text was extracted
                if result and result.get("text") and result["text"].strip():
                    results.append(result)
                else:
                    error_msg = f"{Path(file_path).name}: No text extracted (file may be empty or corrupted)"
                    errors.append(error_msg)
                    logger.warning(error_msg)
            except Exception as e:
                error_msg = f"{Path(file_path).name}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Failed to process {file_path}: {e}", exc_info=True)

        if errors and not results:
            # If all files failed, raise an exception with all errors
            error_summary = "; ".join(errors)
            raise ValueError(f"All files failed to process. Errors: {error_summary}")

        return results
