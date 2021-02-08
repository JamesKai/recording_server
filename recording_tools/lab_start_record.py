import rpyc
# from rpyc.utils.server import ThreadedServer
import threading
import time
from recording_tools.closable_server.lab_closable_server import RecordingServer


def start_recording():
    # declare connection object ,this is not needed, stating it here as pycharm cannot resolve the issues
    # of pycharm referencing local variable
    conn = None
    try:
        conn = rpyc.connect('localhost', port=18861)
    except ConnectionRefusedError:
        print('Server is not running, start the server now')
        threading.Thread(target=start_server).start()
        time.sleep(1)
        conn = rpyc.connect('localhost', port=18861)
    else:
        # check if it is currently recording
        if conn.root.status():
            print('it is already recording')
            return
    # start recording
    conn.root.start_record()
    print('start recording now')


def start_server():
    from recording_tools.recording_service.lab_record_service import RecordingService
    # create server and run the server
    server = RecordingServer(RecordingService(), port=18861)
    server.start()


if __name__ == '__main__':
    print('running...')
    start_recording()

