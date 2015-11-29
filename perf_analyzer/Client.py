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
from socket import gethostname
from os import getpid, sep
from time import sleep

try:
    import psutil
except ImportError, e:
    print "The 'psutil' package is unavailable on this system!"
    print "Please run 'pip install psutil' and try starting the server again."
    sys.exit(1)

from Common import *

# -- Helper Functions ---------------------------------------------------------


def get_timestamp(dt=None):
    """
    Returns a datetime in an easily readable format.
    :param dt: datetime object to convert to a string. If None, uses current
    datetime.
    :return: See Description.
    """
    if dt is None:
        return str(datetime.utcnow())
    else:
        return str(dt)


def inform_server(partial_url, data):
    """
    Used to log messages to the server.
    :param url: Partial URL path
    :param data: Data to log (a dictionary)
    :return: Nothing.
    """
    data[HOSTNAME] = hostname
    data[PID] = pid
    if not (TIMESTAMP in data):
        data[TIMESTAMP] = get_timestamp()

    req = urllib2.Request(args.server + partial_url)
    req.add_header('Content-Type', 'application/json')
    resp = urllib2.urlopen(req, json.dumps(data))

    return

def do_work(temp_dir):
    """
    Does the actual work required for this benchmarking suite.
    :return: A temporary directory which needs to be deleted.
    """
    global running

    file_unique_id = 0
    chunk_str = "a" * (1000000 * args.chunk)
    final_chunk_str = "a" * (1000000 * (args.file_size % args.chunk))

    final_time = start_time + timedelta(0, args.time)

    while datetime.utcnow() < final_time:
        file_unique_id += 1
        with open(temp_dir + sep + str(file_unique_id), 'w') as f:
            for i in xrange(0, args.file_size / args.chunk):
                f.write(chunk_str)
                f.flush()
            if final_chunk_str != "":
                f.write(final_chunk_str)
                f.flush()
                
        l.info('Rollover (%d)' % file_unique_id)
        inform_server(ROLLOVER_PATH,
                      {
                        CHUNK: args.chunk,
                        FILE_SIZE: args.file_size,
                      })

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
        sleep(args.heartbeat)
    return


def monitor_resources():
    """
    Monitors system resources while the benchmark is running.
    :return: Nothing
    """
    while running:
        cpu_percent = psutil.cpu_percent(args.monitoring)
        swap_memory = psutil.swap_memory()
        inform_server(RESOURCES_PATH,
                      {
                        CPU_UTIL: cpu_percent,
                        MEM_USAGE: swap_memory.percent
                      })
    return


if __name__ == "__main__":

    if sys.version_info.major != 2 and sys.version_info.minor != 7:
        print "This version of Python (" + sys.version + ") is not supported! Please install 2.7."
        sys.exit(1)

    parser = ArgumentParser()
    parser.add_argument("server",
                        help="URL of the 'HD Performance Analyzer' server",
                        type=str,
                        default="http://localhost:8080")
    parser.add_argument("time",
                        help="Amount of time (seconds) to run this benchmark before terminating.",
                        type=int,
                        default=10)
    parser.add_argument("chunk",
                        help="Size of data chunks in MB. Minimum of 10",
                        type=int,
                        default=10)
    parser.add_argument("file_size",
                        help="Size of files in MB. Minimum of 10",
                        type=int,
                        default=50)
    parser.add_argument("heartbeat",
                        help="Amount of time (seconds) to sleep between heartbeat notifications.",
                        type=int,
                        default=5)
    parser.add_argument("monitoring",
                        help="Amount of time (seconds) to sleep between resource monitoring notifications.",
                        type=int,
                        default=10)
    args = parser.parse_args()

    hostname = gethostname()
    pid = getpid()

    # -- Sanity Checks --------------------------------------------------------
    try:
        inform_server("/", {})
    except:
        print "Unable to contact server. Bailing!"
        sys.exit(1)

    if args.time < 1:
        print "'%s' seconds is insufficient time to run this benchmark. Bailing!" % args.time
        sys.exit(1)
    elif args.chunk < 10:
        print "'%s' MB is too small of a chunk size for this benchmark. Bailing!" % args.chunk
        sys.exit(1)
    elif args.file_size < 10:
        print "'%s' MB is too small of a file size for this benchmark. Bailing!" % args.file_size
        sys.exit(1)
    elif args.chunk > args.file_size:
        print "File size must be larger than chunk size. Bailing!"
        sys.exit(1)
    elif args.heartbeat < 1:
        print "'%s' seconds is too small of a heartbeat interval. Bailing!" % args.heartbeat
        sys.exit(1)
    elif args.monitoring < 1:
        print "'%s' seconds is too small of a resource monitoring interval. Bailing!" % args.monitoring
        sys.exit(1)
    elif args.heartbeat > args.time:
        print "The heartbeat interval (%s) must be larger than the time to run this benchmark. Bailing!" % (args.heartbeat, args.time)
        sys.exit(1)
    elif args.monitoring > args.time:
        print "The resource monitoring interval (%s) must be larger than the time to run this benchmark. Bailing!" % (args.monitoring, args.time)
        sys.exit(1)
    # TODO Determine if we can go through at least two rollovers in the time given

    # -- The Good Stuff -------------------------------------------------------
    l = logging.getLogger('perf_analyzer')
    lh = logging.StreamHandler(sys.stdout)
    lf = logging.Formatter(LOG_FORMAT)
    lh.setFormatter(lf)
    l.addHandler(lh)
    l.setLevel(logging.DEBUG)

    temp_dir = tempfile.mkdtemp()  # TODO any way to tell if this is locally mounted?
    l.debug('Files generated by this test will be stored in "%s".' % temp_dir)

    monitor_resources_thread = threading.Thread(target=monitor_resources, args=())
    heartbeat_thread = threading.Thread(target=heartbeat, args=())
    do_work_thread = threading.Thread(target=do_work, args=(temp_dir,))

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
