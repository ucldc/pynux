from httmock import all_requests, HTTMock
from pynux import utils
import json
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

@all_requests
def response_content(url, request):
    content = {
        'entries': [{
            'properties': [],
        }],
        'isNextPageAvailable': False
    }
    return {'status_code': 200,
            'content': json.dumps(content) }

class TestNuxeoFunctions(unittest.TestCase):
    def runTest(self):
        with HTTMock(response_content):
            nx = utils.Nuxeo()
            assert(nx.all())
            assert(nx.all().next())

if __name__ == "__main__":
    test_case = TestNuxeoFunctions()
    test_case.runTest()
