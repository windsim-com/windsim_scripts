from ..apiconfig import Config
import json
import requests


class MapUtil:

    @staticmethod
    def submit_map_api(token, project_id: str, env="test"):
        url = Config.Config.MAP_FUNCTION_URL_TEST
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        }
        with open('map_request.json', 'r') as file:
            data = json.load(file)
            print(data)
            data['projectId'] = str(project_id)
            data['id'] = str(project_id)
            # start_spinner("Generating GWS file...")

            response = requests.post(url, json=data, headers=headers, verify=False)
        if response.status_code == 200:
            print(response)
            # Animation.stop_spinner()
            return response.json()
        if response.status_code == 202:
            print(f"SubmitJob accepted: {response.status_code}")
            return None
        else:
            print(f"SubmitJob failed: {response.status_code} - {response.text}")
            return None

    @staticmethod
    def generate_request(project_id, client_id, ):
        # Generate a request to the map API
        request = {
            "projectId": "00000000-0000-0000-0000-000000000000",
            "id": "00000000-0000-0000-0000-000000000000",
            "terrain": {
                "type": "FeatureCollection",
                "features": []
            }
        }
        return request