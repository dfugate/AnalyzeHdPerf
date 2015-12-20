# ----------------------------------------------------------------------------------------------------------------------
# Copyright (C) 2015 David Fugate dave.fugate@gmail.com
#
# This work is licensed under the Creative Commons
# Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of
# this license, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ or send
# a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
# ----------------------------------------------------------------------------------------------------------------------

import logging
import logging.handlers
import sys

# --SANITY CHECKS-------------------------------------------------------------------------------------------------------

if sys.version_info.major != 2 and sys.version_info.minor != 7:
    print "This version of Python (" + sys.version + ") is not supported! Please install 2.7."
    sys.exit(1)

# --GLOBALS-------------------------------------------------------------------------------------------------------------

# URL partial paths
HEARTBEAT_PATH = "/client_hostnames/heartbeat_duration"
START_PATH = "/client_hostnames/start"
STOP_PATH = "/client_hostnames/stop"
RESOURCES_PATH = "/client_hostnames/resources"
ROLLOVER_PATH = "/client_hostnames/rollover"

# JSON identifiers
HOSTNAME = 'hostname'
TIMESTAMP = 'timestamp'
CHUNK = 'chunk_size'
FILE_SIZE = 'file_size'
CPU_UTIL = 'cpu_util'
MEM_USAGE = 'mem_usage'

# Other
LOG_FORMAT = '%(asctime)-15s - %(levelname)-8s - %(message)s'
DATETIME_FORMAT = '%Y_%m_%d_%H_%M_%S_%f'


# --HELPER FUNCTIONS ---------------------------------------------------------------------------------------------------

def sanity_check_config(args):
    """
    Runs some sanity checks on command-line arguments.
    :param args: Command-line arguments.
    :return: Nothing. Kills Python if there's a critical error.
    """
    if args.benchmark_time < 1:
        print "'%s' seconds is insufficient time to run this benchmark. Bailing!" % args.benchmark_time
        sys.exit(1)

    elif args.chunk_size < 10:
        print "'%s' MB is too small of a chunk_size size for this benchmark. Bailing!" % args.chunk_size
        sys.exit(1)

    elif args.file_size < 10:
        print "'%s' MB is too small of a file size for this benchmark. Bailing!" % args.file_size
        sys.exit(1)

    elif args.heartbeat_interval < 1:
        print "'%s' seconds is too small of a heartbeat interval. Bailing!" % args.heartbeat_interval
        sys.exit(1)

    elif args.monitoring_interval < 1:
        print "'%s' seconds is too small of a resource monitoring interval interval. Bailing!" % args.monitoring_interval
        sys.exit(1)

    elif args.heartbeat_interval > args.benchmark_time:
        print "Heartbeat interval (%s) must be larger than the benchmark time (%s). Bailing!" % (args.heartbeat_interval, args.benchmark_time)
        sys.exit(1)

    elif args.monitoring_interval > args.benchmark_time:
        print "Resource monitoring interval (%s) must be larger than the benchmark time (%s). Bailing!" % (args.monitoring_interval, args.benchmark_time)
        sys.exit(1)


# -----------------------------------------------------------------------------------------------------------------------
class PersistentBufferingHandler(logging.handlers.BufferingHandler):
    """
    Subclass of BufferingHandler which *never* throws lows away.
    """

    def flush(self):
        """
        Overridden
        :return: Nothing
        """
        pass
