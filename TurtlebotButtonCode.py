'''
Created on Jun 9, 2017

@author: kristentan
'''
# Monitor the kobuki's button status

import roslib
import rospy
from kobuki_msgs.msg import ButtonEvent
from geometry_msgs.msg import Twist


class kobuki_button(goforward):

    def __init__(self):
        rospy.init_node("kobuki_button")        

        #monitor kobuki's button events
        rospy.Subscriber("/mobile_base/events/button",ButtonEvent,self.ButtonEventCallback)

        #rospy.spin() tells the program to not exit until you press ctrl + c.  If this wasn't there... it'd subscribe and then immediatly exit (therefore stop "listening" to the thread).
        rospy.spin();


    
    def ButtonEventCallback(self,data):
        if ( data.state == ButtonEvent.RELEASED ) :
            state = "released"
        else:
            state = "pressed"  
            if ( data.button == ButtonEvent.Button0 ) :
                button = "B0"
                try:
                    super(GoForward())
                except:
                    rospy.loginfo("GoForward node terminated.")
            elif ( data.button == ButtonEvent.Button1 ) :
                button = "B1"
            else:
                button = "B2"
        rospy.loginfo("Button %s was %s."%(button, state))
    

if __name__ == '__main__':
    try:
        kobuki_button()
    except rospy.ROSInterruptException:
        rospy.loginfo("exception")
