"""
Sensor Manager -- manages multiple HPS-3D640 sensors.
Automatically uses Mock mode on non-Windows / when DLL is absent.
Emits Qt signals with updated point cloud data.
"""
from __future__ import annotations

import os
import sys
import platform
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

SDK_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "..", "..", "windows", "Python SDK", "HPS3D_DEMO"
))

def _sdk_available() -> bool:
    if platform.system() != "Windows":
        return False
    dll_path = os.path.join(SDK_DIR, "HPS3D_SDK.dll")
    if not os.path.exists(dll_path):
        return False
    try:
        import ctypes
        ctypes.cdll.LoadLibrary(dll_path)
        return True
    except Exception as e:
        print(f"[ERROR] HPS3D SDK Load Error: {e}")
        return False

SDK_AVAILABLE = _sdk_available()


@dataclass
class ElevatorConfig:
    elevator_id: str
    ip: str = "192.168.30.202"
    port: int = 12345
    max_occupancy: float = 80.0
    baseline_points: Optional[int] = None


@dataclass
class ElevatorState:
    config: ElevatorConfig
    connected: bool = False
    device_id: int = 99
    point_cloud: Optional[np.ndarray] = None
    occupancy: float = 0.0
    status: str = "ALLOW"
    bypass_count_24h: int = 0
    bypass_count_7d: int = 0
    runtime_seconds: float = 0.0
    last_stats: dict = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)

    def update_runtime(self):
        self.runtime_seconds = time.time() - self.start_time

    @property
    def runtime_str(self) -> str:
        s = int(self.runtime_seconds)
        h, m = divmod(s, 3600)
        m, sec = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{sec:02d}"


class SensorSignals(QObject):
    data_updated = pyqtSignal(str, object, dict)
    connection_changed = pyqtSignal(str, bool)
    occupancy_updated = pyqtSignal(str, float, str)
    log_message = pyqtSignal(str)


class SensorManager:
    def __init__(self):
        self.signals = SensorSignals()
        self._elevators: Dict[str, ElevatorState] = {}
        self._sensors: Dict[str, object] = {}
        self._lock = threading.Lock()
        self._sdk_failed = False

    @property
    def elevator_ids(self):
        return list(self._elevators.keys())

    def get_state(self, elevator_id: str) -> Optional[ElevatorState]:
        return self._elevators.get(elevator_id)

    def add_elevator(self, config: ElevatorConfig, num_people: int = 0) -> bool:
        eid = config.elevator_id
        if eid in self._elevators:
            return False
        state = ElevatorState(config=config)
        with self._lock:
            self._elevators[eid] = state
        self._start_sensor(eid, num_people)
        self.signals.log_message.emit(f"[INFO] Added elevator: {eid}")
        return True

    def remove_elevator(self, elevator_id: str):
        sensor = self._sensors.pop(elevator_id, None)
        if sensor:
            sensor.stop()
        with self._lock:
            self._elevators.pop(elevator_id, None)
        self.signals.log_message.emit(f"[INFO] Removed elevator: {elevator_id}")

    def retry_connection(self, elevator_id: str):
        state = self._elevators.get(elevator_id)
        if not state:
            return
        
        # Stop existing sensor if any
        sensor = self._sensors.pop(elevator_id, None)
        if sensor and hasattr(sensor, 'stop'):
            sensor.stop()

        self._sdk_failed = False
        state.connected = False
        self.signals.connection_changed.emit(elevator_id, False)
        self.signals.log_message.emit(f"[INFO] Retrying connection for {elevator_id}...")
        
        # Give it a tiny delay to ensure socket cleanup
        threading.Timer(0.5, lambda: self._start_sensor(elevator_id, 0)).start()

    def update_max_occupancy(self, elevator_id: str, value: float):
        state = self._elevators.get(elevator_id)
        if state:
            state.config.max_occupancy = value

    def set_baseline(self, elevator_id: str):
        state = self._elevators.get(elevator_id)
        if state and state.point_cloud is not None:
            state.config.baseline_points = len(state.point_cloud)
            self.signals.log_message.emit(
                f"[INFO] Baseline set for {elevator_id}: "
                f"{state.config.baseline_points} points"
            )

    def reset_baseline(self, elevator_id: str):
        state = self._elevators.get(elevator_id)
        if state:
            state.config.baseline_points = None
            self.signals.log_message.emit(
                f"[INFO] Baseline cleared for {elevator_id}"
            )

    def stop_all(self):
        for sensor in self._sensors.values():
            sensor.stop()
        self._sensors.clear()

    def _start_sensor(self, eid: str, num_people: int = 0):
        if SDK_AVAILABLE and not self._sdk_failed:
            try:
                self._start_real_sensor(eid)
            except Exception as e:
                self._sdk_failed = True
                self.signals.log_message.emit(
                    f"[WARN] Sensor unavailable ({e}), all elevators use Mock mode"
                )
                self._start_mock_sensor(eid, num_people)
        else:
            self._start_mock_sensor(eid, num_people)

    def _start_mock_sensor(self, eid: str, num_people: int):
        from core.sensor_mock import MockSensor
        idx = list(self._elevators.keys()).index(eid)
        
        # Ensure the very first elevator (default view) has people for demonstration
        if idx == 0:
            n = 2
        else:
            n = (num_people + idx) % 5
            
        sensor = MockSensor(device_id=idx, num_people=n)
        sensor.set_callback(lambda did, cloud, stats: self._on_data(eid, cloud, stats))
        sensor.start()
        self._sensors[eid] = sensor
        state = self._elevators[eid]
        state.connected = True
        self.signals.connection_changed.emit(eid, True)
        self.signals.log_message.emit(
            f"[MOCK] {eid} started in simulation mode ({n} person(s))"
        )

    def _start_real_sensor(self, eid: str):
        saved_cwd = os.getcwd()
        os.chdir(SDK_DIR)
        try:
            sys.path.insert(0, SDK_DIR)
            from HPS3D_IF import (
                connect_by_ethernet, set_output_callback, set_output_data_type,
                set_point_cloud_mode, set_run_mode, COUTPUTEVENTFUNC,
                OUTPUT_DISTANCE_FULL, MIRROR_DISABLE, RUN_CONTINUOUS,
                EVENT_FULLPOINTCLOUDRECVD, get_point_cloud_data_cb, RET_OK
            )
            state = self._elevators[eid]
            cfg = state.config
            result = connect_by_ethernet(cfg.ip, cfg.port)
            if result['ret_value'] != RET_OK:
                raise RuntimeError(f"Cannot connect {eid} at {cfg.ip}:{cfg.port}")

            device_id = result['device_id']
            state.device_id = device_id

            def _cb(out_id, event, _ctx):
                if event == EVENT_FULLPOINTCLOUDRECVD:
                    d = get_point_cloud_data_cb(out_id)
                    if d['ret_value'] == RET_OK:
                        raw = d['point_cloud_data']
                        count = d['point_cloud_count']
                        cloud = np.array(raw[:count], dtype=np.float32)
                        self._on_data(eid, cloud, {})

            cb_func = COUTPUTEVENTFUNC(_cb)
            self._sensors[eid] = cb_func

            set_output_callback(cb_func, device_id, None)
            set_output_data_type(device_id, OUTPUT_DISTANCE_FULL)
            set_point_cloud_mode(device_id, True, MIRROR_DISABLE)
            set_run_mode(device_id, RUN_CONTINUOUS)

            state.connected = True
            self.signals.connection_changed.emit(eid, True)
            self.signals.log_message.emit(f"[SDK] {eid} connected (ID={device_id})")
        finally:
            os.chdir(saved_cwd)

    def _on_data(self, eid: str, cloud: np.ndarray, stats: dict):
        state = self._elevators.get(eid)
        if not state:
            return
        state.point_cloud = cloud
        state.last_stats = stats
        state.update_runtime()
        self.signals.data_updated.emit(eid, cloud, stats)
