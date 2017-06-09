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
from geometry_msgs.msg import Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion
from kobuki_msgs.msg import PowerSystemEvent, AutoDockingAction, AutoDockingGoal, SensorState #for kobuki base power and auto docking


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

    def __init__(self):
        rospy.init_node("kobuki_button")        

        #monitor kobuki's button events
        rospy.Subscriber("/mobile_base/events/button",ButtonEvent,self.ButtonEventCallback)

        #rospy.spin() tells the program to not exit until you press ctrl + c.  If this wasn't there... it'd subscribe and then immediatly exit (therefore stop "listening" to the thread).
        rospy.spin();
        

    def ButtonEventCallback(self,data):
        button = "%s"%(button)
        if ( data.state == ButtonEvent.RELEASED ) :
            state = "released"
        else:
            state = "pressed"  
            if ( data.button == ButtonEvent.Button0 ) :
                button = "B0"
                navigator = GoToPose()

                # Customize the following values so they are appropriate for your location
                position = {'x': 2.84, 'y' : .739}
                quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}

                rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
                success = navigator.goto(position, quaternion)

                if success:
                    rospy.loginfo("Hooray, reached the desired pose")
                else:
                    rospy.loginfo("The base failed to reach the desired pose")

                #Sleep to give the last log messages time to be sent
                rospy.sleep(1)
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