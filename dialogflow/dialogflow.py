import json
import logging
from abc import abstractmethod

import requests
from requests import HTTPError

logger = logging.getLogger('dialogflow')


class RestEndpoint:
    _BASE_URL = 'https://api.dialogflow.com/v1'
    _PROTOCOL = '20170712'
    # TODO: Remove default access token
    _CLIENT_ACCESS_TOKEN = '1cd8d781623b4d24bb44b611728db998'
    _HEADER = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + _CLIENT_ACCESS_TOKEN
    }

    @staticmethod
    def _parse_result(response):
        try:
            response.raise_for_status()
        except HTTPError:
            logger.warning(
                "Request failed with code {}, server reports '{}'".format(
                    response.status_code,
                    response.text
                )
            )
            response.raise_for_status()
        return response.json()

    @staticmethod
    def _prepare_headers(access_token):
        headers = RestEndpoint._HEADER.copy()
        headers['Authorization'] = 'Bearer ' + access_token
        return headers


class DataEndpoint(RestEndpoint):
    @staticmethod
    @abstractmethod
    def get_all(access_token):
        pass

    @staticmethod
    @abstractmethod
    def get_one(dialogflow_id, access_token):
        pass


class Entities(DataEndpoint):
    _ALL_ENTITIES_URL = '{base}/entities?v={protocol}'.format(base=RestEndpoint._BASE_URL,
                                                              protocol=RestEndpoint._PROTOCOL)
    _ONE_ENTITY_URL = '{base}/entities/{id}?v={protocol}'

    @staticmethod
    def get_all(access_token):
        headers = RestEndpoint._prepare_headers(access_token=access_token)
        response = requests.get(Entities._ALL_ENTITIES_URL, headers=headers)
        return RestEndpoint._parse_result(response)

    @staticmethod
    def get_one(dialogflow_id, access_token):
        headers = RestEndpoint._prepare_headers(access_token=access_token)
        one_intent_url = Entities._ONE_ENTITY_URL.format(base=RestEndpoint._BASE_URL,
                                                         protocol=RestEndpoint._PROTOCOL,
                                                         id=dialogflow_id)
        response = requests.get(one_intent_url, headers=headers)
        return RestEndpoint._parse_result(response)


class Intents(DataEndpoint):
    _ALL_INTENTS_URL = '{base}/intents?v={protocol}'.format(base=RestEndpoint._BASE_URL,
                                                            protocol=RestEndpoint._PROTOCOL)
    _ONE_INTENT_URL = '{base}/intents/{id}?v={protocol}'

    @staticmethod
    def get_all(access_token):
        headers = RestEndpoint._prepare_headers(access_token=access_token)
        response = requests.get(Intents._ALL_INTENTS_URL, headers=headers)
        return RestEndpoint._parse_result(response)

    @staticmethod
    def get_one(dialogflow_id, access_token):
        headers = RestEndpoint._prepare_headers(access_token=access_token)
        one_intent_url = Intents._ONE_INTENT_URL.format(base=RestEndpoint._BASE_URL,
                                                        protocol=RestEndpoint._PROTOCOL,
                                                        id=dialogflow_id)
        response = requests.get(one_intent_url, headers=headers)
        return RestEndpoint._parse_result(response)


class Query(RestEndpoint):
    _QUERY_URL = '{base}/query?v={version}'.format(base=RestEndpoint._BASE_URL, version=RestEndpoint._PROTOCOL)

    @staticmethod
    def from_text(text, access_token, lang='de', session_id='0'):
        headers = RestEndpoint._prepare_headers(access_token=access_token)
        data = {
            'query': text,
            'lang': lang,
            'sessionId': session_id
        }
        data = json.dumps(data)
        response = requests.post(url=Query._QUERY_URL,
                                 data=data,
                                 json=True,
                                 headers=headers)
        return Query._parse_result(response)
