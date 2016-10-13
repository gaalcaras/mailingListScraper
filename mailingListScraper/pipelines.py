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

    def __init__(self):
        self.attributedIds = set()

    def process_item(self, item, spider):
        timeFormat = "%Y-%m-%d %H:%M:%S%z"
        timestamp = datetime.strptime(item['timestampReceived'], timeFormat)

        idFormat = "%Y%m%d%H%M%S"
        emailId = int(timestamp.strftime(idFormat))

        if emailId in self.attributedIds:
            emailId = emailId*10

        self.attributedIds.add(emailId)

        item['emailId'] = emailId

        return item


class CleanReplyto(object):

    def process_item(self, item, spider):
        if item['replyto'] == '':
            item['replyto'] = 'NA'
            return item

        urlBase = re.search('^(.*)/\d{4}\.html', item['url']).group(1)
        item['replyto'] = urlBase + '/' + item['replyto']

        return item


class ParseTimeFields(object):

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

    def process_item(self, item, spider):
        destFile = 'data/{}/{}.html'.format(spider.name, item['emailId'])
        os.makedirs(os.path.dirname(destFile), exist_ok=True)

        with open(destFile, 'w+b') as body:
            for line in item['body']:
                body.write(line.encode('utf-8'))

        return item


class CsvExport(object):

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
        file = open(destFilePath, 'w+b')
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
