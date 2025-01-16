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


def submit_map_api(token, project_id: str, code:str):
    url = f"https://func-mapapi-test-westeurope.azurewebsites.net/api/Terrain/GenerateGwsFile?code={code}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}"
    }
    with open('../map_request.json', 'r') as file:
        data = json.load(file)
        print(data)
        data['projectId'] = str(project_id)
        data['id'] = str(project_id)
        # start_spinner("Generating GWS file...")

        response = requests.post(url, json=data, headers=headers, verify=False)
    if response.status_code == 200:
        print(response)
        # stop_spinner()
        return response.json()
    if response.status_code == 202:
        print(f"SubmitJob accepted: {response.status_code}")
        return None
    else:
        print(f"SubmitJob failed: {response.status_code} - {response.text}")
        return None





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

def generate_file_sas_url(sas_url, file_path):
    url_parts = urlparse(sas_url)
    return urlunparse((url_parts.scheme, url_parts.netloc, f"{url_parts.path}/{file_path}", url_parts.params, url_parts.query, url_parts.fragment))
#
# def upload_folder_to_azure_sas(sas_url, local_folder):
#     for root, dirs, files in os.walk(local_folder):
#         for dir_name in dirs:
#             local_dir_path = os.path.join(root, dir_name)
#             dest_dir_path = os.path.relpath(local_dir_path, local_folder).replace("\\", "/")
#
#             # Create the destination directory using the directory-specific SAS URL
#             dir_sas_url = generate_file_sas_url(sas_url, dest_dir_path)
#             dest_directory_client = ShareDirectoryClient.from_directory_url(dir_sas_url)
#             dest_directory_client.create_directory()
#
#         for file in files:
#             local_file_path = os.path.join(root, file)
#             relative_path = os.path.relpath(local_file_path, local_folder).replace("\\", "/")
#             print(f"Uploading: {relative_path}")
#             #dest_file_path = os.path.join(dest_folder, relative_path).replace("\\", "/")
#             #print(dest_file_path)
#
#             # Create the destination file client using the file-specific SAS URL
#             file_sas_url = generate_file_sas_url(sas_url, relative_path)
#             dest_file_client = ShareFileClient.from_file_url(file_sas_url)
#
#             #print(file_sas_url)
#
#
#             # Upload the file
#             with open(local_file_path, "rb") as file:
#                 dest_file_client.upload_file(file)
#
#     print(f"Project {project_name} {project_id} uploaded")

def submit_job(token, project_id, layout_file_name, project_file_name, cpu_core_count, memory_size_in_gb):
    url = f"{Config.Config.API_BASE_URL}/api/DesktopCloudHybridProject/SubmitJob"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "projectId": project_id,
        "layoutFileName": layout_file_name,
        "projectFileName": project_file_name,
        "cpuCoreCount": cpu_core_count,
        "memorySizeInGB": memory_size_in_gb
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

def get_jobs_status(token, project_id):
    url = f"{Config.Config.API_BASE_URL}/api/Project/GetJobsStatus/{project_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        #print (response.json())
        return response.json()
    else:
        print(f"GetJobsStatus failed: {response.status_code} - {response.text}")
        return None

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

status_dict = {
    0: 'None',
    1: 'Created',
    2: 'InProgress',
    3: 'Completed',
    4: 'Failed',
    5: 'Cancelled',
}

def get_status_str(status_int):
    return status_dict.get(status_int, 'Unknown')



if __name__ == "__main__":
    nodes_max_values = [3000000]  # Add more values as needed

    projects = []

    client_id = f'{os.environ.get("client_id")}'
    # client_id = "a37dfef2-2623-4856-8319-132d20232c86"

    # or you can directly put your credentials here to direct run
    email             = f'{os.environ.get("email")}'
    password          = f'{os.environ.get("password")}'
    #

    project_name = 'STANTEC-' + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%fZ")
    project_type = 1
    #local_folder = r'C:\AcceleratorTests\HundHammer'

    solver = 5
    sweep = 100
    config: Config = Config()
    login: Login = Login(config)
    token = login.login(email, password)
    project_id = Project.Project.add_project(token, project_name, config)
    print(project_id)

    submit_map_api(token, project_id, f'{os.environ.get("code")}')






    #job_response = submit_job(token, str('de54e93c-d398-4723-abce-3b0b01af0455'), layout_file_name, 'HundhammerWithoutTerrain', 1, 1)


    #print(job_response)

    #print(token)

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
