import asyncio
from wikiagent_.wikiagent import create_agents, NamedCallback
from wikiagent_.agent_logging import log_run, save_log



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
    result = run_agent_sync("where do capybaras live?")
    log_entry = log_run(agent, result)
    log_file = save_log(log_entry)
    print(f"\n\nLog saved to: {log_file}")
    print(result.output)


if __name__ == '__main__':
    main()
