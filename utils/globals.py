import colorsys
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import TypedDict

from shared import SessionTimeout, SessionLost, SessionOffline

DEFAULT_PORT = 6742
DEFAULT_ADDRESS = '127.0.0.1'
DEFAULT_TIMEOUT = 5
RETRY_TIMEOUT = 10
RETRY_LIMIT = 12
HEADER_SIZE = 16

CONNECTION_ERRORS = (SessionTimeout, SessionLost, SessionOffline)

MAGIC_ID = bytes('ORGB', 'UTF-8')

class ModeFlags(IntFlag):
    HAS_SPEED = (1 << 0)
    HAS_DIRECTION_LR = (1 << 1)
    HAS_DIRECTION_UD = (1 << 2)
    HAS_DIRECTION_HV = (1 << 3)
    HAS_DIRECTION = 14
    HAS_BRIGHTNESS = (1 << 4)
    HAS_PER_LED_COLOR = (1 << 5)
    HAS_MODE_SPECIFIC_COLOR = (1 << 6)
    HAS_RANDOM_COLOR = (1 << 7)


class ModeDirections(IntEnum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    HORIZONTAL = 4
    VERTICAL = 5
    NOTAPPLICABLE = 10


class ModeColors(IntEnum):
    NONE = 0
    PER_LED = 1
    MODE_SPECIFIC = 2
    RANDOM = 3


class DeviceType(IntEnum):
    MOTHERBOARD = 0
    DRAM = 1
    GPU = 2
    COOLER = 3
    LEDSTRIP = 4
    KEYBOARD = 5
    MOUSE = 6
    MOUSEMAT = 7
    HEADSET = 8
    HEADSET_STAND = 9
    UNKNOWN = 10


class ZoneType(IntEnum):
    SINGLE = 0
    LINEAR = 1
    MATRIX = 2


class SetterPacketType(IntEnum):
    SET_CLIENT_NAME = 50
    RESIZEZONE = 1000
    UPDATELEDS = 1050
    UPDATEZONELEDS = 1051
    UPDATESINGLELED = 1052
    SETCUSTOMMODE = 1100
    UPDATEMODE = 1101


class GetterPacketType(IntEnum):
    CONTROLLER_COUNT = 0
    CONTROLLER_DATA = 1
    DEVICE_LIST_UPDATED = 100


@dataclass
class ValueRange:
    min: int
    max: int
    current: int


@dataclass
class Color(object):
    red: int
    green: int
    blue: int

    @classmethod
    def fromHSV(cls, hue: int, saturation: int, value: int):
        return cls(*(round(i * 255) for i in colorsys.hsv_to_rgb(hue / 360, saturation / 100, value / 100)))

