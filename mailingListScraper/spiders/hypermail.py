# -*- coding: utf-8 -*-
# #############################################
# Hypermail Spider
#
# Archive: http://lkml.iu.edu/hypermail/
# #############################################

import re

import scrapy
from scrapy.loader import ItemLoader
from mailingListScraper.items import Email
from mailingListScraper.spiders.ArchiveSpider import ArchiveSpider


class HypermailSpider(ArchiveSpider):
    name = "hypermail"
    allowed_domains = ["lkml.iu.edu"]

    # Email Lists available from Hypermail archive:
    mailingList = {
        'lkml': 'http://lkml.iu.edu/hypermail/linux/kernel/',
        'alpha': 'http://lkml.iu.edu/hypermail/linux/alpha/',
        'net': 'http://lkml.iu.edu/hypermail/linux/net/'
    }
    defaultList = 'lkml'

    def parse(self, response):
        """
        Extract all of the messages lists (grouped by date).

        @url http://lkml.iu.edu/hypermail/linux/kernel/
        @returns requests 1002
        """

        msgListUrls = response.xpath('//li//a//@href').extract()

        for listRelUrl in msgListUrls:
            msgListUrl = response.url
            msgListUrl += listRelUrl
            request = scrapy.Request(msgListUrl,
                                     callback=self.parseMsgList)

            yield request

    def parseMsgList(self, response):
        """
        Extract all relative URLs to the individual messages.

        @url http://lkml.iu.edu/hypermail/linux/kernel/9506/index.html
        @returns requests 199
        """

        msgRelativeUrls = response.xpath('//li//a//@href').extract()
        urlReg = re.search('^(.*)/index\.html', response.url)
        baseUrl = urlReg.group(1)

        for msgRelativeUrl in msgRelativeUrls:
            if re.match('\d{4,6}', msgRelativeUrl) is None:
                continue

            msgUrl = baseUrl + '/' + msgRelativeUrl
            request = scrapy.Request(msgUrl,
                                     callback=self.parseItem)
            yield request

    def parseItem(self, response):
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

        replytoPattern = '//ul[1]/li[contains((b|strong), "In reply to:")]'
        replytoPattern += '/a/@href'
        link = response.xpath(replytoPattern).extract()
        link = [''] if len(link) == 0 else link

        load.add_value('replyto', link[0])

        # Sometime in 2003, the archive changes and the email pages
        # require specific procedure to extract the following fields:
        specificFields = {
                'senderName': None,
                'senderEmail': None,
                'timeSent': None,
                'timeReceived': None,
                'subject': None
        }

        # Detect new archive system with HTML comment
        newSystem = response.xpath('/comment()[1][contains(., "MHonArc")]')

        if len(newSystem) >= 1:
            # If new archive system is detected...
            specificFields = self.parseNewSystem(response, specificFields)
            bodyBeforeComment = '<!--X-Body-of-Message-->'
            bodyAfterComment = '<!--X-Body-of-Message-End-->'
        else:
            # Otherwise...
            specificFields = self.parseOldSystem(response, specificFields)
            bodyBeforeComment = '<!-- body="start" -->'
            bodyAfterComment = '<!-- body="end" -->'

        # Load all the values from these specific fields
        for key, val in specificFields.items():
            load.add_value(key, val)

        # Final field, the body of the email
        bodyPattern = bodyBeforeComment + '\n?(.*)' + bodyAfterComment

        # Ignore invalid bytes when necessary
        pageBody = response.body.decode('utf-8', 'ignore')
        body = re.search(bodyPattern, pageBody, flags=re.S)
        load.add_value('body', body.group(1))

        return load.load_item()

    def parseNewSystem(self, response, fields):
        """
        Populates the fields dictionary for responses that were generated
        by a new archive system (post 2003).
        """

        who = response.xpath('//meta[@name="Author"]/@content').extract()[0]
        # The author meta field often contains the name and the email :
        # "Sender Name <email@adress.com>"
        whoReg = re.search('^"?([^"]*)"?\s+<(.*)>', who)

        email = who if whoReg is None else whoReg.group(2)

        if 'xxxx' in email:
            # Sometimes the email domain is masked in the Author meta field
            # (ex: "davem@xxxxxxxxxxxxx"). Turns out, more often then not,
            # you can get the domain of the email in the Message Id Field.
            msgId = response.xpath('//comment()[contains(., "X-Message-Id")]')
            domainReg = re.search('@(.*) -->', msgId.extract()[0])
            emailReg = re.search('^<?(.*)@', email)
            email = emailReg.group(1) + '@' + domainReg.group(1)

        fields['senderName'] = email if whoReg is None else whoReg.group(1)
        fields['senderEmail'] = email

        what = response.xpath('//meta[@name="Subject"]/@content').extract()[0]
        fields['subject'] = what

        sent = response.xpath('//comment()[contains(., "X-Date")]').extract()
        sentReg = re.search('<!--X-Date: (.*) -->', sent[0])
        fields['timeSent'] = sentReg.group(1)

        timeXPath = '//strong[contains(., "Date")]/following-sibling::text()'
        timeRaw = response.xpath(timeXPath).extract()[0]
        timeReg = re.search(' (.*)\n', timeRaw)
        fields['timeReceived'] = timeReg.group(1)

        return fields

    def parseOldSystem(self, response, fields):
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
