from aiohttp import ClientSession
import asyncio

async def main():
	url = 'http://httpbin.org/cookies'
	cookies = {'cookies_are': 'working'}
	async with ClientSession(cookies=cookies) as session:
	    async with session.get(url) as resp:
	           print(await resp.text())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
