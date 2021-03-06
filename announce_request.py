import json
import string
from json import JSONDecodeError
from typing import Tuple

import gtts


def validate_text(text) -> Tuple[bool, str]:
    if text is not None:
        if isinstance(text, str):
            if text != "":
                return True, ''
            else:
                return False, 'Payload text can not be empty'
        else:
            return False, 'Payload text is not a string'
    else:
        return False, 'Payload does not contain payload text'


def validate_lang(text) -> Tuple[bool, str]:
    if text is None:
        return True, ""
    if isinstance(text, str):
        if text != "":
            langs = gtts.lang.tts_langs()
            if langs.get(text) is not None:
                return True, f"Language {text} is not supported"
            else:
                return False, 'Language can not be empty'
        else:
            return False, 'Language can not be empty'
    else:
        return False, 'Language is not a string'


def validate_chime(chime) -> Tuple[bool, str]:
    if chime is None:
        return True, ""
    if isinstance(chime, str):
        if chime != "":
            chimes = ["none", "gong"]
            if chime in chimes:
                return True, f"Chime {chime} is not supported"
            else:
                return False, 'Chime can not be empty'
        else:
            return False, 'Chime can not be empty'
    else:
        return False, 'Chime text is not a string'


def validate_volume(value) -> Tuple[bool, str]:
    if value is None:
        return True, ""
    try:
        volume = float(value)
        if 0 <= volume <= 1.0:
            return True, ""
        else:
            return False, "Volume out of Range"
    except ValueError:
        return False, 'Volume is not a float'


class AnnounceRequest:
    payload: string = None
    lang: string = None
    volume: float = None
    chime: string = None

    def __init__(self, payload: string = None, lang: string = None, chime: string = "none", volume: float = 1.0):
        self.payload = payload
        self.lang = lang
        self.chime = chime
        self.volume = volume

    def load_from_json(self, json_str) -> Tuple[bool, str]:
        try:
            data = json.loads(json_str)
            payload_text = data.get("payload")
            text_valid, text_err = validate_text(payload_text)
            if text_valid:
                self.payload = payload_text
            else:
                return False, text_err
            payload_lang = data.get("lang")
            lang_valid, text_err = validate_lang(payload_lang)
            if lang_valid:
                self.lang = payload_lang
            else:
                return False, text_err
            payload_chime = data.get("chime")
            print(payload_chime)
            chime_valid, text_err = validate_chime(payload_chime)
            if chime_valid:
                self.chime = payload_chime
            else:
                return False, text_err
            payload_volume = data.get("volume")
            volume_valid, text_err = validate_volume(payload_volume)
            if volume_valid:
                self.volume = float(payload_volume)
            else:
                return False, text_err
            return True, "OK"

        except JSONDecodeError as e:
            print(e)
            return False, 'Payload is not JSON'

    @property
    def is_valid(self) -> bool:
        res_valid, err = validate_text(self.payload)
        lang_valid, err_lang = validate_lang(self.lang)
        vol_valid, err_vol = validate_volume(self.volume)
        chime_valid, err_vol = validate_chime(self.chime)
        if res_valid and lang_valid and vol_valid and chime_valid:
            if (self.lang is not None) and (self.volume is not None) and (self.chime is not None):
                return True
        return False

    def set_default_values(self):
        if self.lang is None:
            self.lang = "pl"
        if self.chime is None:
            self.chime = "gong"
        if self.volume is None:
            self.volume = 1.0