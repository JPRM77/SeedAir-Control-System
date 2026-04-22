# SeedAir-Control-System 🛸

Official repository for the international eVTOL drone project (EESC-USP/Prof. Glauco Caurin & KTH/Prof. Raffaello Mariani). Developing the full avionics suite (Software, Firmware, Hardware) using ROS 2 Jazzy and PX4 for advanced flight control and autonomous systems. Focused on robust, high-performance aerial robotics.

## 🛠 Tech Stack
- **OS:** Ubuntu 24.04 (Noble Numbat)
- **Middleware:** ROS 2 Jazzy Jalisco
- **Autopilot:** PX4 Autopilot
- **Communication:** Micro-XRCE-DDS

## 📂 Project Structure
- `fixed_wings/`: ROS 2 packages for fixed-wing flight modes and transitions.
- `src/`: Core source code for avionics and control algorithms.

## 🚀 Quick Start
Assuming you have ROS 2 Jazzy installed:

```bash
# Clone the repository (if not already done)
git clone https://github.com

# Build the workspace
colcon build --symlink-install

# Source the environment
source install/setup.bash
```

## 👥 Authors
- **João Paulo R. M.** - Avionics Lead
- **Prof. Glauco Caurin** (EESC-USP)
- **Prof. Raffaello Mariani** (KTH)
