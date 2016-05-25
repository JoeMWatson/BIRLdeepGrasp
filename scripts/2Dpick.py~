#!/usr/bin/env python
import numpy as np
import cv_bridge
import cv2.cv as cv
import cv2
import sys
import os
import rospy
import baxter_interface
from std_msgs.msg import Header
from sensor_msgs.msg import Image
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Point,
    Quaternion,
)

from baxter_core_msgs.srv import (
    SolvePositionIK,
    SolvePositionIKRequest,
)
import argparse
import numpy as np
from grasp.msg import vec
from rospy.numpy_msg import numpy_msg
import tf

#leftLimb = baxter_interface.Limb('left')

def ik_test(pose):
        #rospy.init_node("rsdk_ik_service_client")
        ns = "ExternalTools/left/PositionKinematicsNode/IKService"
        iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
        ikreq = SolvePositionIKRequest()
        hdr = Header(stamp=rospy.Time.now(), frame_id='base')
	new_pose = {'left':PoseStamped(
			header=hdr,
			pose=Pose(
				position=Point(
					x=pose[0],
					y=pose[1],
					z=pose[2],
				),
				orientation=Quaternion(
					x=pose[3],
					y=pose[4],
					z=pose[5],
					w=pose[6],
				),
			),
		),
	}
	ikreq.pose_stamp.append(pose)
        try:
            rospy.wait_for_service(ns, 5.0)
            resp = iksvc(ikreq)
        except (rospy.ServiceException, rospy.ROSException), e:
            rospy.logerr("Service call failed: %s" % (e,))
            return 1
	if (resp.isValid[0]):
        	print("SUCCESS - Valid Joint Solution Found:")
            	# Format solution into Limb API-compatible dictionary
            	limb_joints = dict(zip(resp.joints[0].name, resp.joints[0].position))
            	print limb_joints
        else:
        	print("INVALID POSE - No Valid Joint Solution Found.")
     
        return 0

def callback(data):
	#global leftLimb;
	u  = data.data[0]
	v  = data.data[1]
	th = data.data[2]
	print u,v,th
	limb = baxter_interface.Limb('left')
	pose  = limb.endpoint_pose()
	cart  = pose['position'][0:3]
	qu    = pose['orientation'][0:4]
	euler = tf.transformations.euler_from_quaternion(qu)
	print euler
	qu2 = tf.transformations.quaternion_from_euler(euler[0],euler[1],euler[2])
	new_pose = [cart[0],cart[1],cart[2],qu2[0],qu2[1],qu2[2],qu2[3]]
	tuple(new_pose)	
	result = ik_test(new_pose)
	


def main(args):
	#global x,y
	rospy.init_node('objectGrasp', anonymous=True)
	leftLimb = baxter_interface.Limb('left')
	rospy.Subscriber("vec", numpy_msg(vec), callback)
	print 'here'
	#leftLimb = baxter_interface.Limb('left')
	#print x,y
	rospy.spin()
	return 0

if __name__ == '__main__':
	main(sys.argv)
