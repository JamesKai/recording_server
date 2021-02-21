import threading
import time
import rpyc
import cv2
import numpy as np
import pyautogui as pag
from telegram_tools import telegram_service
from typing import List
from telegram import Bot
from functools import partial
from pathlib import Path
from datetime import datetime as dt
from cv2 import VideoWriter


# create custom RecordingService
class RecordingService(rpyc.Service):
    def __init__(self):
        super(RecordingService, self).__init__()
        # declare saving location
        self.store_path = ''
        self.status = False
        self.record_th = None
        # default record fps to be 14
        self.record_fps = 14
        '''declare shutting service flag, this variable will be 
        read by the server's code, every time an incoming connection 
        is finished, server will check this variable. If found out to be 
        true, then the server will shut down itself'''
        self.shutdown_service_flag: bool = False

        # telegram related
        self.telegram_th = None
        self.subscribers: List[int] = []

    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        print('record server starts')

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_status(self):
        return self.status

    def exposed_get_flag(self):
        return self.shutdown_service_flag

    '''setter for shutting down the service'''

    def exposed_set_flag(self, do_shut_down: bool):
        self.shutdown_service_flag = do_shut_down

    def exposed_add_subscribers(self, subs_id):
        self.subscribers.append(subs_id)

    def exposed_pop_subscribers(self, subs_id):
        self.subscribers.remove(subs_id)

    def exposed_get_subscribers(self):
        return self.subscribers

    def exposed_start_all_services(self, store_path: str, tele_bot_token, port, fps=None):
        self.start_record(store_path, fps=fps)
        self.start_telegram(tele_bot_token, port)

    def exposed_stop_all_services(self, tele_bot_token):
        self.stop_telegram(tele_bot_token)
        self.stop_record()

    def start_record(self, store_path: str, fps=None):
        # update the recording status to true
        self.status = True
        # configure video storage path and frame rate
        self.store_path = store_path
        # if record_fps is not given, use default
        if fps:
            self.record_fps = fps
        # spawn up a recording thread to handle all the recording related stuff
        self.record_th = threading.Thread(target=partial(self.record_process, store_path))
        # starting running the recording thread
        self.record_th.start()

    def start_telegram(self, tele_bot_token, port):
        # spawn up a telegram thread to handle all the telegram stuff
        self.telegram_th = threading.Thread(
            target=partial(telegram_service.start_telegram_service, tele_bot_token, port))
        # make it a daemon server, a daemon server will automatically close itself once the
        # main program is finished
        self.telegram_th.daemon = True
        # starting running the telegram thread
        self.telegram_th.start()

    def stop_record(self):
        # updating the recoding status to false
        self.status = False
        # joining recording thread
        self.record_th.join()

    def stop_telegram(self, tele_bot_token):
        bot = Bot(token=tele_bot_token)
        # send message to each subscribers provided that they are subscribing
        for sub_id in self.subscribers:
            bot.send_message(chat_id=sub_id, text='end recording')
        # joining telegram thread
        self.telegram_th.join()

    def record_process(self, store_path: str):
        video_writer = self.create_video_writer(store_path)

        while self.status:
            # make a screenshot
            img = pag.screenshot()
            # convert these pixels to a proper numpy array to work with OpenCV
            frame = np.array(img)
            # convert colors from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # write the frame
            video_writer.write(frame)
            time.sleep(3)

        RecordingService.clean_up_after_recording(video_writer)

    def create_video_writer(self, store_path: str):
        pth = Path(store_path, dt.now().strftime('%Y_%m_%d_%H_%M') + '.avi')
        pth_in_str = str(pth)
        # display screen resolution, get it from OS settings
        screen_size = pag.size()
        # define the codec
        fourcc = cv2.VideoWriter_fourcc(*"DIVX")
        # create the video writer object
        return cv2.VideoWriter(pth_in_str, fourcc, self.record_fps, screen_size)

    @staticmethod
    def clean_up_after_recording(video_writer: VideoWriter):
        # releasing all the resources after it is stopped
        video_writer.release()
        cv2.destroyAllWindows()


