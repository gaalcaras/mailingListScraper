# Mailing List Scraper

**mailingListScraper** is a tool to extract data from public email lists in a format suitable for data analysis.

For now, this scraper only supports the Linux Kernel Mailing List, using this public archive : [http://lkml.iu.edu/hypermail/linux/kernel/](http://lkml.iu.edu/hypermail/linux/kernel/).

[![Build Status](https://travis-ci.org/gaalcaras/mailingListScraper.svg?branch=master)](https://travis-ci.org/gaalcaras/mailingListScraper)

## Introduction

I am currently developing this scraper to collect data for my PhD ([EHESS](http://ehess.fr/) in Paris, France). If you do see problems with the code, I'll be glad to review your Pull Requests ;-)

If you're interested in using this scraper for your own project, I strongly recommend that you identify yourself in the *user-agent* (`mailingListScraper/settings.py`) so that people can contact you if needed.
Also, be mindful of the potential impact of your scraper on the server's load.


## Set up

Make sure to install [scrapy](https://doc.scrapy.org/en/latest/intro/install.html) and the dependencies first.

```
pip install scrapy python-dateutil
```

Clone the repo and `cd` into it. You're done!

## Quick guide

You can launch a specific spider running this command at the root level of the repo:

```
scrapy crawl hypermail
```

The spider stores extracted emails in a `data` folder, containing:

+ `hypermailByEmail.csv`: all metadata collected is stored in this file, with each row corresponding to an email.
+ `hypermail/*`: a folder containing the content of the emails.
  Each email body is stored in a single `html` file.
  The file is named after its unique id, which is the timestamp for received time (like `20161017142556` for "received on 2016-10-17 at 14:25:56").
  If two or more emails were received at the same time, we append a 0 (or more) at the end of the timestamp.

## Development and testing

This scraper is developed in Python 3.5.2 with the [scrapy](https://doc.scrapy.org/en/latest/) framework.

You can run the `scrapy check` command to run simple tests, with the built-in [Scrapy contracts](https://doc.scrapy.org/en/latest/topics/contracts.html).

While contracts are fine for small verifications, they are not enough: you need to make sure that the data collected is consistent with your expectations.
That's why some basic unit testing is provided in `mailingListScraper/tests`.
Each spider and pipeline is to be tested with "real world" test cases.

The data for these test cases is provided in the `pages` directory.
Test cases consist of three files:

+ `emailId.html`: this is the page used as a Scrapy response to test the methods of the spider.
+ `emailId.json`: this is the data you expect to get from the spider.
  You can test the items extracted after they've been processed by the ItemLoader (`itemOutput`) and after they've been processed by the pipelines (`pipelineOutput`).
+ `emailId.txt`: that is the body you expect to retrieve from the page.

Each time you test a spider, it will iterate through a certain number of test cases.
You can test a specific spider running this command at the root level of the repo:

```
python -m unittest mailingListScraper.tests.hypermail
```

## Privacy

The data is already publicly available online ; I am merely organizing it in a form that is convenient for data analysis.
For instance, I cannot collect email addresses if the email archive hides it.

But when data *is* available and adds valuable information to the dataset, I *will* collect it.
If your email address is not hidden, I do extract it to improve my chances of following an individual user over the years.
Specifically, the same user might change her name but not her email address or the other way around.
Collecting both the name and the email increases the probability of attributing these emails to the same person.

Keep in mind that I will only use the data collected with this scraper for research.
In general, I will never use this data for spamming or targetting users with ads.

If you think I might have collected some of your emails on these public lists, feel free to contact me ([@gaalcaras](https://github.com/gaalcaras)) if you have any questions or requests regarding your personal data.
