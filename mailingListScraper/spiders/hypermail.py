# -*- coding: utf-8 -*-
"""
HypermailSpider helps you scrap the mailing lists on the Hypermail archive
http://lkml.iu.edu/hypermail/
"""

import re

import scrapy
from scrapy.loader import ItemLoader
from mailingListScraper.items import Email
from mailingListScraper.spiders.ArchiveSpider import ArchiveSpider


class HypermailSpider(ArchiveSpider):
    """
    HypermailSpider scraps the mailing lists in the Hypermail archive. There
    are only three of them (lkml, alpha and net). The default option is to
    scrap lkml.
    """
    name = "hypermail"
    allowed_domains = ["lkml.iu.edu"]

    # Email Lists available from Hypermail archive:
    mailing_lists = {
        'lkml': 'http://lkml.iu.edu/hypermail/linux/kernel/',
        'alpha': 'http://lkml.iu.edu/hypermail/linux/alpha/',
        'net': 'http://lkml.iu.edu/hypermail/linux/net/'
    }
    default_list = 'lkml'

    def parse(self, response):
        """
        Extract all of the messages lists (grouped by date).

        @url http://lkml.iu.edu/hypermail/linux/kernel/
        @returns requests 1002
        """

        msglist_urls = response.xpath('//li//a//@href').extract()
        msglist_urls = [response.url + u for u in msglist_urls]

        for url in msglist_urls:
            yield scrapy.Request(url, callback=self.parse_msglist)

    def parse_msglist(self, response):
        """
        Extract all relative URLs to the individual messages.

        @url http://lkml.iu.edu/hypermail/linux/kernel/9506/index.html
        @returns requests 199
        """

        msg_urls = response.xpath('//li//a//@href').extract()
        reg_url = re.search(r'^(.*)/index\.html', response.url)
        base_url = reg_url.group(1)

# TODO: refactor here
        for rel_url in msg_urls:
            if re.match(r'\d{4,6}', rel_url) is None:
                continue

            msg_url = base_url + '/' + rel_url
            yield scrapy.Request(msg_url, callback=self.parse_item)

    def parse_item(self, response):
        """
        Extract fields from the individual email page and load them into the
        item.

        @url http://lkml.iu.edu/hypermail/linux/kernel/0111.3/0036.html
        @returns items 1 1
        @scrapes senderName senderEmail timeSent timeReceived subject body
        @scrapes replyto url
        """

        load = ItemLoader(item=Email(), selector=response)

        # Take care of easy fields first
        load.add_value('url', response.url)

        pattern_replyto = '//ul[1]/li[contains((b|strong), "In reply to:")]'
        pattern_replyto += '/a/@href'
        link = response.xpath(pattern_replyto).extract()
        link = [''] if not link else link

        load.add_value('replyto', link[0])

        # Sometime in 2003, the archive changes and the email pages
        # require specific procedure to extract the following fields:
        specific_fields = {
            'senderName': None,
            'senderEmail': None,
            'timeSent': None,
            'timeReceived': None,
            'subject': None
        }

        # Detect new archive system with HTML comment
        new_system = response.xpath('/comment()[1][contains(., "MHonArc")]')

        if len(new_system) >= 1:
            # If new archive system is detected...
            specific_fields = self.parse_new_system(response, specific_fields)
            body_before_comment = '<!--X-Body-of-Message-->'
            body_after_comment = '<!--X-Body-of-Message-End-->'
        else:
            # Otherwise...
            specific_fields = self.parse_old_system(response, specific_fields)
            body_before_comment = '<!-- body="start" -->'
            body_after_comment = '<!-- body="end" -->'

        # Load all the values from these specific fields
        for key, val in specific_fields.items():
            load.add_value(key, val)

        if self.get_body:
            # Final field, the body of the email
            pattern_body = body_before_comment + '\n?(.*)' + body_after_comment

            # Ignore invalid bytes when necessary
            page_body = response.body.decode('utf-8', 'ignore')
            body = re.search(pattern_body, page_body, flags=re.S)
            load.add_value('body', body.group(1))

        return load.load_item()

    def parse_new_system(self, response, fields):
        """
        Populates the fields dictionary for responses that were generated
        by a new archive system (post 2003).
        """

        who = response.xpath('//meta[@name="Author"]/@content').extract()[0]
        # The author meta field often contains the name and the email :
        # "Sender Name <email@adress.com>"
        reg_who = re.search(r'^"?([^"]*)"?\s+<(.*)>', who)

        email = who if reg_who is None else reg_who.group(2)

        if 'xxxx' in email:
            # Sometimes the email domain is masked in the Author meta field
            # (ex: "davem@xxxxxxxxxxxxx"). Turns out, more often then not,
            # you can get the domain of the email in the Message Id Field.
            msg_id = response.xpath('//comment()[contains(., "X-Message-Id")]')
            reg_domain = re.search('@(.*) -->', msg_id.extract()[0])
            reg_email = re.search('^<?(.*)@', email)
            email = reg_email.group(1) + '@' + reg_domain.group(1)

        fields['senderName'] = email if reg_who is None else reg_who.group(1)
        fields['senderEmail'] = email

        what = response.xpath('//meta[@name="Subject"]/@content').extract()[0]
        fields['subject'] = what

        sent = response.xpath('//comment()[contains(., "X-Date")]').extract()
        reg_sent = re.search('<!--X-Date: (.*) -->', sent[0])
        fields['timeSent'] = reg_sent.group(1)

        xpath_time = '//strong[contains(., "Date")]/following-sibling::text()'
        raw_time = response.xpath(xpath_time).extract()[0]
        reg_time = re.search(' (.*)\n', raw_time)
        fields['timeReceived'] = reg_time.group(1)

        return fields

    def parse_old_system(self, response, fields):
        """
        Populates the fields dictionary for responses that were generated
        by the old archive system (before 2003).
        """

        selectors = {
            'senderName': 'name',
            'senderEmail': 'email',
            'timeSent': 'sent',
            'timeReceived': 'received',
            'subject': 'subject'
        }

        for item, sel in selectors.items():
            xpath = "//comment()[contains(.,'" + sel + "')]"
            comment = response.xpath(xpath).extract()
            value = re.search('"(.*)"', comment[0]).group(1)
            fields[item] = value

        return fields
