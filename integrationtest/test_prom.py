import unittest
import os
import urllib
from git_repo_backup.metrics import push, write_to_textfile

class Test_Prom(unittest.TestCase):
    prom_file_success = "/tmp/success.prom"
    prom_file_failure = "/tmpsdfhsadfasdkjgsadg/success.prom"

    def setUp(self):
        self._gateway = gateway = os.getenv("REPREP_GATEWAY", "localhost:9091")

        try:
            os.remove(self.prom_file_success)
        except FileNotFoundError:
            pass

    def test_pushgateway_empty_host(self):
        with self.assertRaises(ValueError):
            push("")

    def test_pushgateway_none_host(self):
        with self.assertRaises(ValueError):
            push(None)

    def test_pushgateway_success(self):
        push(self._gateway)

    def test_pushgateway_non_existing(self):
        with self.assertRaises(urllib.error.URLError):
            push("non-existing-host:9999")

    def test_textfile_success(self):
        prom_file = self.prom_file_success
        assert not os.path.exists(prom_file)
        write_to_textfile(prom_file)
        assert os.path.exists(prom_file)

    def test_textfile_failure(self):
        prom_file = self.prom_file_failure
        with self.assertRaises(ValueError):
            write_to_textfile(prom_file)