import pyautogui as pag
import numpy as np
import cv2
from typing import Dict

DEFAULT_CONFIDENCE = 0.7


class ParsingText:

    def _rpyc_getattr(self, name):
        if name.startswith("_"):
            # disallow special and private attributes
            raise AttributeError("cannot accept private/special names")
        # allow all other attributes
        return getattr(self, name)

    def __init__(self, config, ocr_reader):
        self.ocr_reader = None
        try:
            self.ocr_reader = ocr_reader
        except Exception:
            print('ocr reader initializing fail')
            return
        self.config = config

    @staticmethod
    def is_valid(input_number):
        if not (type(input_number) == float or type(input_number) == int):
            return False
        elif input_number > min(pag.size()) or input_number < 0:
            return False
        return True

    @staticmethod
    def is_valid_confidence(confidence):
        if confidence is None:
            return False
        if 1 > confidence > 0:
            return True
        return False

    def get_info_of(self, item: str) -> str or None:
        try:
            _config = self.config[item]
        except KeyError:
            print(f'{item}: key is not found')
            return None

        # parse the configuration info
        img, confidence, x_off, y_off, new_width, new_height = _config.values()

        # read image and get location of image
        try:
            left, top, width, height = pag.locateOnScreen(img, confidence=confidence if ParsingText.is_valid_confidence(
                confidence) else DEFAULT_CONFIDENCE)
        except TypeError:
            return None
        else:
            # take screen shot for new location
            info_img_pil = pag.screenshot(
                region=(left + x_off, top + y_off, new_width if ParsingText.is_valid(new_width) else width,
                        new_height if ParsingText.is_valid(new_height) else height))
            # convert PIL image to numpy array
            info_img = cv2.cvtColor(np.array(info_img_pil), cv2.COLOR_RGB2BGR)
            # parse the text from the image
            out_char = self.ocr_reader.ocr_for_single_line(info_img)
            print(f'{item}: {out_char}')
            # join the string
            out_string = "".join(out_char)
            try:
                output = int(out_string)
            except ValueError:
                output = out_string
            # return result
            return output

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
