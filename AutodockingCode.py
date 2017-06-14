'''
Created on Jun 14, 2017

@author: kristentan
'''
'''
Created on Jun 9, 2017

@author: kristentan
'''
'''
Created on Jun 9, 2017

@author: kristentan
'''
# Monitor the kobuki's button status

import roslib
import rospy
from kobuki_msgs.msg import ButtonEvent
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from kobuki_msgs.msg import PowerSystemEvent, AutoDockingAction, AutoDockingGoal, SensorState #for kobuki base power and auto docking
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped, Point, Quaternion, Twist
import json
import urllib2
import time #for sleep()
from smart_battery_msgs.msg import SmartBatteryStatus #for netbook battery
import math #for comparing if Kobuki's power has changed using fabs


class GoToPose():
    def __init__(self):

        self.goal_sent = False

        # What to do if shut down (e.g. Ctrl-C or failure)
        rospy.on_shutdown(self.shutdown)
    
    # Tell the action client that we want to spin a thread by default
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Wait for the action server to come up")

    # Allow up to 5 seconds for the action server to come up
        self.move_base.wait_for_server(rospy.Duration(5))

    def goto(self, pos, quat):
        # Send a goal
        self.goal_sent = True
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(pos['x'], pos['y'], 0.000),
        Quaternion(quat['r1'], quat['r2'], quat['r3'], quat['r4']))

    # Start moving
        self.move_base.send_goal(goal)

    # Allow TurtleBot up to 60 seconds to complete task
        success = self.move_base.wait_for_result(rospy.Duration(60)) 

        state = self.move_base.get_state()
        result = False

        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False
        return result

    def shutdown(self):
        if self.goal_sent:
            self.move_base.cancel_goal()
        rospy.loginfo("Stop")
        rospy.sleep(1)



class kobuki_button():
    
    move_base = False
    button = ""
    
    # Create a ROS node
    rospy.init_node("dock_the_robot")

    # Create an action client
    client = actionlib.SimpleActionClient("/dock", DockAction)
    client.wait_for_server()

    # Create and send a goal
    goal = DockGoal()
    goal.dock_pose.header.frame_id = "base_link"
    goal.dock_pose.pose.position.x = 1.0
    goal.dock_pose.pose.orientation.z = 1.0
    client.send_goal(goal)

    def ButtonEventCallback(self,data):
        if ( data.state == ButtonEvent.RELEASED ) :
            state = "released"
        else:
            state = "pressed"  
            if ( data.button == ButtonEvent.Button0 ) :
                button = "B0"
                self.DockWithChargingStation()
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