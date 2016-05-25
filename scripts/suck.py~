#!/usr/bin/env python
import rospy
import baxter_interface

rospy.init_node('suck')

grip= baxter_interface.Gripper('right')
grip.set_blow_off(0.5)
i=0
while(i<100):
	grip.close()
	i=i+1
	rospy.sleep(0.5)
	grip.open()




