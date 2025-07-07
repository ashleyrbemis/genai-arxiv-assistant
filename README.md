# GenAI Research Assistant: Tailored ArXiv Paper Summaries

## Project Overview

This project implements a personalized arXiv paper recommendation system, leveraging Google's Generative AI (Gemini) and sentence embeddings. It automates the process of identifying relevant new research papers based on a user's specified interests, summarizing them, and providing direct links.

This project was originally developed as a capstone project for the **5-Day Gen AI Intensive Course with Google in collaboration with Ana Ennis** on [Kaggle](https://www.kaggle.com/code/anistellar/genai-capstone-project-cosmic-compass/). This version builds upon the original by providing a robust, modular, and locally executable solution.

## Problem Statement

In today's fast-paced research environment, staying updated with the latest scientific literature can be overwhelming. Researchers often spend significant time sifting through new publications to find relevant papers. This tool aims to streamline that process by intelligently filtering and summarizing papers from the arXiv astrophysics (specifically astro-ph.GA) category that align with specific research interests.

## Data Sources

* **arXiv API:** Fetches metadata (title, abstract, authors, links, etc.) for recent astrophysics preprints.

* **Google Gemini API:** Utilized for advanced natural language understanding to review and summarize paper abstracts and full text.

## Methodology

1. **ArXiv Data Collection:** Automatically queries the arXiv API for new submissions within a specified astrophysics category (`astro-ph.GA`) for a given date range.

2. **Research Interest Definition:** User defines their specific research interests.

3. **Embedding Generation:** Uses the `all-MiniLM-L6-v2` Sentence Transformer model to convert both the user's research interests and paper abstracts into numerical embeddings.

4. **Semantic Similarity Ranking:** Calculates cosine similarity between the research interest embedding and each paper's abstract embedding to rank papers by relevance.

5. **LLM-Powered Filtering & Summarization:** The top-ranked papers are then fed to the Google Gemini Pro model, which performs a more nuanced review to identify the absolute top papers and generates concise, structured summaries including data, methodology, and key findings.

6. **PDF Text Extraction (Optional/Advanced):** Downloads the full PDF for selected papers and extracts text to provide even richer context for summarization.

## Key Findings/Results

* The system successfully identifies and ranks arXiv papers based on user-defined research interests.

* Gemini's summarization capabilities provide quick, digestible insights into complex research papers, now with a clear breakdown of data, methodology, and findings.

* Automates a time-consuming manual process, allowing researchers to efficiently keep up with new literature.

## Technologies Used

* Python 3.9+

* Google Generative AI (Gemini API)

* `feedparser` (for arXiv API parsing)

* `PyPDF2` (for PDF text extraction)

* `sentence-transformers` (for generating embeddings)

* `scikit-learn` (for cosine similarity calculation)

* `python-dotenv` (for secure environment variable management)

* `requests`

* `pytz`

* `lxml`

* `markdown2`

## Project Structure

```
genai-arxiv-assistant/
├── .env                  # Environment variables (ignored by Git)
├── .gitignore            # Specifies files/folders to ignore
├── LICENSE               # MIT License
├── README.md             # Project overview and instructions
├── requirements.txt      # Python dependencies for easy setup
├── main.py               # Main script to run the application
└── src/
    ├── __init__.py       # Makes 'src' a Python package
    ├── arxiv_utils.py    # Functions for arXiv API interaction (dates, metadata, PDF download)
    ├── llm_utils.py      # Functions for LLM interaction (content generation, config, summarization)
    └── pdf_utils.py      # Functions for PDF text extraction

```

## How to Run This Project Locally

To set up and run this project on your local machine, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone [https://github.com/ashleyrbemis/genai-arxiv-assistant.git](https://github.com/ashleyrbemis/genai-arxiv-assistant.git)
   cd genai-arxiv-assistant
   
   ```

2. **Set Up Your Google API Key:**

   * Obtain a Google AI Studio API Key from [Google AI Studio](https://makersuite.google.com/app/apikey).

   * Create a file named `.env` in the root directory of the project.

   * Add your API key to this `.env` file in the following format:

     ```
     GOOGLE_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
     
     ```

     **Important:** Do NOT commit your `.env` file to Git. It's already included in `.gitignore` for your security.

3. **Create and Activate a Conda Environment:**

   ```bash
   conda create --name ds_project_env python=3.9 -y
   conda activate ds_project_env
   
   ```

4. **Install Dependencies:**

   ```bash
   conda install -c conda-forge feedparser pypdf2 markdown2 sentence-transformers scikit-learn pytz requests lxml -y
   pip install "google-genai==1.7.0" python-dotenv
   
   ```

5. **Run the Script:**

   ```bash
   python main.py
   
   ```

   *(The script will print the top relevant papers and their summaries based on the `research_interests` defined within the `main.py` file. You can modify the `research_interests` variable directly to customize it for your needs.)*

**Note on Console Output:**
You might observe messages like `Exception ignored in: <function SyncHttpxClient.__del__ ...>` followed by `AttributeError: 'NoneType' object has no attribute 'CLOSED'` when the script finishes. These are benign messages from the underlying `httpx` library (used by `google-genai`) during Python's interpreter shutdown and do not affect the functionality or output of the project. They can be safely ignored.

## Future Enhancements

* **Interactive Input:** Allow users to input their research interests via command-line arguments or a simple web interface.

* **Broader Categories:** Expand to cover more arXiv categories or allow user selection.

* **Notification System:** Implement email or Slack notifications for new relevant papers.

* **Advanced Filtering:** Add options for filtering by author, publication date, or keywords.

* **Web Interface:** Develop a simple Streamlit or Flask application for a user-friendly interface.

## Contact

* **Ashley Bemis** - arbemis@gmail.com

* LinkedIn: [www.linkedin.com/in/ashley-r-bemis](https://www.linkedin.com/in/ashley-r-bemis)

* Personal Website: <https://ashleyrbemis.github.io/>
