import asyncio
from wikiagent_.wikiagent import create_agents, NamedCallback



agent = create_agents()
agent_callback = NamedCallback(agent)



async def run_agent(user_prompt: str):

    results = await agent.run(
            user_prompt=user_prompt,
            event_stream_handler=agent_callback
    )

    return results



def run_agent_sync(user_prompt: str):
    return asyncio.run(run_agent(user_prompt))


def main():
    result = run_agent_sync("LLM as a Judge")
    print(result.output)


if __name__ == '__main__':
    main()
