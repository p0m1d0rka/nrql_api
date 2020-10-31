import uuid
import logging
from nrql_api.response import Response


class Request:
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.setLevel(logging.INFO)
    account = None
    api_key = None
    api_url = "https://api.newrelic.com/graphql"
    session = None

    @staticmethod
    def configure(account, api_key, session, is_debug=False, api_url="https://api.newrelic.com/graphql"):
        """
        Configure global Request class
        Args:
            account: your newrelic account
            api_key: new relic api key. Account settings -> Users and roles -> find youself
            api_url: url to new relic api. default https://api.newrelic.com/graphql
            session: aiohttp session object
            is_debug: if True then set log level to debug
        Returns: Bool

        """
        if is_debug:
            Request.logger.setLevel(logging.DEBUG)
        Request.account = account
        Request.api_key = api_key
        Request.api_url = api_url
        Request.session = session
        return True

    def __init__(self, nrql_query):
        """
        Request object implements async request to nrql api.
        Args:
            nrql_query: nrql query which we want to search
        Returns:
            Responce object

        """
        self.nrql_query = nrql_query
        self.uuid = uuid.uuid4()

    @property
    def to_graphql_format(self):
        """
        Create graphql format dict for sending to

        """
        query = '''
        query($account: Int!, $query_string: String!)
        {
            actor {
                account(id: $account) {
                    nrql(query: $query_string) {
                        nrql
                        totalResult
                        metadata {
                          timeWindow {
                            since
                            until
                          }
                          facets
                          messages
                        }
                        results
                    }
                }
            }
        }
        '''
        variables = {
            "account": Request.account,
            "query_string": self.nrql_query
        }
        return {"query": query, "variables": variables}

    async def run_async(self):
        headers = {
            "Content-Type": "application/json",
            "API-Key": Request.api_key
        }
        Request.logger.info(f"{self.uuid} - Making request. with query string {self.nrql_query}..")
        async with Request.session.post(Request.api_url, headers=headers, json=self.to_graphql_format) as response:
            Request.logger.info(f"{self.uuid} - Get response with status={response.status}")
            return await response.json()
            # self.logger.debug(f" Finished  with code={response.status}")
            # if response.status == 200:
            #     try:
            #         results_json = await response.json()
            #         results = results_json["data"]["actor"]["account"]["nrql"]["results"]
            #         self.logger.debug(results)
            #         return results
            #     except Exception as e:
            #         self.logger.exception(f"Error while reading content: {e}")
            #         return None, None
            # else:
            #     text = await response.text()
            #     self.logger.error(f"status={response.status} text={text}")
            #     return None, None
