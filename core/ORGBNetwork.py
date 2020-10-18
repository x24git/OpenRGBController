from utils import RawNetworkHandler
from typing import Callable, Union
import utils.globals as setup
import struct
import warnings


class OpenRGBNetworkLayer(RawNetworkHandler):
    def __init__(self, address: str = setup.DEFAULT_ADDRESS, port: int = setup.DEFAULT_PORT, name="OpenRGBClient"):
        self.name = name
        super(OpenRGBNetworkLayer, self).__init__(address, port)

    def open_session(self):
        try:
            super().open_session()
        except setup.CONNECTION_ERRORS:
            # retry recover
            return
        self.send_orgb_message(0, setup.SetterPacketType.SET_CLIENT_NAME, len(self.name), bytes(self.name, 'UTF-8'))

    def send_orgb_message(self, device_id: int, packet_type: Union[setup.SetterPacketType, setup.GetterPacketType],
                          packet_size: int, data: bytes = None):
        if 0 < packet_size != len(data):
            raise ValueError("Something went wrong. Packet size does not match packet contents")
        try:
            header = struct.pack('4s3I', setup.MAGIC_ID, device_id, packet_type, packet_size)
            super().send(header)
            if packet_size > 0 and data:
                if isinstance(packet_type, setup.GetterPacketType):
                    warnings.warn("Packet Type {} does not support sending of data".format(packet_type), UserWarning)
                    return
                super().send(data)
        except setup.CONNECTION_ERRORS as e:
            # retry recover
            print(e)

    def receive_orgb_message(self, callback: Callable[[int, bytes], any] = None):
        try:
            header = super().receive(setup.HEADER_SIZE)
        except setup.CONNECTION_ERRORS as e:
            # retry recover
            print(e)
        magic_id, device_id, packet_type, packet_size = list(struct.unpack('4s3I', header))
        if magic_id == setup.MAGIC_ID:
            if packet_type == setup.GetterPacketType.CONTROLLER_COUNT.value:
                try:
                    data = struct.unpack("I", super().receive(packet_size))
                    if callback:
                        callback(device_id, data[0])
                    else:
                        return data[0]
                except setup.CONNECTION_ERRORS as e:
                    # retry recover
                    print(e)
            elif packet_type == setup.GetterPacketType.CONTROLLER_DATA.value:
                try:
                    data = super().receive(packet_size)
                    if callback:
                        callback(device_id, data)
                    else:
                        return data
                except setup.CONNECTION_ERRORS as e:
                    # retry recover
                    print(e)
        else:
            self.close_session()
            raise ConnectionAbortedError("Connected Server is not an instance of OpenRGB")

