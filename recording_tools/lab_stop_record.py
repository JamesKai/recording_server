import rpyc


def stop_recording(port, tele_bot_token):
    conn = None
    try:
        conn = rpyc.connect('localhost', port=port)
    except ConnectionRefusedError:
        print('Server is not running ')
    else:
        # check if it is previously recording
        if conn.root.status():
            # start recording
            conn.root.stop_all_services(tele_bot_token)
            print('was recording, stop recording now')
        # kill the server after recording is stopped
        conn.root.set_flag(True)
    finally:
        print('it is not recording')


if __name__ == '__main__':
    stop_recording(port=18845, tele_bot_token='1442643915:AAHvFrdv25saG8Nbl_IN4I3BmeOcQdpVdoM')
