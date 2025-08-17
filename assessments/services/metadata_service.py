"""
Metadata Fetching Service for PMID/DOI

This service fetches publication metadata from various sources:
1. PubMed API for PMID
2. CrossRef API for DOI
3. Web scraping as fallback
"""

import requests
import re
import logging
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

try:
    from bs4 import BeautifulSoup
    from Bio import Entrez
except ImportError:
    BeautifulSoup = None
    Entrez = None

logger = logging.getLogger(__name__)


class MetadataFetcher:
    """Fetch metadata from PMID, DOI, or URL"""
    
    def __init__(self):
        # Set Entrez email (required by NCBI)
        if Entrez:
            Entrez.email = "robass@example.com"  # Replace with actual email
        
    def fetch_by_pmid(self, pmid: str) -> Dict[str, str]:
        """Fetch metadata using PubMed ID"""
        try:
            if not Entrez:
                raise ImportError("Biopython required for PMID fetching")
            
            # Clean PMID
            pmid = re.sub(r'\D', '', pmid)
            if not pmid:
                raise ValueError("Invalid PMID")
            
            # Fetch from PubMed
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml")
            records = Entrez.parse(handle)
            
            metadata = {}
            for record in records:
                article = record.get('MedlineCitation', {}).get('Article', {})
                
                # Title
                title = article.get('ArticleTitle', '')
                if isinstance(title, list):
                    title = ' '.join(str(t) for t in title)
                metadata['title'] = str(title).strip()
                
                # Authors
                authors = []
                author_list = article.get('AuthorList', [])
                for author in author_list[:10]:  # Limit to first 10 authors
                    if 'LastName' in author and 'ForeName' in author:
                        full_name = f"{author['ForeName']} {author['LastName']}"
                        authors.append(full_name)
                metadata['authors'] = ', '.join(authors)
                
                # Journal
                journal_info = article.get('Journal', {})
                journal_title = journal_info.get('Title', '') or journal_info.get('ISOAbbreviation', '')
                metadata['journal'] = str(journal_title).strip()
                
                # Publication date
                pub_date = article.get('ArticleDate') or journal_info.get('JournalIssue', {}).get('PubDate', {})
                if pub_date:
                    year = pub_date.get('Year', '')
                    month = pub_date.get('Month', '')
                    day = pub_date.get('Day', '')
                    if year:
                        metadata['year'] = str(year)
                        if month and day:
                            metadata['publication_date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        elif month:
                            metadata['publication_date'] = f"{year}-{month.zfill(2)}"
                        else:
                            metadata['publication_date'] = str(year)
                
                # Abstract
                abstract = article.get('Abstract', {}).get('AbstractText', '')
                if isinstance(abstract, list):
                    abstract_parts = []
                    for part in abstract:
                        if isinstance(part, dict):
                            label = part.get('@Label', '')
                            text = part.get('#text', str(part))
                            if label:
                                abstract_parts.append(f"{label}: {text}")
                            else:
                                abstract_parts.append(text)
                        else:
                            abstract_parts.append(str(part))
                    abstract = ' '.join(abstract_parts)
                metadata['abstract'] = str(abstract).strip()
                
                # DOI (if available)
                doi_list = article.get('ELocationID', [])
                for elocation in doi_list:
                    if elocation.get('@EIdType') == 'doi':
                        metadata['doi'] = str(elocation.get('#text', '')).strip()
                        break
                
                # PMID
                metadata['pmid'] = pmid
                break
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to fetch PMID {pmid}: {str(e)}")
            return self._error_metadata(f"PMID fetch failed: {str(e)}")
    
    def fetch_by_doi(self, doi: str) -> Dict[str, str]:
        """Fetch metadata using DOI via CrossRef API"""
        try:
            # Clean DOI
            doi = doi.strip()
            if doi.startswith('http'):
                doi = doi.split('/')[-2] + '/' + doi.split('/')[-1]
            if not doi.startswith('10.'):
                raise ValueError("Invalid DOI format")
            
            # CrossRef API
            url = f"https://api.crossref.org/works/{doi}"
            headers = {'Accept': 'application/json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            work = data.get('message', {})
            
            metadata = {}
            
            # Title
            titles = work.get('title', [])
            if titles:
                metadata['title'] = str(titles[0]).strip()
            
            # Authors
            authors = []
            author_list = work.get('author', [])
            for author in author_list[:10]:  # Limit to first 10
                given = author.get('given', '')
                family = author.get('family', '')
                if family:
                    if given:
                        authors.append(f"{given} {family}")
                    else:
                        authors.append(family)
            metadata['authors'] = ', '.join(authors)
            
            # Journal
            container_titles = work.get('container-title', [])
            if container_titles:
                metadata['journal'] = str(container_titles[0]).strip()
            
            # Publication date
            pub_date = work.get('published-print') or work.get('published-online')
            if pub_date and 'date-parts' in pub_date:
                date_parts = pub_date['date-parts'][0]
                if len(date_parts) >= 1:
                    metadata['year'] = str(date_parts[0])
                if len(date_parts) >= 3:
                    metadata['publication_date'] = f"{date_parts[0]}-{date_parts[1]:02d}-{date_parts[2]:02d}"
                elif len(date_parts) >= 2:
                    metadata['publication_date'] = f"{date_parts[0]}-{date_parts[1]:02d}"
                else:
                    metadata['publication_date'] = str(date_parts[0])
            
            # Abstract (usually not available via CrossRef)
            abstract = work.get('abstract', '')
            if abstract:
                metadata['abstract'] = str(abstract).strip()
            
            # DOI
            metadata['doi'] = doi
            
            # Volume, Issue, Pages
            metadata['volume'] = str(work.get('volume', '')).strip()
            metadata['issue'] = str(work.get('issue', '')).strip()
            metadata['pages'] = str(work.get('page', '')).strip()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to fetch DOI {doi}: {str(e)}")
            return self._error_metadata(f"DOI fetch failed: {str(e)}")
    
    def fetch_by_url(self, url: str) -> Dict[str, str]:
        """Fetch metadata by scraping webpage"""
        try:
            if not BeautifulSoup:
                raise ImportError("BeautifulSoup4 required for web scraping")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            metadata = {}
            
            # Try to extract title
            title_selectors = [
                'meta[name=\"citation_title\"]',
                'meta[property=\"og:title\"]',
                'title',
                'h1'
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        title = element.get('content', '').strip()
                    else:
                        title = element.get_text().strip()
                    if title and len(title) > 5:
                        metadata['title'] = title
                        break
            
            # Try to extract authors
            author_selectors = [
                'meta[name=\"citation_author\"]',
                'meta[name=\"author\"]',
                '.author',
                '.authors'
            ]
            
            authors = []
            for selector in author_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if element.name == 'meta':
                        author = element.get('content', '').strip()
                    else:
                        author = element.get_text().strip()
                    if author:
                        authors.append(author)
                if authors:
                    break
            
            if authors:
                metadata['authors'] = ', '.join(authors[:10])  # Limit to 10
            
            # Try to extract journal
            journal_selectors = [
                'meta[name=\"citation_journal_title\"]',
                'meta[name=\"journal\"]'
            ]
            
            for selector in journal_selectors:
                element = soup.select_one(selector)
                if element:
                    journal = element.get('content', '').strip()
                    if journal:
                        metadata['journal'] = journal
                        break
            
            # Try to extract year
            year_selectors = [
                'meta[name=\"citation_publication_date\"]',
                'meta[name=\"citation_year\"]',
                'meta[name=\"date\"]'
            ]
            
            for selector in year_selectors:
                element = soup.select_one(selector)
                if element:
                    date_str = element.get('content', '').strip()
                    year_match = re.search(r'(19|20)\\d{2}', date_str)
                    if year_match:
                        metadata['year'] = year_match.group()
                        break
            
            # Try to extract DOI
            doi_selectors = [
                'meta[name=\"citation_doi\"]',
                'meta[name=\"doi\"]'
            ]
            
            for selector in doi_selectors:
                element = soup.select_one(selector)
                if element:
                    doi = element.get('content', '').strip()
                    if doi.startswith('10.'):
                        metadata['doi'] = doi
                        break
            
            # Try to extract PMID
            pmid_selectors = [
                'meta[name=\"citation_pmid\"]',
                'meta[name=\"pmid\"]'
            ]
            
            for selector in pmid_selectors:
                element = soup.select_one(selector)
                if element:
                    pmid = element.get('content', '').strip()
                    if pmid.isdigit():
                        metadata['pmid'] = pmid
                        break
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {str(e)}")
            return self._error_metadata(f"URL fetch failed: {str(e)}")
    
    def _error_metadata(self, error_msg: str) -> Dict[str, str]:
        """Return error metadata"""
        return {
            'error': error_msg,
            'title': '',
            'authors': '',
            'journal': '',
            'year': '',
            'doi': '',
            'pmid': '',
            'abstract': ''
        }
    
    def auto_fetch_metadata(self, identifier: str) -> Dict[str, str]:
        """Auto-detect identifier type and fetch metadata"""
        identifier = identifier.strip()
        
        # Detect identifier type
        if re.match(r'^\\d+$', identifier):
            # Looks like PMID
            return self.fetch_by_pmid(identifier)
        elif re.match(r'^10\\.\\d+/', identifier) or identifier.startswith('doi:'):
            # Looks like DOI
            doi = identifier.replace('doi:', '').strip()
            return self.fetch_by_doi(doi)
        elif identifier.startswith('http'):
            # Looks like URL
            return self.fetch_by_url(identifier)
        else:
            # Try to extract from text
            # Check for DOI patterns
            doi_match = re.search(r'10\\.\\d+/[^\\s]+', identifier)
            if doi_match:
                return self.fetch_by_doi(doi_match.group())
            
            # Check for PMID patterns
            pmid_match = re.search(r'pmid:?\\s*(\\d+)', identifier, re.IGNORECASE)
            if pmid_match:
                return self.fetch_by_pmid(pmid_match.group(1))
            
            return self._error_metadata("Unable to detect identifier type")


def extract_metadata_from_identifier(identifier: str) -> Dict[str, str]:
    """Main function to extract metadata from any identifier"""
    fetcher = MetadataFetcher()
    return fetcher.auto_fetch_metadata(identifier)
