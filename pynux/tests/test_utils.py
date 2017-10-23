from builtins import bytes
import httpretty
from pynux import utils
import json
import sys
import re
import os
import io

import unittest

class TestNuxeoREST(unittest.TestCase):
    def setUp(self):
        self.nx = utils.Nuxeo({
            'api': 'http://mockme/r',
        }, rcfile=io.BytesIO(bytes()))

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
        assert(next(self.nx.all()))
        assert(self.nx.children("asset-library"))
        assert(self.nx.get_metadata(uid= self.nx.get_uid("asset-library")))
        assert(self.nx.get_metadata(path="asset-library"))


if __name__ == '__main__':
    unittest.main()
