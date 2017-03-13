# -*- coding: utf-8 -*-
# pylint: disable=abstract-method
"""
ArchiveSpider provides basic tools for all the other spiders. It focuses
on the command line arguments and the options for each spider.
"""

import re
import scrapy


class ArchiveSpider(scrapy.Spider):
    """
    Provides the tools to interact with the command line arguments.
    """
    name = "archive"
    scraping_lists = []
    start_urls = []
    mailing_lists = {}
    default_list = ''
    start_url = ''
    drop_fields = []
    years = []

    get_body = True

    def __init__(self, body=None, mlist=None, year=None):
        self._set_lists()
        self._mlist(mlist)
        self._getbody(body)
        self._year(year)
        super().__init__()

    def _set_lists(self):
        """
        Sets the mailing_lists property. If start_url exists, then the
        spider will call _getLists() to get the urls directly from
        the archive.
        """

        if not any(self.mailing_lists):
            if self.start_url == "":
                self.logger.error('No start_url or mailing_lists')

    def _year(self, year):
        "Handle the year argument."

        if year is None:
            year = ''
            self.years = []
            self.logger.info('Crawling all years by default.')
            return

        if re.match(r'^\d{4}$', year):
            # Only scrap one year
            self.years = [year.strip()]
        elif re.match(r'\d{4},', year):
            # Scrap several years
            years = year.split(',')
            years = [y.strip() for y in years]
            self.years = years
        elif re.match(r'(\d{4}):(\d{4})', year):
            # Scrap a range of years
            reg = re.search(r'(\d{4}):(\d{4})', year)
            years = range(int(reg.group(1)), int(reg.group(2))+1)
            years = [str(y) for y in years]
            self.years = years

        self.logger.info('Crawling is limited to the following years: ' + ','.join(self.years))

    def _mlist(self, mlist):
        "Handle the mList argument."

        all_lists = ' '.join(self.mailing_lists.keys())

        if mlist is None:
            # Default mailing list
            self.start_urls.append(self.mailing_lists[self.default_list])
            self.scraping_lists = [self.default_list]

            self.logger.info('Crawling ' + self.default_list + ' by default.')
        elif mlist == 'print':
            print('Available lists: ' + all_lists)
            self.close(self, 'Just asking nicely.')
            return
        elif mlist == 'all':
            self.logger.info('Crawling: ' + all_lists + '.')
            self.scraping_lists = self.mailing_lists.keys()

            self.start_urls = self.mailing_lists.values()
        else:
            # Adding start_urls according to mlist argument
            lists = mlist.split(',')
            self.scraping_lists = lists

            for list_name in lists:
                try:
                    url = self.mailing_lists[list_name]
                    self.start_urls.append(url)
                except KeyError:
                    self.logger.warning('Unknown mailing list ' + list_name)

            # In case no mlist argument was valid...
            if not self.start_urls:
                msg = self.name + ' did not recognize any mailing list in your'
                msg += 'mlist argument. Try with something else.'
                self.logger.warning(msg)

    def _getbody(self, body):
        "Handle the body argument."

        if body == "false":
            self.get_body = False
            self.logger.info('Spider will not extract email body.')
