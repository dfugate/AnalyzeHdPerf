# ----------------------------------------------------------------------------------------------------------------------
# Copyright (C) 2015 David Fugate dave.fugate@gmail.com
#
# This work is licensed under the Creative Commons
# Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of
# this license, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ or send
# a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
# ----------------------------------------------------------------------------------------------------------------------

from subprocess import Popen
from os import getlogin, path, devnull
from socket import gethostname, gethostbyname
from datetime import datetime, timedelta

from perf_analyzer import *

from statistics import mean, median, stdev, variance

# --GLOBALS-------------------------------------------------------------------------------------------------------------
MAX_MISSED_HEARTBEATS = 3
DEVNULL = open(devnull, 'w')

# ----------------------------------------------------------------------------------------------------------------------

class ClientInfo(object):
    """
    Responsible for holding benchmarking data on a single client.
    """
    def __init__(self,
                 l,
                 hostname,
                 server_port,
                 benchmark_time,
                 chunk_size,
                 file_size,
                 heartbeat_interval,
                 monitoring_interval):
        """
        Constructor
        :param l: Logger instance
        :param hostname: PC to run the benchmark against. Should have SSH setup to login w/o a password.
        :param server_port: TCP port the server is hosting the REST services at.
        :param benchmark_time: Time (seconds) to run the benchmark for.
        :param chunk_size: File chunk size (MB).
        :param file_size: File size (MB).
        :param heartbeat_interval: Time (seconds) clients should sleep before sending heartbeat notifications.
        :param monitoring_interval: Time (seconds) clients should sleep before sending resource notifications.
        :return:
        """
        self.l = l

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

        self.kicked_off = None
        self.done = False

    def check_status(self):
        """
        Used to check the status of the client.
        :return: True if the client is done.
        """

        if self.done:
            # Previous invocation has determined this client is done...great!
            return True
        elif not(self.stopped is None):
            # Completed since the last check_status invocation...great!
            self.done = True
            return True
        elif self.kicked_off is None:
            # Hasn't even started yet...nothing else to do.
            return False

        # Find the last time we heard from the client...
        last_communication = self.get_last_contact()

        # Determine if the client is dead or not
        presumed_dead_date = last_communication + timedelta(0, self.heartbeat_interval * MAX_MISSED_HEARTBEATS)
        now = datetime.utcnow()
        if now > presumed_dead_date:
            self.l.error('Client on host "%s" (chunk size of "%s") is DEAD!' % (self.hostname,
                                                                                str(self.chunk_size)))
            self.done = True
            return True

        return False

    def run(self):
        """
        Asynchronously runs the benchmark on the remote client.
        :return:
        """
        self.kicked_off = datetime.utcnow()

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

        # Give web server a chance to fire-up (just in case).
        cmd_line += "sleep 5; "

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
             ],
            stdout=DEVNULL,
            stderr=DEVNULL,
        )
        return

    def get_last_contact(self):
        """
        Returns the last time we had any contact with the client.
        :return: See description.
        """
        last_communication = self.kicked_off
        if len(self.heartbeats) > 0:
            last_communication = self.heartbeats[len(self.heartbeats) - 1]

        return last_communication

    def __timestamp_helper(self, dt):
        """
        Helper method converts a datetime to a floating-point timestamp.
        :param dt:
        :return:
        """
        if dt is None:
            return "null"
        else:
            return (dt - datetime(1970, 1, 1)).total_seconds()

    def get_statistics(self):
        """
        Returns various statistics about the benchmark run.
        :return: See description.
        """
        ret_val = {}
        not_applicable = 'N/A'

        if len(self.rollovers) > 1: # Skip the last rollover...it could've been smaller than chunk_size
            rollover_times = []
            last_time = self.started
            for i in xrange(len(self.rollovers)-1):
                rollover_times.append(
                    (self.rollovers[i] - last_time).total_seconds()
                )
                last_time = self.rollovers[i]

            ret_val['rollover_mean'] = self.num_to_seconds(mean(rollover_times))
            ret_val['rollover_median'] = self.num_to_seconds(median(rollover_times))
            ret_val['rollover_stdev'] = self.num_to_seconds(stdev(rollover_times))
            ret_val['rollover_variance'] = self.num_to_seconds(variance(rollover_times))
        else:
            ret_val['rollover_mean'] = not_applicable
            ret_val['rollover_median'] = not_applicable
            ret_val['rollover_stdev'] = not_applicable
            ret_val['rollover_variance'] = not_applicable

        if len(self.resources) > 0:
            cpu_util_list = [x[1] for x in self.resources]
            ret_val['cpu_util_mean'] = self.num_to_percent(mean(cpu_util_list))
            ret_val['cpu_util_median'] = self.num_to_percent(median(cpu_util_list))
            ret_val['cpu_util_stdev'] = self.num_to_percent(stdev(cpu_util_list))
            if len(cpu_util_list) > 1:
                ret_val['cpu_util_variance'] = self.num_to_percent(variance(cpu_util_list))
            else:
                ret_val['cpu_util_variance'] = not_applicable

            mem_usage_list = [x[2] for x in self.resources]
            ret_val['mem_usage_mean'] = self.num_to_megabytes(mean(mem_usage_list))
            ret_val['mem_usage_median'] = self.num_to_megabytes(median(mem_usage_list))
            ret_val['mem_usage_stdev'] = self.num_to_megabytes(stdev(mem_usage_list))
            if len(mem_usage_list) > 1:
                ret_val['mem_usage_variance'] = self.num_to_megabytes(variance(mem_usage_list))
            else:
                ret_val['mem_usage_variance'] = not_applicable
        else:
            ret_val['cpu_util_mean'] = not_applicable
            ret_val['cpu_util_median'] = not_applicable
            ret_val['cpu_util_stdev'] = not_applicable
            ret_val['cpu_util_variance'] = not_applicable
            
            ret_val['mem_usage_mean'] = not_applicable
            ret_val['mem_usage_median'] = not_applicable
            ret_val['mem_usage_stdev'] = not_applicable
            ret_val['mem_usage_variance'] = not_applicable

        return ret_val

    def num_to_percent(self, num):
        """
        Converts a number (integer, float, long) to a user-friendly percentage representation.
        :param num: Number to convert.
        :return: See description.
        """
        return '{:5.2f}%'.format(num)

    def num_to_seconds(self, num):
        """
        Converts a number (integer, float, long) to a user-friendly time representation (seconds).
        :param num: Number to convert.
        :return: See description.
        """
        return '{:.2f} s'.format(num)

    def num_to_megabytes(self, num):
        """
        Converts a number (integer, float, long) to a user-friendly MB representation (seconds).
        :param num: Number to convert.
        :return: See description.
        """
        return '{:.2f} MB'.format(num)

    def to_json(self):
        """
        Converts this object to a JSON representation suitable for JS consumption.
        :return:
        """
        ret_val = "{"
        ret_val += "'hostname':'" + self.hostname + "',"
        ret_val += "'chunk_size':'" + str(self.chunk_size) + "',"
        ret_val += "'started':" + str(self.__timestamp_helper(self.started)) + ","
        ret_val += "'stopped':" + str(self.__timestamp_helper(self.stopped)) + ",\n"

        ret_val += "'resources':["
        for i in xrange(len(self.resources)):
            resource = self.resources[i]
            ret_val += "[" + str(self.__timestamp_helper(resource[0])) + "," + str(resource[1]) + "," + str(resource[2]) + "]"
            if i != (len(self.resources)-1):
                ret_val += ","

        ret_val += "],\n'rollovers':["
        for i in xrange(len(self.rollovers)):
            ro = self.rollovers[i]
            ret_val += str(self.__timestamp_helper(ro))
            if i != (len(self.rollovers)-1):
                ret_val += ","

        ret_val += "]}\n"
        return ret_val


# --MAIN----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    import logging
    ci = ClientInfo(logging.getLogger("testClientInfo"),
                    "localhost",
                    10,
                    10,
                    20,
                    2,
                    5)
    ci.run()
