import easyocr
import pyautogui as pag
import numpy as np
import cv2
from typing import Dict


class ParsingText:
    def __init__(self, config):
        self.ocr_reader = None
        try:
            self.ocr_reader = easyocr.Reader(['en'], gpu=False)
        except Exception:
            return
        print(config)
        self.config = config

    def get_info_of(self, item: str) -> str:
        _config = self.config[item]
        # parse the configuration info
        img, x_off, y_off, new_width, new_height = _config.values()

        # read image and get location of image
        try:
            left, top, width, height = pag.locateOnScreen(img)
        except Exception:
            return '-1'
        else:
            # take screen shot for new location
            info_img_pil = pag.screenshot(region=(left + x_off, top, new_width, height))
            # convert PIL image to numpy array
            info_img = cv2.cvtColor(np.array(info_img_pil), cv2.COLOR_RGB2BGR)
            # parse the text from the image
            out = self.ocr_reader.readtext(info_img)
            # return result
            return out[0][1]

    def get_all_info(self) -> Dict or str:
        # if ocr_reader cannot be set up in parsing object, stop parsing image
        if not self.ocr_reader:
            return "no info"
        # create new dictionary object to store parsing values
        config_keys = self.config.keys()
        info_storage = {}
        # iterate and populate info storage
        for item in config_keys:
            info_storage[item] = self.get_info_of(item)
        return info_storage
