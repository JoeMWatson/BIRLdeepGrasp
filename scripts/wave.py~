#!/usr/bin/env python

import rospy
import baxter_interface

rospy.init_node('Hello_baxter')
rospy.loginfo("Started...")
limb = baxter_interface.Limb('right')

wave1 = {'right_s0': -0.459,'right_s1': -0.202,'right_e0': 1.807,'right_e1': 1.714,'right_w0': -0.906,'right_w1': -1.545,'right_w2': -0.276}

wave2 = {'right_s0': -0.359,'right_s1': -0.202,'right_e0': 1.831,'right_e1': 1.981,'right_w0': -1.979,'right_w1': -1.1,'right_w2': -0.448}

for _move in range(3):
	limb.move_to_joint_positions(wave1)
	limb.move_to_joint_positions(wave2)

quit()
