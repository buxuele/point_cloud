"""
3D Point Cloud Widget — fixed camera, colours and point size.
"""
from __future__ import annotations
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from ui.styles import C_TEXT2, C_SIDEBAR

try:
    import pyqtgraph as pg
    import pyqtgraph.opengl as gl
    _GL_AVAILABLE = True
except Exception:
    _GL_AVAILABLE = False


class PointCloudWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._scatter = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if not _GL_AVAILABLE:
            lbl = QLabel("OpenGL not available.\nInstall PyOpenGL to enable 3D rendering.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color:{C_TEXT2};font-size:14px;background:{C_SIDEBAR};")
            layout.addWidget(lbl)
            return

        self._view = gl.GLViewWidget()
        self._view.setBackgroundColor((8, 12, 20, 255))

        # ── Camera: look at elevator mid-height, from a nice angle ──
        self._view.setCameraPosition(distance=5200, elevation=28, azimuth=310)
        self._view.opts['center'] = pg.Vector(0, 0, 1100)

        # ── Floor grid ──
        grid = gl.GLGridItem()
        grid.setSize(2800, 2400)
        grid.setSpacing(280, 240)
        grid.setColor((30, 60, 90, 80))
        self._view.addItem(grid)

        # ── Elevator bounding box (wireframe) ──
        self._add_elevator_box()

        # ── Scatter ──
        self._scatter = gl.GLScatterPlotItem(pxMode=True)
        self._scatter.setGLOptions('additive')
        self._view.addItem(self._scatter)

        layout.addWidget(self._view)

    def _add_elevator_box(self):
        """Draw a faint wireframe to indicate the elevator cab."""
        W, D, H = 1400, 1200, 2200
        hw, hd = W / 2, D / 2
        corners = np.array([
            [-hw, -hd, 0], [hw, -hd, 0], [hw, hd, 0], [-hw, hd, 0],
            [-hw, -hd, H], [hw, -hd, H], [hw, hd, H], [-hw, hd, H],
        ], dtype=np.float32)
        edges = [
            (0,1),(1,2),(2,3),(3,0),   # floor
            (4,5),(5,6),(6,7),(7,4),   # ceiling
            (0,4),(1,5),(2,6),(3,7),   # verticals
        ]
        color = (60, 65, 75, 120)  # Changed from bluish to grayish
        for a, b in edges:
            line = gl.GLLinePlotItem(
                pos=np.array([corners[a], corners[b]]),
                color=color, width=1.0, antialias=True
            )
            self._view.addItem(line)

    # ── Public API ──────────────────────────────────────────────────

    def update_cloud(self, cloud: np.ndarray):
        if not _GL_AVAILABLE or self._scatter is None:
            return
        if cloud is None or len(cloud) == 0:
            return

        pos = np.asarray(cloud, dtype=np.float32)
        if pos.ndim != 2 or pos.shape[1] != 3:
            return

        z = pos[:, 2].copy()
        z_min, z_max = float(z.min()), float(z.max())
        if z_max > z_min:
            t = (z - z_min) / (z_max - z_min)
        else:
            t = np.zeros(len(z))

        # Changed from deep blue/cyan to monochrome white/grey
        r = np.clip(0.6 + t * 0.4, 0, 1)
        g = np.clip(0.6 + t * 0.4, 0, 1)
        b = np.clip(0.6 + t * 0.4, 0, 1)
        # Higher alpha for additive blending to ensure it's visible on dark background
        a = np.clip(0.4 + t * 0.6, 0.4, 1.0)
        colors = np.column_stack([r, g, b, a]).astype(np.float32)

        # Make points slightly larger again so additive glow works nicely
        in_person = (z >= 200) & (z <= 2000)
        sizes = np.where(in_person, 4.0, 2.0).astype(np.float32)

        try:
            self._scatter.setData(pos=pos, color=colors, size=sizes)
        except Exception as e:
            print(f"[WARN] ScatterPlot setData error: {e}")

    def clear(self):
        if self._scatter:
            empty = np.zeros((1, 3), dtype=np.float32)
            try:
                self._scatter.setData(
                    pos=empty,
                    color=np.zeros((1, 4), dtype=np.float32),
                    size=np.array([1.0], dtype=np.float32)
                )
            except Exception as e:
                print(f"[WARN] ScatterPlot clear error: {e}")

    def cleanup(self):
        """Forcefully clean up OpenGL resources to prevent draw errors on logout/re-login."""
        if not _GL_AVAILABLE or not hasattr(self, '_view'):
            return
        if self._scatter:
            try:
                self._view.removeItem(self._scatter)
            except Exception:
                pass
            self._scatter = None
        self._view.hide()
        self._view.setParent(None)
        self._view.deleteLater()
