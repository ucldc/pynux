#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import sys
import argparse
import os
import re
import StringIO
from urllib2 import HTTPError
import EZID
from pynux import utils
from pynux.utils import utf8_arg
from pprint import pprint as pp


# regular expression to match an ARK
ARK_RE = re.compile('(ark:/\d{5}\/[^/|\s]*)')


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='nxid finds top level objects in Nuxeo and syncs them up with EZID')

    parser.add_argument(
        'path', nargs=1, help='nuxeo path (folder or object)', type=utf8_arg)

    ezid_group = parser.add_argument_group('minting behaviour flags')
    ezid_group.add_argument(
        '--mint', '-m',
        action='store_true',
        help='when an ARK is missing, mint and bind new ARK in EZID')
    ezid_group.add_argument(
        '--create', '-c',
        action='store_true',
        help='when an ARK is found in Nuxeo but not EZID, create EZID')
    ezid_group.add_argument(
        '--update', '-u',
        action='store_true',
        help='when an ARK is found in Nuxeo and EZID, update EZID')
    ezid_group.add_argument(
        '--no-noop-report',
        action='store_true',
        help='override default behaviour of reporting on noops')
    ezid_group.add_argument(
        '--show-erc',
        action='store_true',
        help='show ANVL record that will be sent to EZID')

    conf_group = parser.add_argument_group('EZID configuration and metadata')
    conf_group.add_argument(
        '--ezid-username', help='username for EZID API (overrides rcfile)', type=utf8_arg)
    conf_group.add_argument(
        '--ezid-password', help='password for EZID API (overrides rc file)', type=utf8_arg)
    conf_group.add_argument(
        '--shoulder', help='shoulder (overrides rcfile)', type=utf8_arg)
    conf_group.add_argument(
        '--owner', help='set as _owner for EZID', type=utf8_arg)
    conf_group.add_argument(
        '--status', help='set as _status for EZID (public|reserved|unavailable)', type=utf8_arg)
    conf_group.add_argument(
        '--publisher', help='set as dc.publisher for EZID', type=utf8_arg)
    conf_group.add_argument(
        '--location', help='set location URL prefix for EZID', type=utf8_arg)

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()


    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())

    # read config out of .pynuxrc file
    username = argv.ezid_username or nx.ezid_conf['username']
    password = argv.ezid_password or nx.ezid_conf['password']
    shoulder = argv.shoulder or nx.ezid_conf['shoulder']
    ezid = EZID.EZIDClient(credentials=dict(username=username, password=password))

    # query to select all parent level objects
    documents = nx.nxql(u'''
SELECT * FROM SampleCustomPicture, CustomFile, CustomVideo, CustomAudio
WHERE ecm:path STARTSWITH "{}"
AND ecm:currentLifeCycleState != "deleted"
AND ecm:pos is NULL'''.format(argv.path[0]))

    # if the user gives the full path to a document
    if not any(True for _ in documents):  # https://stackoverflow.com/a/3114640/1763984
        documents = nx.nxql(u'''
SELECT * FROM SampleCustomPicture, CustomFile, CustomVideo, CustomAudio
WHERE ecm:path = "{}"
AND ecm:currentLifeCycleState != "deleted"
AND ecm:pos is NULL'''.format(argv.path[0]))

    report = not(argv.no_noop_report)

    # main loop
    for item in documents:
        # check id for ARK
        ark = find_ark(item['properties']['ucldc_schema:identifier'])
        path = item['path']

        # if there is an ARK, check for a record in EZID
        ezid_status = None
        if ark is not None:
            ezid_status = check_ezid(ark, ezid)

        ezdata = item_erc_dict(
            item,
            owner=argv.owner,            # _owner
            status=argv.status,          # _status
            publisher=argv.publisher,    # dc.publisher
            location=argv.location       # _target
        )

        if argv.show_erc:
            print(EZID.formatAnvlFromDict(ezdata))
            print('')

        # mint
        if not(ark) and not(ezid_status):
            if argv.mint:
                new_ark = ezid.mint(shoulder, ezdata)
                update_nuxeo(item, nx, new_ark)
                print('✓ mint "{}" {}'.format(path, new_ark))
            elif report:
                print('ℹ noop mint "{}"'.format(path))

        # create
        if ark and not(ezid_status):
            if argv.create:
                ezid.create(ark, ezdata)
                print('✓ create "{}" {}'.format(path, ark))
            elif report:
                print('ℹ noop create "{}" {}'.format(path, ark))

        # update
        if ark and ezid_status:
            owner = get_owner(ezid_status)
            if argv.update:
                ezid.update(ark, ezdata)
                print('✓ update "{}" {}'.format(path, ark))
            elif report:
                print('ℹ noop update "{}" {} {}'.format(path, ark, owner))


def get_owner(erc):
    delim = str('_owner:')
    s = StringIO.StringIO(erc)
    for line in s:
       if line.startswith(delim):
           return line.partition(delim)[2].strip()
    return None


def check_ezid(ark, ezid):
    ''' check to see if the ARK is listed in EZID, returns raw ERC or `None`'''
    try:
        sys.stdout = open(os.devnull, 'w')
        return ezid.view(ark)
    except HTTPError:
        return None
    finally:
        sys.stdout = sys.__stdout__


def find_ark(s):
    ''' fish an ARK from the identifier in Nuxeo, return the ARK or `None`'''
    if s:
        ark_test = ARK_RE.search(s)
        if ark_test:
            return ark_test.group(0)
        else:
            return None
    else:
        return None


def update_nuxeo(item, nx, ark):
    ''' update identifiers in Nuxeo '''
    identifier = item['properties'].get('ucldc_schema:identifier')
    new_localidentifier = item['properties']['ucldc_schema:localidentifier']
    # copy any non-ARK identifier to the local identifiers list
    if identifier:
        new_localidentifier.append(identifier)
    update_doc = { 'properties': {
                       'ucldc_schema:identifier': ark,
                       'ucldc_schema:localidentifier': new_localidentifier,
                 }, }
    pp(update_doc)
    nx.update_nuxeo_properties(update_doc, uid=item['uid'])


def item_erc_dict(item, owner=None, status=None, publisher=None, location=None):
    ''' create erc dict for item '''
    # metadata mapping from nuxeo to ERC
    p = item['properties']
    title = p.get('dc:title', '(:unav)')
    if title is None:
        title = '(:unav)'
    type_ = p.get('dc:type', '(:unav)')
    if type_ is None:
        type_ = '(:unav)'
    # repeating creator
    creator_list = p.get('ucldc_schema:creator')
    if creator_list:
        creator = '; '.join(list(str(c.get('name')) for c in creator_list))
    else:
        creator = '(:unav)'
    # just take the first date
    date_list = p.get('ucldc_schema:date')
    if date_list:
        date = date_list[0].get('date')
    else:
        date = '(:unav)'
    #set identifier variable again for use in setting _target
    identifier = p.get('ucldc_schema:identifier')

    ezdata = {
        '_profile': 'dc',
        'dc.title': title,
        'dc.creator': creator,
        'dc.type': type_,
        'dc.date': date,
    }

    if owner:
        ezdata.update({'_owner': owner})
    if status:
        ezdata.update({'_status': status})
    if publisher:
        ezdata.update({'dc.publisher': publisher})
    if location:
    	ezdata.update({'_target': location + identifier})

    return ezdata


# main() idiom for importing into REPL for debugging
if __name__ == "__main__":
    sys.exit(main())
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
