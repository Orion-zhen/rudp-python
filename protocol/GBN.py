import select
from typing import List
from typing import Tuple
from random import random
from utils.args import args
from utils.data import Data

LOST_RATE = args.lost_rate


class GBN(object):
    def __init__(
        self,
        source_socket,
        target_host: str,
        target_port: int,
        buffer_size: int = args.buffer,
        timeout: int = args.timeout,
        window_size=10,
        seq_size=10,
    ) -> None:
        """初始化传输协议

        Args:
            source_socket (socket.socket): 本机用于通信的socket
            target_host (str): 目标主机IP
            target_port (int): 目标主机端口
            buffer_size (int, optional): 缓冲区大小. Defaults to args.buffer.
            timeout (int, optional): 超时时间. Defaults to args.timeout.
            window_size (int, optional): 窗口长度. Defaults to 10.
            seq_size (int, optional): 序列号范围. Defaults to 10.
        """
        self.__source_socket = source_socket
        self.__target = (target_host, target_port)
        self.__buffer_size = buffer_size
        self.__timeout = timeout
        self.__window_size = window_size
        self.__seq_size = seq_size

    @property
    def seq_size(self) -> int:
        return self.__seq_size

    @property
    def window_size(self) -> int:
        return self.__window_size

    @property
    def timeout(self) -> int:
        return self.__timeout

    @property
    def source_socket(self):
        return self.__source_socket

    @property
    def target(self) -> Tuple[str, int]:
        return self.__target

    @property
    def buffer(self) -> int:
        return self.__buffer_size
