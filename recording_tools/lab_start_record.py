import rpyc
import threading
import time
from functools import partial
from recording_tools.closable_server.lab_closable_server import RecordingServer
from typing import Dict


def start_recording(store_path: str, delay_time: float, fps: float, port: int, tele_bot_token: str, config: Dict):
    print('running...')
    # declare connection object ,this is not needed, stating it here as pycharm cannot resolve the issues
    # of pycharm referencing local variable
    try:
        conn = rpyc.connect('localhost', port=port)
    except ConnectionRefusedError:
        print('Server is not running, start the server now')
        threading.Thread(target=partial(start_server, port, config)).start()
        time.sleep(0)
        conn = rpyc.connect('localhost', port=port)
    else:
        # check if it is currently recording
        if conn.root.status():
            print('it is already recording')
            return
    # start recording
    conn.root.start_all_services(store_path, tele_bot_token, port, fps, delay_time, config)
    print('start recording now')


# config_obj is for configuring parsing text, as the obj can only be passed via constructor in RPyC, it is placed here
def start_server(port, config_obj):
    from recording_tools.recording_service.lab_record_service import RecordingService
    # create server and run the server, passing RecordingService object will invoke singleton pattern
    server = RecordingServer(RecordingService(config_obj), port=port)
    server.start()


if __name__ == '__main__':
    my_config = {
        'power': {
            'image': r"C:\Users\James\Desktop\jai.png",
            'x_offset': 100,
            'y_offset': 200,
            'new_width': 200,
            'new_height': 100
        }
    }
    start_recording(r"C:\Users\James\Desktop", delay_time=2, fps=0.5, port=18845,
                    tele_bot_token='1442643915:AAHvFrdv25saG8Nbl_IN4I3BmeOcQdpVdoM', config=my_config)
