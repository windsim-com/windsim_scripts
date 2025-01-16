import requests
import json

import urllib3
from ..apiconfig.Config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Login:

    def __init__(self, config: Config):
        self.spinner_thread = None
        self.config = config
        self.url = config.LOGIN_TEST
    def login(self, email, password, env="test"):
        if env == "test":
            self.url = self.config.LOGIN_TEST
        else:
            self.url = self.config.Login_PROD

        data = {
            "email": email,
            "password": password,
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.url, data=json.dumps(data), headers=headers, verify=False)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None