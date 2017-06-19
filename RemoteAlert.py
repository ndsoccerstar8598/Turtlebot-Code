'''
Created on Jun 19, 2017

@author: kristentan
'''

    
#Most probably the gmail server rejected the connection after the data command (very nasty of them to do so at this stage :). The actual message is most probably this one:

'''
    retcode (421); Msg: 4.7.0 [ip.octets.listed.here      15] Our system has detected an unusual rate of
    4.7.0 unsolicited mail originating from your IP address. To protect our
    4.7.0 users from spam, mail sent from your IP address has been temporarily
    4.7.0 rate limited. Please visit
    4.7.0  https://support.google.com/mail/answer/81126 to review our Bulk Email
    4.7.0 Senders Guidelines. qa9si9093954wjc.138 - gsmtp
How do I know that? Because I've tried it :) with the s.set_debuglevel(1), which prints the SMTP conversation and you can see firsthand what's the issue.

You've got two options here:

Continue using that relay; as explained by Google, it's unencrypted gmail-to-gmail only, and you have to un-blacklist your ip through their procedure
The most fool-proof option is to switch to TLS with authentication
Here's how the changed source looks like:
'''

# skipped your comments for readability
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion
#The following import is necessary to play the medication reminder.
from sound_play.libsoundplay import SoundClient

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

class email():
    def sendEmail(self):
        me = "29kec29@gmail.com"
        my_password = "pi770w98!"
        you = "ndimaria@stevens.edu"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Alert"
        msg['From'] = me
        msg['To'] = you

        html = '<html><body><p>Here is me changing the text to spice up your life!</p></body></html>'
        part2 = MIMEText(html, 'html')

        msg.attach(part2)

        # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
        s = smtplib.SMTP_SSL('smtp.gmail.com')
        # uncomment if interested in the actual smtp conversation
        # s.set_debuglevel(1)
        # do the smtp auth; sends ehlo if it hasn't been sent already
        s.login(me, my_password)

        s.sendmail(me, you, msg.as_string())
        s.quit()
    
if __name__ == '__main__':
    try:
        def sendEmail(self):
            me = "29kec29@gmail.com"
            my_password = "pi770w98!"
            you = "ndimaria@stevens.edu"

            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Alert"
            msg['From'] = me
            msg['To'] = you
            
            html = '<html><body><p>Here is me changing the text to spice up your life!</p></body></html>'
            part2 = MIMEText(html, 'html')

            msg.attach(part2)

            # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
            s = smtplib.SMTP_SSL('smtp.gmail.com')
            # uncomment if interested in the actual smtp conversation
            # s.set_debuglevel(1)
            # do the smtp auth; sends ehlo if it hasn't been sent already
            s.login(me, my_password)

            s.sendmail(me, you, msg.as_string())
            s.quit()
        
        rospy.init_node('nav_test', anonymous=False)
        navigator = GoToPose()

        # Customize the following values so they are appropriate for your location
        position = {'x': -.0114, 'y' : .0226}
        quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}

        rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
        success = navigator.goto(position, quaternion)

        if success:
            rospy.loginfo("Hooray, reached the desired pose")
            sendEmail(email)
            sendEmail() #Or I could just try pasting in the code I have in the class under the rospy.loginfo statement.
        else:
            rospy.loginfo("The base failed to reach the desired pose")

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)

    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")