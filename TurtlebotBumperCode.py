'''
Created on Jun 12, 2017

@author: kristentan
'''
import roslib
import rospy
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import BumperEvent
from kobuki_msgs.msg import Led

class bumper():
    
    def BumperEventCallback(self,data):
        # Publish led1
        self.led1 = rospy.Publisher('/mobile_base/commands/led1', Led, queue_size=10) 
        # Publish led2 
        self.led2 = rospy.Publisher('/mobile_base/commands/led2', Led, queue_size=10)
        if ( data.state == BumperEvent.PRESSED ) :
            bump = True
            self.led2.publish(Led.GREEN)
        else:
            bump = False
            self.led1.publish(Led.RED)
        rospy.loginfo("Bumper Event") 
        rospy.loginfo("Bumper was %s."%(bump))
        rospy.loginfo(data.bumper)
        
    def __init__(self):
        rospy.init_node("bumper")        

        #monitor kobuki's button events
        rospy.Subscriber('mobile_base/events/bumper',BumperEvent,self.BumperEventCallback)

        #rospy.spin() tells the program to not exit until you press ctrl + c.  If this wasn't there... it'd subscribe and then immediatly exit (therefore stop "listening" to the thread).
        rospy.spin();


if __name__ == '__main__':
    try:
        bumper()
    except rospy.ROSInterruptException:
        rospy.loginfo("exception")
