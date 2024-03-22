import socket
from typing import List


class Device(object):
    """提供了对监听端口的进程的抽象"""

    def __init__(
        self, local_port: int, target_host: str, target_port: int, protocol: str
    ) -> None:
        """初始化一个管理端口的类

        Args:
            local_port (int): 本机的端口号
            target_host (str): 目标机器的IP地址
            target_port (int): 目标机器的端口
            protocol (str): 采用的协议(SR, GBN, SW)
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 允许在同一个端口上快速重启服务器
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(("", local_port))

        if protocol == "SR":
            from protocol.SR import SR

            self.__protocol = SR(self.__socket, target_host, target_port)
        elif protocol == "GBN":
            from protocol.GBN import GBN

            self.__protocol = GBN(self.__socket, target_host, target_port)
        elif protocol == "SW":
            from protocol.SW import SW

            self.__protocol = SW(self.__socket, target_host, target_port)

    def send(self, data_path: str):
        """通过这个设备发送数据

        Args:
            data_path (str): 要发送的数据文件的路径
        """
        self.__protocol.send(data_path)

    def recv(self) -> List[str]:
        """从这个设备接收数据

        Returns:
            List[str]: 受到的数据列表
        """
        return self.__protocol.recv()
