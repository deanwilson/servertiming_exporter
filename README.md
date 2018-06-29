# Server-Timing header exporter for Prometheus

The [server timing](https://w3c.github.io/server-timing/) specification
enables a server to communicate performance metrics about the request-
response cycle back to the user agent via a number of methods, including
a HTTP header. This prometheus exporter accepts a URL that exposes that header
and then presents in the metrics in a prometheus friendly format.

Here's a more detailed post, with screen shots, where you can learn more about the
[Server-Timing header](https://www.unixdaemon.net/tools/show-server-side-response-timings-in-chrome-developer-tools/)

## Warning

This is alpha level code. It's being written as a learning example of how you could
write a new prometheus exporter. This is my first attempt so here be dragons.

## Running the exporter

The exporter is written in Python 3 and requires the
`prometheus_client` package.

    git clone https://github.com/deanwilson/servertiming_exporter.git

    cd servertiming_exporter

    # install all the python requirements in a venv
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt

    python3 servertiming.py --url http://127.0.0.1:5000 --debug

Once this is running you can view the metrics:

    curl http://127.0.0.1:8000/

    ... snip ...
    # HELP servertiming_duration_milliseconds Server Timing duration in milliseconds
    # TYPE servertiming_duration_milliseconds gauge
    servertiming_duration_milliseconds{name="mysql"} 3.1
    servertiming_duration_milliseconds{name="redis"} 0.2
    servertiming_duration_milliseconds{name="elasticsearch"} 1.2
    # HELP servertiming_up Scrap success indicator
    # TYPE servertiming_up gauge
    servertiming_up 1.0
    ... snip ...

### Author ###

[Dean Wilson](http://www.unixdaemon.net)
