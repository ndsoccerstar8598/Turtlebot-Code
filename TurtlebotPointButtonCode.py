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

    def __init__(self):
        rospy.init_node("kobuki_button")  
        #tell the action client that we want to spin a thread by default
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("wait for the action server to come up")
        #allow up to 30 seconds for the action server to come up
        self.move_base.wait_for_server(rospy.Duration(30))      

        #monitor kobuki's button events
        rospy.Subscriber("/mobile_base/events/button",ButtonEvent,self.ButtonEventCallback)

        #rospy.spin() tells the program to not exit until you press ctrl + c.  If this wasn't there... it'd subscribe and then immediatly exit (therefore stop "listening" to the thread).
        rospy.spin();
        
    def DockWithChargingStation(self):
        #before we can run auto-docking we need to be close to the docking station..
        if(not self.GoCloseToTheChargingStation()):
            return False
        #We're close to the docking station... so let's dock
        return self.WereCloseDock()
    
    def WereCloseDock(self):
        #The following will start the AutoDockingAction which will automatically find and dock TurtleBot with the docking station as long as it's near the docking station when started
        self._client = actionlib.SimpleActionClient('/dock_drive_action', AutoDockingAction)
        rospy.loginfo("waiting for auto_docking server")
        self._client.wait_for_server()
        rospy.loginfo("auto_docking server found")
        goal = AutoDockingGoal()
        rospy.loginfo("Sending auto_docking goal and waiting for result (times out in 180 seconds and will try again if required)")
        self._client.send_goal(goal)
        
        #Give the auto docking script 180 seconds.  It can take a while if it retries.
        success = self._client.wait_for_result(rospy.Duration(180))
        
        if success:
            rospy.loginfo("Auto_docking succeeded")
            self.charging_at_dock_station = True #The callback which detects the docking status can take up to 3 seconds to update which was causing coffee bot to try and redock (presuming it failed) even when the dock was successful.  Therefore hardcoding this value after success.
            return True
        else:
            rospy.loginfo("Auto_docking failed")
            return False

    def GoCloseToTheChargingStation(self):
        #the auto docking script works well as long as you are roughly 1 meter from the docking station.  So let's get close first...
        rospy.loginfo("Let's go near the docking station")
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        #set a Pose near the docking station
        goal.target_pose.pose = Pose(Point(float(-.0114), float(.0226), float(0)), Quaternion(float(0), float(0), float(0.892), float(-1.5)))
        #start moving
        self.move_base.send_goal(goal)
        #allow TurtleBot up to 60 seconds to get close to 
        success = self.move_base.wait_for_result(rospy.Duration(60)) 
        if not success:
            self.move_base.cancel_goal()
            rospy.loginfo("The base failed to reach the desired pose near the charging station")
            return False
        else:
            # We made it!
            state = self.move_base.get_state()
            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("Hooray, reached the desired pose near the charging station")
                return True
        

    def ButtonEventCallback(self,data):
        button = ""
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