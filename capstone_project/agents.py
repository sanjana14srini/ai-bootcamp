from tools import Agent_Tools
from elasticsearch import Elasticsearch

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import FunctionToolCallEvent
from pydantic import BaseModel
from toyaikit.chat.interface import StdOutputInterface
from toyaikit.chat.runners import PydanticAIRunner
import asyncio



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





def create_agents():
    es = Elasticsearch("http://localhost:9200")
    agent_class = Agent_Tools(es_index=es)


    # Summarizing agent
    summarizing_instructions = """
        You are a helpful assistant that answers user questions only based on arxiv research articles.

        When a user asks a query, you fetch the relevant articles from arxiv using the get_data_to_index tool
        Then you perfrom a search using the search tool.

        You answer the user's question by summarizing these search results.
    """.strip()

    summarizing_tools = [agent_class.get_data_to_index, agent_class.search]

    summarize_agent = Agent(
        name="summarize",
        tools=summarizing_tools,
        instructions=summarizing_instructions,
        model='gpt-4o-mini'
    )

    return summarize_agent

