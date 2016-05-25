#include <ros/ros.h>
#include <pcl_ros/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl_ros/transforms.h>
#include <tf/transform_listener.h>
#include <cv_bridge/cv_bridge.h>
#include <image_transport/image_transport.h>
#include <sensor_msgs/image_encodings.h>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <sensor_msgs/PointCloud2.h>
#include <sensor_msgs/point_cloud2_iterator.h>
#include <pcl/io/io.h>
#include <math.h>
//#include <iostream.h>
typedef pcl::PointCloud<pcl::PointXYZRGB> PointCloud;
using namespace std;


class depthImage {
	public:
		depthImage() {
			cout<<"Advertising"<<endl;
			image_transport::ImageTransport it(nh_);
			pub_ = it.advertise("depthView", 1);
			cout<<"Subscribing"<<endl;
			sub_ = nh_.subscribe("/camera/depth_registered/points", 1, &depthImage::callback, this);
			// <sensor_msgs::PointCloud2>		
		}
		
		void callback(const sensor_msgs::PointCloud2ConstPtr& input) {
			cout<<"Callback"<<endl;
			ros::Rate rate(60.0);
			try {
				// load PC into array via iterator
				sensor_msgs::PointCloud2 in = *input;
				sensor_msgs::PointCloud2Modifier reader(in);
				reader.setPointCloud2FieldsByString(2, "xyz", "rgb");
				sensor_msgs::PointCloud2Iterator<float> iter_x(in, "x");
				sensor_msgs::PointCloud2Iterator<float> iter_y(in, "y");
				sensor_msgs::PointCloud2Iterator<float> iter_z(in, "z");
				float pointArray[640][480][4];
				cv::Mat Rimg(480,640,CV_8U);
				int width  = in.width;
				int height = in.height;
				int count = 0;
				float R    = 0;
				for (; iter_x != iter_x.end(); ++iter_x, ++iter_y, ++iter_z) {
					int r = floor(count/width);
					int c = count%width;
					pointArray[c][r][0] = *iter_x;
					pointArray[c][r][1] = *iter_y;
					pointArray[c][r][2] = *iter_z;
					R = sqrt(pow(*iter_x,2)+pow(*iter_y,2)+pow(*iter_z,2));
					pointArray[c][r][3] = R;
					//cout<<pointArray[c][r][0]<<" "<<pointArray[c][r][0]<<" "<<pointArray[c][r][0]<<endl;
					++count;
					float Rmin = 1.15;
					float Rmax = 1.6;
					if (R>Rmin && R<Rmax) {
						Rimg.at<uchar>(r,c) = int(255*(R-Rmin)/(Rmax-Rmin));
					}
					else if (R<Rmin) {
						Rimg.at<uchar>(r,c) = 0;
					}
					else  {
						Rimg.at<uchar>(r,c) = 255;
					}
				}
				//cout<<maxZ<<" "<<minZ<<" "<<maxR<<" "<<minR<<endl;
				if(nh_.ok()) {
					sensor_msgs::ImagePtr msg = cv_bridge::CvImage(std_msgs::Header(), "mono8", Rimg).toImageMsg();
					pub_.publish(msg);
				}	
				else {
					cout<<"node not okay"<<endl;
				}
				cv::imshow("R", Rimg);
				cv::waitKey(33);
	
			}
			catch (tf::TransformException ex) {
				ROS_ERROR("%s",ex.what());
				ROS_ERROR("Failed");
			}
			rate.sleep();
		}
	
	private:
		ros::NodeHandle nh_;
		image_transport::Publisher pub_;
		ros::Subscriber sub_;	
};


int main(int argc, char** argv)
{
  // Initiate ROS
  ros::init(argc, argv, "depthImage");
  // Create object and go
  depthImage object;
  // Keep it spinning
  ros::spin();
  return 0;
}
