#!/usr/bin/env python

import rospy
import baxter_interface

rospy.init_node('leftPick')
rospy.loginfo("Started...")
leftLimb = baxter_interface.Limb('left')


leftPoint = {'left_w0': -0.220893233203125, 'left_w1': 1.7115390621276856, 'left_w2': 3.0556897259765625, 'left_e0': 0.22166022359619142, 'left_e1': 0.6074563913085937, 'left_s0': -0.33402431618041994, 'left_s1': -0.794602047216797}



leftLimb.move_to_joint_positions(leftPoint)


quit()


