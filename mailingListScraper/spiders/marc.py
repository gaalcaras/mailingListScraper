# -*- coding: utf-8 -*-
"""
MarcSpider helps you scrap the mailing lists on the MARC archive: http://marc.info/.
By default, it will only go through the git development list.
"""

import re
import urllib

import scrapy
from scrapy.loader import ItemLoader

from lxml import html

from mailingListScraper.items import Email
from mailingListScraper.spiders.ArchiveSpider import ArchiveSpider


class MarcSpider(ArchiveSpider):
    """
    MarcSpider scraps the mailing lists in the MARC archive. When you create
    a new instance of MarcSpider, it automatically goes through the index of
    all mailing lists, which can then be scraped accordingly (if you instruct
    it to do so of course).
    """
    name = "marc"
    allowed_domains = ["marc.info"]
    start_url = "http://marc.info/"
    drop_fields = ['timeSent', 'timestampSent']

    # Default list
    default_list = 'git'

    def _set_lists(self):
        """
        Extract path to messages lists for each mailing list.
        """

        res = urllib.request.urlopen(self.start_url).read()
        body = html.fromstring(res)

        a_names = body.xpath('//dd//a/text()')
        a_hrefs = body.xpath('//dd//a/@href')
        a_hrefs = [self.start_url + s for s in a_hrefs]

        self.mailing_lists = dict(zip(a_names, a_hrefs))

    def parse(self, response):
        """
        Extract all of the messages lists (grouped by date).

        @url http://marc.info/?l=git&r=1&w=2
        @returns requests 149
        """
        msglist_urls = response.xpath('//dd//@href').extract()
        msglist_urls = [self.start_url + u for u in msglist_urls]

        for url in msglist_urls:
            yield scrapy.Request(url, callback=self.parse_msglist)

    def parse_msglist(self, response):
        """
        Extract all relative URLs to the individual messages.

        @url http://marc.info/?l=git&r=1&b=201406&w=2
        @returns requests 31 31
        """

        xpath_next = "//pre//a[contains(text(), 'Next')][1]//@href"
        next_url = response.xpath(xpath_next).extract()

        xpath_msg = "//pre//a[contains(@href, '&m')]//@href"
        msg_urls = response.xpath(xpath_msg).extract()
        msg_urls = [response.url + u for u in msg_urls]

        for url in msg_urls:
            yield scrapy.Request(url, callback=self.parse_item)

        if any(next_url):
            next_url = self.start_url + next_url[0]
            yield scrapy.Request(next_url, callback=self.parse_msglist)

    def parse_item(self, response):
        """
        On the message page, extract the item.

        @url http://marc.info/?l=git&m=148889722812631&w=2
        @returns item 1
        @scrapes url subject senderName senderEmail timeReceived body
        """

        load = ItemLoader(item=Email(), selector=response)

        load.add_value('url', response.url)

        title = response.xpath('//title/text()').extract()
        reg_title = re.search("'(.*)'", title[0])
        load.add_value('subject', reg_title.group(1))

        xpath_replyto = "//a[contains(text(), 'prev in thread')]/@href"
        replyto = response.xpath(xpath_replyto).extract()
        if any(replyto):
            load.add_value('replyto', self.start_url + replyto[0])
        else:
            load.add_value('replyto', '')

        meta = response.xpath("//font[@size='+1']//child::text()").extract()
        meta = ''.join(meta).split('\n') # Give each line its element in list
        meta = list(filter(None, meta)) # Remove empty lines

        for line in meta:
            reg = re.search('^([^:]*):(.*)$', line)

            if "List" in reg.group(1):
                load.add_value('mailingList', reg.group(2).strip())
            elif 'From' in reg.group(1):
                from_reg = re.search('(.*)<(.*)>', reg.group(2))

                try:
                    load.add_value('senderName', from_reg.group(1).strip())
                    load.add_value('senderEmail', from_reg.group(2).strip())
                except AttributeError:
                    load.add_value('senderName', reg.group(2).strip())
            elif 'Date' in reg.group(1):
                load.add_value('timeReceived', reg.group(2).strip())

        xpath_body = "//text()[preceding::b/font[@size='+1'] and following::b]"
        body = response.xpath(xpath_body).extract()
        load.add_value('body', ''.join(body))

        load.add_value('timeSent', '')

        return load.load_item()
