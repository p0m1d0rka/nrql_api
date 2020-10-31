import asyncio
from nrql_api.request import NrqlApiRequest
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
load_dotenv()


async def main():
    async with ClientSession() as session:
        account = int(os.environ["NEWRELIC_ACCOUNT"])
        api_key = os.environ["NEWRELIC_APIKEY"]
        NrqlApiRequest.configure(account=account, api_key=api_key, session=session, is_debug=True)
        nrql_query = "SELECT count(*) FROM  PageView WITH TIMEZONE 'Europe/Moscow' FACET deviceType,appName  SINCE '2020-10-29 09:10:00' until '2020-10-29 09:12:00' limit max "
        nrql_query2 = "SELECT count(*) FROM  PageView WITH TIMEZONE 'Europe/Moscow' FACET deviceType, appName SINCE '2020-10-29 09:11:00' until '2020-10-29 09:13:00' limit max TIMESERIES 1 minute  "
        nrql_query3 = "SELECT duration, session FROM  PageView WITH TIMEZONE 'Europe/Moscow' SINCE '2020-10-29 09:10:00' until '2020-10-29 09:11:00' limit 5  "
        r = NrqlApiRequest(nrql_query=nrql_query)
        r2 = NrqlApiRequest(nrql_query=nrql_query2)
        r3 = NrqlApiRequest(nrql_query=nrql_query3)
        re = r.run_async()
        re2 = r2.run_async()
        re3 = r3.run_async()
        responses = await asyncio.gather(re, re2, re3)
        for resp in responses:
            print(resp.to_flat_format())
        # print(responses)
        print("done")

asyncio.run(main())
