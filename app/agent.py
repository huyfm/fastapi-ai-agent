import asyncio

from agents import Agent, Runner, function_tool, SQLiteSession, ModelSettings
from openai.types.responses import ResponseTextDeltaEvent, ResponseReasoningSummaryTextDeltaEvent, ResponseReasoningSummaryTextDoneEvent
from openai.types import Reasoning
from agents import ReasoningItem, MessageOutputItem
from dotenv import load_dotenv
from colorama import Fore, Back, Style

from prompts import email_writer_prompt
from settings import settings

load_dotenv()


@function_tool
def send_email(addr: str, content: str) -> str:
    """Send an email.

    Args:
        addr: valid recipient email address.
        content: sending email content.
    """
    if content:
        return "Sent OK"
    return "Sent FAILED"


async def main():
    agent = Agent(
        name="email writer",
        model="gpt-5.1",
        instructions=email_writer_prompt,
        tools=[send_email],
        model_settings=ModelSettings(
            reasoning=Reasoning(effort="low", summary="detailed"),
        ),
    )

    print("conversations db:", settings.convs_db_uri)
    session = SQLiteSession(session_id="foo-1", db_path=settings.convs_db_uri)

    while True:
        user_input = input("user|>\n")
        result = Runner.run_streamed(agent, input=user_input, session=session)
        print("assistant|>", end="")

        # stream events
        async for event in result.stream_events():
            if event.type == "raw_response_event":
                # print reason
                if isinstance(event.data, ResponseReasoningSummaryTextDeltaEvent):
                    print(Fore.LIGHTBLACK_EX + event.data.delta, end="", flush=True)
                elif isinstance(event.data, ResponseReasoningSummaryTextDoneEvent):
                    print(Style.RESET_ALL)
                # print final answer
                elif isinstance(event.data, ResponseTextDeltaEvent):
                    print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
