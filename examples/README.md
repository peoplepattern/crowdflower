## Spam example

Create the job, using [`spam.txt`](spam.txt), add the "python-example" tag, and mark the test data.

    python spam.py create

Launch it:

    python spam.py launch

Check the status of the job (it's done when `needed_judgments` is 0):

    python spam.py ping

Cross-tabulate the results:

    python spam.py results | cut -d$'\t' -f 1-2 | sort | uniq -c

Download the full dataset:

    python spam.py download > spam.json

I have removed the `_worker_id` fields from the [`spam.json`](spam.json) file included in this repository, but otherwise that file was built using the above process.

And after getting all the responses and downloading the results, delete it:

    python spam.py delete
