"""
Text Extractor Service

Handles extraction of text from multiple sources:
- PDF files
- Web URLs (HTML)
- Plain text
"""

import pdfplumber
from bs4 import BeautifulSoup
import httpx
import re
from typing import Dict, List, Optional


class TextExtractor:
    """Service for extracting text from various sources."""
    
    @staticmethod
    async def extract_from_pdf(file_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with extracted text and metadata
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                sections = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n\n"
                
                # Detect sections based on headings
                sections = TextExtractor._detect_sections(full_text)
                
                return {
                    "raw_text": full_text.strip(),
                    "sections": sections,
                    "page_count": len(pdf.pages),
                    "success": True
                }
        except Exception as e:
            return {
                "raw_text": "",
                "sections": [],
                "error": str(e),
                "success": False
            }
    
    @staticmethod
    async def extract_from_url(url: str) -> Dict[str, any]:
        """
        Extract text from web URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict with extracted text and metadata
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Detect sections
                sections = TextExtractor._detect_sections(text)
                
                return {
                    "raw_text": text,
                    "sections": sections,
                    "url": url,
                    "success": True
                }
        except Exception as e:
            return {
                "raw_text": "",
                "sections": [],
                "error": str(e),
                "success": False
            }
    
    @staticmethod
    async def extract_from_text(text: str) -> Dict[str, any]:
        """
        Process plain text input.
        
        Args:
            text: Plain text content
            
        Returns:
            Dict with processed text and metadata
        """
        # Detect sections
        sections = TextExtractor._detect_sections(text)
        
        return {
            "raw_text": text.strip(),
            "sections": sections,
            "success": True
        }
    
    @staticmethod
    def _detect_sections(text: str) -> List[Dict[str, str]]:
        """
        Detect sections in text based on headings.
        
        Args:
            text: Full text content
            
        Returns:
            List of sections with headings and text
        """
        sections = []
        
        # Common heading patterns in legal documents
        heading_patterns = [
            r'^([A-Z][A-Z\s]+)$',  # ALL CAPS headings
            r'^(\d+\.\s+[A-Z][^.]+)$',  # Numbered headings
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):',  # Title Case with colon
        ]
        
        lines = text.split('\n')
        current_section = {"heading": "Introduction", "text": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a heading
            is_heading = False
            for pattern in heading_patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous section
                    if current_section["text"]:
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        "heading": match.group(1).strip(),
                        "text": ""
                    }
                    is_heading = True
                    break
            
            if not is_heading:
                current_section["text"] += line + " "
        
        # Add last section
        if current_section["text"]:
            sections.append(current_section)
        
        return sections
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Raw text
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (keep alphanumeric and basic punctuation)
        text = re.sub(r'[^a-z0-9\s.,;:!?-]', '', text)
        
        return text.strip()
