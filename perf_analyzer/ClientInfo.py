# ----------------------------------------------------------------------------------------------------------------------
# Copyright (C) 2015 David Fugate dave.fugate@gmail.com
#
# This work is licensed under the Creative Commons
# Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of
# this license, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ or send
# a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
# ----------------------------------------------------------------------------------------------------------------------

from subprocess import Popen
from os import getlogin
from os import path
from socket import gethostname, gethostbyname
from datetime import datetime

from perf_analyzer import *

# ----------------------------------------------------------------------------------------------------------------------

class ClientInfo(object):
    """
    Responsible for holding benchmarking data on a single client.
    """
    def __init__(self,
                 hostname,
                 server_port,
                 benchmark_time,
                 chunk_size,
                 file_size,
                 heartbeat_interval,
                 monitoring_interval):
        """
        Constructor
        :param hostname: PC to run the benchmark against. Should have SSH setup to login w/o a password.
        :param server_port: TCP port the server is hosting the REST services at.
        :param benchmark_time: Time (seconds) to run the benchmark for.
        :param chunk_size: File chunk size (MB).
        :param file_size: File size (MB).
        :param heartbeat_interval: Time (seconds) clients should sleep before sending heartbeat notifications.
        :param monitoring_interval: Time (seconds) clients should sleep before sending resource notifications.
        :return:
        """
        self.hostname = hostname
        self.server_port = server_port
        self.benchmark_time = benchmark_time
        self.chunk_size = chunk_size
        self.file_size = file_size
        self.heartbeat_interval = heartbeat_interval
        self.monitoring_interval = monitoring_interval

        self.started = None
        self.stopped = None
        self.heartbeats = []
        self.resources = []
        self.rollovers = []

        self.done = False

    def run(self):
        """
        Asynchronously runs the benchmark on the remote client.
        :return:
        """
        pkg_path = path.abspath(path.dirname(path.realpath(__file__)))
        simple_dt_str = datetime.utcnow().strftime(DATETIME_FORMAT)
        tmp_dir_name = "/tmp/hdperf_" + str(self.chunk_size) + "_" + simple_dt_str

        # Basic precursor to running the benchmark...give us a clean copy of the Client to work with
        cmd_line = "rm -rf %s; mkdir %s; cp -R %s %s/; cd %s; " % (tmp_dir_name,
                                                                   tmp_dir_name,
                                                                   pkg_path, tmp_dir_name,
                                                                   tmp_dir_name)

        # We need the PWD as part of the Python path. Don't care if we blow-away the existing path (not used)
        cmd_line += "PYTHONPATH=.;export PYTHONPATH; "

        # Now construct the args to the client
        cmd_line += "python perf_analyzer/Client.py %s %s %s %s %s %s %s" % (gethostbyname(gethostname()),
                                                                             self.server_port,
                                                                             self.benchmark_time,
                                                                             self.chunk_size,
                                                                             self.file_size,
                                                                             self.heartbeat_interval,
                                                                             self.monitoring_interval)

        # Run the thing in such a way that it returns control immediately.
        pipe = Popen(
            ["ssh",
             "-oStrictHostKeyChecking=no",
             "-q",
             "%s@%s" % (getlogin(), self.hostname),
             cmd_line
             ])
        return


# --MAIN----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    ci = ClientInfo("localhost",
                    10,
                    10,
                    20,
                    2,
                    5)
    ci.run()
