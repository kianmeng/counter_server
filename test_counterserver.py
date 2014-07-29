import os
import socket
import threading
import unittest

from awesome_print import ap

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
        os.remove(DEFAULT_FILE)
        self.server.shutdown()
        self.server.server_close()

    def _create_client(self):
        """Create multiple client instances."""

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((DEFAULT_HOST, DEFAULT_PORT))
        return client

    def _send_request_command(self, command, *args):
        """Common code to send a request command."""

        client = self._create_client()
        client.send(command)
        result = client.recv(1024)
        client.close()
        return result

    def test_bad_request(self):
        """Test unsupported or missing command."""

        result = self._send_request_command('HELLO')
        self.assertEqual('400 Bad Request\n', result)

    def test_create_counter(self):
        """Test CREATE_COUNTER command."""

        result = self._send_request_command('CREATE_COUNTER foobar')
        self.assertEqual('200 Ok\n', result)

    def test_create_counter_without_label(self):
        """Test CREATE_COUNTER command without label."""

        result = self._send_request_command('CREATE_COUNTER')
        self.assertEqual('401 Bad Request: Missing label\n', result)

    def test_create_duplicate_counter(self):
        """Test CREATE_COUNTER command with duplicate label."""

        self.test_create_counter()
        result = self._send_request_command('CREATE_COUNTER foobar')
        self.assertEqual('402 Bad Request: Duplicate label\n', result)

    def test_increment_counter_missing_label(self):
        """Test INCREMENT_COUNTER command with missing label."""

        result = self._send_request_command('INCREMENT_COUNTER')
        self.assertEqual('401 Bad Request: Missing label\n', result)

    def test_increment_counter_unknown_label(self):
        """Test INCREMENT_COUNTER command with unknown label."""

        result = self._send_request_command('INCREMENT_COUNTER barfoo')
        self.assertEqual('403 Bad Request: Label not found\n', result)

    def test_increment_counter_and_counter_values(self):
        """Test INCREMENT_COUNTER and GET_COUNTER_VALUES commands."""

        result = self._send_request_command('CREATE_COUNTER nose')
        self.assertEqual('200 Ok\n', result)

        result = self._send_request_command('INCREMENT_COUNTER nose')
        self.assertEqual('200 Ok\n', result)

        result = self._send_request_command('GET_COUNTER_VALUES nose')
        self.assertEqual('200 Ok 1\n', result)

    def test_increment_counter_multiple_times_within_minute(self):
        """Test INCREMENT_COUNTER commands multiple times within minute."""

        result = self._send_request_command('CREATE_COUNTER nose')
        self.assertEqual('200 Ok\n', result)

        max = 5
        for i in range(0, max):
            result = self._send_request_command('INCREMENT_COUNTER nose')
            self.assertEqual('200 Ok\n', result)

        result = self._send_request_command('GET_COUNTER_VALUES nose')
        self.assertEqual('200 Ok %d\n' % max, result)

    def test_average_counter_value(self):
        """Test AVERAGE_COUNTER_VALUE command."""

        result = self._send_request_command('AVERAGE_COUNTER_VALUE')
        self.assertEqual('200 Ok\n', result)

if __name__ == '__main__':
    # for those not using nose / nosetests
    # python test_counterserver.py -v
    unittest.main()
