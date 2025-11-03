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
from wikiagent_.tools import AgentTools


class Reference(BaseModel):
    title: str
    url: str

class Section(BaseModel):
    heading: str
    content: str
    references: list[Reference]

class SearchResultArticle(BaseModel):
    title: str
    sections: list[Section]
    references: list[Reference]

    def format_article(self):
        output = f"# {self.title}\n\n"

        for section in self.sections:
            output += f"## {section.heading}\n\n"
            output += f"{section.content}\n\n"
            output += "### References\n"
            for ref in section.references:
                output += f"- [{ref.title}]({ref.url})\n"

        output += "## References\n"
        for ref in self.references:
            output += f"- [{ref.title}]({ref.url})\n"

        return output


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
    # Instanciating the agent_class
    index = AppendableIndex(text_fields=["title", "snippet"])
    agent_class = AgentTools(index=index)


    # Main orchestrator agent
    orchestrator_instructions = """
    Your task is to help the user by answering their questions
    about wikipedia pages.

    When asked a question, you always search using the search tool. 
    Utilize these search results to find relevant wikipedia page content from the get_page tool.

    Use all these results to respond to the user's question.
    Always provide references.

    """.strip()


    agent_tools = [agent_class.get_page, agent_class.search]

    orchestrator = Agent(
        name='orchestrator',
        tools=agent_tools,
        instructions=orchestrator_instructions,
        model='gpt-4o-mini',
        output_type=SearchResultArticle
    )

    
    return orchestrator