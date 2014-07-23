#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from pynux import utils


def main(argv=None):

    parser = argparse.ArgumentParser(
        description='run import of a folder into nuxeo')
    utils.get_common_options(parser)
    required_flags = parser.add_argument_group('there are four required arguments')
    required_flags.add_argument('--leaf_type', 
        help="nuxeo document type for imported leaf nodes", 
        required=True)
    required_flags.add_argument('--input_path',
        help="unix path to files",
        required=True)
    required_flags.add_argument('--target_path', 
        help="target document for import in nuxeo (parent folder where new folder will be created)",
        required=True)
    required_flags.add_argument('--folderish_type',
        help="nuxeo document type for imported folder",
        required=True)
    parser.add_argument('--no_wait',
        help="don't poll/wait for the job to finish",
        dest="no_wait",
        action="store_false")
    parser.add_argument('--poll_interval',
        help="seconds to sleep for if waiting",
        dest="sleep",
        default=20,
        type=int)
    parser.add_argument('--skip_root_folder_creation',
        help="don't create root folder on import",
        dest="skip_root_folder_creation",
        action="store_true")
    if argv is None:
        argv = parser.parse_args()
    nx = utils.Nuxeo(rcfile=argv.rcfile, loglevel=argv.loglevel.upper())
    print nx.import_log_activate()
    print nx.import_one_folder(argv.leaf_type,
        argv.input_path,
        argv.target_path,
        argv.folderish_type,
        wait=argv.no_wait,
        sleep=argv.sleep,
        skip_root_folder_creation=argv.skip_root_folder_creation)
    print nx.call_file_importer_api('status')
    print nx.import_log()


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
