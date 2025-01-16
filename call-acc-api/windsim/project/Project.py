import requests
import time
import json
import uuid
from datetime import datetime, timezone
import os
from urllib.parse import urlparse, urlunparse
# from animation import start_spinner, stop_spinner
from ..login import Login
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

    @staticmethod
    def get_project_upload_uri(token, project_id):
        url = f"{Config.Config.API_BASE_URL}/api/DesktopCloudHybridProject/GetProjectUploadUri/{project_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        print(url)
        response = requests.get(url, headers=headers, verify=False)

        if response.status_code == 200:
            print(response.text)
            return response.text
        else:
            print(f"GetProjectUploadUri failed: {response.status_code} - {response.text}")
            return None

    @staticmethod
    def generate_file_sas_url(sas_url, file_path):
        url_parts = urlparse(sas_url)
        return urlunparse((url_parts.scheme, url_parts.netloc, f"{url_parts.path}/{file_path}", url_parts.params, url_parts.query, url_parts.fragment))

    @staticmethod
    def get_project_output_uri(token, project_id):
        url = f"{Config.Config.API_BASE_URL}/api/Project/GetProjectOutputUri/{project_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        while True:
            response = requests.get(url, headers=headers, verify=False)

            if response.status_code == 200:
                return response.text.strip('"')  # Remove double quotes from the response

            if response.status_code == 404:
                print("Output file not available yet, waiting...")
                time.sleep(10)  # Wait for 10 seconds before checking again
            else:
                print(f"GetProjectOutputUri failed: {response.status_code} - {response.text}")
                return None

