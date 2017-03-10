# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,protected-access
"""
Unit tests for HypermailSpider
"""

import os

def set_cases(spider_name):
    case_dir = os.path.join(os.path.dirname(__file__), 'pages', spider_name)
    file_cases = os.listdir(case_dir)

    cases = set()

    for fpath in file_cases:
        cases.add(os.path.splitext(fpath)[0])

    return cases
