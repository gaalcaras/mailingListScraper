#!/bin/sh

printf "Scrapy contracts" &&
scrapy check &&
python -m unittest -v mailingListScraper.tests.hypermail &&
python -m unittest -v mailingListScraper.tests.marc &&
python -m unittest -v mailingListScraper.tests.pipelines
