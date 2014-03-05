import httpretty
from pynux import utils
import json
import sys
import re

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestNuxeoREST(unittest.TestCase):
    def setUp(self):
        self.nx = utils.Nuxeo()

    @httpretty.activate
    def test_this(self):
        document = {
            'properties': [],
            'uid': 'xxxx'
        }
        results = {
            'entries': [ document ],
            'isNextPageAvailable': False
        }
        httpretty.register_uri(
            httpretty.GET,
            re.compile("(\w+)/@\w+"),
            body=json.dumps(results),
        )
        httpretty.register_uri(
            httpretty.GET,
            re.compile("^((?!\@).)*$"),  # http://stackoverflow.com/a/406408/1763984
            body=json.dumps(document),
        )
        assert(self.nx.all())
        assert(self.nx.all().next())
        assert(self.nx.children("asset-library"))
        assert(self.nx.get_metadata(uid= self.nx.get_uid("asset-library")))
        assert(self.nx.get_metadata(path="asset-library"))
