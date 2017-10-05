# crowdflower

Client library for interacting with the [CrowdFlower](http://www.crowdflower.com/) [API](http://success.crowdflower.com/customer/portal/articles/1288323-api-documentation) with Python.


## Installation

Install from [PyPI](https://pypi.python.org/pypi/crowdflower) with [`setuptools`](https://setuptools.readthedocs.io/):

    easy_install -U crowdflower

Or with [`pip`](https://pip.pypa.io/):

    pip install -U crowdflower

Or install the latest (potentially unreleased and unstable) code from GitHub, using `pip`:

    git+https://github.com/twosigma/ngrid

Or build the source yourself, with `setuptools`:

    git clone https://github.com/peoplepattern/crowdflower.git
    cd crowdflower
    python setup.py develop


## Basic usage

Import like:

    import crowdflower

CrowdFlower API keys are 20 characters long; the one below is just random
characters. (You can find your API key at
[make.crowdflower.com/account/user](https://make.crowdflower.com/account/user).)

    conn = crowdflower.Connection(api_key='LbcxvIlE3x1M8F6TT5hN')

The library will default to an environment variable called `CROWDFLOWER_API_KEY` if
none is specified here:

    conn = crowdflower.Connection()

If you want to cache job responses, like judgments, properties, and tags, you
can initialize the connection with a cache. `cache='filesystem'` is the only
option currently supported, and serializes JSON files to `/tmp/crowdflower/*`.

    conn = crowdflower.Connection(cache='filesystem')


## Inspecting existing jobs

Loop through all your jobs and print the titles:

    for job in conn.jobs():
        print job.properties['title']


## Creating a new job

Create a new job with some new units:

    data = [
        {'id': '1', 'name': 'Chris Narenz', 'gender_gold': 'male'},
        {'id': '2', 'name': 'George Henckels'},
        {'id': '3', 'name': 'Maisy Ester'},
    ]
    job = conn.upload(data)
    update_result = job.update({
        'title': 'Gender labels',
        'included_countries': ['US', 'GB'],  # Limit to the USA and United Kingdom
            # Please note, if you are located in another country and you would like
            # to experiment with the sandbox (internal workers) then you also need
            # to add your own country. Otherwise your submissions as internal worker
            # will be rejected with Error 301 (low quality).
        'payment_cents': 5,
        'judgments_per_unit': 2,
        'instructions': 'some <i>instructions</i> html',
        'cml': 'some layout cml, e.g., '
            '<cml:text label="Sample text field:" validates="required" />',
        'options': {
            'front_load': 1, # quiz mode = 1; turn off with 0
        }
    })

    if 'errors' in update_result:
        print(update_result['errors'])
        exit()

    job.gold_add('gender', 'gender_gold')

Launch job for on-demand workers (the default):

    job.launch(2)

Launch job for internal workers (sandbox):

    job.launch(2, channels=['cf_internal'])

Check the status of the job:

    print job.ping()

Clean up; delete all the jobs that were created by the above example:

    for job in conn.jobs():
        if job.properties['title'] == 'Gender labels':
            print 'Deleting Job#%s' % job.id
            print job.delete()

View annotations collected so far:

    for row in job.download():
        print row


## Example

See the `README.md` in the [`examples/`](https://github.com/peoplepattern/crowdflower/tree/master/examples) directory for a full spam classification example using the freely available [SMS Spam Collection](http://www.dt.fee.unicamp.br/~tiago/smsspamcollection/).


## Debugging / Logging

To turn on verbose logging use the following in your script:

    import logging
    logging.basicConfig(level=logging.DEBUG)


## Motivation

The official [Ruby client](https://github.com/CrowdFlower/ruby-crowdflower) is hard to use, which is surprising, since the CrowdFlower API is so simple.

Which is not to say the [CrowdFlower API](http://success.crowdflower.com/customer/portal/articles/1288323-api-documentation) is all ponies and rainbows, but all the documentation is there on one page, and it does what it says, for the most part. (Though there's more that you can do, beyond what's documented.)

Thus, a thin Python client for the CrowdFlower API.


## References

The CrowdFlower blog is the definitive (but incomplete) source for API documentation:

* [The main API documentation page](http://success.crowdflower.com/customer/portal/articles/1288323) - Last Updated: Jul 31, 2014
* [More info on the API](http://success.crowdflower.com/customer/portal/articles/1327304-integrating-with-the-api) - Last Updated: Jul 31, 2014
* [Details on using API webhooks](http://success.crowdflower.com/customer/portal/articles/1373460-job-settings---api) - Last Updated: Jul 25, 2014
* [Rest API](http://success.crowdflower.com/customer/portal/articles/1549074) - Last Updated: Aug 11, 2014
* [API Request Examples](http://success.crowdflower.com/customer/portal/articles/1553902-curl-request-examples) - Last Updated: Aug 11, 2014
* [CML (CrowdFlower Markup Language)](http://success.crowdflower.com/customer/portal/articles/1290342-cml-crowdflower-markup-language) - Last Updated: Aug 12, 2014

The source code for the official [ruby-crowdflower](https://github.com/CrowdFlower/ruby-crowdflower) project is also helpful in some cases.

This package uses [kennethreitz](https://github.com/kennethreitz)'s [Requests](http://docs.python-requests.org/en/latest/api/) to communicate with the CrowdFlower API over HTTP. Requests is [Apache2 licensed](http://docs.python-requests.org/en/latest/user/intro/#apache2-license).


## Support

Found a bug? Want a new feature?
[File an issue](https://github.com/peoplepattern/crowdflower/issues/new)!


## Contributing

We love open source and working with the larger community to make our codebase even better! If you have any contributions, please fork this repository, commit your changes to a new branch, and then submit a pull request back to this repository (peoplepattern/crowdflower). To expedite merging your pull request, please follow the stylistic conventions already present in the repository. These include:

* Adhere to PEP8
  - We're not super strict on every single PEP8 convention, but we have a few hard requirements:
    + Four-space indentation
    + No tabs
    + No semicolons
    + No wildcard imports
* No trailing whitespace
* Use docstrings liberally

The Apache License 2.0 contains a clause covering the [Contributor License Agreement](http://www.apache.org/licenses/LICENSE-2.0.html#contributions).


## Authors

* [Christopher Brown](https://github.com/chbrown)


## License

Copyright 2014 People Pattern Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

> [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
