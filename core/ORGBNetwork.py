from utils import RawNetworkHandler
from typing import Callable, Union, Optional
from time import sleep
import utils.globals as setup
import threading
import struct
import warnings


class OpenRGBNetworkLayer(RawNetworkHandler):
    def __init__(self, address: str = setup.DEFAULT_ADDRESS, port: int = setup.DEFAULT_PORT, name="OpenRGBClient"):
        self.name = name
        self.lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None
        super(OpenRGBNetworkLayer, self).__init__(address, port)

    def open_session(self):
        try:
            super().open_session()
        except setup.CONNECTION_ERRORS:
            # retry recover
            return
        self.send_orgb_message(0, setup.SetterPacketType.SET_CLIENT_NAME, len(self.name), bytes(self.name, 'UTF-8'))
        self.thread = threading.Thread(target=wait_for_device_update, args=(self,))
        self.thread.start()

    def close_session(self):
        self.thread.do_run = False
        self.thread.join()
        super().close_session()

    def priority_mode(self):
        if self.thread.is_alive():
            self.thread.do_run = False
            self.thread.join()

    def standard_mode(self):
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=wait_for_device_update, args=(self,))
            self.thread.start()

    def send_orgb_message(self, device_id: int, packet_type: Union[setup.SetterPacketType, setup.GetterPacketType],
                          packet_size: int, data: bytes = None, callback: Callable[[int, bytes], any] = None):
        if 0 < packet_size != len(data):
            raise ValueError("Something went wrong. Packet size does not match packet contents")
        try:
            self.lock.acquire()
            header = struct.pack('4s3I', setup.MAGIC_ID, device_id, packet_type, packet_size)
            super().send(header)
            if packet_size > 0 and data:
                if isinstance(packet_type, setup.GetterPacketType):
                    warnings.warn("Packet Type {} does not support sending of data".format(packet_type), UserWarning)
                    self.lock.release()
                    return
                super().send(data)
            if isinstance(packet_type, setup.GetterPacketType):
                result = self.receive_orgb_message(callback)
                self.lock.release()
                return result
            self.lock.release()
        except setup.CONNECTION_ERRORS as e:
            self.lock.release()
            # retry recover
            print(e)

    def receive_orgb_message(self, callback: Callable[[int, bytes], any] = None):
        header = ''
        try:
            header = super().receive(setup.HEADER_SIZE)
        except setup.SessionTimeout as e:
            raise setup.SessionTimeout(e)
        except setup.CONNECTION_ERRORS as e:
            # retry recover
            print(e)
        if not header:
            raise setup.SessionOffline
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
            elif packet_type == setup.GetterPacketType.DEVICE_LIST_UPDATED:
                return False

        else:
            self.close_session()
            raise ConnectionAbortedError("Connected Server is not an instance of OpenRGB")


def wait_for_device_update(network: OpenRGBNetworkLayer):
    thread = threading.current_thread()
    while getattr(thread, "do_run", True):
        network.lock.acquire()
        network.timeout = 0
        try:
            result = network.receive_orgb_message()
            if not result:
                print('Device list Updated')
                # TODO add signal to update devices
            else:
                print("Unexpected Message: {}".format(result))
        except setup.SessionTimeout:
            print("timeout")
        network.timeout = setup.DEFAULT_TIMEOUT
        network.lock.release()
        count = 0
        while getattr(thread, "do_run", True) and count < 10:
            sleep(1)
            count += 1
    print("Gracefully Stopping Watchdog")
