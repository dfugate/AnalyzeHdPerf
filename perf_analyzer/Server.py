import sys

from Common import *

try:
    import bottle
except ImportError, e:
    print "The 'bottle' package is unavailable on this system!"
    print "Please run 'pip install bottle' and try starting the server again."
    sys.exit(1)


class Server(object):
    def __init__(self, num_clients):
        """
        Constructor
        :return: Instance of Server
        """
        self.num_clients = num_clients
        self.client_sessions = {}

    def hello(self):
        """
        Tells the client if the server is operational.
        :return: "Hello!"
        """
        return '<p>Hello!</p>'

    def client_heartbeat(self):
        """
        Client heartbeat.
        :return: Nothing.
        """
        hostname = bottle.request.json[HOSTNAME]
        pid = bottle.request.json[PID]
        timestamp = bottle.request.json[TIMESTAMP]

        print "TODO - heartbeat ", hostname, pid, timestamp

        return {}

    def client_start(self):
        """
        Client has started running a benchmark.
        :return: Nothing.
        """
        hostname = bottle.request.json[HOSTNAME]
        pid = bottle.request.json[PID]
        timestamp = bottle.request.json[TIMESTAMP]

        print "TODO - start ", hostname, pid, timestamp

        return {}

    def client_stop(self):
        """
        Client has stopped running a benchmark.
        :return: Nothing.
        """
        hostname = bottle.request.json[HOSTNAME]
        pid = bottle.request.json[PID]
        timestamp = bottle.request.json[TIMESTAMP]

        print "TODO - stop ", hostname, pid, timestamp

        return {}

    def client_resources(self):
        """
        Client has told us it's current resource usage.
        :return: Nothing.
        """
        hostname = bottle.request.json[HOSTNAME]
        pid = bottle.request.json[PID]
        timestamp = bottle.request.json[TIMESTAMP]
        cpu_util = bottle.request.json[CPU_UTIL]
        mem_usage = bottle.request.json[MEM_USAGE]

        print "TODO - resources ", hostname, pid, timestamp, cpu_util, mem_usage

        return {}

    def client_rollover(self):
        """
        Client has told us it's done writing a file.
        :return: Nothing.
        """
        hostname = bottle.request.json[HOSTNAME]
        pid = bottle.request.json[PID]
        timestamp = bottle.request.json[TIMESTAMP]
        file_size = bottle.request.json[FILE_SIZE]
        chunk = bottle.request.json[CHUNK]

        print "TODO - rollover ", hostname, pid, timestamp, file_size, chunk

        return {}

    def __getClientID(ip, procID):
        """
        Converts an IP address/process ID combination into a single identifier.
        :param ip: IP address of the client machine
        :param procID: Process ID of the client
        :return: See Description.
        """
        return ip + ":" + procID


if __name__ == "__main__":
    s = Server(3) #TODO

    # Initialize routes
    bottle.post("/")(s.hello)
    bottle.post(HEARTBEAT_PATH)(s.client_heartbeat)
    bottle.post(START_PATH)(s.client_start)
    bottle.post(STOP_PATH)(s.client_stop)
    bottle.post(RESOURCES_PATH)(s.client_resources)
    bottle.post(ROLLOVER_PATH)(s.client_rollover)


    bottle.run(host='localhost', port=8080, debug=True)
