import sys
import socket
import select
from typing import Optional, Callable, List
import warnings
from shared import UniqueSingleton, SessionRedefinitionWarning, SessionTimeout, SessionLost, SessionOffline
import utils.globals as setup


SESSION_ERRORS = (ConnectionResetError, BrokenPipeError, TimeoutError, ConnectionRefusedError, ConnectionAbortedError)

if sys.platform.startswith("linux"):
    NOEXITSIGNAL = socket.MSG_NOSIGNAL
else:
    NOEXITSIGNAL = 0


class RawNetworkHandler(object, metaclass=UniqueSingleton):
    def __init__(self, address: str = setup.DEFAULT_ADDRESS, port: int = setup.DEFAULT_PORT):
        self.address = address
        self.port = port
        self.socket: Optional[socket.socket] = None

    def open_session(self):
        if self.socket:
            warnings.warn("Session is already open. Close session before trying to open.", SessionRedefinitionWarning)
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.address, self.port))
        except ConnectionRefusedError as e:
            self.socket = None
            raise SessionOffline from e

    def close_session(self):
        if not self.socket:
            warnings.warn("Session is already closed. Open session before trying to close.", SessionRedefinitionWarning)
            return
        self.socket.close()
        self.socket = None

    def receive(self, size: int, callback: Callable[[bytes], any] = None):
        if not self.socket:
            raise SessionLost
        self.socket.setblocking(False)
        read_sockets, write_sockets, error_sockets = select.select([self.socket], [], [], setup.DEFAULT_TIMEOUT)
        if read_sockets[0]:
            data = bytearray(size)
            try:
                self.socket.recv_into(data)
            except SESSION_ERRORS as e:
                self.close_session()
                raise SessionLost from e
            if data == '\x00' * size:
                self.close_session()
                raise SessionLost("Empty response received. Session Terminated!")
            if callback:
                callback(data)
            else:
                return data
        else:
            raise SessionTimeout('No reply received within allotted timeout period.')

    def send(self, data: bytes):
        if not self.socket:
            raise SessionLost
        try:
            self.socket.send(data, NOEXITSIGNAL)
        except SESSION_ERRORS as e:
            self.close_session()
            raise SessionLost from e
