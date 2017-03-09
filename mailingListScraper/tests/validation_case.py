# -*- coding: utf-8 -*-
"""
Create response and expected values for real data test cases.
"""

import os
import json

from scrapy.http import Request, TextResponse


class ValidationCase:
    """
    Create response and expected values for real data test cases.
    """

    def __init__(self, case_id, spider_name='hypermail'):
        self._destdir = os.path.join(os.path.dirname(__file__), 'pages', spider_name)

        case_id = str(case_id)

        self.validation = self.load_validation(case_id)
        self.raw_item = self.validation['itemOutput']
        self.final_item = self.validation['pipelineOutput']

        self.body = self.load_body(case_id)

        self.response = self.load_response(case_id)

    def load_validation(self, case_id):
        "Load validation data from the json file"

        json_id = case_id + '.json'
        json_path = os.path.join(self._destdir, json_id)

        with open(json_path, 'r') as json_data:
            data = json.load(json_data)

        return data

    def load_body(self, case_id):
        "Load body from the txt file"

        body_id = case_id + '.txt'
        body_path = os.path.join(self._destdir, body_id)

        with open(body_path, 'rb') as txt_file:
            body = txt_file.read().decode('utf-8', 'ignore')

        return body

    def load_response(self, case_id):
        "Create Scrapy Response from the html file"

        url = self.raw_item['url']

        request = Request(url=url)

        page_id = case_id + '.html'
        page_path = os.path.join(self._destdir, page_id)
        page = open(page_path, 'rb')

        response = TextResponse(url=url,
                                request=request,
                                body=page.read().decode('utf-8', 'ignore'),
                                encoding='utf-8')

        page = page.close()

        return response
