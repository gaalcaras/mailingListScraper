# -*- coding: utf-8 -*-

# Scrapy settings for mailingListScraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'mailingListScraper'

SPIDER_MODULES = ['mailingListScraper.spiders']
NEWSPIDER_MODULE = 'mailingListScraper.spiders'

LOG_FILE = 'log.txt'
# Comment the following line when doing development.
# For actual scraping, we don't want all the debugging messages.
LOG_LEVEL = 'INFO'

# Crawl responsibly by identifying yourself (and your website) on the
# user-agent
# USER_AGENT = 'mailingListScraper (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'mailingListScraper.pipelines.ParseTimeFields': 100,
   'mailingListScraper.pipelines.GenerateId': 200,
   'mailingListScraper.pipelines.CleanReplyto': 300,
   'mailingListScraper.pipelines.BodyExport': 800,
   'mailingListScraper.pipelines.CsvExport': 900,
}
