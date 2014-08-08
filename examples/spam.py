import os
import crowdflower

# expects api key to be available in your environment variables; does not use cache
conn = crowdflower.Connection()
job_tag = 'python-example'


def _find_job():
    for job in conn.jobs():
        if job_tag in job.tags:
            return job

def create():
    filename = os.path.join(crowdflower.root, 'examples', 'spam.txt')

    def iter_data(labels=None):
        for i, line in enumerate(open(filename), 1):
            label, text = line.strip().split('\t', 1)
            if labels is None or label in labels:
                # the "text" key is the only required field; the others just help us
                # keep track of what's been annotated and mark which are the test data
                yield {'id': '{}:{}'.format(filename, i), 'text': text, 'label': label}

    # we want to balance ham vs. spam, artificially, for the example
    ham_data = list(iter_data(labels=['ham']))
    spam_data = list(iter_data(labels=['spam']))

    # for gold data, get 25 of each class
    gold_data = ham_data[:25] + spam_data[:25]
    # add the spam_gold key (to trigger)
    for datum in gold_data:
        datum['spam_gold'] = datum['label']

    # for real data, get 100 of each class, and rename the special 'spam_gold' field
    test_data = ham_data[25:][:100] + spam_data[25:][:100]

    job = conn.upload(gold_data + test_data)
    print 'Uploaded %d gold data, %d test data' % (len(gold_data), len(test_data))

    job.update({
        'title': 'Spam detection',
        'max_judgments_per_worker': 50,
        'units_per_assignment': 10,
        'judgments_per_unit': 2,
        'payment_cents': 10,
        'instructions': '''
            <h3>Spam detection</h3>
            <p>Judge whether these text messages are spam or not.</p>
        ''',
        'cml': '''
            {{text}}
            <cml:radios label="spam" validates="required" gold="true">
                <cml:radio label="Spam" value="spam"></cml:radio>
                <cml:radio label="Not spam" value="ham"></cml:radio>
            </cml:radios>
        ''',
        'options': {
            'front_load': 1, # quiz mode = 1; turn off with 0
        }
    })
    print 'Updated job'

    # add the 'python-example' tag so that we can easily find this job later
    job.tags = [job_tag]
    print 'Tagged job as %r' % job_tag

    # because we used the standard _gold postfix for this field,
    # the second argument is actually unecessary
    job.gold_add('spam', 'spam_gold')
    print 'Designated gold data'


def launch():
    job = _find_job()
    job.launch(200)
    print 'Launched Job[%d]' % job.id


def delete():
    job = _find_job()
    print 'Deleting Job[%d]' % job.id
    job.delete()


if __name__ == '__main__':
    import sys
    methods = locals()
    for arg in sys.argv[1:]:
        print arg, '...'
        methods[arg]()
