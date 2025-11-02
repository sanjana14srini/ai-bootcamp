from wikiagent_.main import run_agent_sync
from tests.utils import get_tool_calls



def test_agent_tool_calls_present():
    result = run_agent_sync("LLM as a Judge")
    print(result.output)

    tool_calls = get_tool_calls(result)
    print(tool_calls)
    assert len(tool_calls) > 0, "No tool calls found"
    
