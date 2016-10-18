#!/usr/bin/env python

import os
import json

from scrapy.http import Request, TextResponse


class validationCase:
    def __init__(self, id):
        self.__curDir = os.path.dirname(__file__)
        caseId = str(id).zfill(4)
        self.validation = self.loadValidation(caseId)
        self.rawItem = self.validation['itemOutput']
        self.finalItem = self.validation['pipelineOutput']
        self.body = self.loadBody(caseId)
        self.response = self.loadResponse(caseId)

    def loadValidation(self, caseId):
        jsonId = caseId + '.json'
        jsonPath = os.path.join(self.__curDir, 'pages', jsonId)

        with open(jsonPath, 'r') as jsonData:
            data = json.load(jsonData)

        return data

    def loadBody(self, caseId):
        bodyId = caseId + '.txt'
        bodyPath = os.path.join(self.__curDir, 'pages', bodyId)

        with open(bodyPath, 'rb') as txtFile:
            body = txtFile.read().decode('utf-8', 'ignore')

        return body

    def loadResponse(self, caseId):
        url = self.rawItem['url']

        request = Request(url=url)

        pageId = caseId + '.html'
        pagePath = os.path.join(self.__curDir, 'pages', pageId)
        page = open(pagePath, 'rb')

        response = TextResponse(url=url,
                                request=request,
                                body=page.read().decode('utf-8', 'ignore'),
                                encoding='utf-8')

        page = page.close()

        return response
