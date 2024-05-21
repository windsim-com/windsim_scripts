# Utility to manage the Actuator Disk runs
## Prerequisite setup

Create a project with the following folder structure
```
windsim-projects
-my_AD_project
--my_AD_project_base
```

Set up the base project by the following steps:
1. Import grid file (.gws)
2. Run Terrain (Resolution doesn't matter, set wanted extent)
3. Set Windfields settings
4. Go to objects park layout and set turbines and climatologies
5. Tools-->export objects ('.ows')
6. Copy RunReports.bat into the base project root directory

## Running it piecewise
### Run Setup project
```sh
python actuator_disk.py --mode 'setup' --base_project 'path/to/windsim projects/my_AD_project/my_AD_project_base' --object-file 'Layout 1/AD_layout.ows' --high 20 --low 7
```

The python program will then create 4 copies of the base project so the directory will look like:
```
windsim-projects
-my_AD_project
--my_AD_project_base
--my_AD_project_low_AD
--my_AD_project_high_AD
--my_AD_project_low_free
--my_AD_project_high_free
```
Setting up a project for each of the combinations of windspeed: [low, high] and ActuatorDisk [with, without]


### Run Terrain
```sh
python actuator_disk.py --mode 'terrain' --base_project 'path/to/windsim projects/my_AD_project/my_AD_project_base' --object-file 'Layout 1/AD_layout.ows'
```

This will first run Terrain for the Actuator Disk projects, using the AD_layout.ows file to decide horisontal discretization. Then it will use the Actuator_disk.bws file as the refinement file for the free wind projects and run Terrain for those as well.

### Run WindFields
```sh
python actuator_disk.py --mode 'WindFields' --base_project 'path/to/windsim projects/my_AD_project/my_AD_project_base' --object-file 'Layout 1/AD_layout.ows'
```

This will use run windfields for all projects. And create the 'Layout 1/log/blockage_effect.log' to all projects, which is needed to do postprocessing.

### Run all
Alternativly you can run the whole process at the same time:
```sh
python actuator_disk.py --all --base_project 'path/to/windsim projects/my_AD_project/my_AD_project_base' --object-file 'Layout 1/AD_layout.ows' --high 20 --low 7
```



