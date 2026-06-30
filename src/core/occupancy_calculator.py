"""
Occupancy Calculator.
Computes occupancy percentage from point cloud data vs a stored baseline.
Uses Method A: (current_points - baseline_points) / baseline_points * 100
clamped to [0, 100].
"""
from __future__ import annotations
import numpy as np


class OccupancyCalculator:
    """
    Stateless helper: call compute() each frame.
    """

    # Z-range for "human" region (mm from sensor / floor)
    PERSON_Z_MIN = 200
    PERSON_Z_MAX = 2000

    @classmethod
    def compute(
        cls,
        cloud: np.ndarray,
        baseline_points: int | None,
        max_occupancy_pct: float = 100.0
    ) -> float:
        """
        Returns occupancy in [0.0, 100.0].

        Args:
            cloud: Nx3 float32 point array.
            baseline_points: reference count of empty-elevator points.
                             If None, use a default floor estimate.
            max_occupancy_pct: not used in calculation, kept for API compat.
        """
        if cloud is None or len(cloud) == 0:
            return 0.0

        # Count points in the human-height zone
        z = cloud[:, 2]
        human_mask = (z >= cls.PERSON_Z_MIN) & (z <= cls.PERSON_Z_MAX)
        human_count = int(human_mask.sum())

        if baseline_points is None:
            # Heuristic: assume empty cab has ~50 stray points in human zone
            baseline_human = 50
        else:
            baseline_human = max(baseline_points, 1)

        occ = (human_count / baseline_human) * 100.0
        return float(np.clip(occ, 0.0, 100.0))

    @classmethod
    def auto_baseline(cls, cloud: np.ndarray) -> int:
        """Return the current human-zone point count to use as baseline."""
        if cloud is None or len(cloud) == 0:
            return 50
        z = cloud[:, 2]
        return int(((z >= cls.PERSON_Z_MIN) & (z <= cls.PERSON_Z_MAX)).sum())
