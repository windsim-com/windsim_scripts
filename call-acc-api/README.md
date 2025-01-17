use the following commandline to run this script in python if you have put the credentials into the script

```
python -m windsim.main
```

create a powershell script like __run.ps1__ with following content

```
$Env:project_name_prefix = "STANTEC"

$Env:email = "your email"
$Env:password = "your credentials"
$Env:env="test"
$Env:client_id= "a37dfef2-2623-4856-8319-132d20232c86"
$Env:functionCode= your credentials"
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion"

$output = python -m windsim.main
Write-Host "Output from Python script: $output"
```
