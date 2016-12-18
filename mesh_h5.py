import os
import sys
import h5py
import math
import scipy
import numpy as np
from stl import mesh
import mahotas as mh
from skimage import measure

#import matplotlib.pyplot as plt

MAX_Z = 100
MARGIN = 2
NEURON_ID = 18915
SPLINE_RESOLUTION = 1/16.
OUT_FOLDER = sys.argv[2]
NEURON_ID = int(sys.argv[1])
OUTNAME = os.path.join(OUT_FOLDER,str(NEURON_ID)+'_mesh.stl')
DATA = '/n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5'
DATA = '/home/harvard/2017/data/bf/1017/synapse.h5'

def threshold(arr, val):
    out = np.ones(arr.shape, dtype=arr.dtype)*val
    return np.equal(arr,out)

class Edger:
    def __init__(self,spots):

        # Generate edge_image output and edges input 
        self.edge_image = np.zeros(spots.shape,dtype=np.bool)
        self.max_shape = np.array(self.edge_image.shape)-1
        self.edges = measure.find_contours(spots, 0)
        self.edges.sort(self.sortAll)

    def run(self, edgen):
        if len(edgen) <= 4:
            return []
        y,x = zip(*edgen)
        # get the cumulative distance along the contour
        dist = np.sqrt((np.diff(x))**2 + (np.diff(y))**2).cumsum()[-1]
        # build a spline representation of the contour
        spline, u = scipy.interpolate.splprep([x, y])
        res =  int(math.ceil(SPLINE_RESOLUTION*dist))
        sampler = np.linspace(0, u[-1], res)

        # resample it at smaller distance intervals
        interp_x, interp_y = scipy.interpolate.splev(sampler, spline)
        iy,ix = [[int(math.floor(ii)) for ii in i] for i in [interp_x,interp_y]]
        interp = [np.clip(point,[0,0],self.max_shape) for point in zip(ix,iy)]

        mh.polygon.fill_polygon(interp,self.edge_image)

    def sortAll(self,a,b):
        xylists = [zip(*a),zip(*b)]
        da,db = [np.array([max(v)-min(v) for v in l]) for l in xylists]
        return 2*int((da-db < 0).all())-1

    def runAll(self,k):
        if len(self.edges):
            self.run(self.edges[0])

        return self

class Mesher:
    def __init__(self,volume):
        self.volume = volume
        self.slices = range(self.volume.shape[0])
        self.edge_vol = np.zeros(volume.shape, dtype=np.bool)
        self.runAll()
    def run(self,k):
        edgy = Edger(self.volume[k]).runAll(k)
        self.edge_vol[k] = edgy.edge_image
        print ('k ',k)
    def runAll(self):
        for sliced in self.slices:
            self.run(sliced)
        return self
    def store_mesh(self, filename, bboff):

        arr = [self.edge_vol,0]
        params = {
            'spacing': (1., 1., 1.,),
            'gradient_direction':'ascent'
        }
        verts, faces = measure.marching_cubes(*arr,**params)
        applied_verts = verts[faces]

        mesh_data = np.zeros(applied_verts.shape[0], dtype=mesh.Mesh.dtype)

        for i, v in enumerate(applied_verts):
            mesh_data[i][1] = v + bboff

        m = mesh.Mesh(mesh_data)
        with open(filename, 'w') as f:
            m.save(filename, f)
        return m

#
#
#


with h5py.File(DATA,'r') as f:
    upsamp = 10
    volstack = f[f.keys()[0]]
    z,y,x = volstack.shape
    z = min(z,MAX_Z)

    thresholded_3d = np.zeros([upsamp*z,y,x], dtype=np.bool)
    box_tl,box_br = [[y,x],[0,0]]
    box_up,box_dn = [-1,-1]

    for SLICE in range(z):
        print (SLICE , '/', z)
        za,zb = [upsamp*i for i in [SLICE,SLICE+1]]
        thresholded = threshold(volstack[SLICE], NEURON_ID)
        thresholded_3d[za:zb] = thresholded

        if thresholded.any():
            extent = np.argwhere(thresholded)
            box_tl = np.c_[extent.min(0),box_tl].min(1)
            box_br = np.c_[extent.max(0),box_br].max(1)
            box_dn = za if box_dn < 0 else box_dn
            box_up = zb

zo,ze = [box_dn,box_up]
yo,xo = box_tl
ye,xe = box_br

print ('shape at ',zo,yo,xo)
volume = thresholded_3d[zo:ze, yo:ye, xo:xe].swapaxes(0,1)
vy,vz,vx = volume.shape
z_margin = np.zeros([vy,MARGIN,vx], dtype=bool)
volume = np.concatenate((z_margin,volume,z_margin),axis=1)
x_margin = np.zeros([vy,vz+2*MARGIN,MARGIN], dtype=bool)
volume = np.concatenate((x_margin,volume,x_margin),axis=2)
bb_offset = (yo, zo-MARGIN, xo-MARGIN)

meshy = Mesher(volume)
print ('storing mesh..')
meshy.store_mesh(OUTNAME, bb_offset)
