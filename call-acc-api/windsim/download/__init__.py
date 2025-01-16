#
# def download_when_jobs_finished(token, projects):
#     while True:
#         from datetime import datetime
#
#         for project_id, Project_name in projects:
#             job_statuses = get_jobs_status(token, project_id)
#             if job_statuses:
#                 current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 print(f"{current_time}")
#                 print(f"JobId\tSectorDegree\tIterations\tStatus")
#                 for status in sorted(job_statuses, key=lambda s: s['sectorDegree']):
#                     status_str = get_status_str(status['status'])
#                     print(f"{status['jobId']}\t{status['sectorDegree']}\t{status['iterations']}\t{status_str}")
#
#
#             if job_statuses and all(status["status"] == 3 for status in job_statuses):
#                 while True:
#                     output_uri = get_project_output_uri(token, project_id)
#
#                     if output_uri:
#                         response = requests.get(output_uri, verify=False)
#                         if response.status_code == 200:
#                             local_path = f"C:/temp/{project_name}.zip"
#                             with open(local_path, "wb") as file:
#                                 file.write(response.content)
#                             print("Project downloaded successfully.")
#                             return None
#                         else:
#                             if response.status_code == 404:
#                                 print("Output file not available yet, waiting...")
#                                 time.sleep(10)  # Wait for 10 seconds before checking again
#                             else:
#                                 print(f"Download failed: {response.status_code} - {response.text}")
#                                 break
#                     else:
#                         print("Failed to get output URI.")
#                         break
#         else:
#             time.sleep(60)  # Wait for a minute before polling again