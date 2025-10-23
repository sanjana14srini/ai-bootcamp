import requests
from typing import Optional
from minsearch import AppendableIndex
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import FunctionToolCallEvent
from pydantic import BaseModel
import re
from toyaikit.chat.interface import StdOutputInterface
from toyaikit.chat.runners import PydanticAIRunner
from typing import Any, Dict, Iterable, List
import asyncio



reader_url_prefix = "https://r.jina.ai/"

# Defining all helper classes and functions

class NamedCallback:

    def __init__(self, agent):
        self.agent_name = agent.name

    async def print_function_calls(self, ctx, event):
        # Detect nested streams
        if hasattr(event, "__aiter__"):
            async for sub in event:
                await self.print_function_calls(ctx, sub)
            return

        if isinstance(event, FunctionToolCallEvent):
            tool_name = event.part.tool_name
            args = event.part.args
            print(f"TOOL CALL ({self.agent_name}): {tool_name}({args})")

    async def __call__(self, ctx, event):
        return await self.print_function_calls(ctx, event)


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

    def __init__(self, index):
        self.index = index

    @staticmethod
    def get_all_webpage_data(url) -> Optional[str]:
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
    
    @staticmethod
    def parse_data(raw_data):

        lines = raw_data.splitlines()

        metadata = {
            "title": None,
            "url_source": "",
            "published_time": None,
            "markdown_content": None
        }

        meta_lines = []
        content_start = 0

        # Identify metadata lines at the top (e.g. "Title: ...")
        for i, line in enumerate(lines):
            if re.match(r"^[A-Z][\w\s-]*:\s", line):
                meta_lines.append(line)
            elif not line.strip():  # skip empty lines
                continue
            else:
                content_start = i
                break

        # Parse key-value metadata lines
        for line in meta_lines:
            key, value = line.split(":", 1)
            key = key.lower().strip().replace(" ", "_")
            if key in metadata:
                metadata[key] = value.strip()

            content = "\n".join(lines[content_start:]).strip()

            # Infer title from first Markdown heading if missing
            if not metadata["title"]:
                match = re.search(r"^#\s*(.+)", content)
                if match:
                    metadata["title"] = match.group(1).strip()

            metadata["markdown_content"] = content

        return metadata


    def fetch_web_page(self, params: FetchParams) -> Optional[str]:
        f"""
        Returns web page content for {params}
        """
        # raw_data = cls.get_all_webpage_data(params.url)
        # print(raw_data)
        metadata = self.parse_data(self.get_all_webpage_data(params.url))

        self.add_to_index(self.parse_data(self.get_all_webpage_data(params.url)))

        return metadata["markdown_content"]
    

    def add_to_index(self, metadata):
        content = metadata["markdown_content"]
        chunks = sliding_window(content, size=3000, step=1000)

        for chunk in chunks:
            doc = {
            "title": metadata["title"],
            "url_source": metadata["url_source"],
            "published_time": metadata["published_time"],
            "content": chunk["content"]
            }

            self.index.append(doc)


    def search(self, params: FetchQuery):
        """
        Search the index for documents matching the given query and return the contents.
        """
        result = self.index.search(params.query, num_results=5)
        output = [r["content"] for r in result]

        return "\n\n".join(output)
    


# Instanciating the agent_class
index = AppendableIndex(text_fields=["title", "url_source", "published_time", "content"])
agent_class = AgentTools(index)


# Summarizing agent
summarizing_instructions = """
    You are a helpful assistant that summarizes Wikipedia articles.
""".strip()

summarize_agent = Agent(
    name="summarize",
    instructions=summarizing_instructions,
    # tools= summarize_tool,
    model='gpt-4o-mini'
)


# Main orchestrator agent
orchestrator_instructions = """
Your task is to help the user by answering their questions
about wikipedia pages.

If a user query has NO web url, then use ONLY the search tool. 

In order to fetch the wikipedia page, use the fetch_web_page tool. 
The whole function needs to be run in order to get the webpage content.

Always generate summaries of the webpages using the summarization agent 

If a user query has NO web url, then use ONLY the search tool. 

No need to save summary when using the search tool.
Always save summary when using the fetch_web_page tool.

""".strip()


agent_tools = [agent_class.fetch_web_page, agent_class.search]

orchestrator = Agent(
    name='orchestrator',
    tools=agent_tools,
    instructions=orchestrator_instructions,
    model='gpt-4o-mini',
)

# Defining the orchestrator tool that correctly integrates the summarizing agent into the orchestrator agent
@orchestrator.tool
async def generate_and_save_summary(ctx: RunContext, query: str, summary: bool):
    """
    Runs the summarizing agent to summarize results from the webpages

    and saves the results.

    Args:
        query: raw user request.

    Returns:
        A short text summarizing the answer to user's query
    """

    callback = NamedCallback(summarize_agent)
    results = await summarize_agent.run(user_prompt=query, event_stream_handler=callback)
    
    if summary:
        with open("summary.txt", "a") as file:
            file.write("\n\n\n\n")
            file.write(results.output)

    return results.output


chat_interface = StdOutputInterface()

runner = PydanticAIRunner(
    chat_interface=chat_interface,
    agent=orchestrator
)


async def main():
    result = await runner.run();
    output = result.data 
    print(output)






if __name__ == "__main__":
    asyncio.run(main())