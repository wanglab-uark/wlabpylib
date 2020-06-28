'''
srmat2py.py
Convert SRM results from matlab to python
All rights reserved (c) 2019 Yong Wang
'''
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from matplotlib import path
import copy
import sys

def progressbar(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def get_bac_boundary(ox=0, oy=0, theta=0, 
        width=2000, height=500):
    '''
    get vertices of the bacterium boundary. The bacteria is a rod shape 
    (two circular caps with one rectangle).The center of the bacterium
    is at (ox, oy). The orientation of the bacterium is with an angle of 
    theta (in rad). The width and height are specified too.
    '''
    vx= list()
    vy= list()
    # top
    xc=(width-height)/2.0
    x=np.linspace(-xc,xc,50)
    y=x*0+height/2.0
    vx = vx + x.tolist()
    vy = vy + y.tolist()
    # right circle
    th = np.linspace(np.pi/2, -np.pi/2, 50)
    x = height/2.0*np.cos(th)+xc
    y = height/2.0*np.sin(th)
    vx = vx + x.tolist()
    vy = vy + y.tolist()
    # bottom
    x = np.linspace(xc,-xc,50)
    y = x*0-height/2
    vx = vx + x.tolist()
    vy = vy + y.tolist()
    # left cicle
    th = np.linspace( 3*np.pi/2, np.pi/2, 50)
    x = height/2*np.cos(th)-xc
    y = height/2*np.sin(th)
    vx = vx + x.tolist()
    vy = vy + y.tolist()
    # rotate
    v = np.array([vx,vy]).transpose()
    Rot = np.array([ [np.cos(theta), np.sin(theta)],
                        [-np.sin(theta), np.cos(theta)]])
    v = np.matmul(v, Rot)
    vx = v[:,0]
    vy = v[:,1]
    # shift
    vx = vx + ox
    vy = vy + oy
    return (vx, vy)

def test_get_bac_boundary():
    params = [
        [0, 0, 0, 2000, 500],
        [+1000, -300, 0, 2000, 500],
        [-1000, +1000, 45.0/180*np.pi, 2000, 500],
        [-1000, +1000, 45.0/180*np.pi, 4000, 2000],
        [0, +1000, 240.0/180*np.pi, 2000, 500]
    ]
    for param in params:
        plt.figure()
        vx, vy = get_bac_boundary(*param)
        plt.plot(vx, vy, 'b-')
        plt.axis('equal')
        plt.title('%.1f,%.1f,%.1f,%.1f,%.1f' % 
            (param[0], param[1], param[2], param[3], param[4]))
        plt.show()

def load_srmseg_proj(sspfn='filename.srmseg_proj.mat', margin=-10):
    '''
    load .srmseg_proj.mat file
    The output is a list of cells. Each cell is a dict.
    '''
    output = list()
    if sspfn.endswith('.srmseg_proj.mat'):
        # load in localization data
        locs = np.loadtxt(sspfn[:-16])
        xys = list(zip(locs[:,0], locs[:,1])) # for determining if locs are in each cell
        # load in srmseg_proj.mat data
        lbc = sio.loadmat(sspfn)['project']['LocByCell'][0][0]
        # go through all cells
        for i, c in enumerate(lbc):
            # get the parameters
            ox = c['ox'][0][0][0]
            oy = c['oy'][0][0][0]
            width = c['width'][0][0][0]
            height = c['height'][0][0][0]
            theta = c['theta'][0][0][0]
            # determine the boundary (note that the vx,vy in the mat are not updated)
            vx, vy = get_bac_boundary(ox, oy, theta, width, height)
            vp = path.Path(list(zip(vx,vy)))
            incell = vp.contains_points(xys, radius=margin)
            idx = np.argwhere(incell)[:,0]
            if len(idx)>0:
                loc = locs[idx,:]
                cell = {'sspfn': sspfn, 'locfn': sspfn[:-16],
                        'cell_id': i,
                        'ox': ox, 'oy': oy, 
                        'width': width, 'height': height,
                        'theta': theta,
                        'vx': vx, 'vy': vy,
                        'idx': idx, 'loc': loc}
                output.append(cell)
    else:
        print('ERROR: load_srmseg_proj(sspfn): sspfn must ends with ".srmseg_proj.mat"!')
    return output

def translate_rotate_cell(cell):
    '''
    translate the cell to origin (0,0) and rotate the cell such that the 
    long axis is along the x-axis.
    '''
    newcell = copy.deepcopy(cell)
    ox = newcell['ox']
    oy = newcell['oy']
    theta = newcell['theta']
    loc = newcell['loc']
    pos = loc[:,[0,1]]
    pos[:,0] = pos[:,0] - ox
    pos[:,1] = pos[:,1] - oy
    R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    pos = np.matmul(pos,R)
    loc[:,0] = pos[:,0]
    loc[:,1] = pos[:,1]
    newcell['ox'] = 0
    newcell['oy'] = 0
    newcell['theta'] = 0
    newcell['loc'] = loc
    return newcell

