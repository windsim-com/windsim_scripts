# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Created on Thu Aug 26 14:45:54 2021
Modified on September 2024


Note, may need to run as python -m visualizations.visualizations from parent folder
For Visual Studio Code use launch.json
        ```
            "module": "visualizations.${fileBasenameNoExtension}",
        ```

@author: kklee & gvk
"""
from pathlib import Path
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
from pyvista import Plotter

from .readers.xyz_reader import Grid
from .readers.phi_reader import Phi


import matplotlib.animation as animation
from matplotlib.widgets import Slider

pv.global_theme.axes.box = True
pv.global_theme.axes.show = True

class Slicer():
    def __init__(self, coord: Path, phi: Path, var: str='VCRT'):
        self.coord = np.load(coord)['coord_centered']
        self.phi = np.load(phi)
        self.fig, self.ax = plt.subplots()
        self.field = self.get_field(var).T
        self.X = self.coord[:,:,:,0] 
        self.Y = self.coord[:,:,:,1] 
        self.Z = self.coord[:,:,:,2]
        self.label = None
        self.x_grid = None
        self.y_grid = None
        self.plane='y'

        self.setup_fig(var, self.plane)
        self.update(0)

        print(f'The coordinate system has the following dimensions: (x,y,z)={self.X.shape}')
        print(f'The field  has the following dimensions: (x,y,z)={self.field.shape}')


    def get_field(self, var: str):
        try:
            field = self.phi['data'][np.nonzero(self.phi['headers'] == var)[0][0]]
            field = field.transpose(0,2,1)
        except IndexError: 
            exit(f"Exiting: No data found: Possible variables from phi file: {self.phi['headers']}")
        return field
    
    def _slider(self):
        axamp = plt.axes([0.2, .03, 0.50, 0.02])
        if self.plane=='x':
            self.samp = Slider(axamp, 'Meter', 0, self.X.shape[1]-1, valinit=0)
        elif self.plane =='y':
            self.samp = Slider(axamp, 'Meter', 0, self.Y.shape[0]-1, valinit=0)

        self.samp.on_changed(self.update_slider)

    def setup_fig(self, var: str, plane: str='x'):
        fig, ax = self.fig, self.ax
        ax.set_title('Boundary Conditions for '+var+' at border '+ plane)
        ax.set_xlabel(var)
        ax.set_ylabel('z')
        
        if plane=='x':
            self.label = self.ax.contourf(self.X[:,0,:], self.Z[:,0,:], self.field[:,0,:self.Z.shape[1]])
        elif plane =='y':
            self.label = self.ax.contourf(self.Y[0,:,:], self.Z[0,:,:], self.field[0,:,:self.Z.shape[1]])
        cbar = fig.colorbar(self.label)
        cbar.ax.set_ylabel(var)
        self._slider()
        fig.canvas.mpl_connect('button_press_event', self.on_click)


    def update_plot(self, num):
        return self.label
    
    def update_slider(self, val):
        self.update(val)

    def update(self, val):
        val=int(val)
        # print(val)
        if self.x_grid: # Test all but should work
            for c in self.label.collections:
                c.remove()
            for item in self.x_grid:
                item.remove()
            for item in self.y_grid:
                item.remove()
        if self.plane == 'x':
            self.label = self.ax.contourf(self.X[:,val,:], self.Z[:,val,:], self.field[:,val,:self.Z.shape[1]])
            self.x_grid = self.ax.plot(self.X[:,val,:], self.Z[:,val,:], 'k-', lw=0.5, alpha=0.5)
            self.y_grid = self.ax.plot(self.X[:,val,:].T, self.Z[:,val,:].T, 'k-', lw=0.5, alpha=0.5)
        elif self.plane =='y':
            self.label = self.ax.contourf(self.Y[val,:,:], self.Z[val,:,:], self.field[val,:,:self.Z.shape[1]])
            self.x_grid = self.ax.plot(self.Y[val,:,:], self.Z[val,:,:], 'k-', lw=0.5, alpha=0.5)
            self.y_grid = self.ax.plot(self.Y[val,:,:].T, self.Z[val,:,:].T, 'k-', lw=0.5, alpha=0.5)


        self.fig.canvas.draw_idle()

    def on_click(self, event):
        # Check where the click happened
        return
    
    





class Visualizator():
    def __init__(self, coords: Path, ):
        self.path = coords

    def elevation(self):
        coord = np.load(self.path /'coord_file.npz')['coord_centered']
        fig,ax=plt.subplots(figsize=(14,14))
        ax.set_title('Terrain')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        
        plt.contourf(coord[:,:,0,0], coord[:,:,0,1], coord[:,:,0,2],cmap='gist_earth')#cmap='terrain'
        plt.colorbar()
        plt.show()



    def slice3D(self, variable: str, plotter: Plotter):
        fields = np.load(temp_folder / 'phi_file.npz')
        coord = np.load(self.path /'coord_file.npz')['coord_centered']

        try:
            field = fields['data'][np.nonzero(fields['headers'] == variable)[0][0]]
            field = field.transpose(0,2,1)
            print(field.shape)
        except IndexError: 
            exit(f"Exiting: No data found: Possible variables from phi file: {fields['headers']}")
        
        grid = pv.StructuredGrid(coord[:,:,:,0], coord[:,:,:,1], coord[:,:,:,2]*7)
        grid[variable] = field.flatten()
        plotter.add_mesh_slice(grid)
        return plotter
    
class Slicer3D:
    def __init__(self, coord_path: Path, phi_path: Path):
        self.coords = np.load(coord_path)['coord_centered']
        self.fields = np.load(phi_path)
        self.field = self._field()
        self.field_grid = pv.StructuredGrid(self.coords[:,:,:,0], self.coords[:,:,:,1], self.coords[:,:,:,2]*7)

    def initiate_plotter(self):
        plotter = pv.Plotter(notebook=False, )
        return plotter
    
    def elevation3D(self, plotter: Plotter):
        coords = self.coords

        ground = pv.StructuredGrid(coords[:,:,0,0], coords[:,:,0,1], coords[:,:,0,2]*7)
        ground['Elevation'] = ground.points[:,2]
        plotter.add_mesh(ground, scalars=ground['Elevation'], cmap='gist_earth', name='Terrain')#, show_edges=True)

        return plotter
    
    def _field(self, variable: str='VCRT'):
        try:
            field = self.fields['data'][np.nonzero(self.fields['headers'] == variable)[0][0]]
            field = field.transpose(0,2,1)
        except IndexError: 
            exit(f"Exiting: No data found: Possible variables from phi file: {self.fields['headers']}")
        return field
    
    def _set_field_grid_variable(self, variable: str= 'VCRT'):
        self.field = self._field(variable)
        self.field_grid[variable] = self.field.flatten()


    
    # def draggable_slice(self, variable: str, plotter: Plotter):
    #     field_grid = pv.StructuredGrid(self.coords[:,:,:,0], self.coords[:,:,:,1], self.coords[:,:,:,2]*7)
    #     field_grid[variable] = self.field.flatten()
    #     plotter.add_mesh_slice(field_grid)
    #     return plotter



class Slice():
    def __init__(self, mesh):
        self.mesh = mesh
        self.output = self.mesh.slice()  # Expected PyVista mesh type
        # default parameters
        self.center = self.mesh.center
        self.kwargs = {
            'cell': 30,
            }

    def __call__(self, param, value):
        self.kwargs[param] = value
        self.update()

    def update(self):
        # This is where you call your simulation
        print(self.kwargs)
        result = self.mesh.slice(origin=(self.mesh.center[0], self.kwargs['cell'], self.mesh.center[2]), normal='y')
        self.output.copy_from(result)
        return


if __name__ == "__main__":
    # Prepare and unzip
    base = Path('C:/Users/GullikKillie/Documents/WindSim Projects 12/patagonia-2024-06-12T080332/')
    project_path = base
    doc_folder = base  / 'my_documentation'
    sec_to_plot = '072_red'

    # Loading grid
    grid=Grid()
    grid.read(project_path / 'windfield' / f'{sec_to_plot}.xyz')
    grid.computeCellCenterCoord()
    grid.save(path = doc_folder / f'{sec_to_plot}.xyz.npz')
    grid_data = grid.load(path = doc_folder / f'{sec_to_plot}.xyz.npz')

    # Loading phi file
    phi=Phi()
    phi.read(project_path / 'windfield' / f'{sec_to_plot}.phi')
    phi.save(path = doc_folder / f'{sec_to_plot}.phi.npz')

    # Variable to select
    # var = 'VCRT'
    var = 'UCRT'
    # var = 'KE  '
    # var= "TEM1"
    # var= 'P1  '

    slicer = Slicer(coord=doc_folder / f'{sec_to_plot}.xyz.npz', phi=doc_folder/ f'{sec_to_plot}.phi.npz', var=var)
    ani = animation.FuncAnimation(slicer.fig, slicer.update_plot, interval=1, save_count=500)
    plt.show()

    slicer3D = Slicer3D(coord_path= doc_folder / f'{sec_to_plot}.xyz.npz', phi_path= doc_folder / f'{sec_to_plot}.phi.npz')
    plotter = slicer3D.initiate_plotter()
    plotter = slicer3D.elevation3D(plotter)
    # plotter = slicer3D.draggable_slice('TEM1', plotter)
    slicer3D._set_field_grid_variable('VCRT')
    slice = Slice(slicer3D.field_grid)
    print(slicer3D.field_grid.bounds)
    plotter.add_mesh(slice.output)
    plotter.add_slider_widget(
        callback=lambda value: slice('cell', int(value)),
        rng=[slicer3D.field_grid.bounds[0], slicer3D.field_grid.bounds[1]],
        value=30,
        title="Slice",
        pointa=(0.025, 0.1),
        pointb=(0.31, 0.1),
        style='modern',
    )

    plotter.show()










