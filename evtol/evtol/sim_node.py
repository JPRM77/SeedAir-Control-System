import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as qpsd

from geometry_msgs.msg import TwistStamped
from geometry_msgs.msg import PoseStamped

from mavros_msgs.srv import CommandVtolTransition
from mavros_msgs.msg import AttitudeTarget
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode
from mavros_msgs.srv import CommandBool
from mavros_msgs.srv import CommandTOL
from mavros_msgs.msg import ExtendedState

class SimNode(Node):
	def __init__(self):
		super().__init__('sim_node')

		#### COMMUNICATION ####
		self.pose_sub = self.create_subscription(PoseStamped, '/mavros/local_position/pose', self.pose_callback, qpsd)
		self.status_sub = self.create_subscription(State, '/mavros/state', self.status_callback, qpsd)
		self.vtol_sub = self.create_subscription(ExtendedState, '/mavros/extended_state', self.vtol_callback, qpsd)

		self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
		self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
		self.transitioning_client = self.create_client(CommandVtolTransition, '/mavros/cmd/vtol_transition')
		self.set_client = self.create_client(SetMode, '/mavros/set_mode')		
		while not self.arming_client.wait_for_service(timeout_sec=5.0) or not self.takeoff_client.wait_for_service(timeout_sec=5.0) or not self.transitioning_client.wait_for_service(timeout_sec=5.0) or not self.set_client.wait_for_service(timeout_sec=5.0):
			self.get_logger().warn("[INITIALIZATION] At least one of the Services is not initialized yet!")

		self.vel_pub = self.create_publisher(TwistStamped, '/mavros/setpoint_velocity/cmd_vel', 10)
		self.att_pub = self.create_publisher(AttitudeTarget, '/mavros/setpoint_raw/target', 10)


		#### STATE VARIABLES ####
		self.last_time = self.get_clock().now()
		self.machine_state = 0
		self.states = [self.arming_state, self.takeoff_state, self.monitoring_state, self.transitioning_state, self.preparing_state, self.offboard_state, self.return2launch_state]
		#self.state_dict = {1:self.arming_state, 2:self.takeoff_state, 3:self.monitoring_state, 4:self.transitioning_state, 5:self.preparing_state}
		self.cycle_counter = 0
		self.takeoff_success = False

		self.pose_now = PoseStamped()
		self.state_now = State()
		self.vtol_now = ExtendedState()
		self.vtol_first = True

		#### TIMER ####
		self.timer_period = 0.02
		self.timer = self.create_timer(self.timer_period, self.timer_callback)
	
	#### STATES ####	
	def arming_state(self): #1. Arm the motors	
		now = self.get_clock().now()
		if (now - self.last_time).nanoseconds >= 5e9:
			self.last_time = self.get_clock().now()
			if not self.state_now.armed:
				self.arming_request(True)

	def takeoff_state(self): #2. The drone enters takeoff
		now = self.get_clock().now()
		if (now - self.last_time).nanoseconds >= 5e9:
			self.last_time = self.get_clock().now()
			if self.state_now.mode != 'AUTO.TAKEOFF':
				self.set_request('AUTO.TAKEOFF')

			if self.state_now.mode == 'AUTO.TAKEOFF':
				self.takeoff_request(0.0, 0.0, 0.0, 0.0, 30.0)
				#self.machine_state = 2
				#self.cycle_counter = 0

	def monitoring_state(self): #3. Check if the drones is in the proper takeoff height before changing
		if self.cycle_counter % 50 == 0:
			self.get_logger().info('[MONITORING] Entered the monitoring state!')

		if self.pose_now.pose.position.z >= 25.0:
			self.get_logger().info('[MONITORING] Monitoring Complete!')
			self.machine_state = 3
			self.cycle_counter = 0

		self.cycle_counter += 1		
		self.machine_state += 1	

	def transitioning_state(self): #4. Transition from Quadricopter to Fixed-wings
		if self.cycle_counter % 50 == 0:
			self.get_logger().info('[TRANSITIONING] Entered the transitioning state!')

		now = self.get_clock().now()
		if (now - self.last_time).nanoseconds >= 5e9:
			if self.vtol_now.vtol_state != 3:
				self.get_logger().info('[TRANSITIONING] Sending the transitioning request!')
				self.transitioning_request(3)

		self.cycle_counter += 1		

	def preparing_state(self): #5. Keep publishing data until it is possible to enter offboard
		self.vel_publish('base_link', 15.0, 0.0, 0.0, 0.0, 0.0, 0.0)
		self.cycle_counter += 1
		if self.cycle_counter >= 40:
			self.machine_state = 5

	def offboard_state(self): #6. Keep autonomous control of the drone
		self.vel_publish('base_link', 15.0, 0.0, 0.0, 0.0, 0.0, 0.0)
		now = self.get_clock().now()
		if (now - self.last_time).nanoseconds >= 5e9:
			self.last_time = now
			if not self.state_now.mode == 'OFFBOARD':
				self.set_request('OFFBOARD')

	def return2launch_state(self): #7. Return to Launch (After mission is completed)
		pass


	#### COMMUNICATION ####
	## SUBSCRIBERS ##
	def pose_callback(self, msg):
		self.pose_now = msg
	def status_callback(self, msg):
		self.state_now = msg
	def vtol_callback(self, msg):
		self.vtol_now = msg
		if self.vtol_first:
			self.vtol_first = False
			self.get_logger().info(f'The value of vtol_state is: {self.vtol_now.vtol_state}')

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
			self.machine_state = 1
			self.cycle_counter = 0
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
			if response.success:
				self.takeoff_success = True
				self.machine_state = 2
				self.cycle_counter = 0
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
			if response.success:
				self.machine_state = 4
				self.cycle_counter = 0
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
			if self.machine_state == 5:
				self.machine_state = 6
				self.cycle_counter = 0
		except Exception as e:
			self.get_logger().warn(f"[SETMODE] ERROR at Set Mode: {e}")



	## PUBLISHERS ##
	def vel_publish(self, frame_id, linear_x, linear_y, linear_z, angular_x, angular_y, angular_z):
		msg = TwistStamped()
		msg.header.stamp = self.get_clock().now().to_msg()
		msg.header.frame_id = frame_id

		msg.twist.linear.x = linear_x
		msg.twist.linear.y = linear_y
		msg.twist.linear.z = linear_z

		msg.twist.angular.x = angular_x
		msg.twist.angular.y = angular_y
		msg.twist.angular.z = angular_z
		
		self.vel_pub.publish(msg)

	def att_publish(self, frame_id, type_mask, ori_x, ori_y, ori_z, ori_w, thrust):
		msg = AttitudeTarget()

		msg.header.stamp = self.get_clock().now().to_msg()
		msg.header.frame_id = frame_id
		
		msg.orientation.x = ori_x 
		msg.orientation.y = ori_y 
		msg.orientation.z = ori_z 
		msg.orientation.w = ori_w 

		msg.thrust = thrust

		self.att_pub.publish(msg)
		
	#### SUPPORT FUNCTIONS ####



	#### TIMER ####
	def timer_callback(self):
		self.states[self.machine_state]()



def main(args=None):
	rclpy.init(args=args)

	node = SimNode()

	try:
		rclpy.spin(node)
	except Exception as e:
		node.get_logger().warn(f'ERROR at rotation: {e}')
	finally:
		node.destroy_node()
		rclpy.shutdown()
	
if __name__ == '__main__':
	main()
