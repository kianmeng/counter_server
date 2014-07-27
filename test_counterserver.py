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

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _create_client(self):
        """Create multiple client instances."""

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((DEFAULT_HOST, DEFAULT_PORT))
        return client

    def test_uppercase(self):
        """Test CounterRequestHandler.handle() works as intended."""

        client = self._create_client()
        client.send('hello world')
        result = client.recv(2014)
        client.close()
        self.assertEqual('HELLO WORLD', result)

    def test_multiple_connection(self):
        """This is to make sure that we can have multiple test cases against
        one server instance."""

        client = self._create_client()
        client.send('world hello')
        result = client.recv(2014)
        client.close()
        self.assertEqual('WORLD HELLO', result)


if __name__ == '__main__':
    # for those not using nose / nosetests
    # python test_counterserver.py -v
    unittest.main()
