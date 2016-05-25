#!/usr/bin/env python
import os
import sys
import baxter_interface
import rospy
import argparse
from sensor_msgs.msg import Image
from std_msgs.msg import (
    UInt16,
)

#subfuction to send image to publisher (head screen)
def getImg(msg):
	displayPub = rospy.Publisher('/robot/xdisplay',Image, latch=True) # publisher is camera
	# send image to baxter display
	displayPub.publish(msg)
#subfuction to publish image	
def stream2disp(camera_topic):
	sub = rospy.Subscriber(camera_topic, Image, getImg) #subscriber is screen
	rate = rospy.Rate(100)
	print("Sending to head...")
	while not rospy.is_shutdown():
		rate.sleep()
#subfuction to publish image	
def main():
	res = (1280,800)
	# shutdown all cameras first 
	leftCam = baxter_interface.CameraController("left_hand_camera")
	leftCam.close()
	rightCam = baxter_interface.CameraController("right_hand_camera")
	rightCam.close()
	#headCam = baxter_interface.CameraController("head_camera")
	#headCam.close()
	# define Node
	rospy.init_node('useCam')
	#define argument for command line
	arg_fmt = argparse.RawDescriptionHelpFormatter
	parser = argparse.ArgumentParser(formatter_class=arg_fmt,description=main.__doc__)
	parser.add_argument('-c', '--camera', choices=['left', 'right', 'head'], required=True,help="the camera to display")
	args = parser.parse_args(rospy.myargv()[1:])
	# define camera
	if(args.camera == 'left'):
		leftCam.open()
		leftCam.resolution = res
		camera_topic = '/cameras/left_hand_camera/image'
	if(args.camera == 'right'):
		rightCam.resolution = res
		rightCam.open()
		camera_topic = '/cameras/right_hand_camera/image'
	#if(args.camera == 'head'):
	#	headCam.resolution = res
	#	headCam.open()
	#	camera_topic = '/cameras/head_camera/image'
	stream2disp(camera_topic)
	print("closing...")
	return 0
	
if __name__ == '__main__':
    sys.exit(main())

