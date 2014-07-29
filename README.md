# crowdflower

Client library for interacting with the [CrowdFlower](http://www.crowdflower.com/) [API](http://success.crowdflower.com/customer/portal/articles/1288323-api-documentation) with Python.


## Installation

Install from PyPI:

    easy_install -U crowdflower

Or install the latest version GitHub:

    git clone https://github.com/chbrown/crowdflower.git
    cd crowdflower
    python setup.py develop


## Import examples

Import:

    import crowdflower

CrowdFlower API keys are 20 characters long; the one below is just random characters.

    conn = crowdflower.Connection('LbcxvIlE3x1M8F6TT5hN')

The library will default to an environment variable called `CROWDFLOWER_API_KEY` if
none is specified here:

    conn = crowdflower.Connection()

If you want to cache job responses, like judgments, properties, and tags, you
can initialize the connection with a cache. `cache='filesystem'` is the only
option currently supported, and serializes JSON files to `/tmp/crowdflower/*`.

    conn = crowdflower.Connection(cache='filesystem')


## More examples

Loop through all your jobs and print the titles:

    for job in conn.jobs():
        print job.properties['title']

Create a new job with some new units:

    data = [
        {'id': '1', 'name': 'Chris Narenz', 'gender_gold': 'male'},
        {'id': '2', 'name': 'George Henckels'},
        {'id': '3', 'name': 'Maisy Ester'},
    ]
    job = conn.upload(data)
    job.update({
        'title': 'Gender labels',
        'included_countries': ['US', 'GB'],  # Limit to the USA and United Kingdom
        'payment_cents': 5,
        'judgments_per_unit': 2,
        'instructions': <some instructions html>,
        'cml': <some layout cml>,
        'options': {
            'front_load': 1, # quiz mode = 1; turn off with 0
        }
    })
    job.gold_add('gender', 'gender_gold')

    print job


## Motivation

The official [Ruby client](https://github.com/CrowdFlower/ruby-crowdflower) is hard to use, which is surprising, since the CrowdFlower API is so simple.

Which is not to say the [CrowdFlower API](http://success.crowdflower.com/customer/portal/articles/1288323-api-documentation) is all ponies and rainbows, but all the documentation is there on one page, and it does what it says, for the most part. (Though there's more that you can do, beyond what's documented.)

Thus, a thin Python client for the CrowdFlower API.


## References

This package uses [kennethreitz](https://github.com/kennethreitz)'s [Requests](http://docs.python-requests.org/en/latest/api/) to communicate with the CrowdFlower API over HTTP. Requests is [Apache2 licensed](http://docs.python-requests.org/en/latest/user/intro/#apache2-license).

* [The main API documentation page](http://success.crowdflower.com/customer/portal/articles/1288323)
* [More info on the API](http://success.crowdflower.com/customer/portal/articles/1327304-integrating-with-the-api)
* [Details on using API webhooks](http://success.crowdflower.com/customer/portal/articles/1373460-job-settings---api)


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
