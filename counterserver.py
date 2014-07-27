import SocketServer


class CounterRequestHandler(SocketServer.BaseRequestHandler):
    """The request handler class for our counter server."""

    def handle(self):
        data = self.request.recv(1024)
        self.request.send(data.upper())
        return

if __name__ == '__main__':
    HOST, PORT = "localhost", 5263

    server = SocketServer.TCPServer((HOST, PORT), CounterRequestHandler)
    server.serve_forever()
