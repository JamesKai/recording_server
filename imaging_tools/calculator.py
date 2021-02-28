from datetime import datetime as dt

from imaging_tools.parsing_text import ParsingText


class Calculator:

    def _rpyc_getattr(self, name):
        if name.startswith("_"):
            # disallow special and private attributes
            raise AttributeError("cannot accept private/special names")
        # allow all other attributes
        return getattr(self, name)

    def __init__(self, parsing: ParsingText):
        self.parsing = parsing
        self.start_label = 0
        self.start_time = dt.timestamp(dt.now())
        self.total_label = self.get_total_label()

    def estimate_finish_time(self) -> str:
        if self.get_total_label() is None:
            return 'total label count is not detected'
        current_label = self.get_current_label()
        if type(current_label) != (int or float):
            return 'total label count is not detected correctly'
        current_time = Calculator.get_current_time()
        diff_in_label = current_label - self.start_label
        if diff_in_label < 10:
            return "More info needed, result will be sent to you in a moment"
        diff_in_time = current_time - self.start_time
        period = diff_in_time / diff_in_label
        finish_time = (self.total_label - current_label) * period + current_time
        display_time = dt.fromtimestamp(finish_time)
        return f"{display_time.hour} : {display_time.minute}"

    @staticmethod
    def get_current_time():
        return dt.timestamp(dt.now())

    def get_current_label(self):
        return self.parsing.get_info_of('current_label')

    def set_total_label(self, label_count):
        self.total_label = label_count

    def get_total_label(self):
        return self.parsing.get_info_of('total_label')
