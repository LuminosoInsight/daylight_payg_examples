
import json
import requests


class LumiPaygSdk:

    def __init__(self,
                 api_url='http://44.202.215.50/api/v5/',
                 useragent='LumiPaygSdk',
                 token=None):
        self.api_url = api_url
        if not self.api_url.endswith('/'):
            self.api_url += "/"
        self.useragent = useragent
        self.token = token

    def __str__(self):
        return f"{self.api_url}"

    def get_token(self, username, password):
        req_body = {
            'email': username,
            'description': 'api token',
            'password': password
        }
        resp = requests.post(
            self.api_url+"payg/tokens", 
            json=req_body,
            headers={'user-agent': self.useragent, 
                     'Content-Type': 'application/json'})
        return resp.text

    def set_token(self, token):
        self.token = token

    def get_projects(self, workspace_id=None):
        req_body = {}
        if workspace_id:
            req_body['workspace_id'] = workspace_id         

        print("calling get_projects")
        resp = requests.get(
            self.api_url+"projects", 
            json=req_body,
            headers={'user-agent': self.useragent, 
                     'Content-Type': 'application/json',
                     'Authorization': 'Token '+self.token})

        return resp.text

    def create_project(self, project_name, 
                       language, description="",
                       workspace_id=None):
        req_body = {'name': project_name,
                    'language': language,
                    'description': description
                    }

        if workspace_id:
            req_body['workspace_id'] = workspace_id

        print("calling get_projects")
        resp = requests.post(
            self.api_url+"projects",
            json=req_body,
            headers={'user-agent': self.useragent, 
                     'Content-Type': 'application/json',
                     'Authorization': 'Token '+self.token})
        print(f"resp: {resp}")
        return resp.text

    def upload(self, project_id, docs):
        req_body = {'docs': docs
                    }

        print("calling upload")
        resp = requests.post(
            f"{self.api_url}projects/{project_id}/upload", 
            json=req_body,
            headers={'user-agent': self.useragent, 
                     'Content-Type': 'application/json',
                     'Authorization': 'Token '+self.token})
        # print(f"upload resp: {resp.text}")
        return resp.text

    def build(self, project_id, skip_sentiment_build=False):
        req_body = {}
        if skip_sentiment_build:
            req_body['skip_sentiment']: skip_sentiment_build
        
        resp = requests.post(
            f"{self.api_url}projects/{project_id}/build", 
            json=req_body,
            headers={'user-agent': self.useragent, 
                     'Content-Type': 'application/json',
                     'Authorization': 'Token '+self.token})
        print(f"resp: {resp.text}")
        return resp.text
       