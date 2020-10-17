import argparse
import pprint
import requests
import time

from prometheus_client import start_http_server, Summary, Gauge


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary("request_processing_seconds", "Time spent processing request")


class ServerTimingExporter:
    def __init__(self, url, debug=False):
        self.url = url
        self.debug = debug

        self.header = self.get_header()
        self.timing = self.parse_header()

    def get_header(self, timeout=2.0):
        """Get the Server-Timing header from the provided URL."""
        header = None
        try:
            req = requests.get(self.url, timeout=timeout)
            header = req.headers.get("Server-Timing", None)
        except requests.exceptions.RequestException as e:
            if self.debug:
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(e)

        return header

    def parse_header(self):
        """Extract each metric and fields from a Server-Timing header"""
        timings = {}
        if not self.header:
            return timings

        metrics = self.header.split(",")

        for metric in metrics:
            fields = metric.split(";")
            metric_name = fields.pop(0).strip()
            timings[metric_name] = {}

            for field in fields:
                name, value = field.split("=")
                timings[metric_name][name] = value

        return timings

    @property
    def timings(self):
        return self.timing


@REQUEST_TIME.time()
def process_request(url, gauges, debug=False):
    exporter = ServerTimingExporter(url, debug)
    timings = exporter.timings

    if debug:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(timings)

    for name in timings.keys():
        # default to 0.0 if no 'dur' value is provided
        # Server-Timing: missedCache is a valid header
        duration = timings[name].get("dur", 0.0)
        gauges["servertiming_duration"].labels(name).set(duration)


def initialise_gauages(url):
    # initialise the Gauges
    # TODO:
    # this has to be done once and assumes the header does not add new values.
    # it would be better to inspect the registered guages and add more as
    # needed

    gauges = {}
    gauges["servertiming_duration"] = Gauge(
        "servertiming_duration_milliseconds",
        "Server Timing duration in milliseconds",
        ["name"],
    )

    # assume everything works unless we explicitly say otherwise
    gauges["servertiming_up"] = Gauge("servertiming_up", "Scrap success indicator")
    gauges["servertiming_up"].set(1)

    return gauges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        dest="url",
        required=True,
        help="URL to fetch. This must provide a Server-Timing header",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Add debug information to stdout",
    )
    opts = parser.parse_args()

    gauges = initialise_gauages(opts.url)

    start_http_server(8000)

    while True:
        process_request(opts.url, gauges, opts.debug)
        # TODO: rework this to only call url when metics is hit.
        time.sleep(10)


if __name__ == "__main__":
    main()
