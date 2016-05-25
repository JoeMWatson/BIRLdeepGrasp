#include <ros/ros.h>
#include <cv_bridge/cv_bridge.h>
#include <image_transport/image_transport.h>
#include <sensor_msgs/image_encodings.h>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>
#include<opencv2/features2d/features2d.hpp>
#include <opencv2/opencv.hpp>
#include <opencv2/objdetect/objdetect.hpp>
#include<iostream>
#include<stdio.h>
#include<vector>

using namespace std;
using namespace cv;


static const std::string OPENCV_WINDOW = "Image window";

int main(int argc, char** argv)
{
  ros::init(argc, argv, "faceIdent");
  Mat image=imread("/home/baxter-birl/catkin_ws/src/grasp/src/team.jpg");
  if(!image.data)	{
        cout<<"Could not open or find the image"<<std::endl;
  }
  cout<<"here 1"<<endl;
  namedWindow("input");
  namedWindow("output");
  cv::imshow("input",image);
  cv::waitKey(30);
  CascadeClassifier face_cascade;
  
  if (!face_cascade.load("/home/baxter-birl/catkin_ws/src/grasp/src/haarcascade_frontalface_default.xml")){
  cout<<"load error"<<endl;
  }
  ///home/baxter-birl/catkin__ws/src/grasp/src
  vector<Rect> faces;
  face_cascade.detectMultiScale(image,faces,1.5,3, CV_HAAR_SCALE_IMAGE, cvSize(30,30));
  cout<<"here 2"<<endl;
  cout<<faces.size()<<endl;
  for(size_t i=0;i<faces.size();i++ )	{
  	cout<<"I'm"<<endl;
	rectangle(image,faces[i],Scalar(0,125,165),2,8,0);
	cout<<"looping"<<endl;
  }

  cv::imshow("output", image);
  cv::waitKey(500);
  ros::spin();
  return 0;
}

