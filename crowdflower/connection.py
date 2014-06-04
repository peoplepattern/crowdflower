import os
import json
import requests
import grequests

import logging
from pprint import pformat

logger = logging.getLogger(__name__)


API_URL = 'https://api.crowdflower.com/v1'
API_KEY = os.getenv('CROWDFLOWER_API_KEY')


def merge(*dicts):
    return dict((key, value) for d in dicts if d for key, value in d.items())


class Connection(object):
    def __init__(self, api_key=API_KEY, api_url=API_URL):
        self.api_key = api_key
        self.api_url = api_url

    def _prepare_request(self, path, method, params, data, headers):
        url = self.api_url + path
        kwargs = dict(
            params=merge(params, dict(key=self.api_key)),
            headers=merge(headers, dict(Accept='application/json'))
        )
        if data:
            kwargs['headers']['Content-Type'] = 'application/json'
            # N.b.: CF expects newline-separated JSON, not actual JSON
            # e.g., this would fail with a status 500: kwargs['data'] = json.dumps(data)
            kwargs['data'] = '\n'.join(json.dumps(datum) for datum in data)
        return method, url, kwargs

    def request(self, path, method='GET', params=None, data=None, headers=None):
        method, url, kwargs = self._prepare_request(path, method, params, data, headers)
        response = requests.request(method, url, **kwargs)
        try:
            return response.json()
        # except simplejson.scanner.JSONDecodeError:
        except Exception:
            # should raise something like an APIException if JSON parse fails, but oh well
            return response.text

    def grequest(self, path, method='GET', params=None, data=None, headers=None):
        method, url, kwargs = self._prepare_request(path, method, params, data, headers)
        return grequests.request(method, url, **kwargs)

    def jobs(self):
        for job_response in self.request('/jobs').json():
            job = Job(job_response['id'], self)
            # populate the Job's properties, since we have all the data anyway
            job._properties = job_response
            yield job

    def job(self, job_id):
        return Job(job_id, self)

    def upload(self, data):
        '''
        TODO: allow setting Job parameters at the same time
        '''
        job_response = self.request('/jobs/upload', method='POST', data=data)
        job = Job(job_response['id'], self)
        job._properties = job_response
        return job


class Job(object):
    '''
    Read / Write attributes
        auto_order
        auto_order_threshold
        auto_order_timeout
        cml
        cml_fields
        confidence_fields
        css
        custom_key
        excluded_countries
        gold_per_assignment
        included_countries
        instructions
        js
        judgments_per_unit
        language
        max_judgments_per_unit
        max_judgments_per_contributor
        min_unit_confidence
        options
        pages_per_assignment
        problem
        send_judgments_webhook
        state
        title
        units_per_assignment
        webhook_uri

    Read-only attributes
        completed
        completed_at
        created_at
        gold
        golds_count
        id
        judgments_count
        units_count
        updated_at

    Not sure about:
        payment_cents

    '''
    READ_WRITE_FIELDS = ['auto_order', 'auto_order_threshold', 'auto_order_timeout', 'cml', 'cml_fields', 'confidence_fields', 'css', 'custom_key', 'excluded_countries', 'gold_per_assignment', 'included_countries', 'instructions', 'js', 'judgments_per_unit', 'language', 'max_judgments_per_unit', 'max_judgments_per_contributor', 'min_unit_confidence', 'options', 'pages_per_assignment', 'problem', 'send_judgments_webhook', 'state', 'title', 'units_per_assignment', 'webhook_uri']

    def __init__(self, job_id, connection):
        self.id = job_id
        self._connection = connection
        # cacheable:
        self._properties = {}
        self._units = {}

    def __json__(self):
        return self.properties

    def __repr__(self):
        return pformat(self.properties)

    @property
    def properties(self):
        if len(self._properties) == 0:
            self._properties = self._connection.request('/jobs/%s' % self.id)
        return self._properties

    @property
    def units(self):
        if len(self._units) == 0:
            self._units = self._connection.request('/jobs/%s/units' % self.id)
        return self._units

    def clear_units(self, parallel=20):
        reqs = (self._connection.grequest('/jobs/%s/units/%s' % (self.id, unit_id), method='DELETE')
            for unit_id in self.units.keys())
        for response in grequests.imap(reqs, size=parallel):
            yield response

    def upload(self, data):
        return self._connection.request('/jobs/%s/upload' % self.id, method='POST', data=data)

    def update(self, props):
        params = {'job[%s]' % key: value for key, value in props.items()}
        self._properties = {}
        return self._connection.request('/jobs/%s' % self.id, method='PUT', params=params)

    def delete(self):
        return self._connection.request('/jobs/%s' % self.id, method='DELETE')


class Unit(object):
    '''
    Read / Write attributes
        job_id
        missed_count
        difficulty
        state
        data
        agreement

    Read-only attributes
        updated_at
        created_at
        judgments_count
        id
    '''
