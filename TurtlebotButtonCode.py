'''
Created on Jun 9, 2017

@author: kristentan
'''
# Monitor the kobuki's button status

import roslib
import rospy
from kobuki_msgs.msg import ButtonEvent
from geometry_msgs.msg import Twist

class GoForward():
    def __init__(self):
        # initiliaze
        rospy.init_node('GoForward', anonymous=False)

    # tell user how to stop TurtleBot
        rospy.loginfo("To stop TurtleBot CTRL + C")

        # What function to call when you ctrl + c    
        rospy.on_shutdown(self.shutdown)
        
    # Create a publisher which can "talk" to TurtleBot and tell it to move
        # Tip: You may need to change cmd_vel_mux/input/navi to /cmd_vel if you're not using TurtleBot2
        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
     
    #TurtleBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
        r = rospy.Rate(10);

        # Twist is a datatype for velocity
        move_cmd = Twist()
    # let's go forward at 0.2 m/s
        move_cmd.linear.x = 0.2
    # let's turn at 0 radians/s
    move_cmd.angular.z = 0

    # as long as you haven't ctrl + c keeping doing...
        while not rospy.is_shutdown():
        # publish the velocity
            self.cmd_vel.publish(move_cmd)
        # wait for 0.1 seconds (10 HZ) and publish again
            r.sleep()
                        
        
    def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Stop TurtleBot")
    # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
        self.cmd_vel.publish(Twist())
    # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
        rospy.sleep(1)

class kobuki_button():

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
        GoForward()
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