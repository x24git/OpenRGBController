from dataclasses import dataclass
from typing import List, TypedDict, Tuple, Optional
import struct
from utils import unpack_helper
from utils.globals import *


@dataclass
class ORGBColor(Color):

    @classmethod
    def construct(cls, data: bytearray):
        size = struct.calcsize("BBBx")
        r, g, b = struct.unpack("BBBx", data[0:size])
        return cls(r, g, b), data[size:]

    @classmethod
    def calcsize(cls):
        return struct.calcsize("BBBx")


@dataclass
class ORGBLEDInfo:
    name: str
    zone_idx: int
    color: Optional[ORGBColor] = None

    @classmethod
    def construct(cls, data: bytearray):
        (name_size,), data = unpack_helper("<H", data)
        (name, zone_idx), data = unpack_helper("<{}sI".format(name_size), data)
        return cls(name.decode('UTF-8').rstrip('\x00'), zone_idx), data

@dataclass
class ORGBMZoneInfo:
    name: str
    category: int
    led_range: ValueRange
    height: int
    width: int
    matrix: List[List]
    leds: Optional[List[ORGBLEDInfo]] = None

    @classmethod
    def construct(cls, data: bytearray):
        (name_size,), data = unpack_helper("<H", data)
        (name, category, min_led, max_led, current_led,
         matrix_size), data = unpack_helper("<{}si3IH".format(name_size), data)
        category = ZoneType(category)
        led_range = ValueRange(min_led, max_led, current_led)
        height = width = 0
        matrix = []
        if category == ZoneType.MATRIX and matrix_size > 0:
            (height, width), data = unpack_helper("<2I", data)
            matrix = [[] for x in range(height)]
            for y in range(height):
                y_column, data = unpack_helper("<{}I".format(width), data)
                matrix[y] = list(map(lambda x: x if x != 0xFFFFFFFF else None, list(y_column)))
        return cls(name.decode('UTF-8').rstrip('\x00'), category, led_range, height, width, matrix, []), data


@dataclass
class ORGBModeInfo:
    name: str
    dev_id: int
    flags: ModeFlags
    speed: ValueRange
    color_guides: ValueRange
    direction: ModeDirections
    color_mode: ModeColors
    colors: List[ORGBColor]

    @classmethod
    def construct(cls, data: bytearray):
        (name_size,), data = unpack_helper("<H", data)
        (name, dev_id, flags, speed_min, speed_max, color_min, color_max,
         speed, direction, color_mode, num_colors), data = unpack_helper("<{}si8IH".format(name_size), data)
        if ModeFlags.HAS_DIRECTION & flags:
            direction = ModeDirections(direction)
        else:
            direction = ModeDirections.NOTAPPLICABLE
        color_mode = ModeColors(color_mode)
        if ModeFlags.HAS_SPEED & flags:
            speed = ValueRange(speed_min, speed_max, speed)
        else:
            speed = None
        list_colors = []
        if ModeFlags.HAS_MODE_SPECIFIC_COLOR & flags:
            color_guides = ValueRange(color_min, color_max, 0)
            for index in range(num_colors):
                color, data = ORGBColor.construct(data)
                list_colors.append(color)
        else:
            color_guides = None
        return cls(name.decode('UTF-8').rstrip('\x00'), dev_id, flags, speed,
                   color_guides, direction, color_mode, list_colors), data


@dataclass
class ORGBControllerInfo:
    name: str
    description: str
    version: str
    serial: str
    location: str
    device_type: any
    modes: List[ORGBModeInfo]
    zones: List[ORGBMZoneInfo]
    leds: List[ORGBLEDInfo]
    colors: List[ORGBColor]
    active_mode: int

    @classmethod
    def construct(cls, data: bytearray):
        (_, dev_id, name_size), data = unpack_helper("<IiH", data)
        try:
            device_type = DeviceType(dev_id)
        except ValueError:
            device_type = DeviceType.UNKNOWN
        (name, desc_size), data = unpack_helper("<{}sH".format(name_size), data)
        (description, version_size), data = unpack_helper("<{}sH".format(str(desc_size)), data)
        (version, serial_size), data = unpack_helper("<{}sH".format(version_size), data)
        (serial, loc_size), data = unpack_helper("<{}sH".format(serial_size), data)
        (location, num_modes, active_mode), data = unpack_helper("<{}sHi".format(loc_size), data)
        modes = []
        for mode in range(num_modes):
            mode_data, data = ORGBModeInfo.construct(data)
            modes.append(mode_data)
        (num_zones,), data = unpack_helper("<H".format(loc_size), data)
        zones = []
        for zone in range(num_zones):
            zone_data, data = ORGBMZoneInfo.construct(data)
            zones. append(zone_data)
        (num_leds,), data = unpack_helper("<H".format(loc_size), data)
        leds = []
        for led in range(num_leds):
            led_data, data = ORGBLEDInfo.construct(data)
            leds.append(led_data)
        (num_colors,), data = unpack_helper("<H".format(loc_size), data)
        colors = []
        for color in range(num_colors):
            color_data, data = ORGBColor.construct(data)
            colors.append(color_data)
        for idx, led in enumerate(leds):
            led.color = colors[idx]
            zones[led.zone_idx].leds.append(led)

        return cls(name.decode('UTF-8').rstrip('\x00'), description.decode('UTF-8').rstrip('\x00'),
                   version.decode('UTF-8').rstrip('\x00'), serial.decode('UTF-8').rstrip('\x00'),
                   location.decode('UTF-8').rstrip('\x00'), device_type, modes, zones, leds, colors, active_mode)




