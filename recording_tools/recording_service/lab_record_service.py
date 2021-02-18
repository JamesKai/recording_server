import threading
import pyautogui as pag
import rpyc
import cv2
import numpy as np
from rpyc.utils.server import ThreadedServer
from telegram_tools import telegram_service
from typing import List
from telegram import Bot


# create custom RecordingService
class RecordingService(rpyc.Service):
    def __init__(self):
        super(RecordingService, self).__init__()
        print('record server starts')
        self.status = False
        self.record_th = None
        # default record fps to be 14
        self.record_fps = 14
        self.shutdown_service_flag: bool = False

        # telegram related
        self.telegram_th = None
        self.subscribers:List[int] = []

    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        pass

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_get_status(self):
        return 'Recorder is on' if self.status else 'Recorder is off'

    def exposed_status(self):
        return self.status

    def exposed_get_flag(self):
        return self.shutdown_service_flag

    def exposed_set_flag(self, do_shut_down: bool):
        self.shutdown_service_flag = do_shut_down

    def exposed_start_record(self):
        self.status = True
        self.record_th = threading.Thread(target=self.record_process)
        self.record_th.start()
        # telegram related
        self.telegram_th = threading.Thread(target=telegram_service.start_telegram_service)
        # make it a daemon server
        self.telegram_th.daemon = True
        self.telegram_th.start()

    def exposed_end_record(self):
        bot = Bot(token='1442643915:AAHvFrdv25saG8Nbl_IN4I3BmeOcQdpVdoM')
        for sub_id in self.subscribers:
            bot.send_message(chat_id=sub_id, text='end recording')
        self.status = False
        self.record_th.join()
        # telegram related
        self.telegram_th.join()

    def exposed_set_fps(self, val: int) -> str:
        if self.status:
            return 'cannot change fps during recording'
        if val < 0 or val > 60:
            return 'cannot be changed, fps limit to 0-60'
        self.record_fps = val
        return f'changed fps to {val}'

    def exposed_get_fps(self) -> int:
        return self.record_fps

    def exposed_add_subscribers(self, subs_id):
        self.subscribers.append(subs_id)

    def exposed_pop_subscribers(self, subs_id):
        self.subscribers.remove(subs_id)

    def exposed_get_subscribers(self):
        return self.subscribers

    def record_process(self):
        # display screen resolution, get it from your OS settings
        screen_size = pag.size()
        # define the codec
        fourcc = cv2.VideoWriter_fourcc(*"DIVX")
        # create the video writer object
        video_writer = cv2.VideoWriter(r"C:\Users\James\Documents\IAMS\Software Development\ScreenRecord\output.avi"
                                       , fourcc, self.record_fps, screen_size)
        while self.status:
            # make a screenshot
            img = pag.screenshot()
            # convert these pixels to a proper numpy array to work with OpenCV
            frame = np.array(img)
            # convert colors from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # write the frame
            video_writer.write(frame)

        # releasing all the resources after it is stopped
        video_writer.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    server_already_on = False
    try:
        rpyc.connect('localhost', port=18861)
        print('server is already on')
        server_already_on = True
    except ConnectionRefusedError:
        print('initial server')
    if not server_already_on:
        # shared the same service instance across multiple request from client
        thread_server = ThreadedServer(RecordingService(), port=18861)
        thread_server.start()