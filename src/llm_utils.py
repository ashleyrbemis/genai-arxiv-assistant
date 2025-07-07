from google import genai
from google.genai import types

def generate_content_with_history(prompt, client, chat_session=None):
    """Generates content with chat history using genai.Client.
    Accepts the 'client' object as an argument."""
    try:
        if chat_session is None:
            # Ensure client is valid before creating chat session
            if client is None:
                print("Error: GenAI client is None in generate_content_with_history.")
                return None, None
            chat_session = client.chats.create(model='gemini-2.0-flash')
        
        # Ensure chat_session is valid before sending message
        if chat_session is None:
            print("Error: Chat session is None before sending message.")
            return None, None

        response = chat_session.send_message(prompt)
        return response, chat_session
    except Exception as e:
        print(f"Error in generate_content_with_history: {e}")
        # Optionally, print more details about the response if available
        # if 'response' in locals() and hasattr(response, 'candidates'):
        #     print(f"Response candidates: {response.candidates}")
        # if 'response' in locals() and hasattr(response, 'prompt_feedback'):
        #     print(f"Response prompt feedback: {response.prompt_feedback}")
        return None, None


def update_chat_config(chat_session, new_config):
    """Updates the chat session configuration."""
    # Create a new GenerateContentConfig object with the updated parameters
    updated_config = types.GenerateContentConfig(**new_config)

    # Update the chat session's config attribute
    chat_session.config = updated_config

    return chat_session


def summarize_text_with_llm(text, client, chat_session, prompt="Placeholder prompt, actual prompt constructed below"):
    """Summarizes the given text using a GenerativeModel with few-shot prompting."""
    try:
        new_config={
            "max_output_tokens": 1024,
            "temperature": 0.3,
            "top_p": 0.8
        }
        if chat_session is None:
            print("Error: chat_session is None when calling update_chat_config.")
            return None

        chat_session = update_chat_config(chat_session, new_config)

        # Few-shot examples - UPDATED FOR SECTIONED OUTPUT
        few_shot_examples = [
            {
                "input": "This paper investigates the properties of dark matter halos using high-resolution N-body simulations. We find a strong correlation between halo concentration and formation time.",
                "output": """**Title:** Dark Matter Halo Concentration and Formation Time
**Authors:** J. Doe, E. Black, et al.
**ArXiv Link:** http://arxiv.org/abs/2401.12345v1

### Data Used
This study primarily utilized data generated from high-resolution N-body cosmological simulations, specifically dark matter-only runs, which tracked the evolution of structure formation in a Lambda-CDM universe.

### Methodology
The methodology involved identifying dark matter halos at various cosmic epochs within the simulations and calculating their concentration parameters. Halo formation times were determined based on the accretion history of half their final mass. Correlation analysis was then performed between these two properties.

### Key Findings
The major finding is a strong, inverse correlation between a dark matter halo's final concentration and its formation time. Halos that formed earlier were found to be significantly more concentrated, suggesting that early assembly leads to denser inner structures."""
            },
            {
                "input": "We present observations of a new exoplanet candidate using the Kepler space telescope. Photometric analysis indicates a planet with a radius of 2.5 Earth radii and an orbital period of 15 days.",
                "output": """**Title:** Discovery and Characterization of Kepler-1234b
**Authors:** A. Smith, B. Jones, et al.
**ArXiv Link:** http://arxiv.org/abs/2402.67890v1

### Data Used
The research relied on photometric time-series data acquired by the Kepler space telescope, focusing on brightness measurements of the host star to detect periodic dimmings indicative of planetary transits.

### Methodology
The methodology involved analyzing the high-precision light curves to identify potential transit events. Follow-up photometric modeling was conducted to derive the planet's radius, orbital period, and other physical characteristics from the observed transit depths and durations.

### Key Findings
The key finding is the discovery of Kepler-1234b, a new exoplanet candidate. Preliminary characterization suggests it has a radius of approximately 2.5 Earth radii and an orbital period of 15 days, placing it in the 'super-Earth' or 'mini-Neptune' category. This discovery contributes to understanding exoplanet demographics."""
            }
        ]

        # --- CORRECTED: Build example_prompt_text BEFORE constructing full_prompt ---
        example_prompt_text = ""
        for example in few_shot_examples:
            example_prompt_text += f"Paper Input: {example['input']}\nSummary Output:\n{example['output']}\n\n"

        # --- CORRECTED: Single definition of full_prompt ---
        full_prompt = f"""Please summarize the following research paper. Your summary should be structured into clear sections using Markdown headings (e.g., '### Data Used', '### Methodology', '### Key Findings').
        For each summary, include:
        - **Paper Title**
        - **Short Author List**
        - **ArXiv Link**
        - **Data Used**
        - **Methodology**
        - **Key Findings**

        Follow the structure and detail shown in the examples provided.

        Here's a quick look at some example summaries:

        {example_prompt_text}

        Now, summarize the following research paper:
        {text}
        """

        # Corrected call to generate_content_with_history - passing 'client' directly
        response, chat_session = generate_content_with_history(full_prompt, client, chat_session)
        
        if response is None or not hasattr(response, 'text') or not response.text:
            print(f"Warning: generate_content_with_history returned no text for summarization.")
            return None

        return response.text
    except Exception as e:
        print(f"Error during LLM summarization: {e}")
        return None
