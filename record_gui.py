import sys
from PySide2.QtWidgets import QApplication, QWidget, QPushButton
from PySide2.QtCore import Slot, QRunnable, QThreadPool
import pyautogui as pag
import cv2
import os
import numpy as np
import time


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
        # define recorder object
        self.recorder = Recorder()
        self.recorder.set_status(True)
        self.worker = Worker(self.recorder)
        # start the run method in the worker, i.e. the recording method of recorder
        self.thread_pool.start(self.worker)

    @Slot()
    def stop_recording(self):
        """Stop Recording and create video."""
        print("Stop Button has been pressed")
        # update the status to be false.
        self.recorder.set_status(False)



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


class Worker(QRunnable):
    def __init__(self, recorder):
        super(Worker, self).__init__()
        self.recorder = recorder

    def run(self) -> None:
        self.recorder.recording()


class Recorder:
    def __init__(self):
        self.set_video_writer()
        self.record_status:bool = False

    def set_video_writer(self):
        # display screen resolution, get it from your OS settings
        screen_size = pag.size()
        # define the codec
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        # create the video writer object
        self.video_writer = cv2.VideoWriter("output1.avi", fourcc, 12.0, screen_size)

    def set_status(self, status:bool):
        self.record_status = status

    def stop_recording(self):
        cv2.destroyAllWindows()
        self.video_writer.release()

    # run this method in another thread
    def recording(self):
        while self.record_status:
            # make a screenshot
            img = pag.screenshot()
            # convert these pixels to a proper numpy array to work with OpenCV
            frame = np.array(img)
            # convert colors from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # write the frame
            self.video_writer.write(frame)
        # make sure everything is closed when exited
        self.stop_recording()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
