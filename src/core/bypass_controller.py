"""
Bypass Controller.
Sends a serial port signal when occupancy exceeds the threshold for > 3 seconds.
Also drives STATUS updates and records bypass events.
"""
from __future__ import annotations

import time
import threading
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal


class BypassController(QObject):
    """
    One instance per elevator.
    Call update(occupancy, threshold) each frame.
    Emits status_changed when ALLOW ↔ BYPASS transition occurs.
    """

    DELAY_SECONDS = 3.0

    status_changed = pyqtSignal(str, str)   # (elevator_id, "ALLOW"|"BYPASS")
    bypass_triggered = pyqtSignal(str)      # elevator_id

    def __init__(self, elevator_id: str, serial_port: Optional[str] = None,
                 baud_rate: int = 9600, delay_seconds: float = 3.0, parent=None):
        super().__init__(parent)
        self.elevator_id = elevator_id
        self.delay_seconds = delay_seconds
        self._serial_port = serial_port
        self._baud_rate = baud_rate
        self._ser = None
        self._lock = threading.Lock()

        self._current_status = "ALLOW"
        self._over_threshold_since: Optional[float] = None  # timestamp
        self._bypass_active = False

        if serial_port:
            self._open_serial()

    # Public API

    @property
    def status(self) -> str:
        return self._current_status

    def update(self, occupancy: float, threshold: float):
        """Call this every data frame with the latest occupancy %."""
        now = time.time()
        over = occupancy >= threshold

        with self._lock:
            if over:
                if self._over_threshold_since is None:
                    self._over_threshold_since = now
                elapsed = now - self._over_threshold_since
                if elapsed >= self.delay_seconds and not self._bypass_active:
                    self._activate_bypass()
            else:
                if self._bypass_active:
                    self._deactivate_bypass()
                self._over_threshold_since = None

    def close(self):
        if self._ser and self._ser.is_open:
            self._ser.close()

    # Internal

    def _activate_bypass(self):
        self._bypass_active = True
        self._current_status = "BYPASS"
        self._send_serial_signal(b"\xFF")   # Bypass ON byte
        self.status_changed.emit(self.elevator_id, "BYPASS")
        self.bypass_triggered.emit(self.elevator_id)

    def _deactivate_bypass(self):
        self._bypass_active = False
        self._current_status = "ALLOW"
        self._send_serial_signal(b"\x00")   # Bypass OFF byte
        self.status_changed.emit(self.elevator_id, "ALLOW")

    def _open_serial(self):
        try:
            import serial
            self._ser = serial.Serial(
                self._serial_port, self._baud_rate, timeout=1
            )
        except Exception as e:
            print(f"[BypassController] Serial open failed: {e}")
            self._ser = None

    def _send_serial_signal(self, data: bytes):
        if self._ser and self._ser.is_open:
            try:
                self._ser.write(data)
            except Exception as e:
                print(f"[BypassController] Serial write failed: {e}")
