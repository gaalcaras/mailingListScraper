# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,protected-access
"""
Unit tests for MarcSpider.
"""

import unittest
import re

from mailingListScraper.tests.validation_case import ValidationCase
from mailingListScraper.pipelines import CleanReplyto, ParseTimeFields, GetMailingList, GenerateId
from mailingListScraper.pipelines import CleanSenderEmail

from mailingListScraper.spiders.marc import MarcSpider

class TestBase(unittest.TestCase):
    """
    Creates a bunch of useful settings for testing spiders.
    """

    def setUp(self):
        self.spider = MarcSpider()
        self.cases = [
            '20070731223613'
            ]

        # Enable long strings comparisons
        self.maxDiff = None # pylint: disable=invalid-name

class TestGetMailingList(TestBase):
    """
    Test if the spider gets all the mailing lists in the MARC archive.
    """

    def test_number_items(self):
        self.spider._set_lists()
        self.assertEqual(len(self.spider.mailing_lists), 3700)

    def test_url_match(self):
        self.spider._set_lists()
        self.assertEqual(self.spider.mailing_lists['git'], 'http://marc.info/?l=git&r=1&w=2')
        self.assertEqual(self.spider.mailing_lists['postgis-devel'],
                         'http://marc.info/?l=postgis-devel&r=1&w=2')

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

    def test_clean_sender_email(self):
        pipeline = CleanSenderEmail()

        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = pipeline.process_item(case.raw_item, self.spider)

                # Compare test and validation data
                self.assertEqual(case.final_item['senderEmail'],
                                 test_item['senderEmail'])

class TestPipelineGenerateId(TestBase):

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
