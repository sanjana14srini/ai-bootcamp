from wikiagent_.main import run_agent_sync
from tests.utils import get_tool_calls
from wikiagent_.wikiagent import SearchResultArticle


def test_agent_tool_calls_present():
    result = run_agent_sync("LLM as a Judge")
    # print(result.output)

    tool_calls = get_tool_calls(result)

    search_tool_calls = 0
    get_page_tool_calls = 0
    for call in tool_calls:
        if call.name == 'search':
            search_tool_calls += 1
        if call.name == 'get_page':
            get_page_tool_calls += 2


    assert len(tool_calls) > 0, "No tool calls found"
    assert search_tool_calls > 0, "No calls made for search tool"
    assert get_page_tool_calls > 1, "get_page tool was not called multiple times"

    
def test_agent_adds_references():
    user_prompt = "What is LLM evaluation?"
    result = run_agent_sync(user_prompt)

    article: SearchResultArticle = result.output
    print(article.format_article())

    tool_calls = get_tool_calls(result)
    assert len(tool_calls) >= 3, f"Expected at least 3 tool calls, got {len(tool_calls)}"

    assert len(article.sections) > 0, "Expected at least one section in the article"
    assert len(article.references) > 0, "Expected at least one reference in the article"
