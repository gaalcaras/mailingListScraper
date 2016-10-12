# Mailing List Scraper

**mailingListScraper** is a tool to extract data from public email lists in a format suitable for data analysis.

For now, this scraper only supports the Linux Kernel Mailing List, using this public archive : [http://lkml.iu.edu/hypermail/linux/kernel/](http://lkml.iu.edu/hypermail/linux/kernel/).

*Disclaimer:*

+ The hypermail spider is NOT ready for production use yet.
+ This scraper is developed in Python 3.5.2 with the [scrapy](https://doc.scrapy.org/en/latest/) framework.

## Set up

Make sure to install [scrapy](https://doc.scrapy.org/en/latest/intro/install.html) first.

```
pip install scrapy
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

## Development and testing

Some basic unit testing is provided in `mailingListScraper/tests`.
The main goal is to make sure that the data collected is consistent with your expectations.


You can test a specific spider running this command at the root level of the repo:

```
python -m unittest mailingListScraper.tests.hypermail
```
