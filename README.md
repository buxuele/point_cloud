# LiDAR Lift Monitor

A PyQt6-based monitoring system for LiDAR-equipped elevators.
It provides real-time 3D point cloud visualization, occupancy estimation, and bypass control for crowded elevators.

## Architecture & Refactoring (v2.0)
- The codebase has been refactored into a `src/` directory structure for better modularity.
- **UI & Aesthetics**: The interface features a strictly monochrome dark theme (Cold Grey/White) to ensure a premium, restrained professional look, completely free of generic "tech blue" and hover animations. Navigation enforces explicit text labels for all buttons, avoiding ambiguous icon-only designs.
- **Account System**: A multi-user JSON registry (`data/accounts.json`) provides role-based access control. The `admin` role can add/remove users through the dedicated Account Management dialog, while standard `user` accounts have restricted privileges.
- **Fail-Fast SDK**: The sensor connection incorporates a fast-fail fallback to a Mock mode if the HPS3D SDK DLL is missing or errors out, preventing blocking UI startup on unsupported environments.

## Running the Project
The project uses a Python virtual environment.
Run the startup script:
`just_run.bat`

(If first time, or if missing dependencies, use `setup_and_run.bat`).

## Running Tests
To run the comprehensive unit and integration test suite, execute:
`venv\Scripts\python.exe src\tests\test_all.py`

## Tech Stack
- **Python 3.10+**
- **PyQt6** for the GUI (Monochrome strict dark theme)
- **PyQtGraph / PyOpenGL** for 3D point cloud rendering
- **Numpy** for point cloud math

## Experience & Pitfalls
- **Ctypes and DLL pathing**: The HPS3D SDK DLL expects its dependencies and internal relative paths to be valid. You must temporarily `os.chdir()` into the DLL directory before calling the connect function and restore the original working directory `cwd` immediately afterward in a `finally` block.
- **Socket Blocking**: The SDK's ethernet connection method is a blocking call that takes ~3 seconds per device to time out. Attempting connections sequentially on the main thread will lock the UI for 15+ seconds. The fail-fast mechanism (recording SDK availability on the first fail) circumvents this.
- **Color Aesthetics**: When attempting to create a premium, clean application, less is more. Tech-blue gradients and hover animations look cheap; pure white/grey typography on deeply contrasted dark panels works much better.
# point_cloud
# point_cloud
