# -*- coding: utf-8 -*-
import scrapy

from scrapy.loader import ItemLoader
from mailingListScraper.items import Email

import re


class HypermailSpider(scrapy.Spider):
    name = "hypermail"
    allowed_domains = ["lkml.iu.edu"]
    start_urls = (
        'http://lkml.iu.edu/hypermail/linux/kernel/9506/0000.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/0106.3/0269.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/0007.1/1040.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/0211.2/0196.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/9910.1/0253.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/9704.1/0107.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/9606.3/0278.html'
    )

    def parse(self, response):
        load = ItemLoader(item=Email(), selector=response)

        selectors = {'senderName': 'name',
                     'senderEmail': 'email',
                     'timeSent': 'sent',
                     'timeReceived': 'received',
                     'subject': 'subject'}

        for item, sel in selectors.items():
            xpath = "//comment()[contains(.,'" + sel + "')]"
            comment = response.xpath(xpath).extract()
            value = re.search('"(.*)"', comment[0]).group(1)
            load.add_value(item, value)

        load.add_value('url', response.url)

        replytoPattern = '//ul[1]/li[contains(b, "In reply to:")]/a/@href'
        link = response.xpath(replytoPattern).extract()

        if len(link) == 0:
            link = ['']

        load.add_value('replyto', link[0])

        bodyPattern = '<!-- body="start" -->\n?(.*)<!-- body="end" -->'
        body = re.search(bodyPattern, response.body.decode(), flags=re.S)
        load.add_value('body', body.group(1))

        return load.load_item()
