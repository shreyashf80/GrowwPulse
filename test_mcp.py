import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def list_tools():
    url = "https://shreyash-mcp-server-production-5d26.up.railway.app/sse"
    print(f"Connecting to {url}...")
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Initialized!")
                tools = await session.list_tools()
                for t in tools.tools:
                    print(f"- {t.name}: {t.description}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(list_tools())
