import random
from CellModeller.Regulation.ModuleRegulator import ModuleRegulator
from CellModeller.Biophysics.BacterialModels.CLBacterium import CLBacterium
from CellModeller.GUI import Renderers
import numpy
import math

from CellModeller.Signalling.GridDiffusion import GridDiffusion #add
from CellModeller.Integration.CLCrankNicIntegrator import CLCrankNicIntegrator #add
from CellModeller.Integration.ScipyODEIntegrator import ScipyODEIntegrator #add


max_cells = 400000
#Specify parameter for solving diffusion dynamics #Add
grid_dim = (64, 8, 12) # dimension of diffusion space, unit = number of grid
grid_size = (4, 4, 4) # grid size
grid_orig = (-128, -14, -8) # where to place the diffusion space onto simulation space


def setup(sim):
    # Set biophysics, signalling, and regulation models
    biophys = CLBacterium(sim, max_substeps=8, max_cells=max_cells, max_contacts=32, max_sqs=192**2, jitter_z=False, reg_param=2, gamma=10)
 
    # add the planes to set physical  boundaries of cell growth
    biophys.addPlane((0,-16,0), (0,1,0), 1)
    biophys.addPlane((0,16,0), (0,-1,0), 1)

    sig = GridDiffusion(sim, 1, grid_dim, grid_size, grid_orig, [10.0])
    integ = CLCrankNicIntegrator(sim, 1, 5, max_cells, sig, boundcond='reflect')

    # use this file for reg too
    regul = ModuleRegulator(sim, __file__)	
    # Only biophys and regulation
    sim.init(biophys, regul, sig, integ)


    # Specify the initial cell and its location in the simulation
    sim.addCell(cellType=0, pos=(-20.0,0,0))  #Add
    sim.addCell(cellType=1, pos=(20.0,0,0)) #Add



    # Add some objects to draw the models
    therenderer = Renderers.GLBacteriumRenderer(sim)
    sim.addRenderer(therenderer)
    sigrend = Renderers.GLGridRenderer(sig, integ) # Add
    sim.addRenderer(sigrend) #Add

    sim.pickleSteps = 10



def init(cell):
    # Specify mean and distribution of initial cell size
    cell.targetVol = 2.5 + random.uniform(0.0,0.5)
    # Specify growth rate of cells
    cell.growthRate = 2.0

def numSignals(): 
    return 1

def numSpecies(): 
    return 1

def specRateCL(): # Add if/else
    return '''
    const float D1 = 0.1f;
    const float k1 = 1.f;

    float x0 = species[0];
    float x0_sig = signals[0];
    
    if (cellType==0){
    rates[0] = k1 + D1*(x0_sig-x0)*area/gridVolume;
    } else {
    }
    '''

    # D1 = diffusion rate of x0 
    # k1 = production rate of x0
    

  

def sigRateCL(): #Add
    return '''
    const float D1=0.1f;
    float x0 = species[0];
    float x0_sig = signals[0];
    rates[0] = -D1*(x0_sig-x0)*area/gridVolume;
    '''
    # D1 = diffusion rate of x0 

def update(cells):
    #Iterate through each cell and flag cells that reach target size for division
    for (id, cell) in cells.iteritems():
        cell.color = [0.1, 0.1+cell.species[0]/20.0, 0.1]
        if cell.volume > cell.targetVol:
            a = 1
            cell.asymm = [a,1]
            cell.divideFlag = True

def divide(parent, d1, d2):
    # Specify target cell size that triggers cell division
    d1.targetVol = 2.5 + random.uniform(0.0,0.5)
    d2.targetVol = 2.5 + random.uniform(0.0,0.5)
