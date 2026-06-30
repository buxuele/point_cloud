"""
Mock sensor data generator.
Simulates HPS-3D640 point cloud output for development.
"""
import numpy as np
import math
import time
import threading


class MockSensor:
    CAB_W = 1400
    CAB_D = 1200
    CAB_H = 2200

    def __init__(self, device_id: int, num_people: int = 0):
        self.device_id = device_id
        self.num_people = num_people
        self._running = False
        self._thread = None
        self._callback = None
        self._noise_offset = np.random.uniform(0, 2 * math.pi)
        # Spread out people to specific fixed coordinates to avoid overlapping
        self._positions = [
            (-350, -250),
            (350, 250),
            (-350, 250),
            (350, -250),
            (0, 0),
            (0, -400)
        ]

    def set_callback(self, callback):
        self._callback = callback

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            t = time.time() + self._noise_offset
            cloud = self._generate_frame(t)
            stats = self._compute_stats(cloud)
            if self._callback:
                self._callback(self.device_id, cloud, stats)
            time.sleep(0.1)

    def _generate_frame(self, t: float) -> np.ndarray:
        points = []
        points.append(self._floor_points(800))
        points.append(self._wall_points(600))
        for i in range(self.num_people):
            if i < len(self._positions):
                base_x, base_y = self._positions[i]
                cx = base_x + math.sin(t * 0.5 + i) * 30
                cy = base_y + math.cos(t * 0.4 + i) * 30
                points.append(self._person_points(cx, cy, n=1500))
        cloud = np.vstack(points).astype(np.float32)
        noise = np.random.normal(0, 3, cloud.shape).astype(np.float32)
        cloud += noise
        return cloud

    def _floor_points(self, n: int) -> np.ndarray:
        x = np.random.uniform(-self.CAB_W / 2, self.CAB_W / 2, n)
        y = np.random.uniform(-self.CAB_D / 2, self.CAB_D / 2, n)
        z = np.random.normal(0, 5, n)
        return np.column_stack([x, y, z])

    def _wall_points(self, n: int) -> np.ndarray:
        pts = []
        for _ in range(n // 4):
            side = np.random.randint(4)
            if side == 0:
                x, y = np.full(1, -self.CAB_W / 2), np.random.uniform(-self.CAB_D / 2, self.CAB_D / 2, 1)
            elif side == 1:
                x, y = np.full(1, self.CAB_W / 2), np.random.uniform(-self.CAB_D / 2, self.CAB_D / 2, 1)
            elif side == 2:
                x, y = np.random.uniform(-self.CAB_W / 2, self.CAB_W / 2, 1), np.full(1, -self.CAB_D / 2)
            else:
                x, y = np.random.uniform(-self.CAB_W / 2, self.CAB_W / 2, 1), np.full(1, self.CAB_D / 2)
            z = np.random.uniform(0, self.CAB_H, 1)
            pts.append(np.column_stack([x, y, z]))
        return np.vstack(pts) if pts else np.zeros((1, 3))

    def _person_points(self, cx: float, cy: float, n: int = 1500) -> np.ndarray:
        pts = []
        n_torso = int(n * 0.75)
        z_torso = np.random.uniform(200, 1550, n_torso)
        theta = np.random.uniform(0, 2 * math.pi, n_torso)
        r_x = np.random.normal(0, 200, n_torso)
        r_y = np.random.normal(0, 120, n_torso)
        taper = np.clip((z_torso - 200) / 1350, 0.4, 1.0)
        x = cx + r_x * np.cos(theta) * 0.5 * taper
        y = cy + r_y * np.sin(theta) * 0.5 * taper
        x = np.clip(x, cx - 250, cx + 250)
        y = np.clip(y, cy - 150, cy + 150)
        pts.append(np.column_stack([x, y, z_torso]))

        n_head = n - n_torso
        phi = np.random.uniform(0, math.pi, n_head)
        theta2 = np.random.uniform(0, 2 * math.pi, n_head)
        r2 = 90
        x2 = cx + r2 * np.sin(phi) * np.cos(theta2)
        y2 = cy + r2 * np.sin(phi) * np.sin(theta2)
        z2 = 1650 + r2 * np.cos(phi)
        pts.append(np.column_stack([x2, y2, z2]))
        return np.vstack(pts)

    @staticmethod
    def _compute_stats(cloud: np.ndarray) -> dict:
        if len(cloud) == 0:
            return {'aver_distance': 0, 'max_distance': 0, 'min_distance': 0, 'point_count': 0}
        z = cloud[:, 2]
        return {
            'aver_distance': float(z.mean()),
            'max_distance': float(z.max()),
            'min_distance': float(z.min()),
            'point_count': len(cloud),
        }
