from cmd import Cmd
import pyautogui as pag
import cv2
import numpy as np
import threading


class MyPrompt(Cmd):
    prompt = 'enter_prompt>> '
    into = "Welcome! Type ? to list commands"

    def __init__(self):
        super(MyPrompt, self).__init__()
        self.status = False
        self.record_th = threading.Thread(target=self.record_process)

    def do_get_status(self,inp):
        print('Recorder is on' if self.status else 'Recorder is off')

    def do_exit(self, inp) -> bool:
        print('Bye')
        return True

    def do_st_record(self, inp):
        self.status = True
        self.record_th.start()

    def do_end_record(self, inp):
        self.status = False
        self.record_th.join()

    def record_process(self):
        # display screen resolution, get it from your OS settings
        screen_size = pag.size()
        # define the codec
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        # create the video writer object
        video_writer = cv2.VideoWriter("output1.avi", fourcc, 12.0, screen_size)
        while self.status:
            # make a screenshot
            img = pag.screenshot()
            # convert these pixels to a proper numpy array to work with OpenCV
            frame = np.array(img)
            # convert colors from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # write the frame
            video_writer.write(frame)


if __name__ == '__main__':
    MyPrompt().cmdloop()
    print('finished the cmd loop')
