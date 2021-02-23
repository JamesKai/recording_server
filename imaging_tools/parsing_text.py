import pyautogui as pag
import numpy as np
import cv2
from typing import Dict


class ParsingText:
    def __init__(self, config, ocr_reader):
        self.ocr_reader = None
        try:
            self.ocr_reader = ocr_reader
        except Exception:
            return
        print(config)
        self.config = config

    @staticmethod
    def is_valid(input_number):
        if not (type(input_number) == float or type(input_number) == int):
            return False
        elif input_number > min(pag.size()) or input_number < 0:
            return False
        return True

    def get_info_of(self, item: str) -> str:
        _config = self.config[item]
        # parse the configuration info
        img, x_off, y_off, new_width, new_height = _config.values()

        # read image and get location of image
        try:
            left, top, width, height = pag.locateOnScreen(img)
        except TypeError:
            return '-1'
        else:
            # take screen shot for new location
            info_img_pil = pag.screenshot(
                region=(left + x_off, top + y_off, new_width if ParsingText.is_valid(new_width) else width,
                        new_height if ParsingText.is_valid(new_height) else height))
            # convert PIL image to numpy array
            info_img = cv2.cvtColor(np.array(info_img_pil), cv2.COLOR_RGB2BGR)
            # parse the text from the image
            out_char = self.ocr_reader.ocr_for_single_line(info_img)
            print(out_char)
            # join the string
            out_string = "".join(out_char)
            # return result
            return out_string

    def get_all_info(self) -> Dict or str:
        # if ocr_reader cannot be set up in parsing object, stop parsing image
        if not self.ocr_reader:
            return "no info as ocr reader is not found"
        # create new dictionary object to store parsing values
        config_keys = self.config.keys()
        info_storage = {}
        # iterate and populate info storage
        for item in config_keys:
            info_storage[item] = self.get_info_of(item)
        return info_storage
