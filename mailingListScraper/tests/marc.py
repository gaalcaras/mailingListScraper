# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,protected-access
"""
Unit tests for MarcSpider.
"""

import unittest
import re

from mailingListScraper.tests.validation_case import ValidationCase
from mailingListScraper.tests.utils import set_cases

from mailingListScraper.spiders.marc import MarcSpider

class MarcTest(unittest.TestCase):

    def setUp(self):
        self.spider = MarcSpider()
        self.cases = set_cases(self.spider.name)

        # Enable long strings comparisons
        self.maxDiff = None # pylint: disable=invalid-name

    def _setup(self):
        self.spider = MarcSpider()

    def test_nb_items_mailing_list(self):
        """
        Test if the spider gets all the mailing lists in the MARC archive.
        """
        self.spider._set_lists()
        self.assertEqual(len(self.spider.mailing_lists), 3711)

    def test_accuracy_mailing_lis(self):
        """
        Test if the spider gets the right mailing lists in the MARC archive.
        """
        self.spider._set_lists()
        self.assertEqual(self.spider.mailing_lists['git'], 'http://marc.info/?l=git&r=1&w=2')
        self.assertEqual(self.spider.mailing_lists['postgis-devel'],
                         'http://marc.info/?l=postgis-devel&r=1&w=2')

    def test_extract_all_items(self):
        """
        Test how the Spider and the ItemLoaders deal with several test pages.
        This test only concerns the Item extraction in the Spider (xpath, etc.)
        and the ItemLoader stuff (input and output processor) for all fields,
        except the body of the email.
        """
        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = self.spider.parse_item(case.response)

                # Compare test and validation data
                for item, true_value in case.raw_item.items():
                    with self.subTest(item=item):
                        self.assertEqual(true_value, test_item[item])

    def test_extract_body(self):
        """
        Test how the Spider and the ItemLoaders deal with several test pages.
        This test only concerns the Item extraction in the Spider (xpath, etc.)
        and the ItemLoader stuff (input and output processor), only for the body.
        """
        for case_id in self.cases:
            with self.subTest(case_id=case_id):
                # Create a validation case and generate test data
                case = ValidationCase(case_id, self.spider.name)
                test_item = self.spider.parse_item(case.response)

                case_body = re.sub('\n$', '', str(case.body))
                test_body = re.sub('\n$', '', test_item['body'])

                self.assertEqual(test_body, case_body)

if __name__ == '__main__':
    unittest.main()
