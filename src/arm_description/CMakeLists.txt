cmake_minimum_required(VERSION 3.8)
project(arm_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf launch rviz config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/gui_to_controller.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
