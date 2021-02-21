import rpyc
import threading
import time
from functools import partial
from recording_tools.closable_server.lab_closable_server import RecordingServer


def start_recording(store_path: str, delay_time: float, fps: float, port: int, tele_bot_token: str):
    print('running...')
    # declare connection object ,this is not needed, stating it here as pycharm cannot resolve the issues
    # of pycharm referencing local variable
    try:
        conn = rpyc.connect('localhost', port=port)
    except ConnectionRefusedError:
        print('Server is not running, start the server now')
        threading.Thread(target=partial(start_server, port)).start()
        time.sleep(0)
        conn = rpyc.connect('localhost', port=port)
    else:
        # check if it is currently recording
        if conn.root.status():
            print('it is already recording')
            return
    # start recording
    conn.root.start_all_services(store_path, tele_bot_token, port, fps, delay_time)
    print('start recording now')


def start_server(port):
    from recording_tools.recording_service.lab_record_service import RecordingService
    # create server and run the server
    server = RecordingServer(RecordingService(), port=port)
    server.start()


if __name__ == '__main__':
    start_recording(r"C:\Users\James\Desktop", delay_time=2, fps=0.5, port=18845,
                    tele_bot_token='1442643915:AAHvFrdv25saG8Nbl_IN4I3BmeOcQdpVdoM')
