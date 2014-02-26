#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""update nuxeo"""
import sys
import argparse
import json
from pynux import utils
from pprint import pprint as pp


def main(argv=None):
    """main"""
    parser = argparse.ArgumentParser(
        description='nuxeo metadata via REST API, one record'
    )
    parser.add_argument('file', nargs=1, help="application/json+nxentity")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--uid', help="update specific nuxeo uid")
    group.add_argument('--path', help="update specific nuxeo path")

    if argv is None:
        argv = parser.parse_args()

    # todo; add these defaults as parameters as well as env
    nx = utils.Nuxeo()
    pp(argv.file[0])
    jfile = argv.file[0]
    uid = argv.uid
    path = argv.path
    json_data = open(jfile)
    data = json.load(json_data)
    ret = {}
    if uid:				# use uid supplied at command line
        ret = nx.update_nuxeo_properties(data, uid=uid)
    elif path:				# use path supplied at command line
        ret = nx.update_nuxeo_properties(data, path=path)
    # if no uid nor path was specified on the command line, then
    # prefer "path": to "uid": when importing files because the file may have
    # come from another machine where the uuids are different
    else:
        uid = nx.get_uid(data.get('path')) or data.get('uid')
        ret = nx.update_nuxeo_properties(data, uid=uid)
    if not ret:
        print "no uid found, specify --uid or --path"
        exit(1)
    pp(ret)


# main() idiom for importing into REPL for debugging
if __name__ == "__main__":
    sys.exit(main())

"""
Copyright © 2014, Regents of the University of California
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
