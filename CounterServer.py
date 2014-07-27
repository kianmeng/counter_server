import SocketServer

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5263


class CounterRequestHandler(SocketServer.BaseRequestHandler):
    """The request handler class for our counter server."""

    def handle(self):
        data = self.request.recv(1024)
        self.request.send(data.upper())
        return


class CounterServer(SocketServer.TCPServer):
    """The wrapper for the TCPServer class so we can use it for unit testing
    and additional features.

    To start the server, just type python CounterServer.py.
    To kill the server, type Ctrl-C.
    """

    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)


if __name__ == '__main__':
    server = CounterServer((DEFAULT_HOST, DEFAULT_PORT), CounterRequestHandler)
    server.serve_forever()