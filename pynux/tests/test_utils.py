import httpretty
from pynux import utils
import json
import sys
import re

import unittest

class TestNuxeoREST(unittest.TestCase):
    def setUp(self):
        self.nx = utils.Nuxeo()

    @httpretty.activate
    def runTest(self):
        content = {
            'entries': [{
                'properties': [],
            }],
            'isNextPageAvailable': False
        }
        httpretty.register_uri(
            httpretty.GET,
            re.compile("localhost"),
            body=json.dumps(content),
        )
        assert(self.nx.all())
        assert(self.nx.all().next())

if __name__ == '__main__':
    unittest.main()
