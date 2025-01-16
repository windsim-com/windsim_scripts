from ..apiconfg import Config


class ModelUtil:
    @staticmethod
    def submit_job(token, project_id):
        url = f"{Config.Config.API_BASE_URL}/api/DesktopCloudHybridProject/SubmitJob"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "projectId": "105e2e82-8028-43e3-a5e4-fc7fbb3ad64f",
            "xMin": 616348,
            "xMax": 638948,
            "yMin": 5213436,
            "yMax": 5236035,
            "maximumNumberOfCells": 10000,
            "horizontalGridingType": 0,
            "horizontalResolution": 10,
            "cellSize": 30,
            "numberOfCellsZ": 30,
            "simpleRefinementXMin": 626621,
            "simpleRefinementXMax": 628624,
            "simpleRefinementYMin": 5223716,
            "simpleRefinementYMax": 5225718,
            "heightDistributionFactor": 0.3,
            "heightAboveTerrain": -999,
            "forestType": 0,
            "forestList": {},
            "numberOfForests": 0
        }
        response = requests.post(url, json=data, headers=headers, verify=False)

        if response.status_code == 200:
            print(response.json())
            return response.json()
        if response.status_code == 202:
            print(f"SubmitJob accepted: {response.status_code}")
            return None
        else:
            print(f"SubmitJob failed: {response.status_code} - {response.text}")
            return None
