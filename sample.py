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
        ENTITY_GUID = os.environ["ENTITY_GUID"]
        NrqlApiRequest.configure(account=account, api_key=api_key, session=session, is_debug=True)
        nrql_query = "SELECT count(*) FROM  PageView WITH TIMEZONE 'Europe/Moscow' FACET deviceType,appName  SINCE '2020-10-29 09:10:00' until '2020-10-29 09:12:00' limit max "
        nrql_query2 = "SELECT count(*) FROM  PageView WITH TIMEZONE 'Europe/Moscow' FACET deviceType, appName SINCE '2020-10-29 09:11:00' until '2020-10-29 09:13:00' limit max TIMESERIES 1 minute  "
        nrql_query3 = "SELECT * FROM Public_APICall  SINCE 1613553189 until 1613553289 limit 10 "
        nrql_query4 = f"SELECT average(newrelic.timeslice.value) FROM Metric facet host,metricTimesliceName WHERE `entity.guid` = '{ENTITY_GUID}' AND metricTimesliceName='GC/ParNew' OR metricTimesliceName='GC/ConcurrentMarkSweep' SINCE 1613553189 until 1613554189  TIMESERIES 1 minute"
        # r = NrqlApiRequest(nrql_query=nrql_query)
        # r2 = NrqlApiRequest(nrql_query=nrql_query2)
        r3 = NrqlApiRequest(nrql_query=nrql_query4)
        # re = r.run_async()
        # re2 = r2.run_async()
        re3 = r3.run_async()
        responses = await asyncio.gather(re3)
        for resp in responses:
            headers, data = resp.to_flat_format()
        print(responses)
        print(headers)
        print(data)

asyncio.run(main())
