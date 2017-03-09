# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,protected-access
"""
Unit tests for HypermailSpider
"""

import unittest
import re

from mailingListScraper.tests.validation_case import ValidationCase

from mailingListScraper.pipelines import CleanReplyto, ParseTimeFields
from mailingListScraper.pipelines import GenerateId, GetMailingList

from mailingListScraper.spiders.hypermail import HypermailSpider


class TestBase(unittest.TestCase):
    """
    Creates a bunch of useful settings for testing spiders.
    """

    def setUp(self):
        self.spider = HypermailSpider()
        self.cases = [
            19950623163756,
            19960629003529,
            19970409195757,
            19980323182147,
            19991008202739,
            20000824142828,
            20010625115259,
            20011129134159,  # Encoding problems in the page
            20021117003913,
            20030816004422,
            20041202122725,
            20050426154225,
            20060208021218,
            20070524191655,
            20111008231656,
            20150930190314,  # No senderName, only email with xxxx
            20160930024050
            ]

        # Enable long strings comparisons
        self.maxDiff = None # pylint: disable=invalid-name


class TestItemExtraction(TestBase):
    """
    Testing how the Spider and the ItemLoaders deal with several test pages.
    This test only concerns the Item extraction in the Spider (xpath, etc.)
    and the ItemLoader stuff (input and output processor).
    """

    def test_item_extraction(self):
        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = self.spider.parse_item(case.response)

                # Compare test and validation data
                for item, true_value in case.raw_item.items():
                    with self.subTest(item=item):
                        self.assertEqual(true_value, test_item[item])

    def test_body(self):
        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = self.spider.parse_item(case.response)

                case_body = re.sub('\n$', '', str(case.body))
                test_body = re.sub('\n$', '', test_item['body'])

                self.assertEqual(test_body, case_body)


class TestPipelines(TestBase):
    """
    Testing pipelines on "raw outputs" defined in the json test cases.
    """

    def test_clean_reply_to(self):
        pipeline = CleanReplyto()

        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = pipeline.process_item(case.raw_item, self.spider)

                # Compare test and validation data
                self.assertEqual(case.final_item['replyto'], test_item['replyto'])

    def test_parse_time_fields(self):
        pipeline = ParseTimeFields()

        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = pipeline.process_item(case.raw_item, self.spider)

                # Compare test and validation data
                self.assertEqual(case.final_item['timestampSent'],
                                 test_item['timestampSent'])
                self.assertEqual(case.final_item['timestampReceived'],
                                 test_item['timestampReceived'])

    def test_get_mailing_list(self):
        pipeline = GetMailingList()

        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = pipeline.process_item(case.raw_item, self.spider)

                # Compare test and validation data
                self.assertEqual(case.final_item['mailingList'],
                                 test_item['mailingList'])


class TestPipelineGetMailingList(TestBase):

    def test_matching(self):
        email_lists = {
            'lkml':
                'http://lkml.iu.edu/hypermail/linux/kernel/9910.1/0253.html',
            'alpha':
                'http://lkml.iu.edu/hypermail/linux/alpha/9508.2/0012.html',
            'net':
                'http://lkml.iu.edu/hypermail/linux/net/9509.1/0008.html'
        }

        pipeline = GetMailingList()

        for result, url in email_lists.items():
            with self.subTest(url=url):
                test_item = {'url': url, 'mailingList': ''}
                test_result = pipeline.process_item(test_item, self.spider)
                self.assertEqual(result, test_result['mailingList'])


class TestPipelineGenerateId(TestBase):

    def test_id_format(self):
        item = {'timestampReceived': '1995-06-20 12:35:45-0500'}

        pipeline = GenerateId()
        result = pipeline.process_item(item, self.spider)

        self.assertEqual(result['emailId'], 19950620123545)

    def test_id_unicity(self):
        item1 = {'timestampReceived': '1995-06-20 12:35:45-0500'}
        item2 = {'timestampReceived': '1995-06-20 12:35:45-0500'}

        pipeline = GenerateId()

        result1 = pipeline.process_item(item1, self.spider)
        result2 = pipeline.process_item(item2, self.spider)

        self.assertEqual(result1['emailId'], 19950620123545)
        self.assertEqual(result2['emailId'], 199506201235450)

    def test_real_data(self):
        pipeline = GenerateId()
        parse_time = ParseTimeFields()

        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = parse_time.process_item(case.raw_item, self.spider)
                test_item = pipeline.process_item(test_item, self.spider)

                # Compare test and validation data
                self.assertEqual(case.final_item['emailId'],
                                 test_item['emailId'])

if __name__ == '__main__':
    unittest.main()
