import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication(sys.path)
try:
    win = MainWindow()
    print("MainWindow instantiated successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
