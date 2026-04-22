# SeedAir-Control-System 🛸

Official repository for the international eVTOL drone project (EESC-USP/Prof. Glauco Caurin & KTH/Prof. Raffaello Mariani). Developing the full avionics suite (Software, Firmware, Hardware) using ROS 2 Jazzy and PX4 for advanced flight control and autonomous systems. Focused on robust, high-performance aerial robotics.

## 🛠 Tech Stack
**Companion Cumputer:**
- **Hardware:** Raspberry Pi 4B
- **OS:** Ubuntu 24.04 (OS)
- **Middleware:** ROS 2 Jazzy Jalisco
- **Software:** MAVROS Python

<br>

**Flight Controller:**
- **Hardware:** Cube Orange
- **Firmware:** NuttX (RTOS)
- **Middleware:** PX4 Autopilot
- **Software:** uORB C++
- **Communication:** MAVLINK

## 📂 Project Structure
- `fixed_wings/`: ROS 2 packages for fixed-wing flight modes and transitions.
- `src/`: Core source code for avionics and control algorithms.
- `Support_Files/`: Files created to help the project development

## 🚀 Quick Start
Assuming you have ROS 2 Jazzy installed:

```bash
# Clone the repository (if not already done)
git clone https://github.com/JPRM77/SeedAir-Control-System.git

# Build the workspace
colcon build --symlink-install

# Source the environment
source install/setup.bash
```

## 👥 Authors
- **João Pedro Ruiz Magalhães** - Avionics Lead (USP)
- **Lucas da Rosa Leite** - Avionics Member (USP)
- **Hicham Benkhalfa** - Avionics Member (KTH)
- **Prof. Glauco Caurin** - Professor (USP)
- **Prof. Raffaello Mariani** - Professor (KTH)
