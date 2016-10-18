# Mailing List Scraper

**mailingListScraper** is a tool to extract data from public email lists in a format suitable for data analysis.

For now, this scraper only supports the Linux Kernel Mailing List, using this public archive : [http://lkml.iu.edu/hypermail/linux/kernel/](http://lkml.iu.edu/hypermail/linux/kernel/).

*Disclaimer:*

+ The hypermail spider is NOT ready for production use yet.
+ This scraper is developed in Python 3.5.2 with the [scrapy](https://doc.scrapy.org/en/latest/) framework.

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
