use the following commandline to run this script


create a powershell script with following content

```
$Env:project_name_prefix = "STANTEC"

$Env:email = "your email"
$Env:password = "your password"
$Env:client_id = "your client id"
$Env:env="test"

$pythonVersion = python --version
Write-Host "Python version: $pythonVersion"

$output = python -m windsim.main
Write-Host "Output from Python script: $output"
```
```
python -m windsim.main
```