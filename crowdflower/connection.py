import os
import json
from crowdflower.exception import CrowdFlowerError, CrowdFlowerJSONError
from requests import Request, Session
# I regret that python-requests can't handle merging lists of params
from requests.utils import to_key_val_list

from crowdflower import logger
from crowdflower.job import Job
from crowdflower.cache import FilesystemCache, NoCache, cacheable, keyfunc


class Connection(object):
    DEFAULT_API_KEY = os.getenv('CROWDFLOWER_API_KEY')
    DEFAULT_API_URL = 'https://api.crowdflower.com/v1'
    _cache_key_attrs = ('api_key',)

    def __init__(self, cache=None, api_key=DEFAULT_API_KEY, api_url=DEFAULT_API_URL):
        self.api_key = api_key
        self.api_url = api_url

        if cache == 'filesystem':
            self._cache = FilesystemCache()
        # elif ... others?
        else:
            self._cache = NoCache()

        self._session = Session()
        # self._session.params['key'] = self.api_key
        # self._session.verify = False


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

        # merge params with the api key
        req.params = to_key_val_list(req.params) + [('key', self.api_key)]
        prepared_req = self._session.prepare_request(req)
        logger.debug('Request params: {}'.format(req.params))

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

    def job(self, job_id):
        # doesn't actually call anything
        return Job(job_id, self)

    @property
    @cacheable()
    def job_ids(self):
        '''
        The API documentation does not specify this, but there is a hard-coded
        limit=10 parameter on the /jobs endpoint, and no total count, so we must
        page through until we get a response with fewer than 10 items.

        Apparently, other parameters, like query='pt' and fields[]='tags' don't work.
        '''
        page = 0
        while True:
            page += 1
            params = dict(page=page)
            jobs_response = self.request('/jobs', params=params)
            for job_properties in jobs_response:
                # somehow add the Job's properties to the cache, since we have all the data anyway?
                yield job_properties['id']
            if len(jobs_response) < 10:
                break

    def jobs(self):
        '''
        This is separated from job_ids to aid in caching. They have no cause
        to be separate except to avoid marshaling issues when encoding/decoding.
        '''
        for job_id in self.job_ids:
            yield Job(job_id, self)

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
        # bust cache of job_ids
        self._cache.remove(keyfunc(self, 'job_ids'))
        return job

    def account(self):
        '''
        This is very short and simple, but it's not documented in the API.
        '''
        return self.request('/account')
