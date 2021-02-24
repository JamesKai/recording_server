import threading
import rpyc
import cv2
import asyncio
import numpy as np
import pyautogui as pag
from telegram_tools import telegram_service
from imaging_tools.parsing_text import ParsingText
from functools import partial
from pathlib import Path
from datetime import datetime as dt
from telegram_tools.telegram_service import TelegramDispatcher


class RecordingService(rpyc.Service):

    def __init__(self, config_obj, ocr_reader):
        super(RecordingService, self).__init__()
        self.config_obj = config_obj
        self.ocr_reader = ocr_reader
        # declare saving location
        self.store_path = ''
        self.status = False
        self.record_th = None
        '''declare shutting service flag, this variable will be 
        read by the server's code, every time an incoming connection 
        is finished, server will check this variable. If found out to be 
        true, then the server will shut down itself'''
        self.shutdown_service_flag: bool = False

        # telegram related
        self.telegram_th = None
        self.exposed_telegram_dispatch = None

    def exposed_status(self):
        return self.status

    def exposed_get_flag(self):
        return self.shutdown_service_flag

    '''setter for shutting down the service'''

    def exposed_set_flag(self, do_shut_down: bool):
        self.shutdown_service_flag = do_shut_down

    def exposed_start_all_services(self, store_path: str, tele_bot_token: str, port: int, fps: float,
                                   delay_time: float):
        self.start_record(store_path, delay_time, fps)
        self.start_telegram(tele_bot_token, port)

    def exposed_stop_all_services(self):
        self.stop_telegram()
        self.stop_record()

    def start_record(self, store_path: str, delay_time: float, fps: float):
        # update the recording status to true
        self.status = True
        # configure video storage path and frame rate
        self.store_path = store_path
        # spawn up a recording thread to handle all the recording related stuff
        self.record_th = threading.Thread(
            target=partial(self.record_process, store_path, fps, delay_time))
        # starting running the recording thread
        self.record_th.start()

    def start_telegram(self, tele_bot_token: str, port: int):
        # spawn up a telegram thread to handle all the telegram stuff
        self.telegram_th = threading.Thread(
            target=partial(telegram_service.start_telegram_service, tele_bot_token, port))
        '''make it a daemon server, a daemon server will automatically close itself once the
        main program is finished '''
        self.telegram_th.daemon = True
        # starting running the telegram thread
        self.telegram_th.start()
        self.exposed_telegram_dispatch = TelegramDispatcher(tele_bot_token)

    def stop_record(self):
        # updating the recoding status to false
        self.status = False
        # joining recording thread
        self.record_th.join()

    def stop_telegram(self):
        self.exposed_telegram_dispatch.send_all_subs(message='end recording')
        # joining telegram thread
        self.telegram_th.join()

    def record_process(self, store_path: str, fps: float, delay_time: float):
        # create video writer
        video_writer = RecordingService.create_video_writer(store_path, fps)
        # create parsing object
        parsing = ParsingText(config=self.config_obj, ocr_reader=self.ocr_reader)
        capture_count = 0

        async def record_task():
            # make a screenshot
            img = pag.screenshot()
            # convert these pixels to a proper numpy array to work with OpenCV
            frame = np.array(img)
            # convert colors from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # write the frame
            video_writer.write(frame)

        async def delay_task():
            await asyncio.sleep(delay_time)

        async def send_info_task():
            if capture_count % 2 == 0:
                info = parsing.get_all_info()
                self.exposed_telegram_dispatch.send_all_subs(message=info.__str__())

        async def tasks():
            recording_task = asyncio.create_task(record_task())
            delaying_task = asyncio.create_task(delay_task())
            sending_task = asyncio.create_task(send_info_task())
            await recording_task
            await delaying_task
            await sending_task

        # keep recording until the status is off
        while self.status:
            asyncio.run(tasks())
            capture_count += 1

        # clean up video writer
        video_writer.release()

    @staticmethod
    def create_video_writer(store_path: str, fps: float):
        pth = Path(store_path, dt.now().strftime('%Y_%m_%d_%H_%M') + '.avi')
        pth_in_str = str(pth)
        # display screen resolution, get it from OS settings
        screen_size = pag.size()
        # define the codec
        fourcc = cv2.VideoWriter_fourcc(*"DIVX")
        # create the video writer object
        return cv2.VideoWriter(pth_in_str, fourcc, fps, screen_size)
