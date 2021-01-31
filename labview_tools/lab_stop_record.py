import rpyc


def stop_recording():
    conn = None
    try:
        conn = rpyc.connect('localhost', port=18861)
    except ConnectionRefusedError:
        print('Server is not running ')
    else:
        # check if it is previously recording
        if conn.root.status():
            # start recording
            conn.root.end_record()
            print('was recording, stop recording now')
    finally:
        print('it is not recording')


if __name__ == '__main__':
    stop_recording()
