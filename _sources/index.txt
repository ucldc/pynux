.. pynux documentation master file, created by
   sphinx-quickstart on Thu Mar  6 18:38:10 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pynux documentation
===================

`code on github
<https://github.com/ucldc/pynux>`_

`README and LICENSE
<https://github.com/ucldc/pynux/blob/master/README.md>`_

`for use with Nuxeo Platform 5.8
<http://www.nuxeo.com/en/products/nuxeo-platform-5.8>`_


Rest API Commands
-----------------
``
`nuxeo-rest-api
<http://doc.nuxeo.com/display/public/NXDOC/REST+API>`_
``
just a small part of this API is implimented in ``pynux``.


listing commands
~~~~~~~~~~~~~~~~

These commands list documents in nuxeo. 

By default ``uid`` and ``path`` with be printed on standard out.

Specifing an ``--outdir`` parameter with a directory name will cause a
JSON dump of the list to be output, with one ``.json`` file per 
document.  **TODO:** what if a document path contains ``.json``?  Should 
outdir use uids for file names?

nxls
````
.. program-output:: nxls -h

nxql
````
.. program-output:: nxql -h

nxql_all
````````
``SELECT * FROM Documents``

Does not support ``--outdir``

.. program-output:: nxql_all -h

update command
~~~~~~~~~~~~~~

nxup1
`````

update one nuxeo document from a ``.json`` input file.

if no uid nor path was specified on the command line, then look in the 
JSON file and prefer
``"path":`` to ``"uid":`` when because the JSON file may have
come from another machine where the uuids are different.  If no
documentid is found it exits with an error.

Nuxeo JSON output is returned on standard out.  Nuxeo returns the
JSON of the updated document.  (**TODO** I guess nxup1 could check the
returned JSON and make sure it looks like the update was a-okay.)

.. program-output:: nxup1 -h

Platform (bulk) importer commands
---------------------------------

`nuxeo-platform-importer
<https://connect.nuxeo.com/nuxeo/site/marketplace/package/nuxeo-platform-importer>`_

pilog
~~~~~
init and set up logging.

.. program-output:: pilog -h

pistatus
~~~~~~~~
check if an import is running.  Don't run more than one job at once!
Will return HTTP result from nuxeo on standard out which will either
be ``Running`` or ``Not Running``.

.. program-output:: pistatus -h

pifolder
~~~~~~~~

Trigger ``/run`` of bulk importer.  By default, it won't exit until
the async loading is finished, so that it can be used from a batch
script.

.. program-output:: pifolder -h

Library
-------

.. automodule:: pynux.utils

.. autoclass:: pynux.utils.Nuxeo
   :members:
   :private-members:

.. autofunction:: pynux.utils.get_common_options
