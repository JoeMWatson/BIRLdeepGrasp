#!/usr/bin/env python
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
os.environ['GLOG_minloglevel'] = '2'
import caffe
import math
from rospy.numpy_msg import numpy_msg
from grasp.msg import vec
from shapely.geometry import Polygon

def nothing(x):
    pass

count = 0;
#Background Subtractor
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
MOG = cv2.BackgroundSubtractorMOG2(50,50,False)
MOG2 = cv2.BackgroundSubtractorMOG2(100,50,False)
#ConvNet
modelFile  = '/home/birl/ros_ws/src/grasp/caffe/graspDeploy.prototxt'
weightFile = '/home/birl/ros_ws/src/grasp/caffe/caffeGraspTrainX_iter_10000.caffemodel'
graspNet = caffe.Net(modelFile, weightFile, caffe.TEST)
caffe.set_mode_cpu()
depth = np.zeros((480,640)).astype('uint8')
right = np.zeros((480,640)).astype('uint8')
# blob detector markers
params = cv2.SimpleBlobDetector_Params()
params.minThreshold = 1
params.filterByArea = True
params.minArea = 1
detector = cv2.SimpleBlobDetector(params)
# blob detector move
params = cv2.SimpleBlobDetector_Params()
params.minThreshold = 1
params.maxThreshold = 200
params.filterByArea = True
params.minArea = 20
params.maxArea = 224**2
detector2 = cv2.SimpleBlobDetector(params)
# HSV tuning window
window = 1
if window :
	LMAX  = 50
	hl = 72
	hh = 120
	sl = 70
	sh = 225
	vl = 0
	vh = 255
	cv2.namedWindow('image')
	cv2.createTrackbar('LMAX','image',LMAX,100,nothing)
	cv2.createTrackbar('hl','image',hl,255,nothing)
	cv2.createTrackbar('hh','image',hh,255,nothing)
	cv2.createTrackbar('sl','image',sl,255,nothing)
	cv2.createTrackbar('sh','image',sh,255,nothing)
	cv2.createTrackbar('vl','image',vl,255,nothing)
	cv2.createTrackbar('vh','image',vh,255,nothing)


def feat2rect(x,y,w,h,th):
	al = np.arctan2(h,w)
	diag = np.sqrt(w**2+h**2)
	angle = th + al
	cent = np.array((x,y))
	vec = np.array((diag*np.cos(angle)/2, diag*np.sin(angle)/2))
	vec2 = np.array((w*np.cos(th), w*np.sin(th)))
	pt1x,pt1y = cent - vec
	pt3x,pt3y = cent + vec # opposite points
	pt2x,pt2y = np.array((pt1x,pt1y)) + vec2
	pt4x,pt4y = np.array((pt3x,pt3y)) - vec2
	return np.array((int(pt1x),int(pt1y),int(pt2x),int(pt2y),int(pt3x),int(pt3y),int(pt4x),int(pt4y)))

def rect2img(img,points,u,v,name):
	cv2.circle(img,(u,v),3,(255,0,0),-1)
	cv2.line(img,(points[0],points[1]),(points[2],points[3]),(255,0,0),1)
	cv2.line(img,(points[2],points[3]),(points[4],points[5]),(0,255,0),1)
	cv2.line(img,(points[4],points[5]),(points[6],points[7]),(255,0,0),1)
	cv2.line(img,(points[6],points[7]),(points[0],points[1]),(0,255,0),1)
	cv2.imshow(name, img)
	cv2.waitKey(1)

def rect2image(img,points,u,v):
	cv2.circle(img,(u,v),3,(255,0,0),-1)
	cv2.line(img,(points[0],points[1]),(points[2],points[3]),(255,0,0),1)
	cv2.line(img,(points[2],points[3]),(points[4],points[5]),(0,255,0),1)
	cv2.line(img,(points[4],points[5]),(points[6],points[7]),(255,0,0),1)
	cv2.line(img,(points[6],points[7]),(points[0],points[1]),(0,255,0),1)
	return img



def stream(cameraTopic,depthTopic):
	rate = rospy.Rate(0.5)
	depthSub = rospy.Subscriber(depthTopic, Image, callback2, queue_size=1)#, buff_size = 2**10)
	imageSub = rospy.Subscriber(cameraTopic, Image, callback, queue_size=1)#, buff_size = 2**10)
	print("Displaying. Press Ctrl-C to stop...")
	while not rospy.is_shutdown():
		rate.sleep()
		
def callback(data):
	streamDisp(data)

def callback2(data):
	streamDisp2(data)


def streamDisp2(data):
	global depth	
	bridge = cv_bridge.CvBridge()
	try:
		cv_image = bridge.imgmsg_to_cv2(data,desired_encoding='passthrough')
		#print cv_image
		depth = cv_image
	except cv_bridge.CvBridgeError, e:
		print e

	

def streamDisp(data):
	global MOG,MOG2, kernel,graspNet,depth,count,detector,detector2
	bridge = cv_bridge.CvBridge()
	try:
		cv_image = bridge.imgmsg_to_cv2(data,desired_encoding='bgr8')
	except cv_bridge.CvBridgeError, e:
		print e
	# display image
	mask = MOG.apply(cv_image)
	mask2 = MOG2.apply(depth)
	#cv2.imshow('depth', depth)
	#cv2.waitKey(1)
	count = count+1
	if (count<50):
		print 'training...'
	elif ((count-50)%20 == 0):
		# combine streams
		rgd = np.copy(cv_image)
		rgd[:,:,0] = depth[:,:]
		
		#cv2.imshow('rgd', rgd)
		#cv2.waitKey(1)
		# apply mash
		mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
		#mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel)
		#mask2 = cv2.bitwise_not(mask2)
		maskAll = cv2.bitwise_and(mask,mask2)
		rgdM = cv2.bitwise_and(rgd,rgd,mask = mask)
		#rgdM = rgd
		#rgdM = cv2.bitwise_and(rgd,rgd,mask = maskAll)
		#cv2.imshow('rgdM1', rgdM)
		#cv2.waitKey(1)
		#rgdM = cv2.bitwise_and(rgdM,rgdM,mask = mask2)
		#cv2.imshow('rgdM2', rgdM)
		#cv2.waitKey(1)
		imageM = cv2.bitwise_and(cv_image,cv_image,mask = mask)
		#imageM = cv2.bitwise_and(imageM,imageM,mask = mask2)
		#cv2.imshow('imageM', imageM)
		#cv2.waitKey(1)
		#cv2.imshow('rgdM', rgdM)
		#cv2.waitKey(1)
		# image is 640x480
		# crop to 224x224
		rgdMCrop = rgdM[480-224:480, 320-112:320+112]	
		imageM = imageM[480-224:480, 320-112:320+112]	
		rows, cols, ch = rgdMCrop.shape
		T = np.float32([[1,0,0],[0,1,-55]])
		rgdMCropT = cv2.warpAffine(rgdMCrop,T,(cols,rows))
		imageB = cv2.blur(rgdMCropT,(50,50))
		gray = cv2.cvtColor(imageB,cv2.COLOR_BGR2GRAY)
		ret,thresh0 = cv2.threshold(gray,10,255,cv2.THRESH_BINARY_INV)
		keypoints = detector2.detect(thresh0)
		imageB = cv2.drawKeypoints(thresh0,keypoints,np.array([]),(0,0,255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		tx = 0
		ty = 0
		if len(keypoints)>0:
			tx = 112-keypoints[0].pt[0]
			ty = 112-keypoints[0].pt[1]#-55
			T = np.float32([[1,0,tx],[0,1,ty]])
			rgdMCropT = cv2.warpAffine(rgdMCropT,T,(cols,rows))
		imageM = cv2.warpAffine(imageM,T,(cols,rows))
		imageMCrop = rgdMCropT
		inImg = (rgdMCropT.transpose((2,0,1))-144.0)/255
		graspNet.blobs['data'].data[...] = inImg
		pred=graspNet.forward()
		x,y,w,h,c2,s2 = np.array(pred.values(), dtype='float').reshape(-1)
		x=int(x*224)
		y=int(y*224)
		w=(w*224)
		h=(h*224)
		print w,h
		u=int(x+(320-112)-tx)
		v=int(y+(480-224)-ty+55)
		print x,y,w,h,c2,s2
		th = (np.arctan2(s2,c2))/2
		th1= np.arccos(c2)/2
		th2=np.arcsin(s2)/2
		points=feat2rect(u,v,w,h,th)
		rect2img(imageMCrop,feat2rect(x,y,w,h,th),x,y,'raw')
		rect2img(cv_image,feat2rect(u,v,w,h,th),u,v,'full')
		vecPub = rospy.Publisher('vec', numpy_msg(vec), queue_size=10)
		#print np.float32(u),np.float32(v),th
		vecPub.publish(np.array((np.float32(u),np.float32(v),np.float32(th))))
		# assessment
		if window :
			LMAX = cv2.getTrackbarPos('LMAX','image')
			hl = cv2.getTrackbarPos('hl','image')
			hh = cv2.getTrackbarPos('hh','image')
			sl = cv2.getTrackbarPos('sl','image')
			sh = cv2.getTrackbarPos('sh','image')
			vl = cv2.getTrackbarPos('vl','image')
			vh = cv2.getTrackbarPos('vh','image')
		else : 
			hl = 37
			hh = 139
			sl = 70
			sh = 225
			vl = 0
			vh = 255
		#cv2.imshow('imageM', imageM)
		#cv2.waitKey(1)
		hsv = cv2.cvtColor(imageM, cv2.COLOR_BGR2HSV)
		lower_red = np.array([hl,sl,vl])
       		upper_red = np.array([hh,sh,vh])
		mask = cv2.morphologyEx(cv2.inRange(hsv, lower_red, upper_red), cv2.MORPH_OPEN, kernel)
		imageM = cv2.bitwise_and(imageM,imageM,mask = mask)
		imageM = cv2.blur(imageM,(5,5))
		cv2.imshow('a',imageM)
		gray = cv2.cvtColor(imageM,cv2.COLOR_BGR2GRAY)
		ret,thresh = cv2.threshold(gray,10,255,cv2.THRESH_BINARY_INV)
		keypoints = detector.detect(thresh)
		dw = 25
		dh = 14
		if len(keypoints)>0:
			print 'keypoints'
			grasps = []
			thetaA = []
			imageC = cv2.drawKeypoints(cv_image,keypoints,np.array([]),(0,0,255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
			if len(keypoints)>1:
				print len(keypoints)
				for i in range(0,len(keypoints)-1):
					for k in range(1,len(keypoints)-i):
						x1 = int(keypoints[i].pt[0]+(320-112)-tx)
						x2 = int(keypoints[i+k].pt[0]+(320-112)-tx)
						y1 = int(keypoints[i].pt[1]+(480-224)-ty)
						y2 = int(keypoints[i+k].pt[1]+(480-224)-ty)
						Y = keypoints[i+k].pt[1]-keypoints[i].pt[1]
						X = keypoints[i+k].pt[0]-keypoints[i].pt[0]
						L = np.sqrt(X**2 + Y**2)
						cv2.circle(cv_image,(x1,y1),5,(0,0,255),-1)
						if L<LMAX:
						
							#cv2.line(cv_image,(int(keypoints[i].pt[0]),int(keypoints[i].pt[1])),(int(keypoints[i+1].pt[0]),int(keypoints[i+1].pt[1])),(0,255,0))
							alpha = np.arctan2(Y,X)
							dth = alpha - np.pi/2 
							L = np.sqrt(X**2 + Y**2)
							print L
							N = int(np.floor(L/5))
							for j in range(0,N):
								dx = x1 + np.cos(alpha)*j*L/N
								dy = y1 + np.sin(alpha)*j*L/N
								imageC = rect2image(cv_image,feat2rect(dx,dy,dw,dh,dth),int(dx),int(dy))
								a = feat2rect(dx,dy,dw,dh,dth)
								grasps.append(Polygon([(a[0],a[1]),(a[2],a[3]),(a[4],a[5]),(a[6],a[7])]))
								thetaA.append(dth)
							#thresh = rect2image(thresh,feat2rect(x,y,w,h,th),int(x),int(y))
			else:
				x1 = int(keypoints[0].pt[0]+(320-112)-tx)
				y1 = int(keypoints[0].pt[1]+(480-224)-ty)
				for i in range(0,10):
					dth = np.pi*i/10
					imageC = rect2image(cv_image,feat2rect(x1,y1,dw,dh,dth),int(x1),int(y1))
					a = feat2rect(x1,y1,dw,dh,dth)
					grasps.append(Polygon([(a[0],a[1]),(a[2],a[3]),(a[4],a[5]),(a[6],a[7])]))
					thetaA.append(dth)
			if len(grasps)>0:
				a = feat2rect(u,v,w,h,th)
				output = Polygon([(a[0],a[1]),(a[2],a[3]),(a[4],a[5]),(a[6],a[7])])
				AIF = np.zeros((len(grasps),1))
				thEr = np.zeros((len(grasps),1))
				grasp = np.asarray(grasps)
				thh= np.asarray(thetaA)
				for i in range(0,len(grasps)):
					AIF[i] = grasp[i].intersection(output).area
					a = abs(th - thh[i])
					thEr[i] = np.arctan2(np.sin(2*a),np.cos(2*a))/2
				areaMx = np.amax(AIF)
				ind = np.argmax(AIF)
				aif = areaMx/output.area
				thdif = thEr[ind]
				print 'area intersection factor'
				print aif
				print 'theta error'
				print thdif
		else: 
			print 'no keypoints'
		rect2img(imageMCrop,feat2rect(x,y,w,h,th),x,y,'raw')
		rect2img(cv_image,feat2rect(u,v,w,h,th),u,v,'full')
		cv2.imshow('image', thresh)
		cv2.waitKey(1)
		cv2.imshow('blob detect', imageB)
		cv2.waitKey(1)

		

def main(args):
	rospy.init_node('graspNet', anonymous=True)
	MOG = cv2.BackgroundSubtractorMOG2()
	cameraTopic = '/camera/rgb/image_color'
	depthTopic = '/depth'
	stream(cameraTopic,depthTopic)
	print 'complete!'
	cv2.destroyAllWindows()
	return 0

if __name__ == '__main__':
	main(sys.argv)
