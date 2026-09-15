#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Float64MultiArray
from builtin_interfaces.msg import Duration


class GuiToController(Node):
    def __init__(self):
        super().__init__('gui_to_controller')

        self.arm_joints = [
            'joint1_shoulder_yaw',
            'joint2_shoulder_pitch',
            'joint3_elbow_pitch',
            'joint4_wrist_pitch',
            'joint5_wrist_yaw',
            'joint6_wrist_roll',
        ]

        self.gripper_joints = [
            'gripper_left_finger_joint',
            'gripper_right_finger_joint',
        ]

        self.arm_pub = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', 10
        )
        self.gripper_pub = self.create_publisher(
            Float64MultiArray, '/gripper_controller/commands', 10
        )

        self.sub = self.create_subscription(
            JointState, '/gui_joint_states', self.joint_state_callback, 10
        )

        self.get_logger().info('GUI to Gazebo Controller Bridge Node running.')

    def joint_state_callback(self, msg: JointState):
        name_to_pos = dict(zip(msg.name, msg.position))

        # 1. Kirim posisi lengan ke arm_controller
        if all(j in name_to_pos for j in self.arm_joints):
            traj = JointTrajectory()
            traj.joint_names = self.arm_joints

            point = JointTrajectoryPoint()
            point.positions = [float(name_to_pos[j]) for j in self.arm_joints]
            point.time_from_start = Duration(sec=0, nanosec=100000000)  # 0.1 detik untuk pergerakan halus
            traj.points.append(point)

            self.arm_pub.publish(traj)

        # 2. Kirim posisi capit ke gripper_controller
        if all(j in name_to_pos for j in self.gripper_joints):
            grip_msg = Float64MultiArray()
            grip_msg.data = [float(name_to_pos[j]) for j in self.gripper_joints]
            self.gripper_pub.publish(grip_msg)


def main(args=None):
    rclpy.init(args=args)
    node = GuiToController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
