import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_arm_description = get_package_share_directory('arm_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(pkg_arm_description, 'urdf', 'arm.urdf.xacro')
    rviz_config = os.path.join(pkg_arm_description, 'rviz', 'arm.rviz')
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    # 1. Robot State Publisher (sim time aktif)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    # 2. Gazebo Sim (Harmonic)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # 3. Spawn Robot Model di Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name', 'service_robot',
            '-topic', 'robot_description',
            '-z', '0.0',
        ],
    )

    # 4. ROS-Gazebo Bridge (Clock sync)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen',
    )

    # 5. Controller Spawners
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller'],
        output='screen',
    )

    gripper_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller'],
        output='screen',
    )

    # 6. Bridge Node GUI -> Controller
    gui_bridge_node = Node(
        package='arm_description',
        executable='gui_to_controller.py',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # 7. Slider GUI (Remap ke /gui_joint_states)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
        }],
        remappings=[
            ('joint_states', 'gui_joint_states'),
        ],
    )

    # 8. RViz2 (Membaca /joint_states asli Gazebo)
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot,
        bridge,
        joint_state_broadcaster,
        arm_controller,
        gripper_controller,
        gui_bridge_node,
        joint_state_publisher_gui,
        rviz,
    ])
