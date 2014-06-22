import os
import json
from crowdflower.exception import CrowdFlowerError, CrowdFlowerJSONError
from requests import Request, Session
from grequests import AsyncRequest

# from crowdflower import logger
from crowdflower.job import Job


def merge(*dicts):
    return dict((key, value) for d in dicts if d for key, value in d.items())


class Connection(object):
    DEFAULT_API_KEY = os.getenv('CROWDFLOWER_API_KEY')
    DEFAULT_API_URL = 'https://api.crowdflower.com/v1'

    def __init__(self, api_key=DEFAULT_API_KEY, api_url=DEFAULT_API_URL):
        self.api_key = api_key
        self.api_url = api_url

        self._session = Session()
        self._session.params['key'] = self.api_key
        self._session.verify = False


    def __repr__(self):
        return '<{:} using {:} with key {:}...>'.format(self.__class__.__name__, self.api_url, self.api_key[:6])


    def create_request(self, path, method='GET', **kw):
        url = self.api_url + path
        return Request(method=method, url=url, **kw)

    def send_request(self, req):
        '''
        returns requests.Response object

        raise
        '''
        # requests gotcha: even if send through the session, request.prepare()
        # does not get merged with the session's attributes, so we have to call
        # session.prepare_request(...)
        prepared_req = self._session.prepare_request(req)
        res = self._session.send(prepared_req)
        if res.status_code != 200:
            # CrowdFlower responds with a '202 Accepted' when we request a bulk
            # download which has not yet been generated, which means we simply
            # have to wait and try again
            raise CrowdFlowerError(req, res)
        return res

    def request(self, path, method='GET', params=None, headers=None, data=None):
        # simple request helper
        if headers is None:
            headers = dict()
        headers.update(Accept='application/json')
        req = self.create_request(path, method=method, params=params, headers=headers, data=data)
        res = self.send_request(req)
        try:
            # what Requests might actually raise is a simplejson.scanner.JSONDecodeError,
            # but I'm pretty sure that's the only error .json() might raise, so we don't
            # to type-match it.
            return res.json()
        except Exception, err:
            raise CrowdFlowerJSONError(req, res, err)

    # def grequest(self, path, method='GET', params=None, data=None, headers=None):
    #     method, url, kwargs = self._prepare_request(path, method, params, data, headers)
    #     return AsyncRequest(method, url, **kwargs)

    def job(self, job_id):
        # lazy; doesn't actually call anything
        return Job(job_id, self)

    def jobs(self):
        for job_response in self.request('/jobs').json():
            job = Job(job_response['id'], self)
            # populate the Job's properties, since we have all the data anyway
            job._properties = job_response
            yield job

    def upload(self, units):
        '''
        TODO: allow setting Job parameters at the same time
        '''
        headers = {'Content-Type': 'application/json'}
        # N.b.: CF expects newline-separated JSON, not actual JSON
        # e.g., this would fail with a status 500: kwargs['data'] = json.dumps(data)
        data = '\n'.join(json.dumps(unit) for unit in units)

        job_response = self.request('/jobs/upload', method='POST', headers=headers, data=data)
        job = Job(job_response['id'], self)
        job._properties = job_response
        return job
