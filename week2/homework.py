import requests
from typing import Optional

reader_url_prefix = "https://r.jina.ai/"

def get_page_content(url: str) -> Optional[str]:
    """
    Fetch the Markdown content of a web page using the Jina Reader service.

    This function prepends the Jina Reader proxy URL to the provided `url`,
    sends a GET request with a timeout, and decodes the response as UTF-8 text.

    Args:
        url (str): The URL of the page to fetch.

    Returns:
        Optional[str]: The Markdown-formatted content of the page if the request
        succeeds; otherwise, None.

    Raises:
        None: All network or decoding errors are caught and suppressed.
               Logs or error messages could be added as needed.
    """
    reader_url = reader_url_prefix + url

    try:
        response = requests.get(reader_url, timeout=10)
        response.raise_for_status()  # raises for 4xx/5xx HTTP errors
        return response.content.decode("utf-8")
    except (requests.exceptions.RequestException, UnicodeDecodeError) as e:
        # Optional: log or print the error for debugging
        print(f"Error fetching content from {url}: {e}")
        return None