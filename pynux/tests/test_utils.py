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
        content = {
            'entries': [{
                'properties': [],
            }],
            'isNextPageAvailable': False
        }
        httpretty.register_uri(
            httpretty.GET,
            re.compile("(\w+)"),
            body=json.dumps(content),
        )
        assert(self.nx.all())
        assert(self.nx.all().next())
