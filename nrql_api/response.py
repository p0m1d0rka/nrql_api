import logging
import datetime as dt


class NrqlApiResponse:
    """
    Response object from nrql_api

    """
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.setLevel(logging.INFO)

    def __init__(self, status, json_body, headers, method, content_type, exec_time, is_ok, is_debug=False):
        self.status = status
        self.json_body = json_body
        self.headers = headers
        self.method = method
        self.content_type = content_type
        self.exec_time = exec_time
        self.is_ok = is_ok
        if is_debug:
            NrqlApiResponse.logger.setLevel(logging.DEBUG)

    def __repr__(self):
        return str(self.json_body)

    @property
    def is_error(self):
        return not self.is_ok or "errors" in self.json_body

    @property
    def error_message(self) -> str:
        """
        Return first message from errors array inside json_body

        """
        if self.is_error:
            try:
                message = self.json_body["errors"][0]["message"]
                return message
            except KeyError as e:
                NrqlApiResponse.logger.exception(e)
                return f"Exception {e}"
        else:
            return ""

    @property
    def errors(self) -> list:
        """
        Return all errors array

        """
        if self.is_error:
            try:
                l = self.json_body["errors"]
                return l
            except KeyError as e:
                NrqlApiResponse.logger.exception(e)
                return [f"Exception {e}"]
        else:
            return []

    @property
    def results(self) -> dict:
        return self.json_body["data"]["actor"]["account"]["nrql"]["results"]

    @property
    def metadata(self) -> dict:
        """
        Returns dict of metadata

        """
        if self.is_error:
            return {"metadata": "this is error result"}
        else:
            return self.json_body["data"]["actor"]["account"]["nrql"]["metadata"]

    @property
    def is_facet_query(self) -> bool:
        return not (self.metadata["facets"] is None)

    def to_flat_format(self) -> tuple:
        """
        Returns (headers,  list of tuples of data)

        """
        if self.is_facet_query:
            if "beginTimeSeconds" in self.results[0]:
                """
                This is facet query with timeseries, time in second in the each row ["beginTimeSeconds"]
                also we have to get headers from metadata[facets]
                and unpack facet values in each row
                
                """
                headers = [key for key in self.results[0] if type(self.results[0][key]) != list]
                headers = tuple(headers + self.metadata["facets"] + ["timestamp"])
                result_list = []
                for row in self.results:
                    # clickhouse needs this format 2012-03-16 03:53:12
                    facet = row["facet"]
                    timestamp = dt.datetime.fromtimestamp(row["beginTimeSeconds"]).strftime("%Y-%m-%d %H:%M:%S")
                    vals = [vv for vv in row.values() if type(vv) != list]
                    vals = vals + facet + [timestamp]
                    result_list.append(tuple(vals))
                return headers, result_list
            else:
                """
                This is facet query without timeseries, time in second in the metadata in format 
                'timeWindow': {'since': "'2020-10-29 09:10:00'", 'until': "'2020-10-29 09:12:00'"}
                also we have to get headers from metadata[facets]
                and unpack facet values in each row
                """
                headers = [key for key in self.results[0] if type(self.results[0][key]) != list]
                headers = tuple(headers + self.metadata["facets"] + ["timestamp"])
                result_list = []
                for row in self.results:
                    # clickhouse needs this format 2012-03-16 03:53:12
                    facet = row["facet"]
                    timestamp = self.metadata["timeWindow"]["since"].replace("'", "")
                    vals = [vv for vv in row.values() if type(vv) != list]
                    vals = vals + facet + [timestamp,]
                    result_list.append(tuple(vals))
                return headers, result_list
        else:
            """
            Query without facet
            time can be in timestamp, bigintimeseconds or in metadata
            """
            if "beginTimeSeconds" in self.results[0]:
                headers = tuple(self.results[0]) + ("timestamp",)
                result_list = []
                for row in self.results:
                    # clickhouse needs this format 2012-03-16 03:53:12
                    row["timestamp"] = dt.datetime.fromtimestamp(row["beginTimeSeconds"]).strftime("%Y-%m-%d %H:%M:%S")
                    result_list.append(tuple(row.values()))
                return headers, result_list
            elif "timestamp" in self.results[0]:
                headers = tuple(self.results[0])
                result_list = []
                for row in self.results:
                    # clickhouse needs this format 2012-03-16 03:53:12
                    row["timestamp"] = dt.datetime.fromtimestamp(row["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    res = [row[h] for h in headers]

                    result_list.append(tuple(res))

                return headers, result_list
            else:
                """
                Get time from metadata
                """
                headers = tuple(self.results[0]) + ("timestamp",)
                result_list = []
                for row in self.results:
                    # clickhouse needs this format 2012-03-16 03:53:12
                    row["timestamp"] = self.metadata["timeWindow"]["since"].replace("'", "")
                    result_list.append(tuple(row.values()))
                return headers, result_list
