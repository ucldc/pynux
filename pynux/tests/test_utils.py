import httpretty
from pynux import utils
import json
import sys
import re
import os

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
        assert(self.nx.children("asset-library"))
        assert(self.nx.get_metadata(uid= self.nx.get_uid("asset-library")))
        assert(self.nx.get_metadata(path="asset-library"))

class TestConfigFile(unittest.TestCase):
    '''Had a problem with the default config path. Check it here'''
    def testRCFILE(self):
        rcfile = utils._rcfile_
        full_path = os.path.expanduser(rcfile)
        # then expanded path should be different
        self.assertNotEqual(full_path, utils._rcfile_)

if __name__ == '__main__':
    unittest.main()
