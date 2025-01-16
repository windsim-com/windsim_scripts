from ..apiconfig import Config
import json
import requests
from ..animation.Animation import Animation


class MapUtil:
    @staticmethod
    def submit_map_api(token, project_id: str, code: str):
        animation = Animation()
        url = f"https://func-mapapi-test-westeurope.azurewebsites.net/api/Terrain/GenerateGwsFile?code={code}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        with open('./map_request.json', 'r') as file:
            data = json.load(file)
            data['projectId'] = project_id
            data['id'] = project_id

            # spinner = Animation()
            # spinner.start_spinner("Generating GWS file...")  # Start the spinner

            try:
                response = requests.post(url, json=data, headers=headers, verify=False)
            finally:
                pass
                # spinner.stop_spinner()  # Stop the spinner after the operation finishes

            if response.status_code == 200:
                return response.json()
            if response.status_code == 202:
                print(f"SubmitJob accepted: {response.status_code}")
                return response.json()
            else:
                print(f"SubmitJob failed: {response.status_code} - {response}")
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