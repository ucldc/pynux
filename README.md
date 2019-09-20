pynux
=====

[![Build Status](https://travis-ci.org/ucldc/pynux.png?branch=master)](https://travis-ci.org/ucldc/pynux)

python function library for working with nuxeo "REST" APIs.

## Install / Upgrade

latest release

```
pip install https://github.com/ucldc/pynux/tarball/master --upgrade
```

its possible you might need a latter day `pip`

```
pip install --upgrade pip
```

```
pip install git+git://github.com/ucldc/pynux.git
```
or
```
git clone https://github.com/ucldc/pynux.git
cd pynux
python setup.py install
```

### test
```
python setup.py test
```

## [Command and API Documentation](http://ucldc.github.io/pynux/)

## Requirements

### [Nuxeo](http://www.nuxeo.com/)

### REST API

 * [docs.nuxeo.com](http://doc.nuxeo.com/display/public/NXDOC/REST+API) 
 * [marketplace](https://connect.nuxeo.com/nuxeo/site/marketplace/package/nuxeo-rest-api)
 * `nuxeoctl mp-install nuxeo-rest-api`
 * [api viewer](http://doc.nuxeo.com/display/public/NXDOC/Resources+Endpoints)


## Configuration

To configure pynux, you will need to create a file named `.pynuxrc`. You can use a simple text editor to create the file. In a Windows OS, the file should be placed in `C:\Users\Username\`. In a Mac OS, the file should be placed in `~/.pynuxrc` (open a terminal window and type `open .` for the correct location).   

It may be advisable to `chmod 600 .pynuxrc`.

The following is an example default configuration that can be copied-and-pasted into the `.pynuxrc` file:

```ini
[nuxeo_account]
user = Administrator
password = Administrator

[rest_api]
base = http://localhost:8080/nuxeo/site/api/v1
X-NXDocumentProperties = dublincore
# for developers on the UCLDC project; use
# X-NXDocumentProperties = dublincore,ucldc_schema,picture

[ezid]
host = https://ezid.cdlib.org/
username = 
password = 
shoulder = ark:/99999/fk4
```

alternative authentication
```ini
[nuxeo_account]
method = token
X-Authentication-Token = xxxxxxx
```

## Custom Function

```python
# foo.py
def nuxeo_mapper(docs, nx):
    for doc in x:
        print(doc)
        # can use `nx.`... to update the document
```

```
nxls.py / --show-custom-function foo
```

## License 

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
