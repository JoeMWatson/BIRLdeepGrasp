#include <ros/ros.h>
#include <pcl_ros/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl_ros/transforms.h>
#include <tf/transform_listener.h>
//#include <tf2_sensor_msgs.h>
//#include <geometry_msgs/TransformStamped>
#include <sensor_msgs/PointCloud2.h>
#include<pcl/io/io.h>

typedef pcl::PointCloud<pcl::PointXYZRGB> PointCloud;

ros::Publisher pub;
tf::TransformListener *tf_listener; 
tf::TransformListener *tf_listener2; 

void callback(const PointCloud::ConstPtr& in) 
{
  ros::Rate rate(10.0);
  try {
	  PointCloud out;
	  tf_listener->waitForTransform( "/torso","/camera_link", ros::Time(0), ros::Duration(120.0));	
	  bool b = tf_listener2->waitForTransform("/base", "/camera_rgb_optical_frame", ros::Time(0), ros::Duration(120.0));	
	  
	  //tf_listener->lookupTrainsform()
	  if (b) {
	  	pcl_ros::transformPointCloud("/base", *in, out, *tf_listener);
	  }
	  //pcl::toROSMsg(out,out2)
	  pub.publish(out);
  }
  catch (tf::TransformException ex) {
  	ROS_ERROR("%s",ex.what());
	ROS_ERROR("Failed");
  }
  rate.sleep();
}

int main(int argc, char** argv)
{
  ros::init(argc, argv, "kinectTransform");
  ros::NodeHandle nh1;
  pub = nh1.advertise<PointCloud> ("transformedPointCloud", 1);
  
  tf_listener    = new tf::TransformListener(ros::Duration(10000.0));
  tf_listener2    = new tf::TransformListener(ros::Duration(10000.0));
  ros::NodeHandle nh2;
  ros::Subscriber sub = nh2.subscribe<PointCloud>("/camera/depth_registered/points", 1, callback);

  ros::spin();
}
