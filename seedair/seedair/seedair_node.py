#### IMPORT GENERIC LIBRARIES ####
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

#### IMPORT MAVROS LIBRARIES ####
from mavros_msgs.srv import SetMode
from mavros_msgs.srv import CommandBool
from mavros_msgs.srv import CommandTOL
from mavros_msgs.srv import CommandVtolTransition 


class SeedAirNode(Node):
	def __init__(self):
		super().__init__('seedair_node')

		#### COMUNICATION VARIABLES ####
		## SUBSCRIBERS ##

		## CLIENTS ##
		self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
		self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
		self.set_client = self.create_client(SetMode, '/mavros/set_mode')
		self.transitioning_client = self.create_client(CommandVtolTransition, '/mavros/cmd/vtol_transition')

		## PUBLISHERS ##

		#### STATE VARIABLES ####
		self.machine_state = 1
		self.state = [self.arming_state, self.takeoff_state, self.monitoring, self.transitioning_state, self.preparing_state, self.offboard_state, self.follow_setpoint_state, self.drop_seed_state, self.return2launch_state]

		#### TIMER ####
		self.timer_period = 0.02
		self.timer = self.create_timer(self.timer_period, self.timer_callback)	

	#### COMMUNICATION FUNCTIONS ####
	## SUBSCRIBERS ##	

	## CLIENTS ##
        def arming_request(self, value):
                request = CommandBool.Request()
                request.value = value

                self.arming_call = self.arming_client.call_async(request)
                self.arming_call.add_done_callback(self.arming_response)
        def arming_response(self, future):
                response = future.result()
                try:
                        self.get_logger().info(f"[ARMING] The drone has been armed successfully! Arming Result: {response.result}")
                except Exception as e:
                        self.get_logger().warn(f"[ARMING] ERROR at arming: {e}")

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
                        self.get_logger().info(f"[TAKEOFF] Takeoff Successful! Takeoff Result: {response.result}")
                except Exception as e:
                        self.get_logger().warn(f"[TAKEOFF] ERROR at Takeoff: {e}")

        def transitioning_request(self, state):
                request = CommandVtolTransition.Request()
                request.state = state
                request.header.stamp = self.get_logger().now().to_msg()

                self.transitioning_call = self.transitioning_client.call_async(request)
                self.transitioning_call.add_done_callback(self.transitioning_response)
        def transitioning_response(self, future):
                response = future.result()
                try:
                        self.get_logger().info(f"[TRANSITIONING] Transition Successful! Transition Result: {response.result}")
                except Exception as e:
                        self.get_logger().warn(f"[TRANSITIONING] ERROR at Transitioning: {e}")

        def set_request(self, custom_mode):
                request = SetMode.Request()
                request.custom_mode = custom_mode

                self.set_call = self.set_client.call_async(request)
                self.set_call.add_done_callback(self.set_response)

        def set_response(self, future):
                response = future.result()
                try:
                        self.get_logger().info(f"[SETMODE] Set Mode Successful! Takeoff mode_sent: {response.mode_sent}")
                except Exception as e:
                        self.get_logger().warn(f"[SETMODE] ERROR at Set Mode: {e}")

	## PUBLISHERS ##

	#### MACHINE STATES ####
	def arming_state(self): #1. Arm the drone
		pass
	def takeoff_state(self):
		pass

	#### SUPPORT FUNCTIONS ####


	#### TIMER ####
	def timer_callback(self):
		self.state[self.machine_state - 1]()


def main(args=None):
	rclpy.init(args=args)

	node = SeedAirNode()

	try:
		rclpy.spin(node)
	except Exception as e:
		self.get_logger().warn(f"ERROR at rotation: {e}")
	finally:
		node.destroy_node()
		rclpy.shutdown()

if __name__ == '__main__':
	main()

