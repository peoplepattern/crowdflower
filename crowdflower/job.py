import csv
import json
import shutil
import zipfile
from pprint import pformat
from cStringIO import StringIO

from crowdflower import logger
from crowdflower.exception import CrowdFlowerError
from crowdflower.cache import cacheable, keyfunc
from crowdflower.serialization import rails_params


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
    _cache_key_attrs = ('id',)

    def __init__(self, job_id, connection):
        self.id = job_id
        self._connection = connection
        self._cache = self._connection._cache

    def __repr__(self):
        return pformat(self.properties)

    def _cache_flush(self, func_attr):
        self._cache.remove(keyfunc(self, func_attr))

    @property
    @cacheable()
    def properties(self):
        return self._connection.request('/jobs/%s' % self.id)


    @cacheable('tags')
    def get_tags(self):
        res = self._connection.request('/jobs/%s/tags' % self.id)
        return [item['name'] for item in res]

    def set_tags(self, tags):
        params = rails_params({'tags': tags})
        self._connection.request('/jobs/%s/tags' % self.id, method='PUT', params=params)
        self._cache_flush('tags')

    tags = property(get_tags, set_tags)

    def add_tags(self, tags):
        params = rails_params({'tags': tags})
        self._connection.request('/jobs/%s/tags' % self.id, method='POST', params=params)
        self._cache_flush('tags')


    @property
    @cacheable()
    def units(self):
        '''
        Returns a list of units, e.g.,

            [
                {
                    '_unit_id': '495781935',
                    'id': 'may25_1029',
                    'text': 'remember when I was in hospital for four months nd it was my birthday nd everyone forgot nd no one even came to visit me'
                },
                {
                    '_unit_id': '495781936',
                    'id': 'may25_1030',
                    'text': 'I had the wifi taken away and I can't have any friends over what a great Summer!'
                }
                ...
            ]

        N.b.: this is not the same format that CrowdFlower responds with, which is more like:

            {
                '495781935': {
                    'id': 'may25_1029',
                    'text': 'remember when I was in hospital for four months nd it was my birthday nd everyone forgot nd no one even came to visit me'
                },
                '495781936': {
                    'id': 'may25_1030',
                    'text': 'I had the wifi taken away and I can't have any friends over what a great Summer!'
                }
                ...
            }

        But since we are caching and de-paginating, it's better to return a list (by being an iterator)

        Neither `page` nor `limit` query parameters are documented, but they work as expected. Page numbering starts at 1, and the limit has a maximum of 1000 (which is also the default).

        The returned units are not fully hydrated; in fact, the response only includes each unit id and the original unit payload. To see the crowd's responses, you must use /jobs/{job.id}/units/{unit.id}, or the bulk download method (see Job.download()).

        '''
        page = 0
        while True:
            page += 1
            params = dict(page=page)
            units_response = self._connection.request('/jobs/%s/units' % self.id, params=params)
            for unit_id, unit_properties in units_response.items():
                # hopefully the user has not specified '_unit_id' as a custom field
                unit_properties['_unit_id'] = unit_id
                yield unit_properties
            if len(units_response) < 1000:
                break

    def delete_unit(self, unit_id):
        response = self._connection.request('/jobs/%s/units/%s' % (self.id, unit_id), method='DELETE')
        # bust cache if the request did not raise any errors
        self._cache_flush('units')
        return response

    def upload_unit(self, unit):
        '''
        Uploads a single unit to the job.
        '''
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({'unit': {'data': unit}})
        res = self._connection.request('/jobs/%s/units' % self.id, method='POST', headers=headers, data=data)

        # reset cached units
        self._cache_flush('units')

        return res

    def upload(self, units):
        headers = {'Content-Type': 'application/json'}
        data = '\n'.join(json.dumps(unit) for unit in units)
        logger.debug('Uploading data to Job[%d]: %s', self.id, data)
        res = self._connection.request('/jobs/%s/upload' % self.id, method='POST', headers=headers, data=data)

        # reset cached units
        self._cache_flush('units')

        return res

    def update(self, props):
        params = rails_params({'job': props})
        logger.debug('Updating Job[%d]: %r', self.id, params)

        try:
            res = self._connection.request('/jobs/%s' % self.id, method='PUT', params=params)
        except CrowdFlowerError, exc:
            # CrowdFlower sometimes likes to redirect the PUT to a non-API page,
            # which will raise an error (406 Not Accepted), but we can just
            # ignore the error since it comes after the update is complete.
            # This is kind of a hack, since we sometimes want to follow redirects
            # (e.g., with downloads), but following redirects is more properly
            # not the default
            if exc.response.status_code != 406:
                logger.info('Ignoring 406 "Not Accepted" error: %r', exc);
            else:
                raise

        # reset cached properties
        self._cache_flush('properties')

        return res

    def channels(self):
        '''
        Manual channel control is deprecated.

        The API documentation includes a PUT call at this endpoint, but I'm
        not sure if it actually does anything.
        '''
        return self._connection.request('/jobs/%s/channels' % self.id)

    def legend(self):
        '''
        From the CrowdFlower documentation:

        > The legend will show you the generated keys that will end up being
        > submitted with your form.
        '''
        return self._connection.request('/jobs/%s/legend' % self.id)

    def gold_reset(self):
        '''
        Mark all of this job's test questions (gold data) as NOT gold.

        Splitting the /jobs/:job_id/gold API call into gold_reset() and
        gold_add() is not faithful to the API, but resetting gold marks
        and adding them should not have the same API endpoint in the first place.
        '''
        params = dict(reset='true')
        res = self._connection.request('/jobs/%s/gold' % self.id, method='PUT', params=params)
        # reset cache
        self._cache_flush('properties')
        self._cache_flush('units')
        return res

    def gold_add(self, check, check_with=None):
        '''
        Configure the gold labels for a task.

        * check: the name of the field being checked against
            - Can call /jobs/{job_id}/legend to see options
            - And as far as I can tell, the job.properties['gold'] field is a
              hash with keys that are "check" names, and values that are "with" names.
        * check_with: the name of the field containing the gold label for check
            - Crowdflower calls this field "with", which is a Python keyword
            - defaults to check + '_gold'

        I'm not sure why convert_units would be anything but true.
        '''
        params = dict(check=check, convert_units='true')
        if check_with is not None:
            params['with'] = check_with
        res = self._connection.request('/jobs/%s/gold' % self.id, method='PUT', params=params)
        # reset cache
        self._cache_flush('properties')
        self._cache_flush('units')
        return res

    def launch(self, units_count, channels=('on_demand',)):
        '''
        `units_count` is the number of units to order
        `channels` should be some non-empty combination of 'cf_internal'
            (sandbox mode) and / or 'on_demand' (normal)
        '''
        channels = list(channels)
        data = rails_params(dict(channels=channels, debit=dict(units_count=units_count)))
        res = self._connection.request('/jobs/%s/orders' % self.id, method='POST', params=data)
        self._cache_flush('properties')
        return res

    def cancel(self):
        '''
        Cancel this job and refund your account for any judgments not yet received.
        '''
        res = self._connection.request('/jobs/%s/cancel' % self.id, method='PUT')
        self._cache_flush('properties')
        return res

    def ping(self):
        '''
        Determine the status of a job.

        Returns a data structure like this:
            {
                "all_units": 298,
                "golden_units": 239,
                "ordered_units": 49,
                "all_judgments": 168,
                "needed_judgments": 0,
                "tainted_judgments": 45,
                "completed_gold_estimate": 239,
                "completed_non_gold_estimate": 49,
                "completed_units_estimate": 288
            }
        '''
        return self._connection.request('/jobs/%s/ping' % self.id)

    def delete(self):
        '''
        Deletes the entire job permanently
        '''
        return self._connection.request('/jobs/%s' % self.id, method='DELETE')

    def copy(self, all_units=None, gold=None):
        '''
        Copy this job and return the new one.

        When all_units='true', copies the entire job (the gold argument is ignored).
        When gold='true', copies the job with only its test questions.
        When both gold and all_units are None, copies all the settings of the job, but without its rows.
        '''
        params = dict()
        if all_units is not None:
            params = {'all_units': all_units}
        elif gold is not None:
            params = {'gold': gold}
        response = self._connection.request('/jobs/%s/copy' % self.id, method='GET', params=params)
        return Job(response['id'], self._connection)

    def download(self, full=True):
        '''The resulting CSV will have headers like:

            _unit_id
                Integer
                Unique ID per unit
            _created_at
                Date: m/d/yyyy hh:mm:ss
            _golden
                Enum: "true" | "false"
            _canary
                Always empty, ???
            _id
                Integer
                Unique ID per judgment
            _missed
                ???
            _started_at
                Date: m/d/yyyy hh:mm:ss
                Can use
            _tainted
                Always false, ???
            _channel
                Enum: "neodev" | "clixsense" | [etc.]
            _trust
                Always 1, ???
            _worker_id
                Integer
                Unique ID per worker
            _country
                3-letter ISO code
            _region
                String
                A number for all countries except UK, USA, Canada (others?)
            _city
                String
                City name
            _ip
                String
                IPv4 address

        And then the rest just copies over whatever fields were originally used, e.g.:

            id
            text
            sentiment
            sentiment_gold
        '''
        # pulls down the csv endpoint, unzips it, and returns a list of all the rows
        params = dict(full='true' if full else 'false')
        # use .csv, not headers=dict(Accept='text/csv'), which Crowdflower rejects
        req = self._connection.create_request('/jobs/%s.csv' % self.id, method='GET', params=params)
        res = self._connection.send_request(req)
        # because ZipFile insists on seeking, we can't simply pass over the res.raw stream
        fp = StringIO()
        fp.write(res.content)
        # ZipFile does fp.seek(0) itself
        zf = zipfile.ZipFile(fp)
        for zipinfo in zf.filelist:
            zipinfo_fp = zf.open(zipinfo)
            reader = csv.DictReader(zipinfo_fp)
            for row in reader:
                yield {key: value.decode('utf8') for key, value in row.items()}

    @property
    @cacheable()
    def judgments(self):
        return self.download()

    def download_csv(self, filepath, report_type='full'):
        '''
        Basically the same as job.judgments but without parsing the CSV.

        The given 'report_type' determines the output format. From the
        documentation:

        * full: Returns the full report containing every judgment
        * aggregated: Returns the aggregate report containing the aggregated
          response for each row
        * json: Returns the JSON report containing the aggregated response, as
          well as the individual judgments, for each row

        The CrowdFlower API (as of 2015-05-13) also supports the following
        undocumented 'report_type' values:

        * source
        * workset

        References:
        * https://success.crowdflower.com/hc/en-us/articles/202703425-CrowdFlower-API-Requests-Guide#get_results
        '''
        params = {}
        if report_type is not None:
            params['type'] = report_type
        # even type=json uses the .csv extension. I guess because JSON's values
        # are at least partly separated by commas?
        req = self._connection.create_request('/jobs/%s.csv' % self.id, method='GET', params=params)
        res = self._connection.send_request(req)
        fp = StringIO()
        fp.write(res.content)
        zf = zipfile.ZipFile(fp)
        zipinfo = zf.filelist[0]
        fsrc = zf.open(zipinfo)
        with open(filepath, 'w') as fdst:
            shutil.copyfileobj(fsrc, fdst)

    def regenerate(self, report_type='full'):
        '''
        Triggers regeneration of a report on the CrowdFlower servers.

        This will most likely return before regeneration is complete. Depending
        on the size of your job's results, you may need to wait a bit before
        downloading the CSV will succeed.

        :param report_type: any valid report_type that can be passed to
        download_csv, e.g., 'full', 'aggregated', 'source', etc.
        '''
        params = {}
        if report_type is not None:
            params['type'] = report_type
        req = self._connection.create_request('/jobs/%s/regenerate' % self.id, method='POST', params=params)
        self._connection.send_request(req)
