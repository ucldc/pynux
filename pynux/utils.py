#!/usr/bin/env python
# -*- coding: ascii -*-

"""
pynux.utils
~~~~~~~~~~~~~

python function library for working with nuxeo "REST" APIs.

"""

from pprint import pprint as pp
import requests
import json
import urlparse
import sys
from time import sleep


class Nuxeo:
    def __init__(self, conf={}):
        # http://stackoverflow.com/a/17501381/1763984
        defaults = {
            "user": "Administrator",
            "password": "Administrator",
            "api": "http://localhost:8080/nuxeo/site/api/v1",
            "fileImporter": "http://localhost:8080/nuxeo/site/fileImporter"}
        self.conf = {}
        self.conf.update(defaults)
        self.conf.update(conf)
        self.auth = (self.conf["user"], self.conf["password"])

    def _recursive_get(self, url, params, documents, current_page_index):
        params.update({'currentPageIndex': current_page_index})
        res = requests.get(url, params=params, auth=self.auth)
        pp(res.url)
        res.raise_for_status()
        result_dict = json.loads(res.text)
        out_list = result_dict['entries']
        documents.extend(out_list)
        if result_dict['isNextPageAvailable']:
            self._recursive_get(url, params, documents, current_page_index + 1)
        return

    #
    ######## utility functions for nuxeo
    #

    def nxql(self, query):
        """page through the results for an nxql query"""
        url = self.conf["api"] + "/path/@search"
        params = {
            'pageSize': '100',
            'query': query
        }
        documents = []
        self._recursive_get(url, params, documents, 1)
        return documents

    def all(self):
        """page through the results for all"""
        return self.nxql('SELECT * FROM Document')

    def children(self, path):
        """get child documents of a path"""
        url = self.conf["api"] + "/path/" + path + "/@children"
        params = {'pageSize': '10000'}
        res = requests.get(url, params=params, auth=(self.auth))
        res.raise_for_status()
        result_dict = json.loads(res.text)
        return result_dict['entries']

    def get_uid(self, path):
        """look up uid from the path"""
        url = urlparse.urljoin(self.conf['api'] + "/", "path") + path
        res = requests.get(url, auth=self.auth)
        res.raise_for_status()
        return json.loads(res.text)['uid']

    def get_metadata(self, **documentid):
        """get metadata for a path"""
        if len(documentid) != 1:
            raise TypeError("either uid or path")
        url = ""
        if 'path' in documentid:
            url = self.conf['api'] + "/path" + documentid['path'] + "/"
        elif 'uid' in documentid:
            url = self.conf['api'] + "/id/" + documentid['uid'] + "/"
            pp(url)
        else:
            raise Exception("no document id found")
        headers = {'X-NXDocumentProperties': 'ucldc_schema,dublincore'}
        res = requests.get(url, headers=headers, auth=self.auth)
        res.raise_for_status()
        return json.loads(res.text)

    def update_nuxeo_properties(self, properties, **documentid):
        """update nuxeo document properties"""
        if len(documentid) != 1:
            raise TypeError("either uid or path")
        uid = documentid['uid'] or self.get_uid(documentid['path'])
        if not uid:
            raise Exception("no uid found")
        url = self.api + "/id/" + uid + "/"
        headers = {'X-NXDocumentProperties': 'ucldc_schema,dublincore',
                   'Content-Type': 'application/json+nxentity'}
        # copy what we want from the input json into the payload
        payload = {}
        payload['uid'] = uid
        payload['properties'] = properties
        res = requests.put(url,
                           data=json.dumps(payload),
                           auth=self.auth,
                           headers=headers)
        res.raise_for_status()
        return json.loads(res.text)

    def call_file_importer_api(self, verb, params):
        """generic wrapper to make GET calls to this API"""
        url = "{0}/{1}".format(self.conf['fileImporter'], verb)
        pp((url, params))
        res = requests.get(url, params=params, auth=self.auth)
        res.raise_for_status()
        return res.text

    def wait_file_importer(self):
        url = "{0}/{1}".format(self.conf['fileImporter'], "status")
        res = requests.get(url, auth=self.auth)
        res.raise_for_status()
        if res.text == 'Not Running':
            return True
        else:
            sleep(20)
            sys.stdout.write('.')
            sys.stdout.flush()
            self.wait_file_importer()


def test():
    """ Testing Docstring"""
    pass

if __name__ == '__main__':
    test()
