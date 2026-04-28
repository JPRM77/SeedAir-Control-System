#!/bin/bash
(
cd ../../..
colcon build --symlink-install
source install/setup.bash
ros2 run "evtol" "$1"
)
