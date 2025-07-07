import os
from dotenv import load_dotenv
import datetime
import requests
import xml.etree.ElementTree as ET # Keep this for ET.fromstring in main.py
import io # Not explicitly used, but if it was in original, remove if not needed
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from google.genai import types
import contextlib # for httpx error

# Load environment variables from .env file
# Explicitly specifying '.env' to ensure it finds the file
load_dotenv('.env')

# --- Import functions from your new modules ---
from src.arxiv_utils import get_arxiv_dates, extract_arxiv_metadata, convert_abs_url_to_pdf_url, download_pdf
from src.llm_utils import generate_content_with_history, update_chat_config, summarize_text_with_llm
from src.pdf_utils import extract_text_from_pdf

# --- API Key & Client Initialization ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please create a .env file with GOOGLE_API_KEY=YOUR_KEY.")

client = genai.Client(api_key=GOOGLE_API_KEY)

# --- Embedding Model Initialization ---
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


# --- Define research interests ---
research_interests = "I'm interested in the connection between molecular gas and star formation in nearby galaxies, with a focus on dense molecular gas."
print(f"Your research interests are: {research_interests}") # This will still print as it goes to stdout, not stderr

# --- ArXiv API Query Setup and Execution ---
start_date, end_date = get_arxiv_dates()

print(f"Start date (YYYYMMDDHHMM): {start_date}")
print(f"End date (YYYYMMDDHHMM): {end_date}")

base_url = "http://export.arxiv.org/api/query?"
category = "astro-ph.GA"
sort_by = "submittedDate"
sort_order = "ascending"
start = 0
max_results = 100
search_query = f"search_query=cat:{category}+AND+submittedDate:[{start_date}+TO+{end_date}]"
url = f"{base_url}{search_query}&sortBy={sort_by}&sortOrder={sort_order}&start={start}&max_results={max_results}"

print(f"API Request URL for new astro-ph uploads: {url}")

try:
    response = requests.get(url)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"An error occurred during the API request: {e}")
    response = None

arxiv_metadata = []
if response:
    try:
        arxiv_metadata = extract_arxiv_metadata(response.text)
    except ET.ParseError as e:
        print(f"Error parsing the arXiv API response: {e}")
        arxiv_metadata = []

# --- Embedding Generation and Paper Ranking ---
paper_embeddings = {
    paper['id']: embedding_model.encode(paper['abstract'])
    for paper in arxiv_metadata if paper['abstract'] is not None and paper['id'] is not None
}

if arxiv_metadata and paper_embeddings:
    research_interests_embedding = embedding_model.encode(research_interests)

    ranked_papers = []
    for paper in arxiv_metadata:
        if paper['id'] in paper_embeddings:
            similarity = cosine_similarity([research_interests_embedding], [paper_embeddings[paper['id']]])[0][0]
            ranked_papers.append({'metadata': paper, 'similarity': similarity})

    ranked_papers.sort(key=lambda item: item['similarity'], reverse=True)
    top_relevant_papers = ranked_papers[:5]

    llm_prompt_content = f"""Based on your research interests: "{research_interests}", please review the following arXiv paper metadata and identify the most relevant ones. The papers are pre-ranked based on the semantic similarity of their abstracts to your interests.

    ArXiv Paper Metadata (Top Relevant):
    """
    arxiv_urls = []
    for i, item in enumerate(top_relevant_papers):
        paper = item['metadata']
        arxiv_urls.append(paper['id'])
        llm_prompt_content += f"""
    --- Paper {i+1} (Similarity: {item['similarity']:.4f}) ---
    Title: {paper['title']}
    ArXiv ID: {paper['id']}
    Authors: {', '.join([author['name'] for author in paper['authors']])}
    Publish Date: {paper['published']}
    Abstract: {paper['abstract']}
    Categories: {', '.join(paper['categories'])}
    """

    llm_prompt_content += """

    Based on the above metadata (ranked by abstract similarity), please identify the top 3 papers that would be of most interest, considering both the similarity score and the content of the abstract. For each of these top 3 papers, list the **Title**, **Similarity**, **ArXiv ID**, **Author List**, **ArXiv Publish Date**, **Abstract**, and a brief **Reasoning** explaining why it aligns with the research interests: "{research_interests}". Format your response in Markdown, with each piece of metadata on a new line.
    """

    prompt = llm_prompt_content
    try:
        chat_session = None
        response_from_llm, chat_session = generate_content_with_history(prompt, client, chat_session=None)
        print("\n--- LLM Response: Top Relevant Papers (Based on Embeddings and LLM Review) ---\n")
        print(response_from_llm.text)
    except Exception as e:
        print(f"An error occurred while generating the LLM response: {e}")
else:
    print("No arXiv metadata or paper embeddings were successfully generated, so the LLM cannot identify papers of interest.")

# --- Main Execution Block for PDF Download and Summarization (this is still inside the 'with' block) ---
if __name__ == "__main__": # This inner if __name__ == "__main__": is redundant but harmless
                            # if it was already there, you can leave it or remove it.
                            # The outer 'with' block now ensures suppression.

    all_summaries = ""
    all_summaries_list = []

    if arxiv_urls:
        for i, arxiv_url in enumerate(arxiv_urls):
            print(f"\n--- Processing Paper {i+1} ---")
            print(f"arXiv URL: {arxiv_url}")

            pdf_url = convert_abs_url_to_pdf_url(arxiv_url)
            print(f"PDF URL: {pdf_url}")

            pdf_path = download_pdf(pdf_url)

            if pdf_path:
                extracted_text = extract_text_from_pdf(pdf_path)

                if extracted_text:
                    summary = summarize_text_with_llm(extracted_text, client, chat_session)

                if summary:
                        all_summaries_list.append(f"**Paper {i+1}: {summary}\n")
                else:
                        all_summaries_list.append(f"Failed to generate summary for Paper {i+1}\n")

                if pdf_path:
                    os.remove(pdf_path)
                    print(f"Deleted the downloaded PDF: {pdf_path}")

            else:
                all_summaries_list.append(f"Failed to download PDF for Paper {i+1}\n")

        final_summary = "Good morning! Here's a quick look at some papers you might find relevant\n\n" + "\n".join(all_summaries_list)

        print("\n--- All Paper Summaries ---")
        print(final_summary)

    else:
        print("No arXiv URLs found for detailed summarization.")