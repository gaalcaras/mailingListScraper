# Mailing List Scraper

[![Build Status](https://travis-ci.org/gaalcaras/mailingListScraper.svg?branch=master)](https://travis-ci.org/gaalcaras/mailingListScraper)

**mailingListScraper** is a tool to extract data from public email lists in a format suitable for data analysis.

<!-- vim-markdown-toc Redcarpet -->
* [Introduction](#introduction)
* [User guide](#user-guide)
  * [Installation](#installation)
  * [Quick start](#quick-start)
  * [Collected data](#collected-data)
    * [CSV file](#csv-file)
    * [XML file](#xml-file)
  * [Options](#options)
    * [mlist](#mlist)
    * [body](#body)
    * [year](#year)
* [Development and testing](#development-and-testing)
  * [Development](#development)
  * [Testing](#testing)
* [Privacy](#privacy)

<!-- vim-markdown-toc -->

## Introduction

If you want to make some data analysis on a mailing list, first you need a dataset.
`mailingListScraper` is a python tool enabling you to process the unstructured data available in public mailing list archives.
The data is saved as `.csv` and `.xml` for easy statistical analysis, data modeling, text mining, machine learning, etc.

`mailingListScraper` is organized around [Mailing List Archives](https://en.wikipedia.org/wiki/Electronic_mailing_list#Archives).
They usually store many mailing lists and provide a web interface to browse and read the emails.

Supported archives include:

| Email Archive | Lists # | Emails # | Default Mailing List |
| --- | --- | --- | --- |
|[Hypermail](http://lkml.iu.edu/hypermail/) | 3 ([list](http://lkml.iu.edu/hypermail/linux/)) | 2,5m+ | [Linux Kernel Mailing List](http://lkml.iu.edu/hypermail/linux/kernel) |
|[MARC](http://marc.info/)| 3500+ ([list](http://marc.info/))| 80m+ | [git](http://marc.info/?l=git&r=1&w=2) |


## User guide

### Installation

Make sure to install [scrapy](https://doc.scrapy.org/en/latest/intro/install.html) and the dependencies first.

```
pip install -r requirements.txt
```

Clone the repo and `cd` into it. You're done!

### Quick start

**I strongly recommend that you identify yourself in the user-agent** (`mailingListScraper/settings.py`) so that people can contact you if needed.
Also, be mindful of the potential impact of your scraper on the server's load.

mailingListScraper is composed of several spiders.
Each spider targets a specific email archive, which can host one or several mailing lists.

You can launch a spider running this command at the root level of the repo:
```
scrapy crawl {archiveName}
```

For instance, if I want to collect data from the [Hypermail](http://lkml.iu.edu/hypermail/) archive:

```
scrapy crawl hypermail
```

If the archive hosts multiple mailing lists, the spider only crawls one of them by default and lets you know which one.
In the Hypermail case, that's the Linux Kernel Mailing List :

```
[hypermail] INFO: Crawling the LKML by default.
```

That's it!
The spider is collecting data.

### Collected data

The spider stores extracted emails in a `data` folder, containing:

+ `{ArchiveName}ByEmail.csv`: all metadata collected are stored in this file, with each row corresponding to an email.
    If you only crawl one mailing list, then the name is `{mailingList}ByEmail.csv` (and column `mailingList` is dropped).
+ `{ArchiveName}{year}Bodies.xml`: a XML file with the email body, in which each item is an email .
    If you only crawl one mailing list, then the name is `{mailingList}{year}Bodies.xml` (and node `mailingList` is dropped).

#### CSV file

Each row corresponds to an email, each column to one of the following fields:

| Field | Example |Comment |
| --- | --- | --- |
| mailingList | `lkml` | Migth be dropped if you only crawl through one mailing list. |
| emailId | `20161017142556` | The timestamp for received time ("received on 2016-10-17 at 14:25:56"). If two or more emails were received at the same time, we append a 0 (or more) at the end of the timestamp. |
| senderName | `Linus Torvalds` | If no name is found, will be the email.|
| senderEmail | `foo@bar.com` | Might not be complete.|
| timestampSent | `20161017142556+0500` | Based upon previous field, a timestamp with timezone (if available). Will be "NA" if timeSent is "NA" or cannot be parsed. Some mailing list don't have one, so the whole column will be dropped. |
| timestampReceived | `20161017142556+0500` | Based upon previous field, a timestamp with timezone (if available). Will be "NA" if timeReceived is "NA" or cannot be parsed.|
| subject | `Re: [PATCH v1] oops` | Pretty obvious :) |
| url | `http://archive.org/mailingList/msg2.html` | The url of the message. |
| replyto | `http://archive.org/mailingList/msg1.html` | The url of the message the current email replies to. |

When the scraper fails to extract the relevant information from the email, the field is marked as "NA".

#### XML file

The body of the emails is stored in an XML file, with some metadata, to make text mining easier.
It's organized like this:

```xml
<?xml version="1.0" encoding="utf-8"?>
<emails>
  <email>
    <emailId>20060130061212</emailId>
    <senderName>Linus Torvalds</senderName>
    <senderEmail>foo@bar.com</senderEmail>
    <timestampReceived>2006-01-30 06:12:12-0400</timestampReceived>
    <subject>Re: [PATCH v1] oops</subject>
    <body>bla bla bla</body>
  </email>
</emails>
```

Each email is an item node.

This is how you would load the data with the [tm](https://cran.r-project.org/web/packages/tm/index.html) package in R.

```r
library('tm')

# Define custom XML reader
ml_reader <- readXML(
  spec = list(id = list("node", "/email/emailId"),
              content = list("node", "/email/body"),
              datetimestamp = list("node", "/email/timestampReceived"),
              subject = list("node", "/email/subject"),
              author = list("node", "/email/senderName"),
              author_email = list("node", "/email/senderEmail")
              ),
  doc = PlainTextDocument()
)

# Create custom source
ml_source <- function(x) {
  XMLSource(x, function(tree) XML::xmlChildren(XML::xmlRoot(tree)), ml_reader)
}

# Load documents as a VCorpus for example
ml <- VCorpus(ml_source("./lkml2017Bodies.xml"))
```

### Options

The spiders accept arguments from the command line.
You can combine them to adjust the scope of your crawl.

Say I only care about the metadata of the emails sent in 1995, but I want to crawl all the lists in the Hypermail archive:

```
scrapy crawl hypermail -a mlist=all -a body=false -a year=1995
```

#### mlist

You can provide a comma separated list of mailing lists for a specific spider:

```
scrapy crawl archiveName -a mlist=mailinglist1,mailinglist2
```

To print the available mailing lists in an archive:

```
scrapy crawl hypermail -a mlist=print
```

To crawl every mailing list in the archive:

```
scrapy crawl hypermail -a mlist=all
```

#### body

Since downloading the body of each email can take up a lot of disk space, you can disable it:

```
scrapy crawl archiveName -a body=false
```

#### year

By default, the spiders crawl through every message in the mailing list.
If you're only interested in a specific period of time, you can use the year argument for that.

You can focus on one year:

```
scrapy crawl marc -a year=2006
```

Or you can give it a comma separated list of years:

```
scrapy crawl marc -a year=2006,2011
```

Or even a range of years:

```
scrapy crawl marc -a year=2006:2008
```

## Development and testing

I am currently developing this scraper to collect data for my PhD ([EHESS](http://ehess.fr/) in Paris, France). If you do see problems with the code, I'll be glad to review your Pull Requests ;-)

### Development

This scraper is developed in Python 3.5.2 with the [scrapy](https://doc.scrapy.org/en/latest/) framework.

**Before you start working on your own spiders**, you should set the `LOG_LEVEL` setting (`mailingListScraper/settings.py`) to `DEBUG` (or just uncomment the line).

### Testing

You can run the `scrapy check` command to run simple tests, with the built-in [Scrapy contracts](https://doc.scrapy.org/en/latest/topics/contracts.html).

While contracts are fine for small verifications, they are not enough: you need to make sure that the data collected is consistent with your expectations.
That's why some basic unit testing is provided in `mailingListScraper/tests`.
Each spider and pipeline is to be tested with "real world" test cases.

The data for these test cases is provided in the `pages` directory.
Cases are organized into subfolders, named after their spiders.
In these subfolders, you'll find the test cases which consist of three files:

+ `emailId.html`: this is the page used as a Scrapy response to test the methods of the spider.
+ `emailId.json`: this is the data you expect to get from the spider.
  You can test the items extracted after they've been processed by the ItemLoader (`itemOutput`) and after they've been processed by the pipelines (`pipelineOutput`).
+ `emailId.txt`: that is the body you expect to retrieve from the page.

Each time you test a spider, it will iterate through a certain number of test cases.
You can test a specific spider running this command at the root level of the repo:

```
python -m unittest mailingListScraper.tests.hypermail
```

Pipelines can also be tested:

```
python -m unittest mailingListScraper.tests.pipelines
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
