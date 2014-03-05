import httpretty
from pynux import utils
import json
import sys
import re

import unittest

class TestNuxeoREST(unittest.TestCase):
    def setUp(self):
        self.nx = utils.Nuxeo({
            'api': 'http://mockme/r',
            "fileImporter": 'http://mockme/f'
        })

    @httpretty.activate
    def runTest(self):
        document = {
            'properties': [],
            'uid': 'xxxx'
        }
        results = {
            'entries': [ document ],
            'isNextPageAvailable': False
        }
        def request_callback(request, uri, headers):
            if '@' in uri:
                return (200, headers, json.dumps(results))
            else:
                return (200, headers, json.dumps(document))

        httpretty.register_uri(
            httpretty.GET,
            re.compile("(\w+)"),
            body=request_callback,
        )
        assert(self.nx.all())
        assert(self.nx.all().next())

if __name__ == '__main__':
    unittest.main()
