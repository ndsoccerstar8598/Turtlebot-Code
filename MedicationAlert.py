'''
Created on Jun 14, 2017
@author: kristentan
'''

import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion
#The following import is necessary to play the medication reminder.
from sound_play.libsoundplay import SoundClient
import datetime
import MySQLdb
import time


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
        

        
class issueReminder():
        
    def shutdown(self):
        rospy.loginfo("Stop")
        rospy.sleep(1)
        
    def reminder(self):
        self.soundhandle = SoundClient()
        rospy.sleep(1)
        self.soundhandle.say("It is time to take your medication.")
        rospy.loginfo("Saying reminder now!")
    

if __name__ == '__main__':
    try:
        
        def __init__(self):
            rospy.on_shutdown(self.shutdown)
            
        #def init(soundplay):
            #rospy.init_node(soundplay)
        
        def shutdown(self):
            rospy.loginfo("Stop")
            rospy.sleep(1)
            
        def reminder(self):
            self.soundhandle = SoundClient()
            rospy.sleep(1)
            self.soundhandle.say("It is time to take your medication.")
            rospy.loginfo("Saying reminder now!")
        
        rospy.init_node('nav_test', anonymous=False)
        navigator = GoToPose()

        # Customize the following values so they are appropriate for your location
        position = {'x': .668, 'y' : -.896}
        quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}

        
        rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
        
        
        now = datetime.datetime.now()
        rospy.loginfo(now)
        if (now.minute+1 == 59):
            when = now.replace(hour=now.hour, minute=now.minute+1, second=0, microsecond=0)
        else:
            when = now.replace(hour=now.hour, minute=now.minute+1, second=0, microsecond=0)
            
        hour = 10
        minute = 6
        while (now.hour == hour and now.minute != minute):
            now = datetime.datetime.now()
            rospy.loginfo("Waiting for the correct alert time.")
            rospy.loginfo(now.minute)
            rospy.sleep(1)
        
        success = navigator.goto(position, quaternion)

        if success:
            rospy.loginfo("Hooray, reached the desired pose")
            reminder(issueReminder()) #Originally I got the 0 argument passed error. Then I tried to pass self, and that did not work. I ended up having to pass the class itself to the method because the word "self" in the reminder method refers to the issueReminder class?
            issueReminder() #Or I could just try pasting in the code I have in the class under the rospy.loginfo statement.
        else:
            rospy.loginfo("The base failed to reach the desired pose")

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)
        

    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")