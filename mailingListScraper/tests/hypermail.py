# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,protected-access
"""
Unit tests for HypermailSpider
"""

import unittest
import re

from mailingListScraper.tests.validation_case import ValidationCase
from mailingListScraper.tests.utils import set_cases

from mailingListScraper.spiders.hypermail import HypermailSpider


class HypermailTest(unittest.TestCase):

    def setUp(self):
        self.spider = HypermailSpider()
        self.cases = set_cases(self.spider.name)

        # Enable long strings comparisons
        self.maxDiff = None # pylint: disable=invalid-name

    def test_all_items(self):
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

if __name__ == '__main__':
    unittest.main()
