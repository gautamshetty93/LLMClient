import asyncio
import os

from llm_clients import  OpenAIClient


async def main() -> None:
    prompt = "Explain async I/O in one sentence."

    openai = OpenAIClient(api_key=os.environ["OPENAI_API_KEY"])
    # anthropic = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])

    try:
        openai_answer = await openai.ask(prompt, model="gpt-5")
        print("OpenAI:", openai_answer)

        # anthropic_answer = await anthropic.ask(
        #     prompt,
        #     model="YOUR_ANTHROPIC_MODEL",
        # )
        # print("Anthropic:", anthropic_answer)
    finally:
        await openai.close()
        # await anthropic.close()


if __name__ == "__main__":
    asyncio.run(main())

