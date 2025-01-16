import requests
import time
import json
import uuid
from datetime import datetime, timezone
import os
from urllib.parse import urlparse, urlunparse
# from animation import start_spinner, stop_spinner
from ..login import Login
from config import Config
import urllib3
from ..apiconfig import Config
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Project:

    @staticmethod
    def add_project(token: str, project_name: str, config: Config):

        data = {
            "name": project_name,
            "projectType": 1
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(config.ADD_PROJECT_TEST, data=json.dumps(data), headers=headers, verify=False)

        if response.status_code == 200:
            id = str(response.text.replace('"',''))
            print(f"Project added: {project_name} {id}")
            return id
        else:
            print(f"Adding project failed: {response.status_code} - {response.text}")