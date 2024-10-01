# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Created on Thu Aug 26 14:45:54 2021
Modified on September 2023


@author: kklee & gvk
"""

import numpy as np
import fortranformat as ff
import matplotlib.pyplot as plt
import py7zr


import sys

from pathlib import Path


class Phi:
    def __init__(self):
        #all the variables specified in the beginning of the phi file
        self.Vars={}
        #especially important quantaties are stored extra
        self.nx=0
        self.ny=0
        self.nz=0
        
        #the x,y and z-locations give the east, north and high cell faces
        #Pcorr gives the mean pressure correction at each slab
        self.Xloc=[]
        self.Yloc=[]
        self.Zloc=[]
        self.Pcorr=[]
        
        #storedFields contain the fields that are available via this phi file and StoredFieldsNum the total number of stored fields
        self.FieldNames=[]
        self.NumStoredFields=0
        self.phi=np.array([])
        
        #store thw specified file
        self.file=""
            
    def getShape(self):
        #print(self.nz,self.nx,self.ny)
        #print(self.phi.shape)
        return self.phi[0].shape
        
    def getField(self,field):
        if(len(field)!=4):
            sys.exit('field variable needs to have 4 characters in length.')
        ifield=0
        for i in range(self.NumStoredFields):
            if self.FieldNames[i]==field:
                ifield=i
        #print(self.FieldNames[ifield], "is returned!!")
        return self.phi[ifield]             

        
    def read(self,fileIN: Path):
        
        self.file=fileIN
        if not fileIN.is_file():
           with py7zr.SevenZipFile(fileIN.append_suffix('7z'), mode='r') as z: # type: ignore
               z.extractall(fileIn.parent) # type:ignore


        phiFile = open(fileIN,'r');
        
        print("**********************READING ",fileIN,"**********************")

        #THE HEADER
        #line 1:;
        #phoenics title and version
        header= phiFile.readline()
        #print(header)
        
        self.Vars={}
        liste=[]
        #line2:
        #6 logical specifying the following variables
        reader=ff.FortranRecordReader('(1X,6L1)')
        liste=reader.read(phiFile.readline())
        self.Vars["CARTES"]=liste[0]
        self.Vars["ONEPHS"]=liste[1]
        self.Vars["BFC"]=liste[2]
        self.Vars["XCYCLE"]=liste[3]
        self.Vars["CCM"]=liste[4]
        self.Vars["LCMPRS"]=liste[5]
        
        #line 3:
        #14 integers specifying the following variables
        reader=ff.FortranRecordReader('(1X,7I10)')
        liste=reader.read(phiFile.readline())    
        self.Vars["NX"]=liste[0]
        self.Vars["NY"]=liste[1]
        self.Vars["NZ"]=liste[2]
        self.Vars["NPHI"]=liste[3]
        self.Vars["DEN1"]=liste[4]
        self.Vars["DEN2"]=liste[5]
        self.Vars["EPOR"]=liste[6]
    
        liste=reader.read(phiFile.readline())    
        self.Vars["NPOR"]=liste[0]
        self.Vars["HPOR"]=liste[1]
        self.Vars["VPOR"]=liste[2]
        self.Vars["LENREC"]=liste[3]
        self.Vars["NUMBLK"]=liste[4]
        self.Vars["NMATST"]=liste[5]
        self.Vars["NFMAK1"]=liste[6]
    
        #line 4:
        #6 float variables
        #fortran format: Ew.d with E specifying scientific notation, w is the total width including exponent and d specifies the number of decimal places
        #fortran format: 1P shifts the decimal point by one place for example 0.123E+03 is shown as 1.230E+02 when 1P is active
        #on chams website the specified format is '(1X,6(1PE13.6))' this is not working for negative numbers, since the first space 1X should be reserved for a minus sign --> choose 6(1PE13.6) only instead
#        reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
        reader=ff.FortranRecordReader('(6(1PE13.6))')
        liste=reader.read(phiFile.readline())    
        self.Vars["RINNER"]=liste[0]
        self.Vars["NPRPHI"]=liste[1]
        self.Vars["RNFPWV"]=liste[2]
        self.Vars["NFMAK2"]=liste[3]
        self.Vars["RDMAT1"]=liste[4]
        self.Vars["IDMAT2"]=liste[5]
        
        #print(self.Vars)
        self.nx=self.Vars["NX"]
        self.ny=self.Vars["NY"]
        self.nz=self.Vars["NZ"]  
    
        #line 5:
        #names of the variables (NPHI is the max. number of variables that could be stored)
        #to map the names with the TF values showing which variable is stored in the same order it is important to keep the order here!
        names=[]
        liste=[]
        for i in range(int(self.Vars["NPHI"]/19)):
            reader=ff.FortranRecordReader('(1X,19A4)')
            names.extend(reader.read(phiFile.readline()))
        if(self.Vars["NPHI"]%19!=0):
            reader=ff.FortranRecordReader('(1X,19A4)')
            liste=reader.read(phiFile.readline())
            for i in range(int(self.Vars["NPHI"]%19)):          
                names.append(liste[i])
        #print(names)
    
        
        #line 6:
        #x location of east cell faces (NX reals)
        #Xloc=[]
        for i in range(int(self.nx/6)):
            reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
            line=phiFile.readline()
            self.Xloc.extend(reader.read(line))
        if(self.nx%6!=0):
            reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
            line=phiFile.readline()
            liste=reader.read(line)
            for i in range(self.nx%6):
                self.Xloc.append(liste[i])
    
        
        #line 7:
        #y location of north cell faces (NY reals)
        #Yloc=[]
        for i in range(int(self.ny/6)):
            reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
            line=phiFile.readline()
            self.Yloc.extend(reader.read(line))
        if(self.ny%6!=0):
            reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
            line=phiFile.readline()
            liste=reader.read(line)
            for i in range(self.ny%6):
                self.Yloc.append(liste[i])
        
        
        #line 8:
        #z location of high cell faces (NZ reals)
        #Zloc=[]
        for i in range(int(self.nz/6)):
            reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
            line=reader.read(phiFile.readline())
            self.Zloc.extend(line)
        if(self.nz%6!=0):
            reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
            line=phiFile.readline()
            liste=reader.read(line)
            for i in range(self.nz%6):
                self.Zloc.append(liste[i])
        #print(Zloc)
        
        
        #line 9:
        #mean pressure corrections at each slab (Nz reals)
        #Pcorr=[]
        for i in range(int(self.nz/6)):
            reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
            self.Pcorr.extend(reader.read(phiFile.readline()))
        if(self.nz%6!=0):
            reader=ff.FortranRecordReader('(1X,6(1PE13.6))')
            liste=reader.read(phiFile.readline())
            for i in range(self.nz%6):
                self.Pcorr.append(liste[i])
      
        #line 10:        
        #stored variables (NPHI logicals stating if the corresponding variable at the same place in names array is containe in the current phi file)
        reader=ff.FortranRecordReader('(1X,79L1)')
        #storing a list of booleans indicating which variables of names is stored
        StoredFields=[]
        for i in range(int(self.Vars["NPHI"]/79)):
            StoredFields.extend(reader.read(phiFile.readline()))
        if(self.Vars["NPHI"]%79!=0):
            liste=reader.read(phiFile.readline())
            for i in range(int(self.Vars["NPHI"]%79)):          
                StoredFields.append(liste[i])
                
        #print(StoredFields,len(StoredFields))
        #extract the stored variables in the right order
        self.NumStoredFields=0
        for i,b in enumerate(StoredFields):
            if b:
                self.NumStoredFields+=1
                self.FieldNames.append(names[i])
                
        print("---------------------------------------------------------------------------------")
        print("---------------------------CONTAINED VARIABLES-----------------------------------")
        print("---------------------------------------------------------------------------------")
        print(self.NumStoredFields, " stored variables are found: ",self.FieldNames)
        print("---------------------------------------------------------------------------------")
        print("---------------------------------------------------------------------------------")    
    
          
        #THE FIELDS  
        #fortran format: Ew.d with E specifying scientific notation, w is the total width including exponent and d specifies the number of decimal places
        #fortran format: 1P shifts the decimal point by one place for example 0.123E+03 is shown as 1.230E+02 when 1P is active
        #on chams website the specified format is '(1X,6(1PE13.6))' this is not working for negative numbers, since the first space 1X should be reserved for a minus sign --> choose 6(1PE13.6) only instead
        reader=ff.FortranRecordReader('(6(1PE13.6))')
        self.phi=np.empty([self.NumStoredFields,self.nz,self.nx,self.ny])
        for iz in range(self.nz):
            for iphi in range(self.NumStoredFields):
                slab=[]
                liste=[]
                for ixy in range(int((self.nx*self.ny)/6)):
                    line=phiFile.readline()
                    slab.extend(reader.read(line))
                if((self.nx*self.ny)%6!=0):
                    line=phiFile.readline()
                    liste=reader.read(line)
                    #print("last line :",(Vars["NX"]*Vars["NY"])%6,line)
                    for i in range((self.nx*self.ny)%6):
                        slab.append(liste[i])
                #print(Vars["NX"]*Vars["NY"])
                #print(len(slab))
                for ix in range(self.nx):
                    for iy in range(self.ny):   
                            self.phi[iphi,iz,ix,iy]=slab[iy+ix*(self.ny)]
                            
    def plotVerticalProfile(self,grid,X=0,Y=0,field="P1  ",fig=None,index=111):
        if fig is None:
            fig=plt.figure()
       
        f=self.getField(field)
        #print(grid.nx,grid.ny,grid.nz)
        #print(grid.coord_phiCC.shape)
        #print(f.shape)

        ind=list(map(int,str(index)))
        if len(ind)==3:
            ax=fig.add_subplot(index)
            #is the same as ax=fig.add_subplot(ind[0],ind[1],ind[2])
        elif len(ind)==4:
            ax=fig.add_subplot(ind[0],ind[1],int(str(ind[2])+str(ind[3])))
        else:
            sys.exit("Index with more than 4 places is not accepted!")
        ax.set_title('IX='+str(X) +', IY='+ str(Y) )
        #ax.set_title('Verical Profile for '+field+' at IX='+str(X) +', IY='+ str(Y) )
        ax.set_xlabel(field)
        ax.set_ylabel('z')  
        ax.plot(f[:,X,Y],grid.coord_phiCC[X,Y,:,2],color='blue')
        ax.scatter(f[:,X,Y],grid.coord_phiCC[X,Y,:,2],marker="x",color="blue")
        plt.show()
                        
    def plotField(self,grid,field="P1  "):
        print("vtk plot not implemented yet")

    def save(self, path: Path):
        np.savez_compressed(path, data=self.phi, headers=self.FieldNames)

    def load(self, path: Path):
        
        # print(fields['headers'])

        return np.load(path)



if __name__ == "__main__":

    """Here we assume that we have a project named dummy and the contents of the temp folder has been stored in my_documentation.
    The sector 005 has also been completed and lies in the windfields solver. Also need to unzip the full xyz file"""

    base = Path('C:/Users/GullikKillie/Documents/WindSim Projects 12/Support/dummy/Oslofjorden')
    project_path = base / 'base - coarse_low_top - longer'
    temp_folder = base / 'base - coarse_low_top - longer' / 'my_documentation'

    # grid = Grid()
    # grid.read(project_path / 'WindField' / '005_red.xyz')
    # grid.getCellCenterCoord()

    #%%
    phi_file=Phi()
    phi_file.read(project_path / "windfield" / "005.phi")
    # phi_file.plotVerticalProfile(grid)
    phi_file.save(temp_folder / 'phi_file.npz')

    # def load():
    #     fields = np.load(temp_folder / 'phi_file.npz')
    #     # print(fields['headers'])

    # print(timeit.timeit(load, number=10000, globals=globals()))

    # print(fields['headers'])
    # print(fields['data'][1,1,1])
# %%
