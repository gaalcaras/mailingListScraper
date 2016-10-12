#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from mailingListScraper.tests.validationCase import validationCase
from mailingListScraper.pipelines import CleanReplyto
from mailingListScraper.pipelines import ParseTimeFields

from mailingListScraper.spiders.hypermail import HypermailSpider
import re


class TestBase(unittest.TestCase):
    def setUp(self):
        self.spider = HypermailSpider()
        self.cases = [19950623163756,
                      20010625115259]
        self.maxDiff = None


class TestItemExtraction(TestBase):
    """
    Testing how the Spider and the ItemLoaders deal with several test pages.
    This test only concerns the Item extraction in the Spider (xpath, etc.)
    and the ItemLoader stuff (input and output processor).
    """

    def testItemExtraction(self):
        for caseId in self.cases:
            with self.subTest(caseId=caseId):
                # Create a validation case and generate test data
                case = validationCase(caseId)
                testItem = self.spider.parse(case.response)

                # Compare test and validation data
                for item, trueValue in case.rawItem.items():
                    with self.subTest(item=item):
                        self.assertEqual(trueValue, testItem[item])

    def testBody(self):
        for caseId in self.cases:
            with self.subTest(caseId=caseId):
                # Create a validation case and generate test data
                case = validationCase(caseId)
                testItem = self.spider.parse(case.response)

                caseBody = re.sub('\n$', '', case.body)
                testBody = re.sub('\n$', '', testItem['body'])

                self.assertEqual(testBody, caseBody)


class TestPipelines(TestBase):
    """
    Testing pipelines on "raw outputs" defined in the json test cases.
    """

    def testCleanReplyto(self):
        for caseId in self.cases:
            with self.subTest(caseId=caseId):
                # Create a validation case and generate test data
                case = validationCase(caseId)
                testItem = CleanReplyto.process_item(self, case.rawItem,
                                                     self.spider)

                # Compare test and validation data
                self.assertEqual(case.finalItem['replyto'],
                                 testItem['replyto'])

    def testParseTimeFields(self):
        for caseId in self.cases:
            with self.subTest(caseId=caseId):
                # Create a validation case and generate test data
                case = validationCase(caseId)
                testItem = ParseTimeFields.process_item(self, case.rawItem,
                                                        self.spider)

                # Compare test and validation data
                self.assertEqual(case.finalItem['timestampSent'],
                                 testItem['timestampSent'])
                self.assertEqual(case.finalItem['timestampReceived'],
                                 testItem['timestampReceived'])

if __name__ == '__main__':
    unittest.main()
