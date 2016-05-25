#!/usr/bin/env python
import tf
import numpy as np

R1 = tf.transformations.quaternion_matrix([-0.448, 0.758, -0.475, -0.018])[0:3,0:3]
T1 = np.array([0.523,0.414,0.449])
R2 = tf.transformations.quaternion_matrix([0.082, 0.967, -0.154, -0.186])[0:3,0:3]
T2 = np.array([0.167,-0.556,0.392])

print R1
print T1
print R2
print T2

print T1.shape
print R1.shape

RT = np.dot(R2,R1)
TT = np.add(T1,np.dot(np.linalg.inv(R1),T2))

print RT
print TT

RT2 = np.zeros((4,4))
RT2[0:3,0:3] = RT
RT2[3,3] = 1
euler = tf.transformations.euler_from_matrix(RT2)
print euler
