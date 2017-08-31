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
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        'path', nargs=1, help='nuxeo document path', type=utf8_arg)

    ezid_group = parser.add_argument_group('minting behaviour')

    ezid_group.add_argument(
        '--no-noop-report',
        action='store_true',
        help='override default behaviour of reporting on noops')
    ezid_group.add_argument(
        '--mint',
        action='store_true',
        help='when an ARK is missing, mint and bind new ARK in EZID')
    ezid_group.add_argument(
        '--create',
        action='store_true',
        help='when an ARK is found in Nuxeo but not EZID, create EZID')
    ezid_group.add_argument(
        '--update',
        action='store_true',
        help='when an ARK is found in Nuxeo and EZID, update EZID')

    conf_group = parser.add_argument_group('EZID configuration')

    conf_group.add_argument(
        '--shoulder', help='alternative shoulder to the one in the rcfile')

    conf_group.add_argument(
        '--owner', help='set as _owner for EZID')

    conf_group.add_argument(
        '--ezid-username', help='username for EZID API')

    conf_group.add_argument(
        '--ezid-password', help='password for EZID API')

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()


    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())

    # read config out of .pynuxrc file
    username = nx.ezid_conf['username']
    password = nx.ezid_conf['password']
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

        # mint
        if not(ark) and not(ezid_status):
            if argv.mint:
                print(EZID.formatAnvlFromDict(item_erc_dict(item, argv.owner)))
                new_ark = ezid.mint(shoulder, item_erc_dict(item, argv.owner))
                update_nuxeo(item, nx, new_ark)
                print('✓ minted "{}" {}'.format(path, new_ark))
            elif report:
                print('ℹ mint "{}"'.format(path))

        # create
        if ark and not(ezid_status):
            if argv.create:
                # ezid.create()
                print('going to create')
            elif report:
                print('ℹ create "{}" {}'.format(path, ark))

        # update
        if ark and ezid_status:
            owner = get_owner(ezid_status)
            if argv.update:
                # ezid.update()
                print('going to update')
            elif report:
                print('ℹ update "{}" {} {}'.format(path, ark, owner))



def get_owner(erc):
    delim = '_owner:'
    s = StringIO.StringIO(erc)
    for line in s:
       if line.startswith(delim):
           return line.partition(delim)[2].strip()
    return None


def check_ezid(ark, ezid):
    ''' check to see if the ARK is listed in EZID, returns raw ERC or `None`'''
    try:
        sys.stdout = open(os.devnull, 'w')
        ret = ezid.view(ark)
    except HTTPError:
        sys.stdout = sys.__stdout__
        return None

    sys.stdout = sys.__stdout__
    return ret

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


def item_erc_dict(item, owner):
    ''' create erc dict for item, don't set the target untill it is published '''
    # metadata mapping from nuxeo to ERC
    p = item['properties']
    title = p.get('dc:title', '(:unav)')
    type_ = p.get('dc:type', '(:unav)')
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

    ezdata = {
        '_profile': 'dc',
        'dc.title': title,
        'dc.creator': creator,
        'dc.publisher': '',
        'dc.type': type_,
    }

    if owner:
        ezdata.update({'_owner': owner})

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
