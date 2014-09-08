## crowdflower - a Python client for the CrowdFlower API

We on the engineering team at People Pattern use open source software <i>all the time</i>, like software engineers almost anywhere. We are committed to [giving](https://github.com/scalanlp/nak/commits?author=jasonbaldridge) [back](https://github.com/n8han/giter8/pull/140) [to](https://github.com/twitter/finatra/pull/156) [the](https://github.com/ansible/ansible/pull/7824) open source community.
Thus far, these contributions have been bugfixes, documentation improvements, etc.—good stuff—but today we are announcing the first full project we have open sourced: a Python client for the [CrowdFlower API](http://success.crowdflower.com/customer/portal/articles/1288323-api-documentation), called, simply, "[crowdflower](https://github.com/peoplepattern/crowdflower)."

[CrowdFlower](http://www.crowdflower.com/) is a crowdsourcing platform, similar to [Mechanical Turk](http://www.peoplepattern.com/mechanical-turk/), but at PeoplePattern we work with a lot of different languages, and found that CrowdFlower's more widely distributed workforce is a better fit for some of our crowd-workable tasks.

CrowdFlower provides an official [Ruby client](https://github.com/CrowdFlower/ruby-crowdflower) (which makes sense; their app is Ruby-based), but it is not always kept up to date, and we're more of a Python / Scala shop on the back-end anyway. We use their API in a pipeline that samples the Twitter spritzer for current tweets and has them labeled in various ways, eventually pulling those labels back into our classifiers. All of this happens with minimal manual intervention, which wouldn't be possible without using their API.

## Getting started

For any of the following examples to work, you'll need a CrowdFlower account. As of August 2014, they no longer offer pay-as-you-go accounts, but you can [sign up for a free trial](https://make.crowdflower.com/users/new?redirect_url=https%3A%2F%2Fcrowdflower.com%2Fjobs&app=make). You'll need to grab your API key from [make.crowdflower.com/account/user](https://make.crowdflower.com/account/user), which will look something like `LbcxvIlE3x1M8F6TT5hN`.

The `crowdflower` package is on [PyPI](https://pypi.python.org/pypi/crowdflower), which makes installation super easy once you have Python installed on your machine. Simply run the following at your command line:

    easy_install crowdflower

(You may need to `sudo easy_install crowdflower` if you are using Mac OS X's built-in Python.) Or if you're more into [pip](http://pip.readthedocs.org/), you can use it instead:

    pip install crowdflower

Then, in a new Python session (I recommend [`IPython`](http://ipython.org/)– its tab-completion, combined with `crowdflower`'s liberal docstrings, makes the package a lot easier to explore) or Python source file, type the following:

    import crowdflower
    connection = crowdflower.Connection(api_key='LbcxvIlE3x1M8F6TT5hN')
    print 'Balance:', connection.account()['balance']
    for job in connection.jobs():
        print job.properties['title']

That will print out your account balance and the titles of all your current jobs. If you haven't done anything with your new CrowdFlower account, you'll have a $0.00 balance and no jobs. Let's fix that.

## Full example

First, add at least $10 to your CrowdFlower account. The following task was $6.65 when I ran it, and shouldn't be too far off that when you run it.

Second, you'll need to clone the source repository; the example code is part of the same repository, but is not part of the distributed, importable package.

    git clone https://github.com/peoplepattern/crowdflower.git

Everything you'll need is now in the `examples/` directory.

    cd examples/

We'll be using a [SMS (text messaging) dataset](http://www.dt.fee.unicamp.br/~tiago/smsspamcollection/) that we want to label as "spam" / "not-spam". This dataset is completely labeled, which makes it possible to evaluate the annotations we get back from CrowdFlower, but this means that the task, in itself, is not very useful. You're welcome to incorporate your own incoming text messages; if you're a Mac person and sync your iPhone with local backups, you can grab these pretty easily with the following:

    sqlite3 ~/Library/"Application Support"/MobileSync/Backup/*/3d0d7e5fb2ce288813306e4d4636395e047a3d28 'SELECT text FROM message WHERE is_from_me = 0' | awk '{print "?\t" $0}'

However, for the purposes of this example, I will assume that you are just using the `spam.txt` file without any additions.

The example code ([`spam.py`](https://github.com/peoplepattern/crowdflower/blob/master/examples/spam.py)) assumes that your API key is accessible in the `CROWDFLOWER_API_KEY` environmental variable. So in the shell session that you use to run the commands below, you'll first need to type:

    export CROWDFLOWER_API_KEY=LbcxvIlE3x1M8F6TT5hN

The next command will create the job, using a portion of [`spam.txt`](https://github.com/peoplepattern/crowdflower/blob/master/examples/spam.txt), add the "python-example" tag, and mark some of the data as test questions.

    python spam.py create

You can now preview the job in the CrowdFlower website interface now, and even make modifications to it if you want. If your modifications don't dramatically change the structure of the job, the rest of the steps should still work.
All of the rest of the commands find the job you just created by searching for jobs with the "python-example" tag, so be sure that you leave that tag in place.

However, it's not running yet; you'll need to launch it:

    python spam.py launch

It will take a moment to finish. You can check the status of the job (it's done when `needed_judgments` is 0) with the following command:

    python spam.py ping

Once it's all done, you can cross-tabulate the results:

    python spam.py results | cut -d$'\t' -f 1-2 | sort | uniq -c

And download the full dataset:

    python spam.py download > spam.json

I have removed the `_worker_id` fields from the [`spam.json`](https://github.com/peoplepattern/crowdflower/blob/master/examples/spam.json) file included in this repository, but otherwise that file was built using the above process.

And after getting all the responses and downloading the results, you can delete the job (though you certainly don't have to):

    python spam.py delete

Now that you know what the basic steps are, you can refer to the [`spam.py`](https://github.com/peoplepattern/crowdflower/blob/master/examples/spam.py) source file as a template for how to create and launch your own job, and then download the results.


## Community

We love open source and working with the larger community to make our codebase even better! If you have any contributions, please fork the repository and send us a pull request through GitHub. For more details and instructions on filing issues, refer to the repository [README](https://github.com/peoplepattern/crowdflower).

The `crowdflower` source code is Copyright 2014 People Pattern Corporation and [licensed](https://github.com/peoplepattern/crowdflower/blob/master/LICENSE) under the Apache License, Version 2.0.
