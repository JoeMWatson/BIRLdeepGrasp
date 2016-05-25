#!/usr/bin/env python
import numpy as np
import cv_bridge
import cv2.cv as cv
import cv2
import sys
import os
import rospy
import baxter_interface
from std_msgs.msg import String, Header
from sensor_msgs.msg import Image
import argparse
import numpy as np
from grasp.msg import vec
from rospy.numpy_msg import numpy_msg


qw =  0.029
qx =  0.872
qy = -0.487
qz =  0.041
R = np.array([[1-2*qy**2-2*qz**2,2*qx*qy-2*qz*qw,2*qx*qz+2*qy*qw],[2*qx*qy+2*qz*qw,1-2*qx**2-2*qz**2,2*qy*qz-2*qx*qw],[2*qx*qz-2*qy*qw,2*qy*qz+2*qx*qw,1-2*qx**2-2*qy**2]])
K = np.array([[541.56,0,368.666],[0,551.78,156.74],[0,0,1]])
P = np.array([[568.665,0,381.959,0],[0,558.37,137.1,0],[0,0,1,0]])
T = np.array([[0.6],[0.387],[442]])
RT = np.concatenate((R,T),axis=1);
P2 = np.dot(K,RT)

def callback(data):
	u = data.data[0]
	v = data.data[1]
	th = data.data[2]
	print u,v,th

def main(args):
	#global x,y
	rospy.init_node('objectGrasp', anonymous=True)
	rospy.Subscriber("vec", numpy_msg(vec), callback)
	#print x,y
	rospy.spin()
	return 0

if __name__ == '__main__':
	main(sys.argv)
