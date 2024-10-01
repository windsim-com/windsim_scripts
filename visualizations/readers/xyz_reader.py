# -*- coding: utf-8 -*-
#!/usr/bin/env python
# readers/xyz_reader.py


"""
Created on Thu Aug 26 14:45:54 2021
Modified on September 2023


@author: kklee & gvk
"""

import numpy as np
import py7zr

from pathlib import Path

from numpy.typing import NDArray
from typing import Any, TextIO, Dict

class Grid:
    def __init__(self):
        #==> cfd_nxp,cfd_nyp,cfd_nzp
        self.nx=0
        self.ny=0
        self.nz=0
        self.coord_phi: NDArray[np.float64]=np.array([])
        #CC=cell center
        self.coord_phiCC=np.array([])
        self.groundLevelCC: NDArray[Any]=np.array([])

        
    def read(self,fileIN: Path):
        self.file: Path=fileIN
        if not fileIN.is_file():
            with py7zr.SevenZipFile(fileIN.append_suffix('7z'), mode='r') as z: # type: ignore
                z.extractall(fileIn.parent) # type:ignore

        ID: TextIO = open(fileIN,'r');
        Lines: list[str] = ID.readline().split()
        nn = list(map(int,(Lines)))
        
        #nx,ny,nz gives the number of cells +1 (the number of nodes) --> for cell center coordinates we then have nx-1,ny-1,nz-1 values 
        self.nx = nn[0]
        self.ny = nn[1]
        self.nz = nn[2]
        self.coord_phi= np.zeros((self.nx,self.ny,self.nz,3))
        
        lenrecx = 5
        extra = 0
        
        nrec = int(self.nx * self.ny / lenrecx)
        if (self.nx*self.ny) % lenrecx != 0:
            nrec = nrec + 1
            extra = 5 - (self.nx*self.ny) % lenrecx
        
        dum_scl_1d: NDArray[np.float64] = np.zeros((self.nx*self.ny)+extra)
        for k in range(self.nz):
            
            # x block
            m = -lenrecx
            for irec in range(nrec):
                m = m + lenrecx
                Lines = ID.readline().split()
                entries = list(map(float,Lines))
                dum_scl_1d[m:lenrecx+m] = entries + ([1.] * (5-len(entries))) # Allow for less than 5 entries in some cases

                
            for j in range(self.ny):
                for i in range(self.nx):
                    self.coord_phi[i,j,k,0] = dum_scl_1d[i*self.ny+j]
            
            #% y block
            m = -lenrecx;
            for irec in range(nrec):
                m = m + lenrecx;
                Lines = ID.readline().split()
                entries = list(map(float,Lines))

                dum_scl_1d[m:lenrecx+m] = entries + ([1.] * (5-len(entries)))
            
            for j in range(self.ny):
                for i in range(self.nx):
                    self.coord_phi[i,j,k,1] = dum_scl_1d[i*self.ny+j]
            
            #% z block
            m = -lenrecx;
            for irec in range(nrec):
                m = m + lenrecx;
                Lines = ID.readline().split()
                entries = list(map(float,Lines))

                dum_scl_1d[m:lenrecx+m] = entries + ([1.] * (5-len(entries)))
            
            for j in range(self.ny):
                for i in range(self.nx):
                    self.coord_phi[i,j,k,2] = dum_scl_1d[i*self.ny+j] 
        ID.close()
        
    def computeCellCenterCoord(self):        
        self.coord_phiCC = np.zeros((self.nx-1,self.ny-1,self.nz-1,3))
        self.groundLevelCC = np.zeros((self.nx-1,self.ny-1))
        for j in range(self.ny-1):
            for i in range(self.nx-1):
                self.groundLevelCC[i,j] = (self.coord_phi[i,j,0,2] + self.coord_phi[i+1,j,0,2] + self.coord_phi[i+1,j+1,0,2]+  self.coord_phi[i,j+1,0,2])/4
            
        for k in range(self.nz-1):
            for j in range(self.ny-1):
                for i in range(self.nx-1):
                    
                    r_x_11 = (self.coord_phi[i+1,j,k,0] - self.coord_phi[i,j,k,0])/2 +self.coord_phi[i,j,k,0]
                    r_x_21 = (self.coord_phi[i+1,j+1,k,0] - self.coord_phi[i,j+1,k,0])/2 + self.coord_phi[i,j+1,k,0]
                    r_x_12 = (self.coord_phi[i+1,j,k+1,0] - self.coord_phi[i,j,k+1,0])/2 + self.coord_phi[i,j,k+1,0]
                    r_x_22 = (self.coord_phi[i+1,j+1,k+1,0] - self.coord_phi[i,j+1,k+1,0])/2 + self.coord_phi[i,j+1,k+1,0]
                    
                    self.coord_phiCC[i,j,k,0] = (r_x_11 + r_x_21 + r_x_12 + r_x_22)/4;
                    
                    r_y_11 = (self.coord_phi[i,j+1,k,1] - self.coord_phi[i,j,k,1])/2 + self.coord_phi[i,j,k,1]
                    r_y_21 = (self.coord_phi[i+1,j+1,k,1] - self.coord_phi[i+1,j,k,1])/2 + self.coord_phi[i+1,j,k,1]
                    r_y_12 = (self.coord_phi[i,j+1,k+1,1] - self.coord_phi[i,j,k+1,1])/2 + self.coord_phi[i,j,k+1,1]
                    r_y_22 = (self.coord_phi[i+1,j+1,k+1,1] - self.coord_phi[i+1,j,k+1,1])/2 + self.coord_phi[i+1,j,k+1,1]
                    
                    self.coord_phiCC[i,j,k,1] = (r_y_11 + r_y_21 + r_y_12 + r_y_22)/4;
                    
                    r_z_11 = (self.coord_phi[i,j,k+1,2] - self.coord_phi[i,j,k,2])/2 + self.coord_phi[i,j,k,2]
                    r_z_21 = (self.coord_phi[i+1,j,k+1,2] - self.coord_phi[i+1,j,k,2])/2 + self.coord_phi[i+1,j,k,2]
                    r_z_12 = (self.coord_phi[i,j+1,k+1,2] - self.coord_phi[i,j+1,k,2])/2 + self.coord_phi[i,j+1,k,2]
                    r_z_22 = (self.coord_phi[i+1,j+1,k+1,2]- self.coord_phi[i+1,j+1,k,2])/2 + self.coord_phi[i+1,j+1,k,2]
                    
                    self.coord_phiCC[i,j,k,2] = (r_z_11 + r_z_21 + r_z_12 + r_z_22)/4
                    #to give coordinates above ground level
                    #self.coord_phiCC[i,j,k,2] = self.coord_phiCC[i,j,k,2]- dum_scl_2d_l[i,j]
        
        
    def save(self, path: Path) -> None:
        np.savez_compressed(path, coord_centered=self.coord_phiCC, coord_vertices = self.coord_phi, coord_ground = self.groundLevelCC, headers=['x', 'y','z'])

    def load(self, path: Path) -> Dict[str, NDArray[np.float64]]:

        grid: Dict[str, NDArray[np.float64]] = np.load(path)
        self.coord_phiCC: NDArray[np.float64] = grid['coord_centered']
        self.coord_phi: NDArray[np.float64] = grid['coord_vertices']
        self.groundLevelCC: NDArray[np.float64] = grid['coord_ground']

        return grid




if __name__ == "__main__":

    base = Path('C:/Users/GullikKillie/Documents/WindSim Projects 12/Support/dummy/Oslofjorden')
    project_path = base / 'base - coarse_low_top - longer'
    temp_folder = base / 'base - coarse_low_top - longer' / 'my_documentation'

    #1. investigate the grid
    gridTest=Grid()
    gridTest.read(project_path / 'windfield' / '005.xyz')
    gridTest.save(temp_folder / 'coord_file.npz')
