crowdflower
===========

Minimal client library for interacting with the
`CrowdFlower <http://www.crowdflower.com/>`__ API with Python.

Installation
------------

Install from PyPI:

::

    easy_install crowdflower

Or install the latest version GitHub:

::

    git clone https://github.com/chbrown/crowdflower.git
    cd crowdflower
    python setup.py develop

Example use
-----------

Import:

::

    import crowdflower

CrowdFlower API keys are 20 characters long; the one below is just
random characters.

::

    conn = crowdflower.Connection('LbcxvIlE3x1M8F6TT5hN')

This library will default to an environment variable called
``CROWDFLOWER_API_KEY`` if none is specified here:

::

    conn = crowdflower.Connection()

Loop through all your jobs and print the titles:

::

    for job in conn.jobs():
        print job['title']

Create a new job with some new units:

::

    job = conn.upload(data)
    print job

Fancy stuff
-----------

Run a bunch of DELETE calls on each item in the job.

::

    for delete_response in job.clear_units():
        print delete_response

If you don't want to print the responses, you still need to exhaust the
loop:

::

    list(job.clear_units())

References
----------

This package uses `kennethreitz <https://github.com/kennethreitz>`__'s
`Requests <http://docs.python-requests.org/en/latest/api/>`__ to
communicate with the CrowdFlower API over HTTP.

License
-------

Copyright © 2014 Christopher Brown. `MIT
Licensed <https://raw.github.com/chbrown/crowdflower/master/LICENSE>`__.
