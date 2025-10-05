import os
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import PyPDF2
import docx
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

TOOLSERVER_URL = os.getenv("TOOLSERVER_URL", "http://toolserver:8002")

class DocumentProcessor:
    def __init__(self):
        self.toolserver_url = TOOLSERVER_URL
    
    def process_file(self, file_path: str):
        path = Path(file_path)
        extension = path.suffix.lower()
        
        logger.info(f"Processing file: {path.name} (type: {extension})")
        
        try:
            if extension == '.pdf':
                text = self._extract_pdf(file_path)
            elif extension in ['.docx', '.doc']:
                text = self._extract_docx(file_path)
            elif extension == '.txt':
                text = self._extract_text(file_path)
            elif extension in ['.png', '.jpg', '.jpeg', '.tiff']:
                text = self._extract_image_ocr(file_path)
            else:
                logger.warning(f"Unsupported file type: {extension}")
                return
            
            if text and len(text.strip()) > 0:
                self.process_text(text, metadata={
                    "source": "file",
                    "filename": path.name,
                    "path": str(path),
                    "type": extension
                })
            else:
                logger.warning(f"No text extracted from {path.name}")
        
        except Exception as e:
            logger.error(f"Error processing {path.name}: {e}")
    
    def process_text(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        if not text or len(text.strip()) < 10:
            logger.warning("Text too short to index")
            return
        
        try:
            response = requests.post(
                f"{self.toolserver_url}/v1/documents",
                json={
                    "text": text,
                    "metadata": metadata or {}
                },
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Document indexed successfully: {metadata.get('filename', 'unknown')}")
        
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
    
    def _extract_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
        return text.strip()
    
    def _extract_docx(self, file_path: str) -> str:
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
        return text.strip()
    
    def _extract_text(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            return ""
    
    def _extract_image_ocr(self, file_path: str) -> str:
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='deu')
            return text.strip()
        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return ""
