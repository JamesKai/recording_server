import rpyc
import threading
from functools import partial
from cnocr import CnOcr, NUMBERS
from recording_tools.closable_server.lab_closable_server import RecordingServer
from typing import Dict


def start_recording(store_path: str, delay_time: float, fps: float, port: int, tele_bot_token: str, config: Dict):
    conn = None
    print('running...')
    # declare connection object ,this is not needed, stating it here as pycharm cannot resolve the issues
    # of pycharm referencing local variable
    try:
        conn = rpyc.connect('localhost', port=port)
    except ConnectionRefusedError:
        print('Server is not running, start the server now')
        # load ocr model into memory, only need to load once, run in another thread
        ocr_reader = CnOcr(cand_alphabet=NUMBERS)
        threading.Thread(target=partial(start_server, port, config, ocr_reader)).start()
        _try_connect = True
        while _try_connect:
            try:
                conn = rpyc.connect('localhost', port=port)
            except ConnectionRefusedError:
                continue
            else:
                _try_connect = False
    finally:
        # check if it is currently recording
        if conn.root.status():
            print('it is already recording')
            return
        # start recording
        conn.root.start_all_services(store_path, tele_bot_token, port, fps, delay_time)
        print('start recording now')


# config_obj is for configuring parsing text, as the obj can only be passed via constructor in RPyC, it is placed here
def start_server(port, config_obj, ocr_reader):
    from recording_tools.recording_service.lab_record_service import RecordingService
    # create server and run the server, passing RecordingService object will invoke singleton pattern
    server = RecordingServer(RecordingService(config_obj, ocr_reader), port=port)
    server.start()


if __name__ == '__main__':
    my_config = {
        'current_label': {
            'matching_image': r"C:\Users\James\Pictures\Screenshots\current_label.png",
            'matching_confidence': 0.8,
            'x_offset': 8,
            'y_offset': 38,
            'new_width': 70,
            'new_height': 16
        },
        'total_label': {
            'matching_image': r"C:\Users\James\Pictures\Screenshots\total_label.png",
            'matching_confidence': 0.8,
            'x_offset': 9,
            'y_offset': 38,
            'new_width': 70,
            'new_height': 18
        },
    }
    start_recording(r"C:\Users\James\Desktop\Video", delay_time=2, fps=0.5, port=18845,
                    tele_bot_token='1442643915:AAHvFrdv25saG8Nbl_IN4I3BmeOcQdpVdoM', config=my_config)
