"""
Main Window — assembles all UI components and wires up business logic.
"""
from __future__ import annotations

import os
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QCloseEvent, QAction, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSplitter, QFrame, QSizePolicy,
    QMessageBox, QFileDialog, QTabWidget, QDialog
)

ICON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icons"))

from core.sensor_manager import SensorManager, ElevatorConfig
from core.occupancy_calculator import OccupancyCalculator
from core.bypass_controller import BypassController
from core.account_manager import AccountManager
from core.data_store import DataStore

from ui.elevator_list_widget import ElevatorListWidget
from ui.point_cloud_widget import PointCloudWidget
from ui.status_panel import StatusPanel
from ui.chart_widget import ChartWidget
from ui.log_widget import LogWidget
from ui.add_elevator_dialog import AddElevatorDialog
from ui.settings_dialog import SettingsDialog, load_config
from ui.account_dialog import AccountDialog
from ui.password_dialog import PasswordVerifyDialog
from ui.styles import (
    C_BG, C_SIDEBAR, C_PANEL, C_CARD, C_BORDER,
    C_ACCENT, C_GREEN, C_RED, C_TEXT, C_TEXT2, C_TEXT3
)

from config import DEFAULT_ELEVATORS


class MainWindow(QMainWindow):
    def __init__(self, account_manager: AccountManager):
        super().__init__()
        self._account_mgr = account_manager

        self._sensor_mgr = SensorManager()
        self._data_store = DataStore()
        self._bypass_controllers: dict[str, BypassController] = {}
        self._current_elevator: str | None = None

        self._occ_cache: dict[str, float] = {}

        self._is_alerting = False
        self._alert_timer = QTimer(self)
        self._alert_timer.timeout.connect(self._update_alert_glow)
        self._alert_glow_value = 0
        self._alert_glow_dir = 1

        self._setup_window()
        self._build_ui()
        self._connect_signals()
        self._start_sensors()
        self._ui_refresh_timer = QTimer(self)
        self._ui_refresh_timer.timeout.connect(self._refresh_secondary_stats)
        self._ui_refresh_timer.start(5000)   # every 5 s for counts

    # Window setup

    def _setup_window(self):
        self.setWindowTitle("LiDAR Lift Monitoring System")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 860)
        self.setStyleSheet(f"QMainWindow {{ background: {C_BG}; }}")

    # UI construction

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        root.addWidget(self._make_topbar())

        # Body uses a horizontal splitter
        self._body_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._body_splitter.setChildrenCollapsible(True)

        self._elev_list = ElevatorListWidget()
        self._body_splitter.addWidget(self._elev_list)

        # Center area
        self._center_widget = QWidget()
        self._center_widget.setObjectName("CenterWidget")
        
        center_v_layout = QVBoxLayout(self._center_widget)
        center_v_layout.setContentsMargins(0, 0, 0, 0)
        center_v_layout.setSpacing(0)

        # No separate title bar here; integrated into top bar.

        # Vertical splitter for 3D View and Tabs
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        v_splitter.setChildrenCollapsible(True)

        # 3D point cloud container (for overlay)
        cloud_container = QWidget()
        cloud_grid = QGridLayout(cloud_container)
        cloud_grid.setContentsMargins(0, 0, 0, 0)
        
        self._cloud_widget = PointCloudWidget()
        cloud_grid.addWidget(self._cloud_widget, 0, 0)
        
        # Focus button overlay
        overlay_layout = QVBoxLayout()
        overlay_layout.setContentsMargins(16, 16, 16, 16)
        
        top_h = QHBoxLayout()
        top_h.addStretch()
        
        self._focus_btn = QPushButton(" Focus 3D")
        self._focus_btn.setIcon(QIcon(os.path.join(ICON_DIR, "maximize.svg")))
        self._focus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._focus_btn.setCheckable(True)
        self._focus_btn.setFixedHeight(36)
        self._focus_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_SIDEBAR};
                color: {C_TEXT};
                border: 1px solid {C_BORDER};
                border-radius: 4px;
                font-size: 14px;
                padding: 0 12px;
                outline: none;
            }}
        """)
        top_h.addWidget(self._focus_btn)
        
        overlay_layout.addLayout(top_h)
        overlay_layout.addStretch()
        
        cloud_grid.addLayout(overlay_layout, 0, 0)
        
        v_splitter.addWidget(cloud_container)

        # Tabs for Chart and Log
        self._tabs = QTabWidget()
        
        self._chart = ChartWidget()
        self._tabs.addTab(self._chart, "Bypass Frequency")
        
        self._log = LogWidget()
        self._tabs.addTab(self._log, "System Log")
        
        v_splitter.addWidget(self._tabs)
        
        # Give 3D view much more space by default
        v_splitter.setSizes([700, 200])

        center_v_layout.addWidget(v_splitter, stretch=1)
        
        self._body_splitter.addWidget(self._center_widget)

        # Status panel
        self._status_panel = StatusPanel()
        self._body_splitter.addWidget(self._status_panel)
        
        # Give reasonable default widths
        self._body_splitter.setSizes([200, 800, 290])

        root.addWidget(self._body_splitter, stretch=1)

    def _make_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background: {C_SIDEBAR};
                border-bottom: 1px solid {C_BORDER};
            }}
        """)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Branding / Logo area
        brand_lbl = QLabel("LiDAR Monitor")
        brand_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        brand_lbl.setStyleSheet(f"color: {C_TEXT}; background: transparent;")
        layout.addWidget(brand_lbl)

        layout.addSpacing(16)

        # Runtime label
        self._runtime_lbl = QLabel("Runtime: 00:00:00")
        self._runtime_lbl.setStyleSheet(f"color: {C_TEXT2}; font-size: 13px; background: transparent;")
        layout.addWidget(self._runtime_lbl)

        layout.addStretch()

        # Connection indicator
        self._conn_indicator = QLabel("● Connecting")
        self._conn_indicator.setStyleSheet(f"color: {C_TEXT3}; font-weight: 600; font-size: 13px; background: transparent;")
        layout.addWidget(self._conn_indicator)
        
        layout.addSpacing(8)
        
        # Retry connect
        self._retry_btn = QPushButton(" Retry")
        self._retry_btn.setIcon(QIcon(os.path.join(ICON_DIR, "refresh.svg")))
        self._retry_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._retry_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_TEXT2}; border: none; font-size: 13px; outline: none; }}")
        self._retry_btn.clicked.connect(self._on_retry_connect)
        self._retry_btn.setVisible(False)
        layout.addWidget(self._retry_btn)

        layout.addSpacing(16)

        # Accounts (Admin only)
        self._accounts_btn = QPushButton(" Accounts")
        self._accounts_btn.setIcon(QIcon(os.path.join(ICON_DIR, "user.svg"))) # Assumes user.svg exists; if not, no icon is fine but the rule allows icons IF there is text.
        self._accounts_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._accounts_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_TEXT2}; border: none; font-size: 13px; outline: none; }}")
        self._accounts_btn.clicked.connect(self._on_accounts)
        if self._account_mgr.current_role == "admin":
            layout.addWidget(self._accounts_btn)
            layout.addSpacing(16)

        # Settings
        settings_btn = QPushButton(" Settings")
        settings_btn.setIcon(QIcon(os.path.join(ICON_DIR, "settings.svg")))
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_TEXT2}; border: none; font-size: 13px; outline: none; }}")
        settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(settings_btn)

        return bar

    # Signal wiring

    def _connect_signals(self):
        # Layout toggles
        self._focus_btn.toggled.connect(self._on_toggle_focus)

        # Sidebar
        self._elev_list.elevator_selected.connect(self._on_elevator_selected)
        self._elev_list.add_elevator_clicked.connect(self._on_add_elevator)

        # Sensor manager
        self._sensor_mgr.signals.data_updated.connect(self._on_sensor_data)
        self._sensor_mgr.signals.connection_changed.connect(self._on_connection_changed)
        self._sensor_mgr.signals.log_message.connect(self._log.append)

        # Status panel
        self._status_panel.apply_occupancy_clicked.connect(self._on_apply_occupancy)
        self._status_panel.set_baseline_clicked.connect(self._on_set_baseline)
        self._status_panel.reset_baseline_clicked.connect(self._on_reset_baseline)
        self._status_panel.export_csv_clicked.connect(self._on_export_csv)

    def _on_export_csv(self):
        eid = self._current_elevator
        if not eid:
            QMessageBox.warning(self, "Error", "No elevator selected.")
            return
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", f"bypass_events_{eid.replace(' ','_')}.csv", "CSV Files (*.csv)"
        )
        if path:
            try:
                self._data_store.export_csv(path, eid)
                QMessageBox.information(self, "Success", f"Data exported successfully to {path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Failed to export CSV: {e}")

    def _on_apply_occupancy(self, max_occ: float):
        eid = self._current_elevator
        if not eid:
            QMessageBox.warning(self, "Error", "No elevator selected.")
            return
        
        dlg = PasswordVerifyDialog(self._account_mgr, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        state = self._sensor_mgr.get_state(eid)
        if state:
            self._sensor_mgr.update_max_occupancy(eid, max_occ)
            occ = self._occ_cache.get(eid, 0.0)
            self._data_store.log_event(eid, "CHANGE_CAPACITY", occ, f"new_limit={max_occ}%")
            self._log.append(f"[INFO] {eid}: Max occupancy set to {max_occ}%")
            QMessageBox.information(self, "Success", f"Max occupancy for {eid} updated to {max_occ}%.")
        else:
            QMessageBox.warning(self, "Error", "Selected elevator is offline.")

    def _on_set_baseline(self):
        eid = self._current_elevator
        if not eid:
            QMessageBox.warning(self, "Error", "No elevator selected.")
            return
        state = self._sensor_mgr.get_state(eid)
        if not state or state.point_cloud is None:
            QMessageBox.warning(self, "Error", "No point cloud data available to set baseline.")
            return

        dlg = PasswordVerifyDialog(self._account_mgr, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
            
        self._sensor_mgr.set_baseline(eid)
        occ = self._occ_cache.get(eid, 0.0)
        base = state.config.baseline_points
        self._data_store.log_event(eid, "SET_BASELINE", occ, f"Points: {base}")
        QMessageBox.information(self, "Success", f"Baseline updated to {base} points.")

    def _on_reset_baseline(self):
        eid = self._current_elevator
        if not eid:
            QMessageBox.warning(self, "Error", "No elevator selected.")
            return

        dlg = PasswordVerifyDialog(self._account_mgr, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        state = self._sensor_mgr.get_state(eid)
        if state:
            self._sensor_mgr.reset_baseline(eid)
            occ = self._occ_cache.get(eid, 0.0)
            self._data_store.log_event(eid, "CLEAR_BASELINE", occ, "OK")
            QMessageBox.information(self, "Success", f"Baseline for {eid} has been reset.")
        else:
            QMessageBox.warning(self, "Error", "Selected elevator is offline.")

    def _on_toggle_focus(self, checked: bool):
        self._elev_list.setVisible(not checked)
        self._tabs.setVisible(not checked)
        self._status_panel.setVisible(not checked)
        if checked:
            self._focus_btn.setIcon(QIcon(os.path.join(ICON_DIR, "minimize.svg")))
            self._focus_btn.setText(" Exit Focus")
        else:
            self._focus_btn.setIcon(QIcon(os.path.join(ICON_DIR, "maximize.svg")))
            self._focus_btn.setText(" Focus 3D")

    # Sensor startup

    def _start_sensors(self):
        for name, ip, port in DEFAULT_ELEVATORS:
            cfg = ElevatorConfig(elevator_id=name, ip=ip, port=port)
            self._sensor_mgr.add_elevator(cfg)
            self._elev_list.add_elevator(name, connected=True)
            self._occ_cache[name] = 0.0

            # Bypass controller
            cfg_file = load_config()
            bc = BypassController(
                elevator_id=name,
                serial_port=cfg_file.get("serial_port") or None,
                baud_rate=cfg_file.get("baud_rate", 9600),
                delay_seconds=cfg_file.get("bypass_delay", 3.0),
                parent=self
            )
            bc.status_changed.connect(self._on_bypass_status)
            bc.bypass_triggered.connect(self._on_bypass_triggered)
            self._bypass_controllers[name] = bc

        # Select first
        if DEFAULT_ELEVATORS:
            first = DEFAULT_ELEVATORS[0][0]
            self._current_elevator = first
            self._elev_list.select_elevator(first)

    # Slots

    @pyqtSlot(str)
    def _on_elevator_selected(self, elevator_id: str):
        self._current_elevator = elevator_id
        self._cloud_widget.clear()

        # Load chart data for this elevator
        events = self._data_store.get_bypass_events(elevator_id, hours=24)
        self._chart.load_data(events)

        # Update status panel from cache
        occ = self._occ_cache.get(elevator_id, 0.0)
        self._status_panel.set_occupancy(occ)
        state = self._sensor_mgr.get_state(elevator_id)
        if state:
            bc = self._bypass_controllers.get(elevator_id)
            self._status_panel.set_status(bc.status if bc else "ALLOW")
            self._status_panel.set_max_occupancy(state.config.max_occupancy)

    @pyqtSlot(str, object, dict)
    def _on_sensor_data(self, elevator_id: str, cloud, stats: dict):
        """Called ~10 fps per elevator from sensor threads via Qt signal."""
        state = self._sensor_mgr.get_state(elevator_id)
        if not state:
            return

        # Calculate occupancy
        occ = OccupancyCalculator.compute(cloud, state.config.baseline_points,
                                          state.config.max_occupancy)
        self._occ_cache[elevator_id] = occ

        # Update bypass controller
        bc = self._bypass_controllers.get(elevator_id)
        if bc:
            bc.update(occ, state.config.max_occupancy)

        # Only update UI for the currently selected elevator
        if elevator_id == self._current_elevator:
            self._cloud_widget.update_cloud(cloud)
            self._status_panel.set_occupancy(occ)
            state.update_runtime()
            self._runtime_lbl.setText(f"Runtime: {state.runtime_str}")

    @pyqtSlot(str, bool)
    def _on_connection_changed(self, elevator_id: str, connected: bool):
        bc = self._bypass_controllers.get(elevator_id)
        bypass = (bc.status == "BYPASS") if bc else False
        self._elev_list.set_status(elevator_id, connected, bypass)
        all_ok = all(
            (self._sensor_mgr.get_state(e) and self._sensor_mgr.get_state(e).connected)
            for e in self._sensor_mgr.elevator_ids
        )
        if all_ok:
            self._conn_indicator.setText("● Connected")
            self._conn_indicator.setStyleSheet(f"color: {C_GREEN}; font-weight: 600; font-size: 13px; background: transparent;")
            self._retry_btn.setVisible(False)
        else:
            self._conn_indicator.setText("● Disconnected")
            self._conn_indicator.setStyleSheet(f"color: {C_RED}; font-weight: 600; font-size: 13px; background: transparent;")
            self._retry_btn.setVisible(True)

    @pyqtSlot(str, str)
    def _on_bypass_status(self, elevator_id: str, status: str):
        if elevator_id == self._current_elevator:
            self._status_panel.set_status(status)
            if status == "BYPASS":
                self._is_alerting = True
                self._alert_timer.start(50)
            else:
                self._is_alerting = False
                self._alert_timer.stop()
                self._center_widget.setStyleSheet("")
        
        state = self._sensor_mgr.get_state(elevator_id)
        connected = state.connected if state else False
        self._elev_list.set_status(elevator_id, connected, status == "BYPASS")
        
        self._log.append(f"[{'WARN' if status=='BYPASS' else 'INFO'}] {elevator_id}: STATUS → {status}")

    @pyqtSlot(str)
    def _on_bypass_triggered(self, elevator_id: str):
        occ = self._occ_cache.get(elevator_id, 0.0)
        self._data_store.log_event(elevator_id, "BYPASS_SENT", occ, "OK")
        # Save snapshot
        state = self._sensor_mgr.get_state(elevator_id)
        if state and state.point_cloud is not None:
            self._data_store.save_snapshot(elevator_id, state.point_cloud)
        # Refresh chart
        if elevator_id == self._current_elevator:
            events = self._data_store.get_bypass_events(elevator_id, hours=24)
            self._chart.load_data(events)


    @pyqtSlot()
    def _on_add_elevator(self):
        dlg = AddElevatorDialog(self)
        if dlg.exec():
            result = dlg.get_result()
            if result:
                cfg = ElevatorConfig(
                    elevator_id=result["name"],
                    ip=result["ip"],
                    port=result["port"],
                    max_occupancy=result["max_occupancy"]
                )
                self._sensor_mgr.add_elevator(cfg)
                self._elev_list.add_elevator(result["name"])
                self._occ_cache[result["name"]] = 0.0

    @pyqtSlot()
    def _on_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._log.append("[INFO] System settings updated.")

    @pyqtSlot()
    def _on_accounts(self):
        dlg = AccountDialog(self._account_mgr, self)
        dlg.exec()

    @pyqtSlot()
    def _on_retry_connect(self):
        if self._current_elevator:
            self._sensor_mgr.retry_connection(self._current_elevator)

    @pyqtSlot()
    def _on_toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _update_alert_glow(self):
        if not self._is_alerting:
            return
        self._alert_glow_value += 5 * self._alert_glow_dir
        if self._alert_glow_value >= 120:
            self._alert_glow_dir = -1
        elif self._alert_glow_value <= 30:
            self._alert_glow_dir = 1
        
        # Red breathing border
        alpha = self._alert_glow_value / 255.0
        self._center_widget.setStyleSheet(
            f"#CenterWidget {{ border: 2px solid rgba(248, 81, 73, {alpha}); }}"
        )

    def _refresh_secondary_stats(self):
        """Refresh bypass counts every 5 seconds."""
        eid = self._current_elevator
        if eid:
            c24 = self._data_store.get_bypass_count(eid, hours=24)
            c7d = self._data_store.get_bypass_count(eid, hours=168)
            self._status_panel.set_counts(c24, c7d)
            
            # Update sensor runtime (kept state update but removed panel set_runtime)
            state = self._sensor_mgr.get_state(eid)
            if state:
                state.update_runtime()

    # Close event — show warning

    def closeEvent(self, event: QCloseEvent):
        # Close warning dialog per requirement
        reply = QMessageBox.question(
            self, 'Close Application',
            "Closing the application will immediately stop the Lift Occupancy Monitoring System. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            event.ignore()
            return

        self._data_store.log_event(
            self._current_elevator or "ALL", "APP_CLOSED",
            self._occ_cache.get(self._current_elevator, 0.0), "OK"
        )
        # Clean up 3D view to prevent OpenGL errors on shutdown or re-login
        try:
            self._cloud_widget.cleanup()
        except Exception as e:
            print(f"[WARN] Failed to cleanup 3D view: {e}")
            
        self._sensor_mgr.stop_all()
        for bc in self._bypass_controllers.values():
            bc.close()
        event.accept()
