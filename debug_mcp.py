import asyncio
import json
from groww_pulse.config import load_config
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def run():
    config = load_config()
    server_params = StdioServerParameters(command='python', args=['-m', 'mcp_servers.playstore_reviews'])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool('fetch_reviews', arguments={
                'app_id': config.product.play_store_app_id, 
                'count': 2, 
                'lang': 'en', 
                'sort': 'newest'
            })
            print('CONTENT_LEN:', len(res.content))
            print('CONTENT_TYPE:', type(res.content[0].text))
            print('CONTENT_VALUE:', repr(res.content[0].text)[:200])
            parsed = json.loads(res.content[0].text)
            print('PARSED_TYPE:', type(parsed))
            if isinstance(parsed, list) and len(parsed) > 0:
                print('ELEMENT_TYPE:', type(parsed[0]))
                print('ELEMENT:', repr(parsed[0])[:200])

if __name__ == "__main__":
    asyncio.run(run())
