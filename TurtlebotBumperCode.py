'''
Created on Jun 12, 2017

@author: kristentan
'''
import roslib
import rospy
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import BumperEvent

class bumper():

    def __init__(self):
        rospy.init_node("bumper")        

        #monitor kobuki's button events
        rospy.Subscriber('mobile_base/events/bumper',BumperEvent,BumperEventCallback)

        #rospy.spin() tells the program to not exit until you press ctrl + c.  If this wasn't there... it'd subscribe and then immediatly exit (therefore stop "listening" to the thread).
        rospy.spin();

    def BumperEventCallback(self,data):
        if ( data.state == BumperEvent.PRESSED ) :
            bump = True
        else:
            bump = False
        rospy.loginfo("Bumper Event") 
        rospy.loginfo("Bumper was %s."%(bump))
        rospy.loginfo(data.bumper)


if __name__ == '__main__':
    try:
        bumper()
    except rospy.ROSInterruptException:
        rospy.loginfo("exception")
