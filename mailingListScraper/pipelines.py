# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exporters import CsvItemExporter

import re
import os


class GenerateId(object):

    def process_item(self, item, spider):
        url = re.search('kernel/(.*)\.html', item['url']).group(1)
        cleaned = url.replace('/', '-')
        cleaned = cleaned.replace('.', '-')
        item['emailId'] = cleaned

        return item


class CleanReplyto(object):

    def process_item(self, item, spider):
        if item['replyto'] == '':
            item['replyto'] = 'NA'
            return item

        page = re.search('(.*)\.html', item['replyto']).group(1)
        yearMonth = re.search('(.*-)\d{4}$', item['emailId']).group(1)
        item['replyto'] = yearMonth + page

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
        self.exporter.fields_to_export = ['emailId', 'replyto', 'senderName',
                                          'senderEmail', 'timeSent',
                                          'timeReceived', 'subject', 'url']
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
