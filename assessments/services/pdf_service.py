"""
PDF Text Extraction and Metadata Service

This service handles:
1. PDF text extraction using multiple libraries for robustness
2. Metadata extraction from PDFs
3. Text preprocessing and cleaning
4. Section identification and parsing
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None

logger = logging.getLogger(__name__)


class PDFTextExtractor:
    """Extract text from PDF files using multiple methods for robustness"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.text = ""
        self.metadata = {}
        self.sections = {}
        
    def extract_text(self) -> str:
        """Extract text using the best available method"""
        try:
            # Try pdfplumber first (better for tables and layout)
            if pdfplumber:
                text = self._extract_with_pdfplumber()
                if text and len(text.strip()) > 100:
                    self.text = text
                    return text
            
            # Fallback to PyPDF2
            if PyPDF2:
                text = self._extract_with_pypdf2()
                if text and len(text.strip()) > 100:
                    self.text = text
                    return text
                    
            raise Exception("No suitable PDF extraction method available")
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise
    
    def _extract_with_pdfplumber(self) -> str:
        """Extract text using pdfplumber (preserves layout better)"""
        text = ""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
            raise
        return text
    
    def _extract_with_pypdf2(self) -> str:
        """Extract text using PyPDF2 (fallback method)"""
        text = ""
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
            raise
        return text
    
    def extract_metadata(self) -> Dict[str, str]:
        """Extract metadata from PDF"""
        metadata = {}
        try:
            if PyPDF2:
                with open(self.file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    if pdf_reader.metadata:
                        metadata.update({
                            'title': pdf_reader.metadata.get('/Title', ''),
                            'author': pdf_reader.metadata.get('/Author', ''),
                            'subject': pdf_reader.metadata.get('/Subject', ''),
                            'creator': pdf_reader.metadata.get('/Creator', ''),
                            'producer': pdf_reader.metadata.get('/Producer', ''),
                            'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                        })
        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata: {str(e)}")
        
        self.metadata = metadata
        return metadata
    
    def identify_sections(self) -> Dict[str, str]:
        """Identify major sections in the research paper"""
        if not self.text:
            return {}
        
        sections = {}
        text = self.text.lower()
        
        # Common section patterns
        section_patterns = {
            'abstract': [
                r'abstract\s*\n(.*?)(?=\n\s*(?:keywords?|introduction|background|\d+\.|\n\n))',
                r'summary\s*\n(.*?)(?=\n\s*(?:keywords?|introduction|background|\d+\.|\n\n))'
            ],
            'introduction': [
                r'introduction\s*\n(.*?)(?=\n\s*(?:methods?|materials|methodology|design|\d+\.|\n\n))',
                r'background\s*\n(.*?)(?=\n\s*(?:methods?|materials|methodology|design|\d+\.|\n\n))'
            ],
            'methods': [
                r'methods?\s*\n(.*?)(?=\n\s*(?:results?|findings|analysis|discussion|\d+\.|\n\n))',
                r'methodology\s*\n(.*?)(?=\n\s*(?:results?|findings|analysis|discussion|\d+\.|\n\n))',
                r'materials?\s+and\s+methods?\s*\n(.*?)(?=\n\s*(?:results?|findings|\d+\.|\n\n))'
            ],
            'results': [
                r'results?\s*\n(.*?)(?=\n\s*(?:discussion|conclusions?|limitations|\d+\.|\n\n))',
                r'findings?\s*\n(.*?)(?=\n\s*(?:discussion|conclusions?|limitations|\d+\.|\n\n))'
            ],
            'discussion': [
                r'discussion\s*\n(.*?)(?=\n\s*(?:conclusions?|limitations|references|\d+\.|\n\n))',
            ],
            'conclusion': [
                r'conclusions?\s*\n(.*?)(?=\n\s*(?:references|bibliography|acknowledgments|\d+\.|\n\n))',
            ]
        }
        
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    sections[section_name] = match.group(1).strip()
                    break
        
        self.sections = sections
        return sections
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\n\d+\s*\n', '\n', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Clean up punctuation
        text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def get_text_excerpt(self, start_pattern: str, max_length: int = 500) -> str:
        """Get a text excerpt starting from a pattern"""
        if not self.text:
            return ""
        
        match = re.search(start_pattern, self.text, re.IGNORECASE)
        if match:
            start_pos = match.start()
            excerpt = self.text[start_pos:start_pos + max_length]
            return self.clean_text(excerpt)
        
        return ""


class TextAnalyzer:
    """Analyze extracted text for RoB assessment relevant content"""
    
    def __init__(self, text: str, sections: Dict[str, str] = None):
        self.text = text.lower()
        self.sections = sections or {}
        
    def find_randomization_content(self) -> List[str]:
        """Find sentences related to randomization"""
        patterns = [
            # Direct randomization mentions
            r'[^.]*randomiz[ed|ation][^.]*[.]',
            r'[^.]*random[ly]?\s+allocat[ed|ion][^.]*[.]',
            r'[^.]*random\s+assign[ed|ment][^.]*[.]',
            
            # Sequence generation
            r'[^.]*sequence\s+generat[ed|ion][^.]*[.]',
            r'[^.]*allocation\s+sequence[^.]*[.]',
            r'[^.]*computer[- ]generat[ed|ion][^.]*random[^.]*[.]',
            r'[^.]*random\s+number[s]?\s+generat[ed|or][^.]*[.]',
            
            # Concealment
            r'[^.]*conceal[ed|ment][^.]*[.]',
            r'[^.]*sealed\s+envelope[s]?[^.]*[.]',
            r'[^.]*opaque\s+envelope[s]?[^.]*[.]',
            r'[^.]*central[ized]?\s+randomi[sz]ation[^.]*[.]',
            
            # Block randomization
            r'[^.]*block\s+randomi[sz]ation[^.]*[.]',
            r'[^.]*stratifi[ed|cation][^.]*random[^.]*[.]',
            
            # Baseline characteristics
            r'[^.]*baseline\s+characteristic[s]?[^.]*[.]',
            r'[^.]*baseline\s+difference[s]?[^.]*[.]',
            r'[^.]*baseline\s+imbalance[s]?[^.]*[.]'
        ]
        
        return self._extract_matching_sentences(patterns)
    
    def find_blinding_content(self) -> List[str]:
        """Find sentences related to blinding"""
        patterns = [
            # General blinding
            r'[^.]*blind[ed|ing][^.]*[.]',
            r'[^.]*mask[ed|ing][^.]*[.]',
            r'[^.]*double[- ]blind[^.]*[.]',
            r'[^.]*single[- ]blind[^.]*[.]',
            r'[^.]*open[- ]label[^.]*[.]',
            
            # Participant awareness
            r'[^.]*participant[s]?\s+aware[^.]*[.]',
            r'[^.]*patient[s]?\s+aware[^.]*[.]',
            r'[^.]*subject[s]?\s+aware[^.]*[.]',
            
            # Care provider awareness
            r'[^.]*physician[s]?\s+aware[^.]*[.]',
            r'[^.]*doctor[s]?\s+aware[^.]*[.]',
            r'[^.]*clinician[s]?\s+aware[^.]*[.]',
            r'[^.]*investigator[s]?\s+aware[^.]*[.]',
            r'[^.]*staff\s+aware[^.]*[.]',
            
            # Outcome assessor blinding
            r'[^.]*assessor[s]?\s+blind[ed]?[^.]*[.]',
            r'[^.]*outcome[s]?\s+assessor[^.]*[.]',
            r'[^.]*blinded\s+assessor[^.]*[.]'
        ]
        
        return self._extract_matching_sentences(patterns)
    
    def find_deviation_content(self) -> List[str]:
        """Find sentences related to deviations from protocol"""
        patterns = [
            # Protocol deviations
            r'[^.]*protocol\s+deviation[s]?[^.]*[.]',
            r'[^.]*deviation[s]?\s+from\s+protocol[^.]*[.]',
            r'[^.]*protocol\s+violation[s]?[^.]*[.]',
            
            # Adherence and compliance
            r'[^.]*adheren[ce|t][^.]*[.]',
            r'[^.]*complian[ce|t][^.]*[.]',
            r'[^.]*non[- ]adheren[ce|t][^.]*[.]',
            r'[^.]*non[- ]complian[ce|t][^.]*[.]',
            
            # Crossover and switching
            r'[^.]*cross[- ]?over[^.]*[.]',
            r'[^.]*switch[ed|ing][^.]*treatment[^.]*[.]',
            r'[^.]*chang[ed|ing]\s+treatment[^.]*[.]',
            
            # Discontinuation
            r'[^.]*discontinu[ed|ation][^.]*[.]',
            r'[^.]*withdraw[n|al][^.]*[.]',
            r'[^.]*drop[- ]?out[s]?[^.]*[.]'
        ]
        
        return self._extract_matching_sentences(patterns)
    
    def find_missing_data_content(self) -> List[str]:
        """Find sentences related to missing data"""
        patterns = [
            # Missing data
            r'[^.]*missing\s+data[^.]*[.]',
            r'[^.]*incomplete\s+data[^.]*[.]',
            r'[^.]*data\s+availab[le|ility][^.]*[.]',
            
            # Loss to follow-up
            r'[^.]*loss\s+to\s+follow[- ]?up[^.]*[.]',
            r'[^.]*lost\s+to\s+follow[- ]?up[^.]*[.]',
            r'[^.]*follow[- ]?up\s+data[^.]*[.]',
            
            # Attrition and dropout
            r'[^.]*attrition[^.]*[.]',
            r'[^.]*dropout[s]?[^.]*[.]',
            r'[^.]*withdraw[n|al][^.]*[.]',
            
            # Analysis population
            r'[^.]*intention[- ]to[- ]treat[^.]*[.]',
            r'[^.]*per[- ]protocol[^.]*[.]',
            r'[^.]*complete[d]?\s+case[s]?[^.]*[.]',
            r'[^.]*modified\s+intention[^.]*[.]'
        ]
        
        return self._extract_matching_sentences(patterns)
    
    def find_outcome_measurement_content(self) -> List[str]:
        """Find sentences related to outcome measurement"""
        patterns = [
            # Measurement methods
            r'[^.]*outcome[s]?\s+measure[d|ment][^.]*[.]',
            r'[^.]*assessment\s+method[s]?[^.]*[.]',
            r'[^.]*measurement\s+method[s]?[^.]*[.]',
            
            # Timing and frequency
            r'[^.]*measure[d]?\s+at[^.]*[.]',
            r'[^.]*assess[ed]?\s+at[^.]*[.]',
            r'[^.]*time\s+point[s]?[^.]*[.]',
            r'[^.]*baseline\s+and[^.]*[.]',
            
            # Outcome assessors
            r'[^.]*outcome\s+assessor[s]?[^.]*[.]',
            r'[^.]*independent\s+assessor[^.]*[.]',
            r'[^.]*blinded\s+assessor[^.]*[.]',
            
            # Validity and reliability
            r'[^.]*validat[ed|ion][^.]*[.]',
            r'[^.]*reliab[le|ility][^.]*[.]',
            r'[^.]*inter[- ]rater[^.]*[.]',
            r'[^.]*intra[- ]rater[^.]*[.]'
        ]
        
        return self._extract_matching_sentences(patterns)
    
    def find_selective_reporting_content(self) -> List[str]:
        """Find sentences related to selective reporting"""
        patterns = [
            # Pre-specification
            r'[^.]*pre[- ]specifi[ed|cation][^.]*[.]',
            r'[^.]*protocol[^.]*register[ed]?[^.]*[.]',
            r'[^.]*trial\s+registr[y|ation][^.]*[.]',
            
            # Analysis plan
            r'[^.]*analysis\s+plan[^.]*[.]',
            r'[^.]*statistical\s+plan[^.]*[.]',
            r'[^.]*analytic\s+plan[^.]*[.]',
            
            # Primary/secondary outcomes
            r'[^.]*primary\s+outcome[s]?[^.]*[.]',
            r'[^.]*secondary\s+outcome[s]?[^.]*[.]',
            r'[^.]*primary\s+endpoint[s]?[^.]*[.]',
            
            # Multiple analyses
            r'[^.]*multiple\s+analy[ses|sis][^.]*[.]',
            r'[^.]*subgroup\s+analy[ses|sis][^.]*[.]',
            r'[^.]*post[- ]hoc\s+analy[ses|sis][^.]*[.]'
        ]
        
        return self._extract_matching_sentences(patterns)
    
    def _extract_matching_sentences(self, patterns: List[str]) -> List[str]:
        """Extract sentences matching the given patterns"""
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, self.text, re.IGNORECASE | re.DOTALL)
            matches.extend(found)
        
        # Remove duplicates and clean up
        unique_matches = []
        for match in matches:
            cleaned = match.strip()
            if cleaned and len(cleaned) > 20 and cleaned not in unique_matches:
                unique_matches.append(cleaned)
        
        return unique_matches[:10]  # Limit to 10 most relevant sentences


def extract_pdf_content(file_path: str) -> Dict[str, any]:
    """Main function to extract comprehensive content from PDF"""
    extractor = PDFTextExtractor(file_path)
    
    try:
        # Extract text and metadata
        text = extractor.extract_text()
        metadata = extractor.extract_metadata()
        sections = extractor.identify_sections()
        
        # Analyze for RoB content
        analyzer = TextAnalyzer(text, sections)
        
        rob_content = {
            'randomization': analyzer.find_randomization_content(),
            'blinding': analyzer.find_blinding_content(),
            'deviations': analyzer.find_deviation_content(),
            'missing_data': analyzer.find_missing_data_content(),
            'outcome_measurement': analyzer.find_outcome_measurement_content(),
            'selective_reporting': analyzer.find_selective_reporting_content()
        }
        
        return {
            'success': True,
            'text': text,
            'metadata': metadata,
            'sections': sections,
            'rob_content': rob_content,
            'word_count': len(text.split()) if text else 0
        }
        
    except Exception as e:
        logger.error(f"PDF content extraction failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'metadata': {},
            'sections': {},
            'rob_content': {},
            'word_count': 0
        }
