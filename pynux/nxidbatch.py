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
        description='nxidbatch mints a batch of ARKs')

    parser.add_argument(
        'batchsize', nargs=1, help='size of ARK batch', type=int)

    ezid_group = parser.add_argument_group('minting behaviour flags')
    ezid_group.add_argument(
        '--mint', '-m', action='store_true', help='mint ARKs without prompt')
    ezid_group.add_argument(
        '--output',
        '-o',
        type=lambda x: is_valid_file(parser, x),
        required=True)

    conf_group = parser.add_argument_group('EZID configuration and metadata')
    conf_group.add_argument(
        '--ezid-username',
        help='username for EZID API (overrides rcfile)',
        type=utf8_arg)
    conf_group.add_argument(
        '--ezid-password',
        help='password for EZID API (overrides rc file)',
        type=utf8_arg)
    conf_group.add_argument(
        '--shoulder', help='shoulder (overrides rcfile)', type=utf8_arg)
    conf_group.add_argument(
        '--owner', help='set as _owner for EZID', type=utf8_arg)
    conf_group.add_argument(
        '--status',
        help=
        'set as _status for EZID (default reserved, or public|unavailable)',
        default="reserved",
        type=utf8_arg)
    conf_group.add_argument(
        '--publisher', help='set as dc.publisher for EZID', type=utf8_arg)

    utils.get_common_options(parser)
    if argv is None:
        argv = parser.parse_args()

    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())

    # read config out of .pynuxrc file
    username = argv.ezid_username or nx.ezid_conf['username']
    password = argv.ezid_password or nx.ezid_conf['password']
    shoulder = argv.shoulder or nx.ezid_conf['shoulder']
    ezid = EZID.EZIDClient(credentials=dict(
        username=username, password=password))

    if argv.mint:
        output = open(argv.output, 'w')
    else:
        # https://stackoverflow.com/a/26514097/1763984
        answer = raw_input(
            'Mint a batch {} of {} ARKs with prefix {} with EZID? [y/n]'.
            format(argv.output, argv.batchsize, shoulder))
        if not answer or answer[0].lower() != 'y':
            print('You did not indicate approval')
            exit(1)
        else:
            output = open(argv.output, 'w')

    for __ in range(argv.batchsize[0]):

        # mint
        new_ark = ezid.mint(shoulder)
        print(new_ark, file=output)

    if not (argv.mint):
        print('done')


def is_valid_file(parser, arg):
    # don't want to overwrite a file that exists
    # reverses the logic of https://stackoverflow.com/a/11541450/1763984
    if os.path.exists(arg):
        parser.error(
            "The file %s already exists, please pick a new name." % arg)
    else:
        return arg


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
