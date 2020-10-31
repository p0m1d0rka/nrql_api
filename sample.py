import asyncio
from nrql_api.request import Request
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
load_dotenv()


async def main():
    async with ClientSession() as session:
        account = int(os.environ["NEWRELIC_ACCOUNT"])
        api_key = os.environ["NEWRELIC_APIKEY"]
        Request.configure(account=account, api_key=api_key, session=session, is_debug=True)
        nrql_query = "SELECT count(*) FROM  PageView WITH TIMEZONE 'Europe/Moscow' SINCE '2020-10-29 09:10:00' until '2020-10-29 09:11:00' limit max  "
        nrql_query2 = "SELECT count(*) FROM  PageView WITH TIMEZONE 'Europe/Moscow' SINCE '2020-10-29 09:11:00' until '2020-10-29 09:12:00' limit max  "
        r = Request(nrql_query=nrql_query)
        r2 = Request(nrql_query=nrql_query2)
        re = r.run_async()
        re2 = r2.run_async()
        responses = await asyncio.gather(re, re2)
        print(responses)
        print("done")

asyncio.run(main())
