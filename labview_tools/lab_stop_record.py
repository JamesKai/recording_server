import rpyc


if __name__ == '__main__':
    conn = rpyc.connect('localhost', port=18861).root.end_record()
    print('stop recording now')
