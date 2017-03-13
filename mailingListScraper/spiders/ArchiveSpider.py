# -*- coding: utf-8 -*-
"""
ArchiveSpider provides basic tools for all the other spiders. It focuses
on the command line arguments and the options for each spider.
"""

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

    get_body = True

    def __init__(self, body=None, mlist=None):
        self._set_lists()
        self._mlist(mlist)
        self._getbody(body)

    def _set_lists(self):
        """
        Sets the mailing_lists property. If start_url exists, then the
        spider will call _getLists() to get the urls directly from
        the archive.
        """

        # TODO: à améliorer
        if not any(self.mailing_lists):
            if self.start_url == "":
                self.logger.error('No start_url or mailing_lists')

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
