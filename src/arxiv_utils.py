import datetime
import pytz
import xml.etree.ElementTree as ET
import requests # For the initial API request
import urllib.parse # For convert_abs_url_to_pdf_url's os.path.basename
import urllib.request 
import os             
import time           

def get_arxiv_dates():
    """
    Calculates the date range for arXiv submissions, accounting for weekends,
    and returns them in YYYYMMDDHHMM format.

    Returns:
        A tuple of (start_date_formatted, end_date_formatted).
    """
    eastern = pytz.timezone('US/Eastern')
    now_eastern = datetime.datetime.now(eastern)
    today = now_eastern.date()

    if now_eastern.hour < 20:
        today -= datetime.timedelta(days=1)

    while today.weekday() >= 5:
        today -= datetime.timedelta(days=1)

    latest_weekday = today.strftime("%Y%m%d")

    # Directly construct the submission dates with "14" time.
    start_date_formatted = (today - datetime.timedelta(days=1)).strftime("%Y%m%d") + "1400"
    end_date_formatted = today.strftime("%Y%m%d") + "1400"

    return start_date_formatted, end_date_formatted

def extract_arxiv_metadata(xml_response):
    """Parses the arXiv API Atom feed and extracts all relevant metadata."""
    root = ET.fromstring(xml_response)
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
    papers_metadata = []
    for entry in root.findall('atom:entry', namespace):
        metadata = {}
        # Extract core Atom elements
        title = entry.find('atom:title', namespace)
        metadata['title'] = title.text.strip() if title is not None else None
        id_element = entry.find('atom:id', namespace)
        metadata['id'] = id_element.text.strip() if id_element is not None else None
        published = entry.find('atom:published', namespace)
        metadata['published'] = published.text.strip() if published is not None else None
        updated = entry.find('atom:updated', namespace)
        metadata['updated'] = updated.text.strip() if updated is not None else None
        summary = entry.find('atom:summary', namespace)
        metadata['abstract'] = summary.text.strip() if summary is not None else None

        # Extract authors
        authors = entry.findall('atom:author', namespace)
        metadata['authors'] = []
        for author in authors:
            name = author.find('atom:name', namespace)
            affiliation = author.find('arxiv:affiliation', namespace)
            author_info = {'name': name.text.strip() if name is not None else None,
                           'affiliation': affiliation.text.strip() if affiliation is not None else None}
            metadata['authors'].append(author_info)

        # Extract categories
        categories = [cat.get('term') for cat in entry.findall('atom:category', namespace) if cat.get('scheme') == 'http://arxiv.org/schemas/atom']
        metadata['categories'] = categories

        # Extract primary category
        primary_category = entry.find('arxiv:primary_category', namespace)
        metadata['primary_category'] = primary_category.get('term') if primary_category is not None else None

        # Extract links
        links = entry.findall('atom:link', namespace)
        metadata['links'] = []
        for link in links:
            metadata['links'].append({'href': link.get('href'), 'rel': link.get('rel'), 'title': link.get('title'), 'type': link.get('type')})

        # Extract arXiv-specific elements
        comment = entry.find('arxiv:comment', namespace)
        metadata['comment'] = comment.text.strip() if comment is not None else None
        journal_ref = entry.find('arxiv:journal_ref', namespace)
        metadata['journal_ref'] = journal_ref.text.strip() if journal_ref is not None else None
        doi = entry.find('arxiv:doi', namespace)
        metadata['doi'] = doi.text.strip() if doi is not None else None

        papers_metadata.append(metadata)
    return papers_metadata

def convert_abs_url_to_pdf_url(abs_url):
    """
    Converts an arXiv abstract URL to its corresponding PDF URL using the export.arxiv.org format.

    Args:
        abs_url (str): The arXiv abstract URL (e.g., 'http://arxiv.org/abs/2504.06802v1').

    Returns:
        str: The corresponding arXiv PDF URL (e.g., 'http://export.arxiv.org/pdf/2504.06802v1.pdf').
             Returns None if the input URL is not in the expected format.
    """
    if "arxiv.org/abs/" in abs_url:
        # Split the URL at '/abs/'
        parts = abs_url.split("arxiv.org/abs/")
        if len(parts) == 2:
            arxiv_id_with_version = parts[1].strip()
            # Remove potential 'v' and the version number
            arxiv_id = arxiv_id_with_version.split('v')
            # Construct the PDF URL using the extracted arXiv ID
            pdf_url = f"http://export.arxiv.org/pdf/{arxiv_id_with_version}.pdf"
            return pdf_url
    return None

def download_pdf(pdf_url, max_retries=3, wait_time=3):
    """
    Downloads a PDF from a given URL with retry logic respecting arXiv API limits.

    Args:
        pdf_url (str): The URL of the PDF to download.
        max_retries (int): The maximum number of times to retry the download.
        wait_time (int): The time to wait (in seconds) between retries.

    Returns:
        str or None: The path to the downloaded PDF if successful, otherwise None.
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempting to download: {pdf_url} (Attempt {attempt + 1}/{max_retries})")
            pdf_filename = os.path.basename(urllib.parse.urlparse(pdf_url).path)
            urllib.request.urlretrieve(pdf_url, pdf_filename)
            print(f"Successfully downloaded: {pdf_filename}")
            return pdf_filename
        except urllib.error.URLError as e:
            print(f"Download failed (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Waiting for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Download failed.")
                return None
        except Exception as e:
            print(f"An unexpected error occurred during download (Attempt {attempt + 1}/{max_retries}): {e}")
            return None
        finally:
            # Respect arXiv API rate limit by waiting after each attempt
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            elif attempt == max_retries -1 and attempt > 0:
                time.sleep(wait_time) # Wait after the last attempt as well, if retries occurred
