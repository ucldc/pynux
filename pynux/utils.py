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

class Nuxeo:
    def __init__(self, conf={}):
        # http://stackoverflow.com/a/17501381/1763984
        defaults = { 
                    "user":"Administrator", 
                    "password":"Administrator",
                    "api":"http://localhost:8080/nuxeo/site/api/v1",
                    "fileImporter":"http://localhost:8080/nuxeo/site/fileImporter",
                   }
        self.conf = {}
        self.conf.update(defaults)
        self.conf.update(conf)
        self.auth = (self.conf["user"], self.conf["password"])
        pp(self.conf)


    ######## utility functions for nuxeo

    def nxql(self, query):
        """page through the results for an nxql query"""
        url = self.conf["api"] + "/path/@search"
        def get_recursive(documents, current_page_index):
            params={
                     'pageSize':'100',
                     'query': query,
                     'currentPageIndex': current_page_index,
                   }
            res = requests.get(url, params=params, auth=self.auth)
            res.raise_for_status()
            result_dict = json.loads(res.text)
            out_list = result_dict['entries']
            documents.extend(out_list)
            if result_dict['isNextPageAvailable']:
                self.get_recursive(documents, current_page_index + 1)
            return
        documents = []
        get_recursive(documents, 1)
        return documents

    def all(self):
        """page through the results for all"""
        return self.nxql('SELECT * FROM Document');

    def children(self, path):
        """get child documents of a path"""
        url = self.conf["api"] + "/path/" + path + "/@children"
        params={'pageSize':'10000'}
        res = requests.get(url, params=params, auth=(self.auth))
        res.raise_for_status()
        result_dict = json.loads(res.text)
        return result_dict['entries']

def test():
    """ Testing Docstring"""
    pass
    
if __name__=='__main__':
    test()
