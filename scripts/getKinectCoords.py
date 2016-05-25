#!/usr/bin/env python
import sys
import os
import tf
import cv_bridge
import cv2.cv as cv
import cv2
import rospy
import numpy as np
from sensor_msgs.msg import Image

T1 = np.zeros((4,4))
kinect = np.zeros((480,640,3))
kinect = kinect.astype('uint8')
count = 0;
save = 1;
Rest = np.zeros((3,3))
Test = np.zeros((3,1))

def stream(cameraTopic,kinectTopic):
	rate = rospy.Rate(100)
	
	depthSub = rospy.Subscriber(kinectTopic, Image, callback2)
	imageSub = rospy.Subscriber(cameraTopic, Image, callback)
	print("Displaying. Press Ctrl-C to stop...")
	while not rospy.is_shutdown():
		rate.sleep()
		
def callback(data):
	#
	streamDisp(data)

def callback2(data):
	#
	streamDisp2(data)

def streamDisp2(data):
	#print 'here 4'
	global kinect
	bridge = cv_bridge.CvBridge()
	try:
		cv_image = bridge.imgmsg_to_cv2(data,desired_encoding="bgr8")
	except cv_bridge.CvBridgeError, e:
		print e
	kinect = cv_image
	
	

def streamDisp(data):	
	global kinect
	bridge = cv_bridge.CvBridge()
	try:
		cv_image = bridge.imgmsg_to_cv2(data,desired_encoding='bgr8')
	except cv_bridge.CvBridgeError, e:
		print e
	#display image
	
	chessFind(cv_image,kinect)

def chessFind(left,right):
	global count,Rest,Test,T1,save
	square_size = 20.0
	dim = (9,6)
	objectPoints = np.zeros((np.prod(dim),3), np.float32)
	objectPoints[:,:2] = np.mgrid[0:dim[0],0:dim[1]].T.reshape(-1,2)
	objectPoints *= square_size
	#left = left[200:350,200:400]
	#right = right[350:500,300:500]
	#right = cv2.resize(right,None,fx=1.2,fy=1.2,interpolation = cv2.INTER_CUBIC)
	leftGrey = cv2.cvtColor(left,cv2.COLOR_BGR2GRAY)
	rightGrey = cv2.cvtColor(right,cv2.COLOR_BGR2GRAY)
	#clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	#cv2.fastNlMeansDenoising(leftGrey,10,10,7,21)
	#cv2.fastNlMeansDenoising(rightGrey,10,10,7,21)
	#leftGrey = clahe.apply(leftGrey)
	#rightGrey = clahe.apply(rightGrey)
	ret, leftGrey = cv2.threshold(leftGrey,90,255,cv2.THRESH_BINARY)
	ret, rightGrey = cv2.threshold(rightGrey,190,255,cv2.THRESH_BINARY)

	foundLeft, leftCorners = cv2.findChessboardCorners(leftGrey, dim, flags=cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH)
	
	cv2.drawChessboardCorners(leftGrey,dim,leftCorners,foundLeft)
	foundRight, rightCorners = cv2.findChessboardCorners(rightGrey, dim, flags=cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH)
	
	cv2.drawChessboardCorners(rightGrey,dim,rightCorners,foundRight)
	DLeft = np.matrix([[0.022074600592, -0.0552437804175, -0.00112911356675,0.000909446041186, 0.0135764592874]])
	DRight = np.matrix([[0.156294398165945, -0.1110955775687071, -0.05738453549940395, 0.03114778778348401, 0.0]])
	camMatL1 = np.matrix([[405.947834417, 0.0, 637.310360352], [0.0, 405.947834417, 429.526633118], [0.0, 0.0, 1.0]])

	camMatR1 = np.matrix([[525.785594, 0.0, 333.169827], [0.0, 526554419, 255.206482], [0.0, 0.0, 1.0]])
	if (foundLeft and foundRight and (count < 50)):
		print leftGrey.shape
		leftCorners = leftCorners.reshape(-1,2)
		rightCorners = rightCorners.reshape(-1,2)

		rmsL, camMatL,DistCoL,rVecL,tVecL = cv2.calibrateCamera([objectPoints],[leftCorners],leftGrey.shape,None,None)
		rmsR, camMatR,DistCoR,rVecR,tVecR = cv2.calibrateCamera([objectPoints],[rightCorners],rightGrey.shape,None,None)


		#rmsL, camMatL,DistCoL,rVecL,tVecL = cv2.calibrateCamera([objectPoints],[leftCorners],leftGrey.shape,camMatL1,DLeft,None,flags = cv2.CALIB_USE_INTRINSIC_GUESS)
		#rmsR, camMatR,DistCoR,rVecR,tVecR = cv2.calibrateCamera([objectPoints],[rightCorners],rightGrey.shape,camMatR1,DRight,None,flags = cv2.CALIB_USE_INTRINSIC_GUESS)
		print 'gotcha'
		#print leftCorners.size
		#print rightCorners.size
		stereo_crit = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS,100,1e-5)

		#stereo_flag = cv2.CALIB_FIX_ASPECT_RATIO | cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_SAME_FOCAL_LENGTH | cv2.CALIB_RATIONAL_MODEL
		#stereo_flag = cv2.cv.CV_CALIB_FIX_INTRINSIC | cv2.CALIB_SAME_FOCAL_LENGTH
		#retval, leftMat,distCoLeft,rightMat,distCoRight,R,T,E,F = cv2.stereoCalibrate([objectPoints],[leftCorners],[rightCorners],(480,640),camMatL,DistCoL,camMatR,DistCoR, criteria = stereo_crit, flags = stereo_flag) 
		retval, leftMat,distCoLeft,rightMat,distCoRight,R,T,E,F = cv2.stereoCalibrate([objectPoints],[leftCorners],[rightCorners],(400,640), criteria = stereo_crit)#, flags = stereo_flag) 
		print retval		
		#print camMatL
		#print camMatR
		#print DistCoL
		#print DistCoR
		#print R
		#print T
		Rest = np.add(Rest,R/50.0)
		Test = np.add(Test,T/50.0)
		count = count+1
		print count
		if(save):
			np.save('transform1',T1)
			np.save('rotation2',Rest)
			np.save('translation2',Test)
		#print E
		
	#print foundLeft	
	#print foundRight
	cv2.imshow('Left',leftGrey)
	cv2.waitKey(2)
	cv2.imshow('K',rightGrey)
	cv2.waitKey(2)
	#print count
	if(count == 50):
		#print Rest
		#print Test
		T2 = np.zeros((4,4))
		T2[0:3,0:3] = Rest
		T2[0:3,3] = np.transpose(Test)/1000.0
		T2[3,3] = 1.0
		#print T2
		T3 = np.multiply(T2,T1)
		R2 = T2[0:3,0:3]
		R3 = np.multiply(R2,Rest)
		tran1 = np.transpose(T1[0:3,3]).reshape(3,1)
		Tran3 = np.add(tran1,Test/1000.0)
		eulerAng = tf.transformations.euler_from_matrix(R3,axes='sxyz')
		print eulerAng
		print Tran3
		print tran1
		print Test/1000.0
		print T3
		#return
	

def main(args):
	global T1
	rospy.init_node('kinect_calibration')
	lis = tf.TransformListener()
	# transform sources
	source = "/base"
	cam = "/left_hand_camera"

	rate = rospy.Rate(50)
	while not rospy.is_shutdown():
		try: 
			t,q = lis.lookupTransform("/base","/left_hand_camera",rospy.Time())
			break
		except(tf.LookupException, tf.ConnectivityException,tf.ExtrapolationException):
			continue

	#transforms
	R=tf.transformations.quaternion_matrix(q)
	T1 = R
	T1[0:3,3] = np.transpose(t)
	print T1
	#stereo
	cameraTopic = '/cameras/left_hand_camera/image'
	kinectTopic = '/camera/rgb/image_color'
	stream(cameraTopic,kinectTopic)
	return 0

if __name__ == '__main__':
	main(sys.argv)
