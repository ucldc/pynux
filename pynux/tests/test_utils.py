import httpretty
from pynux import utils
import json
import sys
import re

<<<<<<< HEAD
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestNuxeoREST(unittest.TestCase):
    def setUp(self):
        self.nx = utils.Nuxeo()

    @httpretty.activate
    def test_this(self):
=======
import unittest

class TestNuxeoREST(unittest.TestCase):
    def setUp(self):
        self.nx = utils.Nuxeo({
            'api': 'http://mockme/r',
            "fileImporter": 'http://mockme/f'
        })

    @httpretty.activate
    def runTest(self):
>>>>>>> travis
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
<<<<<<< HEAD

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
=======

        httpretty.register_uri(
            httpretty.GET,
            re.compile("(\w+)"),
            body=request_callback,
        )
        assert(self.nx.all())
        assert(self.nx.all().next())

if __name__ == '__main__':
    unittest.main()
>>>>>>> travis
