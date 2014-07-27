import sys
import threading
import time
import SocketServer

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5263


class CounterRequestHandler(SocketServer.BaseRequestHandler):
    """The request handler class for our counter server."""

    def setup(self):
        print("%s:%s connected" % self.client_address)

    def handle(self):
        data = self.request.recv(1024)
        self.request.send(data.upper())
        return

    def finish(self):
        print("%s:%s disconnected" % self.client_address)


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
