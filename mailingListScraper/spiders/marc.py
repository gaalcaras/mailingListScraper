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

    custom_settings = {
        # Unfortunately, we have to ignore the robots.txt file
        'ROBOTSTXT_OBEY': False,
        # We don't want to overload their servers, so let's be gentle here
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.5,
        'DOWNLOAD_DELAY': 1 # Minimum delay of 1s
    }

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

        if any(self.years):
            urls = []

            for year in self.years:
                urls.extend([u for u in msglist_urls if year in u])

            msglist_urls = urls

        for url in msglist_urls:
            yield scrapy.Request(url, callback=self.parse_msglist)

    def parse_msglist(self, response):
        """
        Extract all relative URLs to the individual messages.

        For instance, on the following page, there are:
        + 30 messages requests
        + 16 threads requests
        + 1 next page request

        @url http://marc.info/?l=git&r=1&b=201406&w=2
        @returns requests 47 47
        """

        xpath_msg = "//pre//a[contains(@href, '&m')]//@href"
        msg_urls = response.xpath(xpath_msg).extract()
        msg_urls = [self.start_url + u for u in msg_urls]

        for url in msg_urls:
            yield scrapy.Request(url, callback=self.parse_item)

        xpath_threads = "//a[contains(@href, '?t=')]/@href"
        thread_urls = response.xpath(xpath_threads).extract()
        thread_urls = [self.start_url + u for u in thread_urls]

        for url in thread_urls:
            yield scrapy.Request(url, callback=self.parse_thread)

        xpath_next = "//pre//a[contains(text(), 'Next')][1]//@href"
        next_url = response.xpath(xpath_next).extract()

        if any(next_url):
            next_url = self.start_url + next_url[0]
            yield scrapy.Request(next_url, callback=self.parse_msglist)

    def parse_thread(self, response):
        """
        Go in the thread list itself to follow message links, if
        they are in the targeted mailing lists.

        For instance, on the following page, there are:
        + 10 messages links to follow (git only)
        + 1 next page link

        @url http://marc.info/?t=111957107900001&r=1&w=2
        @returns requests 11 11
        """

        xpath_msg = "//a[contains(@href, '&m=')]/@href"
        msg_urls = response.xpath(xpath_msg).extract()
        msg_urls = [self.start_url + u for u in msg_urls]

        for url in msg_urls:
            if any(ml in url for ml in self.scraping_lists):
                yield scrapy.Request(url, self.parse_item)

        xpath_next = "//pre//a[contains(text(), 'Next')][1]//@href"
        next_url = response.xpath(xpath_next).extract()

        if any(next_url):
            next_url = self.start_url + next_url[0]
            yield scrapy.Request(next_url, callback=self.parse_thread)

    def parse_item(self, response):
        """
        On the message page, extract the item.

        @url http://marc.info/?l=git&m=148889722812631&w=2
        @returns item 1
        @scrapes url subject senderName senderEmail timeReceived body replyto timeSent
        """

        load = ItemLoader(item=Email(), selector=response)

        load.add_value('url', response.url)

        title = response.xpath('//title/text()').extract()
        reg_title = re.search("'(.*)'", title[0])
        load.add_value('subject', reg_title.group(1))

        xpath_replyto = "//a[contains(text(), 'prev in thread')]/@href"
        replyto = response.xpath(xpath_replyto).extract()

        if any(replyto):
            replyto = self.start_url + replyto[0]
            load.add_value('replyto', replyto)
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
                    from_reg2 = re.search(r'(.*)\((.*)\)', reg.group(2))

                    try:
                        load.add_value('senderName', from_reg2.group(2).strip())
                        load.add_value('senderEmail', from_reg2.group(1).strip())
                    except AttributeError:
                        load.add_value('senderName', reg.group(2))
                        load.add_value('senderEmail', '')

            elif 'Date' in reg.group(1):
                load.add_value('timeReceived', reg.group(2).strip())

        if self.get_body:
            xpath_body = "//text()[preceding::b/font[@size='+1'] and following::b]"
            body = response.xpath(xpath_body).extract()
            load.add_value('body', ''.join(body))
        else:
            load.add_value('body', '')

        load.add_value('timeSent', '')

        return load.load_item()
