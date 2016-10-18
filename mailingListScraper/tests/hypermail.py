#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from mailingListScraper.tests.validationCase import validationCase
from mailingListScraper.pipelines import CleanReplyto
from mailingListScraper.pipelines import ParseTimeFields
from mailingListScraper.pipelines import GenerateId

from mailingListScraper.spiders.hypermail import HypermailSpider
import re


class TestBase(unittest.TestCase):
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
                testItem = self.spider.parseItem(case.response)

                # Compare test and validation data
                for item, trueValue in case.rawItem.items():
                    with self.subTest(item=item):
                        self.assertEqual(trueValue, testItem[item])

    def testBody(self):
        for caseId in self.cases:
            with self.subTest(caseId=caseId):
                # Create a validation case and generate test data
                case = validationCase(caseId)
                testItem = self.spider.parseItem(case.response)

                caseBody = re.sub('\n$', '', str(case.body))
                testBody = re.sub('\n$', '', testItem['body'])

                self.assertEqual(testBody, caseBody)


class TestPipelines(TestBase):
    """
    Testing pipelines on "raw outputs" defined in the json test cases.
    """

    def testCleanReplyto(self):
        pipeline = CleanReplyto()

        for caseId in self.cases:
            with self.subTest(caseId=caseId):
                # Create a validation case and generate test data
                case = validationCase(caseId)
                testItem = pipeline.process_item(case.rawItem, self.spider)

                # Compare test and validation data
                self.assertEqual(case.finalItem['replyto'],
                                 testItem['replyto'])

    def testParseTimeFields(self):
        pipeline = ParseTimeFields()

        for caseId in self.cases:
            with self.subTest(caseId=caseId):
                # Create a validation case and generate test data
                case = validationCase(caseId)
                testItem = pipeline.process_item(case.rawItem, self.spider)

                # Compare test and validation data
                self.assertEqual(case.finalItem['timestampSent'],
                                 testItem['timestampSent'])
                self.assertEqual(case.finalItem['timestampReceived'],
                                 testItem['timestampReceived'])


class TestPipelineGenerateId(TestBase):

    def testIdFormat(self):
        item = {'timestampReceived': '1995-06-20 12:35:45-0500'}

        pipeline = GenerateId()
        result = pipeline.process_item(item, self.spider)

        self.assertEqual(result['emailId'], 19950620123545)

    def testIdUnicity(self):
        item1 = {'timestampReceived': '1995-06-20 12:35:45-0500'}
        item2 = {'timestampReceived': '1995-06-20 12:35:45-0500'}

        pipeline = GenerateId()

        result1 = pipeline.process_item(item1, self.spider)
        result2 = pipeline.process_item(item2, self.spider)

        self.assertEqual(result1['emailId'], 19950620123545)
        self.assertEqual(result2['emailId'], 199506201235450)

    def testRealData(self):
        pipeline = GenerateId()
        parseTime = ParseTimeFields()

        for caseId in self.cases:
            with self.subTest(caseId=caseId):
                # Create a validation case and generate test data
                case = validationCase(caseId)
                testItem = parseTime.process_item(case.rawItem, self.spider)
                testItem = pipeline.process_item(testItem, self.spider)

                # Compare test and validation data
                self.assertEqual(case.finalItem['emailId'],
                                 testItem['emailId'])

if __name__ == '__main__':
    unittest.main()
