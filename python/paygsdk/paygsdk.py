
import requests


class LumiPaygSdk:

    def __init__(self, api_url='http://44.202.215.50/api/v5/'):
        self.api_url = api_url
        if not self.api_url.endswith('/'):
            self.api_url += "/"

    def __str__(self):
        return f"{self.api_url}"

    def get_token(self, username, password):
        print("getting token")
        req_body = {
            'email': username,
            'description': 'api token',
            'password': password
        }
        resp = requests.post(
            self.api_url+"payg/tokens", 
            json=req_body,
            headers={'user-agent': 'payg-example', 
                     'Content-Type': 'application/json'})
        return resp.text
