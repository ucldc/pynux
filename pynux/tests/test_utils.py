from httmock import all_requests, HTTMock
from pynux import utils
import json

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

with HTTMock(response_content):
    nx = utils.Nuxeo()
    assert(nx.all())
    assert(nx.all().next())
