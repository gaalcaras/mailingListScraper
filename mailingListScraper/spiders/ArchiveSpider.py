# -*- coding: utf-8 -*-
# #############################################
# Archive Spider
# #############################################

import scrapy


class ArchiveSpider(scrapy.Spider):
    name = "archive"
    start_urls = []

    def __init__(self, mlist=None):
        self._mList(mlist)

    def _mList(self, mlist):
        "Handle the mList argument."

        allLists = ' '.join(self.mailingList.keys())

        if mlist is None:
            # Default mailing list
            self.start_urls.append(self.mailingList[self.defaultList])
            self.logger.info('Crawling ' + self.defaultList + ' by default.')
        elif mlist == 'print':
            print('Available lists: ' + allLists)
            self.close(self, 'Just asking nicely.')
            return
        elif mlist == 'all':
            self.logger.info('Crawling: ' + allLists + '.')
            self.start_urls = self.mailingList.values()
        else:
            # Adding start_urls according to mlist argument
            lists = mlist.split(',')

            for listName in lists:
                try:
                    url = self.mailingList[listName]
                    self.start_urls.append(url)
                except KeyError:
                    self.logger.warning('Unknown mailing list ' + listName)

            # In case no mlist argument was valid...
            if len(self.start_urls) == 0:
                msg = self.name + ' did not recognize any mailing list in your'
                msg += 'mlist argument. Try with something else.'
                self.logger.warning(msg)
