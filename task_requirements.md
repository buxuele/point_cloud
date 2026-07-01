### Requirement Specification: 3D LiDAR Lift Monitoring System

Develop a C# application that monitors 5–6 elevators in a single machine room using 3D LiDAR sensors. The system analyzes point cloud data to calculate lift capacity and sends a "Bypass/Non-Stop" signal to the lift controller when thresholds are exceeded.

| Category | Functions | Description |
| :--- | :--- | :--- |
| **Capacity Scoring & Signal Action** | Capacity % Calculation | Compute occupancy percentage based on point cloud volume |
| | Bypass Signal | 1. If capacity ≥ user-defined limit, send bypass signal to lift controller.<br>2. Signal must be serial-based. |
| | Baseline Function | 1. Allow setting baseline for different lift sizes.<br>2. Include Clear Baseline button. |
| | Signal Delay | 1. Only send bypass signal if capacity exceeds max limit for >3 seconds.<br>2. No action if threshold exceeded for less than 3 seconds. |
| **User Interface (UI) Requirements**<br>(Look at the UI reference) | Language | English only |
| | Multi-Lift Monitoring | Display real-time status for 5–6 lifts simultaneously. |
| | Sensor Runtime | Show running time of each sensor. |
| | Close Warning | On application exit, show message box:<br>- "Closing the application will immediately stop the Lift Occupancy Monitoring System. Are you sure?"<br>- Options: Yes / No. |
| **Account Management** | Single Account Type | Staff login required. |
| | Account Rights | 1. Set maximum lift capacity % limit per lift.<br>2. Monitor real-time status and sensor health.<br>3. Access dashboard and logs. |
| **Dashboard Features** | Multi-Lift View | Icons for all lifts on one screen. |
| | Live Stream | 3D point cloud visualization for verification. |
| | Bypass Frequency Chart | - Line chart showing bypass signal triggers.<br>- Adjustable time periods: past 24 hours, past 7 days, custom date ranges. |
| **Data Retention Policies**<br>(Saved in PC) | Point Cloud Snapshots | - Save frame when max capacity reached and bypass signal sent.<br>- Retention: 6 months. |
| | Audit Table (CSV Export) | - Log every trigger event: Timestamp, Lift ID, Action, Capacity %, Result.<br>- Actions:<br>  1. Bypass signal sent<br>  2. Set Baseline<br>  3. Clear Baseline<br>  4. Change Capacity %<br>  5. Closed application<br>- Retention: 5 years. |