# Generic Libraries:
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as qpsd
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import TwistStamped

# MAVROS libraries
from mavros_msgs.srv import SetMode
from mavros_msgs.srv import CommandBool
from mavros_msgs.srv import CommandTOL
from mavros_msgs.msg import State

class LandNode (Node):
        #### INICIALIZATION ####
        def __init__ (self):
                super().__init__('land_node')

                #### CONECTIONS ####
                ## SUBSCRIBERS ##
                # Subscriber: State
                self.state_sub = self.create_subscription(State, '/mavros/state', self.state_callback, qpsd)

                # Subscriber: Position
                self.pose_sub = self.create_subscription(PoseStamped, '/mavros/local_position/pose', self.pose_callback, qpsd)

                ## CLIENTS ##
                # Client: Arming
                self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')

                # Client: Takeoff
                self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')

                # Client: SetMode
                self.set_client = self.create_client(SetMode, '/mavros/set_mode')

                ## PUBLISHERS ##
                # Publisher: Velocity
                self.vel_pub = self.create_publisher(TwistStamped, '/mavros/setpoint_velocity/cmd_vel', 10)

                #### DRONES'S CURRENT INFORMATION ####
                ## STATE VARIABLES ##
                self.state = 'ARMING' # The state of the FSM (finite state machine)
                self.current_state = State()
                self.current_pose = PoseStamped()
                self.takeoff_success = False

                ## SUPPORT VARIABLES ##
                self.last_time = self.get_clock().now()
                self.cycle_counter = 0

                #### MAIN ALGORITHYM  ####
                self.timer_period = 0.1
                self.create_timer(self.timer_period, self.timer_callback)

        #### CONNECTION FUNCTIONS ####
        ## SUBSCRIBERS ##
        # Subscriber: State
        def state_callback(self, msg):
                self.current_state = msg

        # Subscriber: Position
        def pose_callback(self, msg):
                self.current_pose = msg

        ## CLIENTS ##
        # Client: Arming
        def arming_request(self, value):
                request = CommandBool.Request()
                request.value = value

                self.arming_call = self.arming_client.call_async(request)
                self.arming_call.add_done_callback(self.arming_response)

        def arming_response(self, future):
                response = future.result()
                try:
                        self.get_logger().info(f'Success: {response.success} | value: {response.result}')
                        self.state = 'TAKEOFF'
                except:
                        self.get_logger().info('ERROR on arming!')

        # Clíent: Takeoff
        def takeoff_request(self, min_pitch, yaw, latitude, longitude, altitude):
                request = CommandTOL.Request()
                request.min_pitch = min_pitch
                request.yaw = yaw
                request.latitude = latitude
                request.longitude = longitude
                request.altitude = altitude

                self.takeoff_call = self.takeoff_client.call_async(request)
                self.takeoff_call.add_done_callback(self.takeoff_response)

        def takeoff_response(self, future):
                response = future.result()
                try:
                        self.get_logger().info(f'Success: {response.success} | value: {response.result}')
                        self.takeoff_success = True
                        self.state = 'MONITORING'
                except:
                        self.get_logger().info('ERROR on arming!')


        # Client: SetMode
        def set_request(self, custom_mode):
                request = SetMode.Request()
                request.custom_mode = custom_mode

                self.set_call = self.set_client.call_async(request)
                self.set_call.add_done_callback(self.set_response)

        def set_response(self, future):
                response = future.result()
                try:
                        self.get_logger().info(f'Mode Sent: {response.mode_sent}')
                except:
                        self.get_logger().warn('ERROR at mode setting!')

        #### MAIN ALGORITHYM ####
        def timer_callback(self):
                if self.state == 'ARMING':
                        now = self.get_clock().now()
                        if (now - self.last_time).nanoseconds > 5e9:
                                self.last_time = now
                                if not self.current_state.armed:
                                        self.arming_request(True)

                elif self.state == 'TAKEOFF':
                        now = self.get_clock().now()
                        if(now - self.last_time).nanoseconds > 5e9:
                                self.last_time = now
                                if not self.takeoff_success:
                                        self.takeoff_request(0.0, 0.0, 0.0, 0.0, 30.0)

                elif self.state == 'MONITORING':
                        if self.current_pose.pose.position.z >= 25.0:
                                self.state = 'PREPARING'

                elif self.state == 'PREPARING':
                        msg = TwistStamped()

                        msg.header.stamp = self.get_clock().now().to_msg()
                        msg.header.frame_id = 'map'

                        msg.twist.linear.x = 0.0
                        msg.twist.linear.y = 15.0
                        msg.twist.linear.z = 0.0

                        msg.twist.angular.x = 0.0
                        msg.twist.angular.y = 0.0
                        msg.twist.angular.z = 0.0

                        self.vel_pub.publish(msg)
                        self. cycle_counter += 1
                        if self.cycle_counter >= 20:
                                self.state = 'OFFBOARD'

                elif self.state == 'OFFBOARD':
                        now = self.get_clock().now()
                        if (now - self.last_time).nanoseconds > 5e9:
                                self.last_time = now
                                if not self.current_state.mode == 'OFFBOARD':
                                        self.set_request('OFFBOARD')

                        msg = TwistStamped()

                        msg.header.stamp = self.get_clock().now().to_msg()
                        msg.header.frame_id = 'map'

                        msg.twist.linear.x = 0.0
                        msg.twist.linear.y = 15.0
                        msg.twist.linear.z = 0.0

                        msg.twist.angular.x = 0.0
                        msg.twist.angular.y = 0.0
                        msg.twist.angular.z = 0.0

                        self.vel_pub.publish(msg)

def main(args=None):
        rclpy.init(args=args)

        node = LandNode()

        try:
                rclpy.spin(node)
        except (KeyboardInterrupt, SystemExit, AttributeError, IndexError) as e:
                node.get_logger().warn(f'ERROR: {e}')
        finally:
                node.destroy_node()
                rclpy.shutdown()

if __name__ == '__main__':
        main()
