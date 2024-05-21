#!/usr/bin/env python

"""actuator_disk.py: Utility script to help with running a WindSim project with the actuator disk. There are currently many manual steps which this helps with, see README.md"""
import sys
from pathlib import Path    
import shutil
import xml.etree.ElementTree as ET
from typing import List
import itertools
from pprint import pprint
import os
import time
import types
import subprocess


if sys.version_info < (3,8):
    print(f"Python version is {sys.version_info}, needs to be 3.9 or newer.")
    sys.exit()

# Defining the project we want to work with
class Project():
    def __init__(self, project_path: Path, layout: str="Layout 1.lws"):
        self.name = project_path.stem
        self.project_file = project_path
        self.layout = layout
        self.base_directory = self.project_file.parent.parent

# Defining the Actuator disk class
class ActuatorDiskRunner:
    def __init__(self, project_path: Path=Path('C:/Users/GullikKillie/Documents/WindSim Projects 12/Actuator_Disk_Flat/Actuator_Disk_Flat_base/Actuator_Disk_Flat.ws'), windsim=Path('C:/Program Files/WindSim/WindSim 12.0.0'), environment=Path('C:/Users/GullikKillie/AppData/Roaming/WindSim/1200/Environment.xml'), owsfile: str='AD_layout', layout='Layout 1.lws'):
        self.project = Project(project_path=project_path, layout=layout)
        self.owsfile = owsfile
        self.project_names = []
        self.windsim = windsim
        self.environment = environment
        self.sectors = self._get_sectors()
        self.threads = self._get_threads()

    def setup_AD(self, windspeeds: List[float] = [7, 20], AD_spacings: int=16):
        """ Creates projects and necessary files to run the actuator disks"""
        
        for AD, windspeed in itertools.product([True, False], windspeeds):
            print(f'Setting up {self.project.name} with AD: {AD} and Windspeed {windspeed}')
            copy_name = self.copy_project(AD=AD, windspeed=windspeed, AD_spacings=AD_spacings)
            self.project_names.append(copy_name)

        print(f'Adding the {self.project.base_directory}/<project>/<layout>/log/blockage_effect.log file to all projects')
        for project_name in self.project_names:
            with open(self.project.base_directory / project_name / self.project.layout.strip('.lws') / 'log' / 'blockage_effect.log', 'w') as outfile:
                outfile.write('\n'.join(str(self.project.base_directory / f'{i}\\') for i in self.project_names))


        return
    

    def _get_sectors(self) -> List[float]:
        """ Read the project file and the number of sectors to run for the projects """
        ET.register_namespace('', 'ProjectParameters.xsd')
        tree = ET.parse(self.project.project_file)
        root = tree.getroot()
        sectors = []
        for sector_element in root.iter('{ProjectParameters.xsd}Sector'):
            sectors.append(sector_element.text)

        return sectors
    
    def _get_threads(self) -> int:
        """ Read the project file and the number of simultaneous simulations to run for the projects """
        ET.register_namespace('', 'ProjectParameters.xsd')
        tree = ET.parse(self.project.project_file)
        root = tree.getroot()
        threads = 1
        for threads_element in root.iter('{ProjectParameters.xsd}ParallelCores'):
            threads = threads_element.text

        return threads

    
    def _replace_or_add_element(self, namespace, field: ET.Element, parameter: str, value: any):
        # This may or may not be available
        parameter_present = False
        for child in field.findall("{ProjectParameters.xsd}"+parameter, namespace):
            parameter_present = True
            child.text = str(value)
        if not parameter_present:
            ows_element = ET.SubElement(field, parameter)
            ows_element.text = str(value)

    def copy_project(self, AD: bool = True, windspeed: float = 7, AD_spacings: int = 8) -> str: 
        """Copies a project with different settings given by the input"""

        copy_name = f'{self.project.name}_AD_{AD}_windspeed_{windspeed}'
        print(f"Making {copy_name} from base {self.project.name}")
        base_dir = self.project.project_file.parent
        dest_dir = self.project.base_directory / copy_name
        
        shutil.copytree(base_dir, dest_dir, dirs_exist_ok=True)

        #Changing the Number of nodes and cells in the project
        ET.register_namespace('', 'ProjectParameters.xsd')
        tree = ET.parse(dest_dir  / f"{self.project.name}.ws")
        root = tree.getroot()

        namespace = {'project_parameters': 'ProjectParameters.xsd'}

        for WindFields in root.findall("{ProjectParameters.xsd}WindField"):
            self._replace_or_add_element(namespace, WindFields, "VelocityBoundaryLayer", windspeed)

        if AD:
            for CFD in root.findall("{ProjectParameters.xsd}CFD"):
                self._replace_or_add_element(namespace, CFD, "RefinementType", 3)
                self._replace_or_add_element(namespace, CFD, "NumberSpacings", AD_spacings)
                self._replace_or_add_element(namespace, CFD, "OWSFile", self.owsfile)

        else:
            for CFD in root.findall("{ProjectParameters.xsd}CFD"):
                self._replace_or_add_element(namespace, CFD, "RefinementType", 2)
                self._replace_or_add_element(namespace, CFD, "RefinementFileName", 'actuator_discs.bws')
        

        ET.indent(tree, '  ')
        tree.write(dest_dir  / f"{self.project.name}.ws", encoding = "UTF-8",  xml_declaration=True)

        project_file = dest_dir  / f"{self.project.name}.ws"
        project_file.replace(f'{dest_dir / copy_name}.ws')

        return copy_name

    def run_Terrains(self):
        # First run the AD projects
        for project_name in self.project_names:
            if 'AD_True' in project_name:

                self.run_Terrain(project_name)
                shutil.copy2(self.project.base_directory / project_name / 'dtm' / 'actuator_discs.bws', self.project.base_directory)
        # Copy actuator_discs.bws to all files
        for project_name in self.project_names:
            shutil.copy2(self.project.base_directory /'actuator_discs.bws', self.project.base_directory / project_name / 'dtm')
        for project_name in self.project_names:
            if 'AD_False' in project_name:
                self.run_Terrain(project_name)

        print("Finished running Terrain")
        

    def run_Terrain(self, name: str):
        os.makedirs('tmp/', exist_ok=True)
        os.chdir('tmp')
        
        print(f'Run Terrain for {name}')
        subprocess.run(f'"{self.windsim / "bin" / "Terrain.exe"}" "{os.path.join(self.project.base_directory, name, name+".ws")}" "{self.project.layout}" "{self.environment}"')
            
        print(f'Run Report[Terrain] for {name}')

        subprocess.run(f'"{self.windsim / "bin" / "Reports.exe"}" "{os.path.join(self.project.base_directory, name, name+".ws")}" "{self.project.layout}" "{self.environment}" 1')

        os.chdir('../')

        shutil.rmtree('tmp')

    def run_WindFields(self):
        # First run the AD projects
        for project_name in self.project_names:
            if 'AD_True' in project_name:
                self.run_WindField(project_name)

        # Then run the non-AD projects
        for project_name in self.project_names:
            if 'AD_False' in project_name:
                self.run_WindField(project_name)

        print("Finished running WindFields")
    

    def run_WindField(self, name: str):
        os.makedirs('tmp/', exist_ok=True)
        os.chdir('tmp')
        i = 1
        processes = []
        for sector in self.sectors:

            print(f'Running WindFields for {name}, sector: {sector}')
            command = f'"{self.windsim / "bin" / "WindFields.exe"}" "{os.path.join(self.project.base_directory, name, name+".ws")}" "{self.project.layout}" "{self.environment}" /si{i}'
            p=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)            
            processes.append(p)
            # subprocess.run(command)
            time.sleep(10)
            i += 1
        i = 0
        for p in processes:
            stdout,stderr = p.communicate()
            print(f"Windfield Out Sector {self.sectors[i]}: ",stdout)
            i+=1
        i=0
        for cp in processes:
            cp.wait()
            stdout,stderr = p.communicate()
            if p.returncode != 0:
                print(f"Windfield Error Sector {self.sectors[i]}: ",stderr)        
            i+=1
        
        print(f'Running Report[WindFields] for {name}')
        subprocess.run(f'"{self.windsim / "bin" / "Reports.exe"}" "{os.path.join(self.project.base_directory, name, name+".ws")}" "{self.project.layout}" "{self.environment}" 2')

        os.chdir('../')

        shutil.rmtree('tmp')



if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Running ActuatorDisk on WindSim Core.", epilog="Example: python actuator_disk.py '--mode' 'setup' '--project' 'C:/Users/<user>/Documents/WindSim Projects/Actuator_Disk_Flat/Actuator_Disk_Flat/Actuator_Disk_Flat.ws' '--windsim' 'C:/Program Files/WindSim/WindSim 12.0.0' '--environment' 'C:/Users/<user>/AppData/Roaming/WindSim/1200/Environment.xml' '--owsfile' 'AD_layout' '--layout' 'Layout 1.lws'")
    parser.add_argument('-m', '--mode', type=str, default='All',
                    help='Mode to run in: setup, terrain, windFields, all')
    parser.add_argument('-p', '--project', type=str, required=True,
                    help='Absolute path of the base project file you want to base the Actuator Disk Projects on.')
    parser.add_argument('-w', '--windsim', type=str, required=True,
                    help='Absolute path of the windsim installation')
    parser.add_argument('-e', '--environment', type=str, required=True, help='Absolute path of the environment file.')
    parser.add_argument('-o', '--owsfile', type=str, required=True, help='Name of the owsfile.')
    parser.add_argument('-l', '--layout',  type=str, required=True, help='Name of the layout file.')
    parser.add_argument('--low', type=float, default=7, help='The windspeed to use for the low case')
    parser.add_argument('--high', type=float, default=20, help='The windspeed to use for the high case')
    parser.add_argument('--AD_spacings', type=int, default=16, help='Number of cells to use for the Actuator Disk')

    args = parser.parse_args()
    # if not args.mode:
    #     args.machine=input('The mode is: ')
    # if not args.project:
    #     args.project=input('The project path is: ')

    

    
    runner = ActuatorDiskRunner(project_path = Path(args.project), windsim=Path(args.windsim), environment=Path(args.environment), owsfile=args.owsfile, layout=args.layout)

    if args.mode == 'setup':
        runner.setup_AD(windspeeds=[args.low, args.high], AD_spacings=args.AD_spacings)
    if args.mode == 'terrain':
        runner.setup_AD(windspeeds=[args.low, args.high], AD_spacings=args.AD_spacings)
        runner.run_Terrains()
    if args.mode == 'windfields':
        runner.setup_AD(windspeeds=[args.low, args.high], AD_spacings=args.AD_spacings)
        runner.run_Terrains()
        runner.run_WindFields()
    if args.mode == 'all':
        runner.setup_AD(windspeeds=[args.low, args.high], AD_spacings=args.AD_spacings)
        runner.run_Terrains()
        runner.run_WindFields()


