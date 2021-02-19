import rpyc


def stop_recording(port=18861):
    conn = None
    try:
        conn = rpyc.connect('localhost', port=port)
    except ConnectionRefusedError:
        print('Server is not running ')
    else:
        # check if it is previously recording
        if conn.root.status():
            # start recording
            conn.root.end_record()
            print('was recording, stop recording now')
        # kill the server after recording is stopped
        conn.root.set_flag(True)
    finally:
        print('it is not recording')


if __name__ == '__main__':
    stop_recording(port=18845)
