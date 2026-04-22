FROM osrf/ros:jazzy-desktop-full

# 1. Instalar dependências básicas
RUN apt-get update && apt-get install -y \
    nano \
    git \
    wget \
    python3-pip \
    sudo \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar MAVROS e ferramentas geográficas
RUN apt-get update && apt-get install -y \
    ros-jazzy-mavros \
    ros-jazzy-mavros-extras \
    geographiclib-tools \
    && rm -rf /var/lib/apt/lists/*

# 3. Instalar datasets do GeographicLib (CRÍTICO para o CommandTOL funcionar)
RUN wget https://raw.githubusercontent.com/mavlink/mavros/ros2/mavros/scripts/install_geographiclib_datasets.sh \
    && bash install_geographiclib_datasets.sh \
    && rm install_geographiclib_datasets.sh

# 4. Clonar o PX4 e instalar dependências do SITL
RUN git clone --branch main https://github.com/PX4/PX4-Autopilot.git /root/PX4-Autopilot \
    && cd /root/PX4-Autopilot \
    && ./Tools/setup/ubuntu.sh --no-interactive

# 5. Criar o Workspace do ROS 2
RUN mkdir -p /root/ros2_ws/src

# 6. Baixar o QGroundControl
#RUN wget -O /root/QGroundControl.AppImage https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage \
#    && chmod +x /root/QGroundControl.AppImage

WORKDIR /root

# 7. Entrypoint para carregar o ROS 2 automaticamente
ENTRYPOINT ["bash", "-c", "source /opt/ros/jazzy/setup.bash && exec \"$@\"", "--"]
