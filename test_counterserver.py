import socket
import threading
import unittest

from CounterServer import *


class CounterServerTest(unittest.TestCase):
    """Default test class against all commands. For better performance, use the
    nosetests -vv or nt -vv command."""

    def setUp(self):
        self.server = CounterServer((DEFAULT_HOST, DEFAULT_PORT), CounterRequestHandler)

        # we've to use threading here otherwise the test script will freeze
        # until we stop it using Ctrl-C.
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True)
        self.server_thread.start()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((DEFAULT_HOST, DEFAULT_PORT))

    def tearDown(self):
        self.client.close()
        self.server.shutdown()
        self.server.server_close()

    def test_uppercase(self):
        """Test CounterRequestHandler.handle() works as intended."""

        self.client.send('hello world')
        result = self.client.recv(2014)
        self.assertEqual('HELLO WORLD', result)

    def test_multiple_connection(self):
        """This is to make sure that we can have multiple test cases against
        one server instance."""

        self.client.send('world hello')
        result = self.client.recv(2014)
        self.assertEqual('WORLD HELLO', result)


if __name__ == '__main__':
    # for those not using nose / nosetests
    # python test_counterserver.py -v
    unittest.main()
