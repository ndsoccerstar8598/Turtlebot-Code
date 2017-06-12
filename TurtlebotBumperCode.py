'''
Created on Jun 12, 2017

@author: kristentan
'''
import roslib
import rospy
from geometry_msgs.msg import Twist
kobuki_msgs.msg import BumperEvent

# Publish led1
self.led1 = rospy.Publisher('/mobile_base/commands/led1', Led, queue_size=10) 
# Publish led2 
self.led2 = rospy.Publisher('/mobile_base/commands/led2', Led, queue_size=10)

rospy.init_node("bumper")

rospy.on_shutdown(self.shutdown)

def shutdown(self):
    rospy.loginfo("Stop!") 
    self.cmd_vel.publish(Twist()) 
    rospy.sleep(1)

#if bump data is received, process here 
#data.bumper: LEFT (0), CENTER (1), RIGHT (2) 
#data.state: RELEASED(0), PRESSED(1) 
def processBump(data): 
    global bump 
    if (data.state == BumperEvent.PRESSED): 
        bump = True 
        self.led2.publish(Led.GREEN)
    else: 
        bump = False 
        self.led1.publish(Led.RED)
    rospy.loginfo("Bumper Event") 
    rospy.loginfo(data.bumper)
    
while not rospy.is_shutdown():
    rospy.Subscriber('mobile_base/events/bumper', BumperEvent, processBump)
