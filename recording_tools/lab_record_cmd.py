from cmd import Cmd
from recording_tools import lab_start_record, lab_stop_record


class MyPrompt(Cmd):
    prompt = 'enter_prompt>> '
    into = "Welcome! Type ? to list commands"

    def __init__(self):
        super(MyPrompt, self).__init__()

    def do_exit(self, inp) -> bool:
        print('Bye')
        return True

    def do_start_record(self, inp):
        lab_start_record.start_recording()

    def do_end_record(self, inp):
        lab_stop_record.stop_recording()


if __name__ == '__main__':
    MyPrompt().cmdloop()
    print('finished the cmd loop')
