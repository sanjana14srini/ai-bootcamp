import requests
from typing import Optional
from minsearch import AppendableIndex
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import FunctionToolCallEvent
from pydantic import BaseModel
import re
import urllib, urllib.request
import feedparser
from toyaikit.chat.interface import StdOutputInterface
from toyaikit.chat.runners import PydanticAIRunner
from typing import Any, Dict, Iterable, List
import asyncio
import mwparserfromhell



# Defining all helper classes and functions

class FetchQuery(BaseModel):
    query: str

class FetchParams(BaseModel):
    url: str


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



# Main agent class that will be used for defining the agent tools
class AgentTools:

    def __init__(self, index, headers=None):
        self.index = index
        if headers is not None:
            self.headers = headers
        else:
            self.headers = {
                "User-Agent": "MyWikipediaApp/1.0"
                }


    def search(self, search_query: str):

        # search_query = search_query.replace(" ", "+")
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_query,
            "srlimit": 10
        }

        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()  # Raise an error if the request failed
        data = response.json()
        
        return data

        # # parse this data
        # document = []
        # for data_chunks in data['query']['search']:
        #     doc = {
        #         "title": data_chunks["title"],
        #         "snippet": data_chunks["snippet"],
        #     }
        #     document.append(doc)
        
        # self.index.append(document)


    
    def get_page(self, page_title: str):

        url = f" https://en.wikipedia.org/w/index.php"

        params = {
            "action": "raw",
            "format": "json",
            "prop": "text",
            "title": page_title,
            "redirects": True
        }
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()  # Raise an error if the request failed
        data = response.text

        return data
        
        # wikicode = mwparserfromhell.parse(data)
        # plain_text = wikicode.strip_code()
        # return plain_text



index = AppendableIndex(text_fields=["title", "snippet"])
agent_class = AgentTools(index=index)

r = agent_class.search("european economic crisis")
# print(r)

# r = agent_class.get_page("capybara")
# print(r)