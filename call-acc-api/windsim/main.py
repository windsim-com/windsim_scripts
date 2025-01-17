import requests
import time
import json
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse
import urllib3
from .apiconfig.Config import Config
from .project import Project

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient
from .login.Login import Login
from .project import Project
import os
from .map import MapUtil
from .domainDiscretization.FishNetUTM import FishNetUTM
from .map.GenerateJson import GenerateJson

status_dict = {
    0: 'None',
    1: 'Created',
    2: 'InProgress',
    3: 'Completed',
    4: 'Failed',
    5: 'Cancelled',
}
nodes_max_values = 3000000  # Add more values as needed


def get_status_str(status_int):
    return status_dict.get(status_int, 'Unknown')


if __name__ == "__main__":
    # 0. get credentials from environment variables
    client_id = f'{os.environ.get("client_id")}'
    email = f'{os.environ.get("email")}'
    password = f'{os.environ.get("password")}'
    #
    # for subdomain in subdomains:
    project_name = 'STANTEC-' + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%fZ")
    project_type = 1

    subdomains, centroid = FishNetUTM.createFishnet("./windsim/domainDiscretization/StantecAreas/StantecAreas.shp", 100,
                                                    0, 100)
    # variables for wind fields
    solver = 5
    sweep = 100
    config: Config = Config()

    # 1. login
    login: Login = Login(config)
    token = login.login(email, password)
    print(token)

    # 2. Create projects
    project_id = Project.Project.add_project(token, project_name, config)
    path = "./windsim/domainDiscretization/jsonData/"

    # 3. Save subdomains as json
    filepath = path + str(project_id) + '_subdomain_data.json'


    GenerateJson.save_requests_as_json(subdomains[0], centroid, project_id, filepath)
    MapUtil.MapUtil.submit_map_api(token, filepath, f'{os.environ.get("functionCode")}')

# job_response = submit_job(token, str('de54e93c-d398-4723-abce-3b0b01af0455'), layout_file_name, 'HundhammerWithoutTerrain', 1, 1)


# print(job_response)

# print(token)

##    for nodes_max in nodes_max_values:
##        # Your existing initialization code
##        project_name = f'Test-API-HundHammer-{nodes_max}-{solver}-{sweep}-{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%fZ")}'
##        local_folder_new = local_folder + f"-{nodes_max}-{solver}-{sweep}"  # new folder name based on NodesMax value
##
##        if not os.path.exists(local_folder_new):
##            shutil.copytree(local_folder, local_folder_new)  # Copy entire project folder
##            
##            # Update the NodesMax and Solver value using text replacement
##            xml_file_path = os.path.join(local_folder_new, project_file_name)
##            with open(xml_file_path, 'r') as f:
##                content = f.read()
##
##            new_content = content.replace('<NodesMax>100000</NodesMax>', f'<NodesMax>{nodes_max}</NodesMax>').replace('<Solver>3</Solver>', f'<Solver>{solver}</Solver>').replace('<Sweep>10</Sweep>', f'<Sweep>{sweep}</Sweep>')
##
##            with open(xml_file_path, 'w') as f:
##                f.write(new_content)
##
##            # Run the command line tools
##            subprocess.run(f'"C:\\Program Files\\WindSim\\WindSim 12.0.0\\bin\\Terrain.exe" "{os.path.join(local_folder_new, project_file_name)}" "{layout_file_name}" "E:\\AcceleratorTests\\environment.xml"')
##            subprocess.run(f'"C:\\Program Files\\WindSim\\WindSim 12.0.0\\bin\\Reports.exe" "{os.path.join(local_folder_new, project_file_name)}" "{layout_file_name}" "E:\\AcceleratorTests\\environment.xml" 1')
##
##            print(f"Project for {nodes_max} created")
##
##        
##        # Your existing API calls
##        token = login(email, password)
##        if token:
##            project_id = add_project(token, project_name, project_type)
##            sas_url = get_project_upload_uri(token, project_id)
##            upload_folder_to_azure_sas(sas_url, local_folder_new)
##            job_response = submit_job(token, str(project_id), layout_file_name, project_file_name, 1, 1)
##            projects.append((project_id, project_name))
##            #download_when_jobs_finished(token, str(project_id), project_name)            
##        else:
##            print("Login failed. Exiting.")
##
##
##    download_when_jobs_finished(token, projects)
