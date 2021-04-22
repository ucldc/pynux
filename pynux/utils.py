#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
pynux.utils
~~~~~~~~~~~

python function library for working with nuxeo "REST" APIs.

"""
from __future__ import unicode_literals
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import requests
import json
import sys
import os
import time
import itertools
import logging
import configparser
from os.path import expanduser
import codecs
import urllib.parse

# set the output to utf8 in py2 or py3
UTF8Writer = codecs.getwriter('utf8')
try:
    # http://stackoverflow.com/a/4374457/1763984
    sys.stdout = UTF8Writer(sys.stdout.detach())
except AttributeError as e:
    sys.stdout = UTF8Writer(sys.stdout)

_loglevel_ = 'ERROR'
_version_ = '1.0.0'

RECURSIVE_NXQL_PROJECT_FOLDER = """SELECT *
FROM Organization
WHERE ecm:path STARTSWITH '{}' AND ecm:isTrashed = 0
"""

RECURSIVE_NXQL_OBJECT = """SELECT *
FROM SampleCustomPicture, CustomFile, CustomVideo, CustomAudio, CustomThreeD
WHERE ecm:path STARTSWITH '{}' AND ecm:isTrashed = 0
ORDER BY ecm:pos"""


def utf8_arg(bytestring):
    try:
        # fix up command line argument for python 2
        # http://stackoverflow.com/a/23085282
        return bytestring.decode(sys.getfilesystemencoding())
    except AttributeError:
        # command line arguments already decoded in python 3
        return bytestring


def escape_path(path):
    return urllib.parse.quote(path, safe=' /')


class Nuxeo(object):
    """utility functions for nuxeo

    Object's data keeps track of URLs and credentials
    for Nuxeo REST API and Nuxeo Platoform Importer / bulk import API

    :param conf: dictionary with ``"user":``, ``"password":``, ``"api":``,  and/or ``"X-NXDocumentProperties":`` to override defaults
    :param rcfile: `ConfigParser`
    :param loglevel: for standard library `logging`
    """

    def __init__(self, conf={}, rcfile=None, loglevel=_loglevel_):
        """configuration for http connections and options"""
        defaultrc = """\
[nuxeo_account]
user = Administrator
password = Administrator

[rest_api]
base = http://localhost:8080/nuxeo/site/api/v1
X-NXDocumentProperties = dublincore
"""
        config = configparser.ConfigParser()
        # first level of defaults hardcoded above
        config.read_string(defaultrc)
        # then, check for an rcfile supplied by the caller
        if rcfile:
            config.read_file(rcfile)
        # otherwise, check a default path in user directory
        elif not(rcfile) and os.path.isfile(expanduser('~/.pynuxrc')):
            config.read(expanduser('~/.pynuxrc'))

        token_auth = bool(
            config.has_option('nuxeo_account', 'method') and
            config.get('nuxeo_account', 'method') == 'token')

        token = None
        if config.has_option('nuxeo_account', 'X-Authentication-Token'):
            token = config.get('nuxeo_account', 'X-Authentication-Token')

        # these are the defaults from the config
        defaults = {
            "auth_method":
                'token' if token_auth else 'basic',
            "user":
                config.get('nuxeo_account', 'user'),
            "password":
                config.get('nuxeo_account', 'password'),
            "api":
                config.get('rest_api', 'base'),
            "X-NXDocumentProperties":
                config.get('rest_api', 'X-NXDocumentProperties'),
            "X-Authentication-Token":
                token,
        }
        self.conf = {}
        self.conf.update(defaults)
        # override the defaults based on conf pased in by caller
        self.conf.update(conf)

        if config.has_section('ezid'):
            self.ezid_conf = {
                "host":
                    config.get('ezid', 'host'),
                "username":
                    config.get('ezid', 'username'),
                "password":
                    config.get('ezid', 'password'),
                "shoulder":
                    config.get('ezid', 'shoulder'),
            }

        # auth and headers for the request object
        self.document_property_headers = {
            'X-NXDocumentProperties': self.conf['X-NXDocumentProperties']
        }
        if self.conf['auth_method'] == 'token':
            self.document_property_headers.update({
                'X-Authentication-Token':
                self.conf['X-Authentication-Token']
            })
            self.auth = None
        else:
            self.auth = (self.conf["user"], self.conf["password"])

        # set debugging level
        numeric_level = getattr(logging, loglevel, None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(
            level=numeric_level, )
        # log some stuff
        self.logger = logging.getLogger(__name__)
        self.logger.info("init Nuxeo object")
        redacted = self.conf
        redacted.update({'password': '...redacted...'})
        self.logger.debug(redacted)

    ## Python generator for paged API resource
    #    based on http://stackoverflow.com/questions/17702785/
    #    see also [Loop like a native](http://www.youtube.com/watch?v=EnSu9hHGq5o)

    def _get_page(self, url, params, current_page_index):
        """get a single page of nuxeo API results

        :param url: url before query string
        :param params:
        :type params: dict of cgi paramaters
        :param current_page_index: current page (index 0)
        :type current_page_index: int
        :returns: json from nuxeo
        """
        params.update({'currentPageIndex': current_page_index})
        res = requests.get(
            url,
            headers=self.document_property_headers,
            params=params,
            auth=self.auth)
        res.raise_for_status()
        self.logger.debug(res.content)
        return json.loads(res.content.decode('utf-8'))

    def _get_iter(self, url, params):
        """generator iterator for nuxeo results

        :param url: url before query string
        :param params:
        :type params: dict of cgi paramaters
        :returns: iterator of nuxeo API results
        """
        for current_page_index in itertools.count():
            result_dict = self._get_page(url, params, current_page_index)
            for document in result_dict['entries']:
                yield document
            if not result_dict['isNextPageAvailable']:
                break

    # REST API functions
    # uses NUXEO_REST_API in self.conf['api']

    def nxql(self, query):
        """generic nxql query

        :returns: iterator of nuxeo API results
        """
        url = u'/'.join([self.conf["api"], "path/@search"])
        params = {'pageSize': '100', 'query': query}
        self.logger.info(query)
        self.logger.debug(url)
        return self._get_iter(url, params)

    def all(self):
        """.nxql("SELECT * FROM Document")

        :returns: iterator of nuxeo API results
        """
        return self.nxql('SELECT * FROM Document')

    def children(self, path):
        """get child documents of a path

        :returns: iterator of nuxeo API results
        """
        url = u'/'.join(
            [self.conf["api"], "path", escape_path(path).strip('/'), "@children"])
        params = {}
        self.logger.info(path)
        self.logger.debug(url)
        return self._get_iter(url, params)

    def recursive_project_folders(self, path):
        nxql = RECURSIVE_NXQL_PROJECT_FOLDER.format(escape_path(path))
        self.logger.debug(nxql)
        return self.nxql(nxql)

    def recursive_objects(self, path):
        nxql = RECURSIVE_NXQL_OBJECT.format(escape_path(path))
        self.logger.debug(nxql)
        return self.nxql(nxql)

    def get_uid(self, path):
        """look up uid from the path

        :param path: nuxeo path for a document
        :type path: string
        :returns: uid
        :rtype: string
        """
        url = u'/'.join([self.conf['api'], "path", escape_path(path).strip('/')])
        res = requests.get(
            url, headers=self.document_property_headers, auth=self.auth)
        res.raise_for_status()
        return json.loads(res.content.decode('utf-8'))['uid']

    def get_metadata(self, **documentid):
        """get metadata for a document

        :param documentid: either uid= or path=
        :returns: json from nuxeo
        """
        uid = ''
        if len(documentid) != 1:
            raise TypeError("either uid or path")
        if 'path' in documentid:
            uid = self.get_uid(documentid['path'])
        elif 'uid' in documentid:
            uid = documentid['uid']
        url = u'/'.join([self.conf['api'], "id", uid])
        res = requests.get(
            url, headers=self.document_property_headers, auth=self.auth)
        res.raise_for_status()
        return json.loads(res.content.decode('utf-8'))

    def update_nuxeo_properties(self, data, **documentid):
        """update nuxeo document properties

        :param data: document properties for nuxeo update
        :type data: dict
        :param documentid: either uid= or path=
        :returns: updated json from nuxeo
        """
        uid = ''
        if len(documentid) != 1:
            raise TypeError("either uid or path")
        if 'path' in documentid:
            uid = self.get_uid(documentid['path'])
        elif 'uid' in documentid:
            uid = documentid['uid']
        url = u'/'.join([self.conf['api'], "id", uid])
        headers = self.document_property_headers
        headers.update({'Content-Type': 'application/json'})

        # copy what we want from the input json into the payload
        payload = {}
        payload['uid'] = uid
        payload['entity-type'] = data.get('entity-type', 'document')
        payload['properties'] = data['properties']
        res = requests.put(
            url, data=json.dumps(payload), auth=self.auth, headers=headers)
        res.raise_for_status()
        r2 = requests.get(url, auth=self.auth, headers=headers)
        r2.raise_for_status()
        return json.loads(r2.content)

    def print_document_summary(self, documents):
        for document in documents:
            path = document.get('path')
            if not path:
                path = ''
            print('\t'.join([document['uid'], document['type'], path]))

    def copy_metadata_to_local(self, documents, local):
        for document in documents:
            uid = document['uid']
            file = os.path.join(local, ''.join([uid, ".json"]))
            dir = os.path.dirname(file)
            self._mkdir(dir)
            with open(file, 'w') as json_file:
                py_json = self.get_metadata(uid=uid)
                out_json = {}
                out_json['uid'] = py_json['uid']
                out_json['path'] = py_json['path']
                out_json["entity-type"] = py_json["entity-type"]
                out_json['properties'] = py_json['properties']
                json_file.write(
                    json.dumps(
                        out_json,
                        sort_keys=True,
                        indent=4,
                        separators=(',', ': ')))


    ## utility functions
    #  generic snippts not customzied to this project

    def _mkdir(self, newdir):
        """works the way a good mkdir should :)
            - already exists, silently complete
            - regular file in the way, raise an exception
            - parent directory(ies) does not exist, make them as well
        """
        # http://code.activestate.com/recipes/82465-a-friendly-mkdir/
        if os.path.isdir(newdir):
            pass
        elif os.path.isfile(newdir):
            raise OSError("a file with the same name as the desired "
                          "dir, '%s', already exists." % newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head):
                self._mkdir(head)
            #print "_mkdir %s" % repr(newdir)
            if tail:
                os.mkdir(newdir)


## Module level function


def get_common_options(argparse_parser):
    """ common options for command line programs that use the library

        :param argvarse_parser: an argparse parser
        :returns: argparse parser parameter group
    """

    def is_valid_file(argparse_parser, arg):
        # http://stackoverflow.com/a/11541450/1763984
        if not os.path.exists(arg):
            argparse_parser.error("The file %s does not exist!" % arg)
        else:
            return open(arg, 'r')  # return an open file handle

    common_options = argparse_parser.add_argument_group(
        'common options for pynux commands')
    common_options.add_argument(
        '--loglevel',
        default=_loglevel_,
        help=''.join([
            "CRITICAL ERROR WARNING INFO DEBUG NOTSET, default is ", _loglevel_
        ]))
    common_options.add_argument(
        '--rcfile',
        default=None,
        help="path to ConfigParser compatible ini file",
        type=lambda x: is_valid_file(argparse_parser, x))
    return common_options


def test():
    """ Testing Docstring"""
    pass


if __name__ == '__main__':
    test()
"""
Copyright © 2017, Regents of the University of California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
- Neither the name of the University of California nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
