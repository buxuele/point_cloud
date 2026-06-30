"""
Comprehensive Unit and Integration Test Suite.
Tests Core components (AccountManager, OccupancyCalculator, DataStore, BypassController, SensorManager).
Runs cleanly via Python's standard unittest library.
"""
from __future__ import annotations

import os
import sys
import time
import shutil
import unittest
from unittest.mock import patch
import numpy as np

# Ensure project src directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication

from core.account_manager import AccountManager
from core.occupancy_calculator import OccupancyCalculator
from core.data_store import DataStore
from core.bypass_controller import BypassController
from core.sensor_manager import SensorManager, ElevatorConfig


class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "test_accounts.json")
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass
        self.patcher = patch('core.account_manager.ACCOUNTS_FILE', self.db_path)
        self.patcher.start()
        self.mgr = AccountManager()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception as e:
                print(f"[WARN] Failed to remove test DB: {e}")

    def test_default_seed(self):
        # Admin should exist
        success = self.mgr.login("admin", "123")
        self.assertTrue(success)
        self.assertEqual(self.mgr.current_role, "admin")

    def test_add_delete_account(self):
        # Add normal user
        success, msg = self.mgr.add_account("user1", "pass123", "user")
        self.assertTrue(success)
        self.assertEqual(msg, "OK")

        # Try logging in
        success = self.mgr.login("user1", "pass123")
        self.assertTrue(success)
        self.assertEqual(self.mgr.current_role, "user")

        # Must log back in as admin to do account management actions
        self.mgr.login("admin", "123")

        # Try adding duplicate (overwrite actually works in json)
        success, msg = self.mgr.add_account("user1", "otherpass", "user")
        self.assertTrue(success) # Because add_account overwrites
        
        # List accounts
        accounts = self.mgr.get_all_accounts()
        usernames = [a["username"] for a in accounts]
        self.assertIn("user1", usernames)
        self.assertIn("admin", usernames)

        # Delete account
        success, msg = self.mgr.remove_account("user1")
        self.assertTrue(success)
        success = self.mgr.login("user1", "otherpass")
        self.assertFalse(success)

        # Must log back in as admin
        self.mgr.login("admin", "123")

        # Cannot delete admin if it's the last one, and cannot delete yourself
        success, msg = self.mgr.remove_account("admin")
        self.assertFalse(success)


class TestOccupancyCalculator(unittest.TestCase):
    def test_empty_cloud(self):
        occ = OccupancyCalculator.compute(None, None)
        self.assertEqual(occ, 0.0)
        
        empty_cloud = np.zeros((0, 3))
        occ = OccupancyCalculator.compute(empty_cloud, None)
        self.assertEqual(occ, 0.0)

    def test_z_clamping_and_count(self):
        points = []
        # z below min (200)
        for _ in range(10):
            points.append([100, 100, 100])
        # z in range (200 - 2000)
        for _ in range(10):
            points.append([100, 100, 500])
        # z above max (2000)
        for _ in range(10):
            points.append([100, 100, 2500])
            
        cloud = np.array(points, dtype=np.float32)
        
        # Test baseline=None -> baseline_human = 50
        # human_count = 10 -> occ = 10 / 50 * 100 = 20%
        occ = OccupancyCalculator.compute(cloud, None)
        self.assertEqual(occ, 20.0)

        # Test baseline=10 -> baseline_human = 10
        # human_count = 10 -> occ = 10 / 10 * 100 = 100%
        occ = OccupancyCalculator.compute(cloud, 10)
        self.assertEqual(occ, 100.0)

        # Test baseline=100 -> baseline_human = 100
        # human_count = 10 -> occ = 10 / 100 * 100 = 10%
        occ = OccupancyCalculator.compute(cloud, 100)
        self.assertEqual(occ, 10.0)

    def test_auto_baseline(self):
        points = [[100, 100, 500], [100, 100, 100], [100, 100, 1500]]
        cloud = np.array(points, dtype=np.float32)
        base = OccupancyCalculator.auto_baseline(cloud)
        self.assertEqual(base, 2)


class TestDataStore(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "test_audit.db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.test_snapshot_dir = os.path.join(os.path.dirname(__file__), "test_snapshots")
        if os.path.exists(self.test_snapshot_dir):
            shutil.rmtree(self.test_snapshot_dir)
        os.makedirs(self.test_snapshot_dir, exist_ok=True)
        
        import core.data_store
        self.orig_ds_snapshot_dir = core.data_store.SNAPSHOT_DIR
        core.data_store.SNAPSHOT_DIR = self.test_snapshot_dir
        
        self.ds = DataStore(self.db_path)

    def tearDown(self):
        import core.data_store
        core.data_store.SNAPSHOT_DIR = self.orig_ds_snapshot_dir
        
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception as e:
                print(f"[WARN] Failed to remove test DB: {e}")
        if os.path.exists(self.test_snapshot_dir):
            try:
                shutil.rmtree(self.test_snapshot_dir)
            except Exception as e:
                print(f"[WARN] Failed to remove test DB: {e}")

    def test_logging(self):
        self.ds.clear_all_data()
        self.assertEqual(self.ds.get_bypass_count("Elevator 01", 24), 0)

        self.ds.log_event("Elevator 01", "BYPASS_SENT", 92.5, "OK")
        self.assertEqual(self.ds.get_bypass_count("Elevator 01", 24), 1)

        events = self.ds.get_bypass_events("Elevator 01", 24)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["occupancy_pct"], 92.5)

    def test_export_csv(self):
        self.ds.clear_all_data()
        self.ds.log_event("Elevator 01", "BYPASS_SENT", 95.0, "OK")
        csv_path = "test_export.csv"
        if os.path.exists(csv_path):
            os.remove(csv_path)
        try:
            self.ds.export_csv(csv_path)
            self.assertTrue(os.path.exists(csv_path))
            with open(csv_path, encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Elevator 01", content)
                self.assertIn("BYPASS_SENT", content)
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)

    def test_snapshots(self):
        cloud = np.random.rand(10, 3).astype(np.float32)
        path = self.ds.save_snapshot("Elevator_01", cloud)
        self.assertTrue(os.path.exists(path))
        loaded = np.load(path)
        self.assertEqual(loaded.shape, (10, 3))


class TestBypassController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if not cls.app:
            cls.app = QApplication([])

    def test_bypass_logic(self):
        ctrl = BypassController("Elevator 01", serial_port=None, delay_seconds=0.1)
        
        status_changes = []
        bypass_triggers = []
        
        ctrl.status_changed.connect(lambda eid, stat: status_changes.append(stat))
        ctrl.bypass_triggered.connect(lambda eid: bypass_triggers.append(eid))

        # 1. Under threshold
        ctrl.update(50.0, 80.0)
        self.assertEqual(ctrl.status, "ALLOW")
        self.assertEqual(len(status_changes), 0)

        # 2. Exceeds threshold
        ctrl.update(90.0, 80.0)
        self.assertEqual(ctrl.status, "ALLOW")
        
        # Wait for delay
        time.sleep(0.15)
        ctrl.update(90.0, 80.0)
        self.assertEqual(ctrl.status, "BYPASS")
        self.assertEqual(len(status_changes), 1)
        self.assertEqual(status_changes[-1], "BYPASS")
        self.assertEqual(len(bypass_triggers), 1)

        # 3. Drops below threshold
        ctrl.update(40.0, 80.0)
        self.assertEqual(ctrl.status, "ALLOW")
        self.assertEqual(len(status_changes), 2)
        self.assertEqual(status_changes[-1], "ALLOW")


class TestSensorManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if not cls.app:
            cls.app = QApplication([])

    def test_sensor_manager_lifecycle(self):
        mgr = SensorManager()
        
        cfg = ElevatorConfig("Elevator 01", ip="127.0.0.1", port=12345, max_occupancy=80.0)
        success = mgr.add_elevator(cfg, num_people=3)
        self.assertTrue(success)
        
        self.assertEqual(mgr.elevator_ids, ["Elevator 01"])
        state = mgr.get_state("Elevator 01")
        self.assertIsNotNone(state)
        self.assertEqual(state.config.max_occupancy, 80.0)

        mgr.update_max_occupancy("Elevator 01", 75.0)
        self.assertEqual(state.config.max_occupancy, 75.0)

        state.point_cloud = np.zeros((100, 3))
        mgr.set_baseline("Elevator 01")
        self.assertEqual(state.config.baseline_points, 100)

        mgr.reset_baseline("Elevator 01")
        self.assertIsNone(state.config.baseline_points)

        mgr.remove_elevator("Elevator 01")
        self.assertEqual(mgr.elevator_ids, [])


if __name__ == "__main__":
    unittest.main()
