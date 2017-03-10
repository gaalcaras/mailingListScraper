# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,protected-access
"""
Unit tests for MarcSpider.
"""

import os

import unittest

from mailingListScraper.pipelines import CleanReplyto, ParseTimeFields
from mailingListScraper.pipelines import GetMailingList, GenerateId
from mailingListScraper.pipelines import CleanSenderEmail

from mailingListScraper.tests.validation_case import ValidationCase

from mailingListScraper.spiders.marc import MarcSpider
from mailingListScraper.spiders.hypermail import HypermailSpider

class TestPipelines(unittest.TestCase):
    """
    Testing pipelines on "raw outputs" defined in the json test cases.
    """
    spiders = []

    def setUp(self):
        self.spiders = {
            'marc': {
                'spider': MarcSpider(),
                'cases': []
                },
            'hypermail': {
                'spider': HypermailSpider(),
                'cases': []
            }
        }

        self.set_cases()

        # Enable long strings comparisons
        self.maxDiff = None # pylint: disable=invalid-name


    def set_cases(self):
        for spider_name in self.spiders:
            case_dir = os.path.join(os.path.dirname(__file__), 'pages', spider_name)
            file_cases = os.listdir(case_dir)

            cases = set()

            for fpath in file_cases:
                cases.add(os.path.splitext(fpath)[0])

            self.spiders[spider_name]['cases'] = cases

    def test_clean_reply_to(self):
        pipeline = CleanReplyto()

        for spider_name, spider in self.spiders.items():
            for case_id in self.spiders[spider_name]['cases']:
                with self.subTest(spider=spider_name, case_id=case_id):
                    # Create a validation case and generate test data
                    case = ValidationCase(case_id, spider_name)
                    test_item = pipeline.process_item(case.raw_item, spider['spider'])

                    # Compare test and validation data
                    self.assertEqual(case.final_item['replyto'], test_item['replyto'])

    def test_parse_time_fields(self):
        pipeline = ParseTimeFields()

        for spider_name, spider in self.spiders.items():
            for case_id in self.spiders[spider_name]['cases']:
                with self.subTest(spider=spider_name, case_id=case_id):
                    # Create a validation case and generate test data
                    case = ValidationCase(case_id, spider_name)
                    test_item = pipeline.process_item(case.raw_item, spider['spider'])

                    # Compare test and validation data
                    self.assertEqual(case.final_item['timestampSent'],
                                     test_item['timestampSent'])
                    self.assertEqual(case.final_item['timestampReceived'],
                                     test_item['timestampReceived'])

    def test_get_mailing_list(self):
        pipeline = GetMailingList()

        for spider_name, spider in self.spiders.items():
            for case_id in self.spiders[spider_name]['cases']:
                with self.subTest(spider=spider_name, case_id=case_id):
                    # Create a validation case and generate test data
                    case = ValidationCase(case_id, spider_name)
                    test_item = pipeline.process_item(case.raw_item, spider['spider'])

                    # Compare test and validation data
                    self.assertEqual(case.final_item['mailingList'],
                                     test_item['mailingList'])

    def test_matching_mailing_list(self):
        pipeline = GetMailingList()
        spider = self.spiders['hypermail']['spider']

        email_lists = {
            'lkml':
                'http://lkml.iu.edu/hypermail/linux/kernel/9910.1/0253.html',
            'alpha':
                'http://lkml.iu.edu/hypermail/linux/alpha/9508.2/0012.html',
            'net':
                'http://lkml.iu.edu/hypermail/linux/net/9509.1/0008.html'
        }

        for result, url in email_lists.items():
            with self.subTest(url=url):
                test_item = {'url': url, 'mailingList': ''}
                test_result = pipeline.process_item(test_item, spider)
                self.assertEqual(result, test_result['mailingList'])

    def test_clean_sender_email(self):
        pipeline = CleanSenderEmail()

        for spider_name, spider in self.spiders.items():
            for case_id in self.spiders[spider_name]['cases']:
                with self.subTest(spider=spider_name, case_id=case_id):
                    # Create a validation case and generate test data
                    case = ValidationCase(case_id, spider_name)
                    test_item = pipeline.process_item(case.raw_item, spider['spider'])

                    # Compare test and validation data
                    self.assertEqual(case.final_item['senderEmail'],
                                     test_item['senderEmail'])

    def test_id_format(self):
        spider = self.spiders['hypermail']['spider']
        pipeline = GenerateId()

        item = {'timestampReceived': '1995-06-20 12:35:45-0500'}

        result = pipeline.process_item(item, spider)

        self.assertEqual(result['emailId'], 19950620123545)

    def test_id_unicity(self):
        spider = self.spiders['hypermail']['spider']
        pipeline = GenerateId()

        item1 = {'timestampReceived': '1995-06-20 12:35:45-0500'}
        item2 = {'timestampReceived': '1995-06-20 12:35:45-0500'}

        result1 = pipeline.process_item(item1, spider)
        result2 = pipeline.process_item(item2, spider)

        self.assertEqual(result1['emailId'], 19950620123545)
        self.assertEqual(result2['emailId'], 199506201235450)

    def test_real_data(self):
        pipeline = GenerateId()
        parse_time = ParseTimeFields()

        for spider_name, spider in self.spiders.items():
            for case_id in self.spiders[spider_name]['cases']:
                with self.subTest(spider=spider_name, case_id=case_id):
                    # Create a validation case and generate test data
                    case = ValidationCase(case_id, spider_name)
                    test_item = parse_time.process_item(case.raw_item, spider['spider'])
                    test_item = pipeline.process_item(test_item, spider['spider'])

                    # Compare test and validation data
                    self.assertEqual(case.final_item['emailId'],
                                     test_item['emailId'])

if __name__ == '__main__':
    unittest.main()
