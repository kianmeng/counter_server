import os
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

    @classmethod
    def tearDownClass(cls):
        """Clean up after all test cases. Only available for Python >= 2.7."""
        os.remove(DEFAULT_FILE)

    def _create_client(self):
        """Create multiple client instances."""

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((DEFAULT_HOST, DEFAULT_PORT))
        return client

    def test_bad_request(self):
        """Test unsupported or missing command."""

        client = self._create_client()
        client.send('HELLO')
        result = client.recv(1024)
        client.close()
        self.assertEqual('400 Bad Request\n', result)

    def test_create_counter_without_label(self):
        """Test CREATE_COUNTER command without label."""

        client = self._create_client()
        client.send('CREATE_COUNTER')
        result = client.recv(1024)
        client.close()
        self.assertEqual('401 Bad Request: Missing label\n', result)

    def test_create_counter(self):
        """Test CREATE_COUNTER command."""

        client = self._create_client()
        client.send('CREATE_COUNTER foobar')
        result = client.recv(1024)
        client.close()
        self.assertEqual('201 CREATED\n', result)

    def test_create_duplicate_counter(self):
        """Test CREATE_COUNTER command with duplicate label."""

        client = self._create_client()
        client.send('CREATE_COUNTER foobar')
        result = client.recv(1024)
        client.close()
        self.assertEqual('402 Bad Request: Duplicate label\n', result)

    def test_increment_counter(self):
        """Test INCREMENT_COUNTER command."""

        client = self._create_client()
        client.send('INCREMENT_COUNTER')
        result = client.recv(1024)
        client.close()
        self.assertEqual('201 CREATED\n', result)

    def test_get_counter_values(self):
        """Test GET_COUNTER_VALUES command."""

        client = self._create_client()
        client.send('GET_COUNTER_VALUES')
        result = client.recv(1024)
        client.close()
        self.assertEqual('200 OK\n', result)

    def test_average_counter_value(self):
        """Test AVERAGE_COUNTER_VALUE command."""

        client = self._create_client()
        client.send('AVERAGE_COUNTER_VALUE')
        result = client.recv(1024)
        client.close()
        self.assertEqual('200 OK\n', result)

if __name__ == '__main__':
    # for those not using nose / nosetests
    # python test_counterserver.py -v
    unittest.main()
