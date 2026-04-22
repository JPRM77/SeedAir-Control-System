#!/bin/bash

echo "[INFO] Setting up video permissions (X11) for Docker..."
# Allows local applications (such as the container running as root) to access the WSLg graphical interface.
xhost +local:root > /dev/null 2>&1

echo "[INFO] Starting the PX4 + ROS 2 Jazzy workspaces in the mirrored network..."
# Starting the container with Named Volumes for data persistence.
docker run --rm --network=host \
  --device=/dev/dxg \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /mnt/wslg:/mnt/wslg \
  -v /usr/lib/wsl:/usr/lib/wsl \
  -v px4_vol:/root/PX4-Autopilot \
  -v ros2_vol:/root/ros2_ws \
  -e DISPLAY=$DISPLAY \
  -e WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
  -e LD_LIBRARY_PATH=/usr/lib/wsl/lib \
  -it px4_ros2_jazzy bash

echo "[INFO] Container closed. Revoking video permissions..."
# Revokes permission for security reasons when exiting the container.
xhost -local:root > /dev/null 2>&1
