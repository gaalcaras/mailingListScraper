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
        'http://lkml.iu.edu/hypermail/linux/kernel/0008.3/0094.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/0211.2/0196.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/9910.1/0253.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/9704.1/0107.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/9606.3/0278.html',
        'http://lkml.iu.edu/hypermail/linux/kernel/0308.2/0009.html'
    )

    def parse(self, response):
        load = ItemLoader(item=Email(), selector=response)

        # Take care of easy fields first
        load.add_value('url', response.url)

        replytoPattern = '//ul[1]/li[contains((b|strong), "In reply to:")]'
        replytoPattern += '/a/@href'
        link = response.xpath(replytoPattern).extract()

        if len(link) == 0:
            link = ['']

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
        body = re.search(bodyPattern, response.body.decode(), flags=re.S)
        load.add_value('body', body.group(1))

        return load.load_item()

    def parseNewSystem(self, response, fields):
        """
        Populates the fields dictionary for responses that were generated
        by a new archive system (post 2003).
        """

        who = response.xpath('//meta[@name="Author"]/@content').extract()[0]
        whoReg = re.search('^(.*) <(.*)>', who)
        fields['senderName'] = whoReg.group(1)
        email = whoReg.group(2)

        if 'xxxxxxxxxxxxx' in email:
            # Sometimes the email domain is masked in the Author meta field
            # (ex: "davem@xxxxxxxxxxxxx"). Turns out, more often then not,
            # you can get the domain of the email in the Message Id Field.
            msgId = response.xpath('//comment()[contains(., "X-Message-Id")]')
            domainReg = re.search('@(.*) -->', msgId.extract()[0])
            emailReg = re.search('^(.*)@', email)
            email = emailReg.group(1) + '@' + domainReg.group(1)

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
