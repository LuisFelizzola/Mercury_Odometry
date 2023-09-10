from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    ld=LaunchDescription()

    #DeclareLaunchArgument(
     #   'serial_port',
      #  default_value='/dev/ttyUSB0',
       # description='Serial port ESP32'
    #)
    publisher =Node(
        package="odometry",
        executable="position_publisher",
        output='screen'
        #parameters=[{'serial_port' : LaunchConfiguration('serial_port')}]
    )
    #subscriber =Node(
     #   package="publisher_subscriber_r",
      #  executable="subscriber"
    #)
    ld.add_action(publisher)
    #ld.add_action(subscriber)
    return ld