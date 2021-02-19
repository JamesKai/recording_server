import rpyc
import threading
import time
from functools import partial
from recording_tools.closable_server.lab_closable_server import RecordingServer


def start_recording(store_path: str, fps, port=18861):
    print('running...')
    # declare connection object ,this is not needed, stating it here as pycharm cannot resolve the issues
    # of pycharm referencing local variable
    conn = None
    try:
        conn = rpyc.connect('localhost', port=port)
    except ConnectionRefusedError:
        print('Server is not running, start the server now')
        threading.Thread(target=partial(start_server, port)).start()
        time.sleep(1)
        conn = rpyc.connect('localhost', port=port)
    else:
        # check if it is currently recording
        if conn.root.status():
            print('it is already recording')
            return
    # start recording
    conn.root.start_record(store_path, fps=fps)
    print('start recording now')


def start_server(port):
    from recording_tools.recording_service.lab_record_service import RecordingService
    # create server and run the server
    server = RecordingServer(RecordingService(), port=port)
    server.start()


if __name__ == '__main__':
    start_recording("C:\\Users\\James\\Downloads", fps=1, port=18845)

