# ----------------------------------------------------------------------------------------------------------------------
# Copyright (C) 2015 David Fugate dave.fugate@gmail.com
#
# This work is licensed under the Creative Commons
# Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of
# this license, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ or send
# a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
# ----------------------------------------------------------------------------------------------------------------------

import sys
import logging

from socket import gethostname
from argparse import ArgumentParser
from datetime import datetime
from time import sleep
from threading import Thread
from os import getcwd, sep

from perf_analyzer import *
from perf_analyzer.ClientInfo import ClientInfo

try:
    import bottle
except ImportError, e:
    print "The 'bottle' package is unavailable on this system!"
    print "Please run 'pip install bottle' and try starting the server again."
    sys.exit(1)


# ----------------------------------------------------------------------------------------------------------------------

class Server(object):
    """
    Benchmark Controller class.

    Controls execution of benchmarks on client machines and also handles incoming
    HTTP requests.
    """
    def __init__(self,
                 client_hostnames,
                 benchmark_time,
                 chunk_size,
                 file_size,
                 heartbeat_interval,
                 monitoring_interval,
                 port,
                 log_file
                 ):
        """
        Constructor
        :param client_hostnames: List of clients to run the benchmarks on.
        :param benchmark_time: Time (seconds) to run the benchmark for before stopping.
        :param chunk_size: Amount of data (bytes) to write on each client before flushing to disk.
        :param file_size: Total size (bytes) of each file created by a client.
        :param heartbeat_interval: Time (seconds) a client is to wait before periodically contacting the server.
        :param monitoring_interval: Time (seconds) a client waits before periodically sending the server perf. data.
        :param port: TCP port number to run the HTTP server on.
        :param log_file: file to dump logs into.
        :return: Instance of this class.
        """
        self.client_hostnames = client_hostnames
        self.benchmark_time = benchmark_time
        self.chunk_size = chunk_size
        self.file_size = file_size
        self.heartbeat_interval = heartbeat_interval
        self.monitoring_interval = monitoring_interval
        self.port = port

        self.hostname = gethostname()
        # Holds client performance data in memory.
        self.client_info_dict = {}

        self.started = None
        self.stopped = None

        self.l = logging.getLogger('server')
        self.l.setLevel(logging.DEBUG)
        lf = logging.Formatter(LOG_FORMAT)

        # Stdout logger
        self.lh = logging.StreamHandler(sys.stdout)
        self.lh.setFormatter(lf)
        self.l.addHandler(self.lh)

        # File logger
        self.fh = logging.FileHandler(log_file, mode='w')
        self.fh.setLevel(logging.INFO)
        self.fh.setFormatter(lf)
        self.l.addHandler(self.fh)

        # We need an in-memory logging handler to render the logs on an HTML page (easily at least).
        self.pbh = PersistentBufferingHandler(1000)
        self.pbh.setLevel(logging.DEBUG)
        self.l.addHandler(self.pbh)

        self.l.info("Clients will run for '%s' seconds and then terminate." % self.benchmark_time)
        self.l.info("Clients will create files containing '%s' MB of data before 'rolling over'." % self.file_size)
        self.l.info("Clients will report back performance data to this server every '%s' seconds." % self.monitoring_interval)
        self.l.info("Clients are to contact this server every '%s' seconds to signal they're still working." % self.heartbeat_interval)

    def run_benchmarks(self):
        """
        Asynchronously run the benchmarks in parallel on all clients.
        :return: None.
        """
        i = 0
        for client_host in self.client_hostnames:
            # Each client gets a different chunk_size-size.
            client_chunk_size = self.chunk_size * (2 ** i)
            client_id = self.__get_client_id(client_host, client_chunk_size)
            self.client_info_dict[client_id] = ClientInfo(self.l,
                                                          client_host,
                                                          self.port,
                                                          self.benchmark_time,
                                                          client_chunk_size,
                                                          self.file_size,
                                                          self.heartbeat_interval,
                                                          self.monitoring_interval)
            i += 1

        self.l.debug("Spawning benchmark processes now...")
        self.started = datetime.utcnow()
        for ci in self.client_info_dict.values():
            ci.run()

        self.client_thread = Thread(target=self.__monitor_clients, args=())
        self.client_thread.start()

    # --HTML VIEWS------------------------------------------------------------------------------------------------------
    def main(self):
        """
        Main HTML page for the benchmark suite.
        :return:
        """
        return bottle.template('main')

    def status(self):
        """
        Real-time status of benchmark testing.
        :return:
        """
        finished = [x for x in self.client_info_dict.values() if x.done and not (x.stopped is None)]
        failed = [x for x in self.client_info_dict.values() if x.done and (x.stopped is None)]
        running = [x for x in self.client_info_dict.values() if not x.done]

        return bottle.template('status', server=self, finished=finished, failed=failed, running=running)

    def report(self):
        """
        Real-time reporting of benchmark testing.
        :return:
        """
        return bottle.template('report', server=self)

    def about(self):
        """
        About this benchmark suite.
        :return:
        """
        return bottle.template('about', server=self)

    def logs(self):
        """
        All logs generated by this suite.
        :return:
        """
        return bottle.template('logs', log_buffer=self.pbh.buffer)

    def hello(self):
        """
        Tells the client if the server is alive.
        :return: "Hello!"
        """
        return {'hello': 'world'}

    def client_heartbeat(self):
        """
        Client heartbeat_interval.
        :return: Nothing.
        """
        client_host = bottle.request.json[HOSTNAME]
        chunk = bottle.request.json[CHUNK]
        client_id = self.__get_client_id(client_host, chunk)

        if not (client_id in self.client_info_dict):
            self.l.error("Unexpected client heartbeat - %s" % client_id)
        else:
            ts_str = bottle.request.json[TIMESTAMP]
            ts = datetime.strptime(ts_str, DATETIME_FORMAT)
            client_info = self.client_info_dict[client_id]
            client_info.heartbeats.append(ts)
            self.l.info("Client heartbeat - %s at %s" % (client_id, ts.isoformat()))

        return {}

    def client_start(self):
        """
        Client has started running a benchmark.
        :return: Nothing.
        """
        client_host = bottle.request.json[HOSTNAME]
        chunk = bottle.request.json[CHUNK]
        client_id = self.__get_client_id(client_host, chunk)

        if not (client_id in self.client_info_dict):
            self.l.error("Unexpected client start - %s" % client_id)
        else:
            ts_str = bottle.request.json[TIMESTAMP]
            ts = datetime.strptime(ts_str, DATETIME_FORMAT)
            client_info = self.client_info_dict[client_id]
            client_info.started = ts

            mem_usage = bottle.request.json[MEM_USAGE]
            client_info.initial_mem_usage = mem_usage

            self.l.info("Client start - %s at %s" % (client_id, ts.isoformat()))

        return {}

    def client_stop(self):
        """
        Client has stopped running a benchmark.
        :return: Nothing.
        """
        client_host = bottle.request.json[HOSTNAME]
        chunk = bottle.request.json[CHUNK]
        client_id = self.__get_client_id(client_host, chunk)

        if not (client_id in self.client_info_dict):
            self.l.error("Unexpected client stop - %s" % client_id)
        else:
            ts_str = bottle.request.json[TIMESTAMP]
            ts = datetime.strptime(ts_str, DATETIME_FORMAT)
            client_info = self.client_info_dict[client_id]
            client_info.stopped = ts
            client_info.done = True
            self.l.info("Client stop - %s at %s" % (client_id, ts.isoformat()))

        return {}

    def client_resources(self):
        """
        Client has told us it's current resource usage.
        :return: Nothing.
        """
        client_host = bottle.request.json[HOSTNAME]
        chunk = bottle.request.json[CHUNK]
        client_id = self.__get_client_id(client_host, chunk)

        if not (client_id in self.client_info_dict):
            self.l.error("Unexpected client resource reporting - %s" % client_id)
        else:
            ts_str = bottle.request.json[TIMESTAMP]
            ts = datetime.strptime(ts_str, DATETIME_FORMAT)
            cpu_util = bottle.request.json[CPU_UTIL]
            mem_usage = bottle.request.json[MEM_USAGE]

            client_info = self.client_info_dict[client_id]
            client_info.resources.append(
                [ts, cpu_util, mem_usage]
            )
            self.l.info("Client resources - %s at %s - CPU=%s and MEMORY=%s" % (client_id,
                                                                                ts.isoformat(),
                                                                                cpu_util,
                                                                                mem_usage))

        return {}

    def client_rollover(self):
        """
        Client has told us it's done writing a file.
        :return: Nothing.
        """
        client_host = bottle.request.json[HOSTNAME]
        chunk = bottle.request.json[CHUNK]
        client_id = self.__get_client_id(client_host, chunk)

        if not (client_id in self.client_info_dict):
            self.l.error("Unexpected client rollover reporting - %s" % client_id)
        else:
            ts_str = bottle.request.json[TIMESTAMP]
            ts = datetime.strptime(ts_str, DATETIME_FORMAT)

            client_info = self.client_info_dict[client_id]
            client_info.rollovers.append(ts)
            self.l.info("Client rollover reporting - %s at %s" % (client_id, ts.isoformat()))

        return {}

    def static(self, file_path):
        """
        Used to serve up CSS/JS/etc. files.
        :param file_path: Server path to static files.
        :return: Static file.
        """
        return bottle.static_file(file_path, root='static')

    def get_favicon(self):
        """
        :return: Favicon file.
        """
        return bottle.static_file('favicon.ico', root='static')

    # --"PRIVATE"-------------------------------------------------------------------------------------------------------
    def __monitor_clients(self):
        """
        Monitors the health of clients.
        :return: None.
        """
        self.l.info("Monitoring the health of clients now.")

        while self.stopped is None:
            sleep(5)

            clients = [x for x in self.client_info_dict.values() if not x.done]
            still_running = False

            for ci in clients:
                if not ci.check_status():
                    still_running = True

            if not still_running:
                self.stopped = datetime.utcnow()

        self.l.info("All clients finished running the benchmark.")
        return

    def __get_client_id(self, client_host, chunk):
        """
        Converts an IP address/process ID combination into a single identifier.
        :param client_host: IP address of the client machine
        :param chunk: Chunk-size of the client (unique)
        :return: See Description.
        """
        return client_host + ":" + str(chunk)


# --MAIN----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    now = datetime.utcnow()
    now_str = now.strftime(DATETIME_FORMAT)
    cwd = getcwd()

    parser = ArgumentParser()
    parser.add_argument("--client",
                        help="Hostname of client to run the benchmark on. Same client can be specified multiple times.",
                        action="append")
    parser.add_argument("--benchmark_time",
                        help="Time (seconds) the benchmark is run for on each client.",
                        type=int,
                        default=20)
    parser.add_argument("--chunk_size",
                        help="Size (MB) clients write to a file before flushing. Minimum of 10MB.",
                        type=int,
                        default=10)
    parser.add_argument("--file_size",
                        help="Size (MB) of files clients generate. Minimum of 10MB.",
                        type=int,
                        default=50)
    parser.add_argument("--heartbeat_interval",
                        help="Time (seconds) for clients to sleep between heartbeat notifications.",
                        type=int,
                        default=5)
    parser.add_argument("--monitoring_interval",
                        help="Time (seconds) for clients to sleep between resource monitoring notifications.",
                        type=int,
                        default=10)
    parser.add_argument("--port",
                        help="TCP port to run the server on.",
                        type=int,
                        default=8080)
    parser.add_argument("--log",
                        help="Text log file for this run.",
                        type=str,
                        default=cwd + sep + "hd_perf_analyzer_" + now_str + ".log")

    args = parser.parse_args()

    if args.client is None:
        # No clients were specified...just run it three times locally with different chunk sizes.
        print "No clients were specified from the command prompt. Will run three locally."
        print ""
        args.client_hostnames = [gethostname()] * 3
    else:
        args.client_hostnames = args.client

    sanity_check_config(args)
    largest_chunk = args.chunk_size * (2 ** (len(args.client_hostnames) - 1))
    if largest_chunk > args.file_size:
        print "File size (%s) must be larger than %s. Bailing!" % (args.file_size, largest_chunk)
        sys.exit(1)

    print "Server logs will be saved to '%s'." % args.log
    print "A much nicer view of these logs can be accessed at 'http://localhost:%s/logs' though." % args.port
    print ""
    print "The real-time status of this benchmark can be viewed at 'http://localhost:%s/status' and" % args.port
    print "The final report, once complete, can be found at 'http://localhost:%s/report'." % args.port
    print "------------------------------------------------------------------------------------------------------------"
    s = Server(
        args.client_hostnames,
        args.benchmark_time,
        args.chunk_size,
        args.file_size,
        args.heartbeat_interval,
        args.monitoring_interval,
        args.port,
        args.log
    )

    # Initialize routes
    bottle.get("/")(s.main)
    bottle.get("/status")(s.status)
    bottle.get("/report")(s.report)
    bottle.get("/logs")(s.logs)
    bottle.get("/about")(s.about)
    bottle.route('/static/:file_path#.+#')(s.static)
    bottle.get("/favicon.ico")(s.get_favicon)

    bottle.post("/hello")(s.hello)
    bottle.post(HEARTBEAT_PATH)(s.client_heartbeat)
    bottle.post(START_PATH)(s.client_start)
    bottle.post(STOP_PATH)(s.client_stop)
    bottle.post(RESOURCES_PATH)(s.client_resources)
    bottle.post(ROLLOVER_PATH)(s.client_rollover)

    s.run_benchmarks()
    bottle.run(host='localhost', port=args.port, debug=True, quiet=True)
    s.client_thread.join()
