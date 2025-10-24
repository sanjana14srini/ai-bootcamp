import os
import sys
import requests
from typing import Any, Dict, Iterable, List
import logging


# setting up the arxiv api
import urllib, urllib.request
import feedparser
from arxiv2text import arxiv_to_text


# Turn off all logging
logging.disable(logging.CRITICAL)


def get_metadata(paper_name="electron", max_results=2):

    paper_name = paper_name.replace(" ", "+")

    url = f'http://export.arxiv.org/api/query?search_query=all:{paper_name}&max_results={max_results}'
    data = urllib.request.urlopen(url).read()
    feed = feedparser.parse(data)


    return feed



def sliding_window(
        seq: Iterable[Any],
        size: int,
        step: int
    ) -> List[Dict[str, Any]]:
    """
    Create overlapping chunks from a sequence using a sliding window approach.

    Args:
        seq: The input sequence (string or list) to be chunked.
        size (int): The size of each chunk/window.
        step (int): The step size between consecutive windows.

    Returns:
        list: A list of dictionaries, each containing:
            - 'start': The starting position of the chunk in the original sequence
            - 'content': The chunk content

    Raises:
        ValueError: If size or step are not positive integers.

    Example:
        >>> sliding_window("hello world", size=5, step=3)
        [{'start': 0, 'content': 'hello'}, {'start': 3, 'content': 'lo wo'}]
    """
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")

    n = len(seq)
    result = []
    for i in range(0, n, step):
        batch = seq[i:i+size]
        result.append({'start': i, 'content': batch})
        if i + size > n:
            break

    return result


def extract_data(feed):
    doc = []
    
    for entry in feed.entries:
        entry_id_url = entry.id
        arxiv_id = entry_id_url.split('/')[-1]

        pdf_url = entry["links"][1]["href"]
        paper_data = arxiv_to_text(pdf_url)

        if paper_data is not None:
            chunks = sliding_window(paper_data, 5000, 1000)
            for chunk in chunks:
                entry_dict = { 
                    "id": arxiv_id,
                    "title": entry.title,
                    "authors": entry.authors,
                    "published": entry.published,
                    "summary": entry.summary,
                    "content": chunk["content"],

                }
                doc.append(entry_dict)
            print(f"successfully extracted the pdf {pdf_url}")
        else:
            print(f"pdf not found for {pdf_url}")
            continue
    return doc




feed = get_metadata("LoRA", 2)
doc = extract_data(feed)
