pynux
=====

[![Build Status](https://travis-ci.org/ucldc/pynux.png?branch=master)](https://travis-ci.org/ucldc/pynux)

python function library for working with nuxeo "REST" APIs.

## Requirements

### REST API

 * [docs.nuxeo.com](http://doc.nuxeo.com/display/public/NXDOC/REST+API) 
 * [marketplace](https://connect.nuxeo.com/nuxeo/site/marketplace/package/nuxeo-rest-api)
 * `nuxeoctl mp-install nuxeo-rest-api`
 * [api viewer](http://doc.nuxeo.com/display/public/NXDOC/Resources+Endpoints)

### Bulk document importer

 * [docs.nuxeo.com](http://doc.nuxeo.com/display/public/ADMINDOC/Bulk+Document+Importer) 
 * [marketplace](https://connect.nuxeo.com/nuxeo/site/marketplace/package/nuxeo-platform-importer)
 * `nuxeoctl mp-install nuxeo-platform-importer`

## Example

### Library

```python
from pynux import utils
nx = utils.Nuxeo()

nx.nxql('SELECT * from Documents');
nx.all()
nx.children("asset-library")
uid = nx.get_uid("asset-library")
nx.get_metadata(uid=uid)
nx.get_metadata(path="asset-library")
```

### Commands

```
nxls [-h] [--outdir OUTDIR] path
nxql [-h] [--outdir OUTDIR] nxql
nxup1 [-h] [--uid UID | --path PATH] file
pifolder [-h] --leaf_type LEAF_TYPE --input_path INPUT_PATH
         --target_path TARGET_PATH --folderish_type FOLDERISH_TYPE
         [--no_wait] [--poll_interval SLEEP]
pistatus [-h]
pilog [-h] [--activate]
```

### config

The following is the default configuration:

```ini
[nuxeo_account]
user = Administrator
password = Administrator

[rest_api]
base = http://localhost:8080/nuxeo/site/api/v1

[platform_importer]
base = http://localhost:8080/nuxeo/site/fileImporter
```

Defaults can be overridden by setting then in `~/.pynuxrc` or `./.pynuyxrc`.  Please `chmod 600 .pynuxrc`.

# License 

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
