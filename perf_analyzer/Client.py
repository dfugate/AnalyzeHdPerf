# ----------------------------------------------------------------------------------------------------------------------
# Copyright (C) 2015 David Fugate dave.fugate@gmail.com
#
# This work is licensed under the Creative Commons
# Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of
# this license, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ or send
# a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
# ----------------------------------------------------------------------------------------------------------------------

import sys
import threading
import tempfile
import shutil
import logging
import json
import urllib2
import logging.handlers

from argparse import ArgumentParser
from datetime import datetime, timedelta
from socket import gethostname, gethostbyname
from os import sep, getcwd
from time import sleep

try:
    import psutil
except ImportError, e:
    print "The 'psutil' package is unavailable on this system!"
    print "Please run 'pip install psutil' and try starting the server again."
    sys.exit(1)

from perf_analyzer import *


# -- HELPERS -----------------------------------------------------------------------------------------------------------

def get_timestamp(dt=None):
    """
    Returns a datetime in an easily readable format.
    :param dt: datetime object to convert to a string. If None, uses current
    datetime.
    :return: See Description.
    """
    if dt is None:
        return datetime.utcnow().strftime(DATETIME_FORMAT)
    else:
        return dt.strftime(DATETIME_FORMAT)


def inform_server(partial_url, data):
    """
    Used to log messages to the server.
    :param partial_url: Partial URL path
    :param data: Data to log (a dictionary)
    :return: Server response.
    """
    # Data common to all requests we send up to the server.
    data[HOSTNAME] = hostname
    data[CHUNK] = args.chunk_size

    # Most invocations of this method will not include the timestamp
    if not (TIMESTAMP in data):
        data[TIMESTAMP] = get_timestamp()

    req = urllib2.Request("http://" + args.server + ":" + args.server_port + partial_url)
    req.add_header('Content-Type', 'application/json')
    # TODO Error-checking. What happens if the server disappears?
    resp = urllib2.urlopen(req, json.dumps(data))

    return resp


def do_work(work_dir, chunk_size, file_size, benchmark_duration):
    """
    Does the actual work required for this benchmarking suite.
    :param work_dir Directory to do write files within.
    :param chunk_size Number of bytes to write to disk before flushing.
    :param file_size Size of the file (bytes) to write.
    :param benchmark_duration Time (seconds) to run the benchmark before terminating.
    :return: A temporary directory which needs to be deleted.
    """
    global running

    try:
        file_unique_id = 0
        # Data blob we'll flush to disk with every write.
        chunk_str = "a" * (1000000 * chunk_size)
        # The last piece of data written *can* be a different size
        final_chunk_str = "a" * (1000000 * (file_size % chunk_size))
        # Time the benchmark must stop by.
        final_time = start_time + timedelta(0, benchmark_duration)

        # We stop the benchmark *only* after complete files have been written to disk; not simply chunks
        while datetime.utcnow() < final_time:
            file_unique_id += 1
            with open(work_dir + sep + str(file_unique_id), 'w') as f:
                for i in xrange(0, file_size / chunk_size):
                    f.write(chunk_str)
                    f.flush()
                if final_chunk_str != "":
                    f.write(final_chunk_str)
                    f.flush()
                
            l.info('Rollover (%d)' % file_unique_id)
            inform_server(ROLLOVER_PATH, {})

    finally:
        running = False

    return


def heartbeat():
    """
    Tells the server that this client is still alive.
    :return: Nothing.
    """
    while running:
        l.debug('Heartbeat')
        inform_server(HEARTBEAT_PATH, {})
        sleep(args.heartbeat_interval)
    return


def monitor_resources(sleep_time):
    """
    Monitors system resources while the benchmark is running.
    :param sleep_time Time to sleep between resource checks.
    :return: Nothing
    """
    while running:
        cpu_percent = psutil.cpu_percent(sleep_time)  # sleeps for args.monitoring_interval seconds
        swap_memory = psutil.swap_memory()
        inform_server(RESOURCES_PATH,
                      {
                        CPU_UTIL: cpu_percent,
                        MEM_USAGE: swap_memory.percent
                      })
    return

def sanity_check_perf(file_size, chunk_size, benchmark_duration, work_dir):
    """
    Checks to see if this client can handle at least two file rollovers in the given time.
    :param file_size: size of files to create (MB)
    :param chunk_size: size of chunks to write to the file (MB)
    :param benchmark_duration: time (seconds) this benchmark has to execute.
    :param work_dir: file system directory we'll be running the benchmarks out of.
    :return: Nothing. Bails out of the process entirely though if the benchmark can't run to completion.
    """
    blob = "a" * (1000000 * chunk_size)

    t0 = datetime.utcnow()
    with open(work_dir + sep + "sanitycheck.txt", 'w') as f:
        f.write(blob)

    time_diff = (datetime.utcnow() - t0).total_seconds()

    # Time needed to write one file
    estimated_file_duration = (float(file_size)/chunk_size) * time_diff

    # Estimated number of files that can be created.
    estimated_total_files = benchmark_duration / estimated_file_duration

    if estimated_total_files < 2.0:
        l.error("Given '%s' MB files, only '%s' could be created in '%s' seconds on this client. Bailing!" % (file_size,
                                                                                                              estimated_total_files,
                                                                                                              benchmark_duration))
        exit(1)
    else:
        l.debug("Given '%s' MB files, approximately '%s' could be created in '%s' seconds." % (file_size,
                                                                                               estimated_total_files,
                                                                                               benchmark_duration))
    return


# --MAIN----------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("server",
                        help="IP address of the server.",
                        type=str)
    parser.add_argument("server_port",
                        help="TCP port on the server accepting HTTP requests.",
                        type=str)
    parser.add_argument("benchmark_time",
                        help="Time (seconds) the benchmark is run for.",
                        type=int)
    parser.add_argument("chunk_size",
                        help="Size (MB) to buffer before flushing to a file. Minimum of 10MB.",
                        type=int)
    parser.add_argument("file_size",
                        help="Size (MB) of files to generate. Minimum of 10MB.",
                        type=int)
    parser.add_argument("heartbeat_interval",
                        help="Time (seconds) for to sleep between heartbeat notifications.",
                        type=int)
    parser.add_argument("monitoring_interval",
                        help="Time (seconds) to sleep between resource monitoring notifications.",
                        type=int)

    args = parser.parse_args()

    temp_dir = tempfile.mkdtemp()  # TODO any way to tell if this is locally mounted?
    hostname = gethostname()
    # If the server is run locally as well...let's assume they haven't setup the network properly
    if gethostbyname(hostname) == args.server:
        args.server = "localhost"

    l = logging.getLogger('client-' + str(args.chunk_size))
    l.setLevel(logging.DEBUG)
    lf = logging.Formatter(LOG_FORMAT)

    lh = logging.StreamHandler(sys.stdout)
    lh.setFormatter(lf)
    l.addHandler(lh)

    fh = logging.FileHandler(getcwd() + sep + "run.log", mode="w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(lf)
    l.addHandler(fh)

    l.debug('Files generated by this test will be stored in "%s".' % temp_dir)

    # --SANITY CHECKS---------------------------------------------------------------------------------------------------
    try:
        inform_server("/hello", {})
    except:
        print "Unable to contact server (%s). Bailing!" % ("http://" + args.server + ":" + args.server_port + "/hello")
        sys.exit(1)

    sanity_check_config(args)
    if args.chunk_size > args.file_size:
        print "File size must be larger than chunk_size size. Bailing!"
        sys.exit(1)

    sanity_check_perf(args.file_size, args.chunk_size, args.benchmark_time, temp_dir)

    # -- The Good Stuff -------------------------------------------------------
    monitor_resources_thread = threading.Thread(target=monitor_resources, args=(args.monitoring_interval,))
    heartbeat_thread = threading.Thread(target=heartbeat, args=())
    do_work_thread = threading.Thread(target=do_work, args=(temp_dir, args.chunk_size, args.file_size, args.benchmark_time))

    start_time = datetime.utcnow()
    l.info('Started at "%s".' % str(start_time))
    inform_server(START_PATH,
                  {
                    'timestamp': get_timestamp(start_time)
                  })

    running = True

    monitor_resources_thread.start()
    heartbeat_thread.start()
    do_work_thread.start()

    do_work_thread.join()
    heartbeat_thread.join()
    monitor_resources_thread.join()

    l.info('Stopped at "%s".' % str(start_time))
    inform_server(STOP_PATH, {})

    l.debug('Removing the temporary directory, "%s", now.' % temp_dir)
    shutil.rmtree(temp_dir)
    l.info('Goodbye!')
