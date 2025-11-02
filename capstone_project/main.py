import asyncio
from agents import create_agents, NamedCallback
from toyaikit.chat.interface import StdOutputInterface
from toyaikit.chat.runners import PydanticAIRunner
import asyncio


agent = create_agents()
agent_callback = NamedCallback(agent)



async def main():
    chat_interface = StdOutputInterface()

    runner = PydanticAIRunner(
        chat_interface=chat_interface,
        agent=agent
    )
    result = await runner.run();
    output = result.data 
    print(output)


if __name__ == "__main__":
    asyncio.run(main())