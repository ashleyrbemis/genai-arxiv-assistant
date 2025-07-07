import PyPDF2
import os # For FileNotFoundError related to os.remove

def extract_text_from_pdf(pdf_path):
    """Extracts text content from a PDF file using PyPDF2."""
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None