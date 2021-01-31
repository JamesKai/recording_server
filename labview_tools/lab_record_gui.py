import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton
from PySide2.QtCore import Slot, QRunnable, QThreadPool
import pyautogui as pag
import cv2
import os
import numpy as np
import time
from labview_tools import lab_start_record, lab_stop_record


class App(QWidget):
    """Inherit the class Thread"""

    def __init__(self):
        """Initialize init"""
        super(App, self).__init__()
        self.title = "Screen Recorder"
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 50
        self.recorder = None
        self.thread_pool = QThreadPool()
        self.worker = None
        self.initUI()

    def initUI(self):
        """Initialize UI"""
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        button = QPushButton("Start Desktop Recorder", self)
        button.setToolTip("Click here to start recording")
        button.move(10, 10)
        button.clicked.connect(self.start_recording)
        button = QPushButton("Take Screenshot", self)
        button.setToolTip("Click here to take screenshot")
        button.move(190, 10)
        button.clicked.connect(self.take_screenshot)
        button = QPushButton("Stop Desktop Recording", self)
        button.setToolTip("Click here to stop recording")
        button.move(320, 10)
        button.clicked.connect(self.stop_recording)
        self.show()
        # do recording once it is spinned up
        # self.start_recording()

    @Slot()
    def start_recording(self):
        lab_start_record.do_recording()

    @Slot()
    def stop_recording(self):
        lab_stop_record.stop_recording()

    @staticmethod
    def take_screenshot():
        """Take screen shot and store to a directory"""
        if not os.path.isdir("screenshot"):
            os.mkdir("screenshot")
        filename = "screenshot/" + str(time.time()) + ".jpg"
        pag.screenshot(filename)
        img = cv2.imread(filename)
        cv2.imshow("Screenshot", img)
        cv2.waitKey(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
