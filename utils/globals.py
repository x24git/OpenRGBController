from enum import IntEnum, IntFlag
from shared import SessionTimeout, SessionLost

DEFAULT_PORT = 6742
DEFAULT_ADDRESS = '127.0.0.1'
DEFAULT_TIMEOUT = 5

CONNECTION_ERRORS = (SessionTimeout, SessionLost)


class ModeFlags(IntFlag):
    HAS_SPEED = (1 << 0)
    HAS_DIRECTION_LR = (1 << 1)
    HAS_DIRECTION_UD = (1 << 2)
    HAS_DIRECTION_HV = (1 << 3)
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


class PacketType(IntEnum):
    REQUEST_CONTROLLER_COUNT = 0
    REQUEST_CONTROLLER_DATA = 1
    SET_CLIENT_NAME = 50
    RGBCONTROLLER_RESIZEZONE = 1000
    RGBCONTROLLER_UPDATELEDS = 1050
    RGBCONTROLLER_UPDATEZONELEDS = 1051
    RGBCONTROLLER_UPDATESINGLELED = 1052
    RGBCONTROLLER_SETCUSTOMMODE = 1100
    RGBCONTROLLER_UPDATEMODE = 1101