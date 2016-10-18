# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exporters import CsvItemExporter

import re
import os
from datetime import datetime
from dateutil.parser import parse as dateParser
from dateutil import tz


class GenerateId(object):
    """
    Generate a unique ID for the email.

    Each email should have its own unique ID. This pipeline generates it with
    the received timestamp, because I make the assumption that few emails will
    share the same timestamp down to the second. For those who do, the (n+1)th
    processed item gets n zeros added to their timestamp.
    """

    def __init__(self):
        self.attributedIds = set()

    def process_item(self, item, spider):
        timeFormat = "%Y-%m-%d %H:%M:%S%z"
        timestamp = datetime.strptime(item['timestampReceived'], timeFormat)

        idFormat = "%Y%m%d%H%M%S"
        emailId = int(timestamp.strftime(idFormat))

        # If two emails were received at the same time, multiply by 10
        # (i.e. add a 0 at the end of the ID)
        emailId = emailId*10 if emailId in self.attributedIds else emailId

        self.attributedIds.add(emailId)

        item['emailId'] = emailId

        return item


class CleanReplyto(object):
    """
    Clean the "replyto" field.

    1. Return NA if not in reply to another email
    2. Reconstruct the entire URL if we only get a relative URL
    """

    def process_item(self, item, spider):
        if item['replyto'] == '':
            item['replyto'] = 'NA'
            return item

        urlBase = re.search('^(.*)/\d{4,6}\.html', item['url']).group(1)
        item['replyto'] = urlBase + '/' + item['replyto']

        return item


class ParseTimeFields(object):
    """
    Create well formated timestamps with existing time fields.

    1. Return NA when appropriate (time missing or unreadable)
    2. Use dateutil to parse the field and format it
    """

    def process_item(self, item, spider):
        times = {
                'timestampSent': 'timeSent',
                'timestampReceived': 'timeReceived'
        }

        timeFormat = "%Y-%m-%d %H:%M:%S%z"

        # Define a default time zone according to the email server setting
        if spider.name == 'hypermail':
            defTZ = tz.tzoffset('EST', -18000)

        for key, val in times.items():
            if item[val] == "":
                item[val] = "NA"
                item[key] = "NA"
                continue

            parsedTime = dateParser(item[val])

            if parsedTime.tzinfo is None:
                parsedTime = parsedTime.replace(tzinfo=defTZ)

            item[key] = parsedTime.strftime(timeFormat)

        return item


class BodyExport(object):
    """
    Export email body to a separate file.
    """

    def process_item(self, item, spider):
        destFile = 'data/{}/{}.html'.format(spider.name, item['emailId'])
        os.makedirs(os.path.dirname(destFile), exist_ok=True)

        with open(destFile, 'wb') as body:
            for line in item['body']:
                body.write(line.encode('utf-8'))

        return item


class CsvExport(object):
    """
    Export items to a csv file.
    """

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        destFilePath = 'data/{}ByEmail.csv'.format(spider.name)
        file = open(destFilePath, 'wb')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = ['emailId', 'senderName',
                                          'senderEmail',
                                          'timeSent', 'timestampSent',
                                          'timeReceived', 'timestampReceived',
                                          'subject', 'url', 'replyto']
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
