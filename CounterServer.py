import datetime
import shelve
import sys
import threading
import time
import SocketServer

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5263
DEFAULT_FILE = 'counter.shelve'


class CounterRequestHandler(SocketServer.BaseRequestHandler):
    """The request handler class for our counter server."""

    def setup(self):
        # enable writeback so we can write all mutated changes back to the
        # file.
        self.store = shelve.open(DEFAULT_FILE, writeback=True)
        print("%s:%s connected" % self.client_address)

    def handle(self):
        data = self.request.recv(1024).strip().split()
        if not data:
            self.request.send("400 Bad Request\n")
            return

        # dispatching command to its corresponding method
        cmd = data[0]
        args = data[1:] if len(data) > 1 else []
        func = getattr(self, cmd, False)
        if not func:
            self.request.send("400 Bad Request\n")
            return
        else:
            func(*args)

    def finish(self):
        self.store.close()
        self.request.close()
        print("%s:%s disconnected" % self.client_address)

    def CREATE_COUNTER(self, *args):
        """Create a counter on our data storage based on the label given."""

        if not args:
            self.request.send("401 Bad Request: Missing label\n")
            return

        label = args[0]
        if label in self.store:
            self.request.send("402 Bad Request: Duplicate label\n")
            return

        self.store[label] = {}
        self.request.send("200 Ok\n")

    def INCREMENT_COUNTER(self, *args):
        if not args:
            self.request.send("401 Bad Request: Missing label\n")
            return

        label = args[0]
        if label not in self.store:
            self.request.send("403 Bad Request: Label not found\n")
            return

        # rounded to the nearest minute

        dt = datetime.datetime.now().replace(second=0)
        ts = int(time.mktime(dt.timetuple()))

        if ts in self.store[label]:
            # check if we've created the counter before within that minute
            count = self.store[label][ts]
            self.store[label][ts] = count + 1
        else:
            # increate the counter for that particular minute
            self.store[label][ts] = 1

        # we need to sync immediately, otherwise the unit test
        # test_increment_counter() will fail.
        self.store.sync()
        self.request.send("200 Ok\n")

    def GET_COUNTER_VALUES(self, *args):
        if not args:
            self.request.send("401 Bad Request: Missing label\n")
            return

        label = args[0]
        if label not in self.store:
            self.request.send("403 Bad Request: Label not found\n")
            return

        # if not period (from_date till to_date) found, just get the last item
        counter = self.store[label]
        if len(counter) == 0:
            count = 0
        else:
            if len(args) == 3:
                sdate = datetime.datetime.strptime(args[1], '%Y-%m-%d/%H:%M:%S').replace(second=0)
                edate = datetime.datetime.strptime(args[2], '%Y-%m-%d/%H:%M:%S').replace(second=0)
                stime = int(time.mktime(sdate.timetuple()))
                etime = int(time.mktime(edate.timetuple()))

                count_set = ((str(v)) for k, v in self.store[label].iteritems() if k >= stime and k <= etime)
                count = ' '.join(count_set)
            else:
                count = counter[counter.keys()[-1]]

        self.request.send("200 Ok %s\n" % count)

    def AVERAGE_COUNTER_VALUE(self, *args):
        if not args:
            self.request.send("401 Bad Request: Missing label\n")
            return

        label = args[0]
        if label not in self.store:
            self.request.send("403 Bad Request: Label not found\n")
            return

        # if not period (from_date till to_date) found, average all values.
        counter = self.store[label]
        average = sum(counter.values()) / len(counter)
        self.request.send("200 Ok %d\n" % average)


class CounterServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """The wrapper for the TCPServer class so we can use it for unit testing
    and additional features.

    To start the server, just type python CounterServer.py.
    To kill the server, type Ctrl-C.
    """

    # to prevent "error: [Errno 98] Address already in use" error
    allow_reuse_address = True

    # kill all spawned threads
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)


def main():
    server = CounterServer((DEFAULT_HOST, DEFAULT_PORT), CounterRequestHandler)
    # listen for connection until Ctrl-C
    try:
        # spawn a new thread for each request
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True  # TODO: doesn't let thread to clean up
        thread.start()
        # to prevent KeyboardInterrupt from being ignored where you've to
        # Ctrl-C multiple times to kill the server.
        while True:
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

if __name__ == '__main__':
    main()
