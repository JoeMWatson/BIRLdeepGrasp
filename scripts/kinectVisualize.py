#!/usr/bin/env python

import numpy as np
from math import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

cloudy = np.load('cloudy.npy')
np.nan_to_num(cloudy)
graspPoint = np.load('graspPoint.npy')

#print cloudy[0:10,:]
#print cloudy[100,:]
#size = np.max(cloudy.shape)
#colours = 
print cloudy.shape
origin = np.transpose(np.matrix([[0,0,0],[1,0,0],[0,1,0],[0,0,1]]))
print cloudy[:,3:6]

fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')

ax.scatter(cloudy[::100,0],cloudy[::100,1],cloudy[::100,2],color=(cloudy[::100,5],cloudy[::100,4],cloudy[::100,3]))
#ax.plot([origin[0,0],origin[0,1]],[origin[1,0],origin[1,1]],zs=[origin[2,0],origin[2,1]],color = 'c') #
#ax.plot([origin[0,0],origin[0,2]],[origin[1,0],origin[1,2]],zs=[origin[2,0],origin[2,2]],color = 'k') #
#ax.plot([origin[0,0],origin[0,3]],[origin[1,0],origin[1,3]],zs=[origin[2,0],origin[2,3]],color = 'm') #
plt.show()
