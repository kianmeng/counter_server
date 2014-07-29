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
        self.store = shelve.open(DEFAULT_FILE)
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
        if self.store.has_key(label):
            self.request.send("402 Bad Request: Duplicate label\n")
            return

        self.store[label] = {}
        self.request.send("201 CREATED\n")

    def INCREMENT_COUNTER(self, *args):
        self.request.send("201 CREATED\n")

    def GET_COUNTER_VALUES(self, *args):
        self.request.send("200 OK\n")

    def AVERAGE_COUNTER_VALUE(self, *args):
        self.request.send("200 OK\n")


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
