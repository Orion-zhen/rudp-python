import json
import select
from typing import List
from typing import Tuple
from random import random
from utils.args import args
from utils.data import Data
from utils.common import encapsulate, fmt_print

LOST_RATE = args.lost_rate


class SW(object):
    def __init__(
        self,
        source_socket,
        target_host: str,
        target_port: int,
        buffer_size: int = args.buffer,
        timeout: int = args.timeout,
        seq_size=10,
    ) -> None:
        """初始化传输协议

        Args:
            source_socket (socket.socket): 本机用于通信的socket
            target_host (str): 目标主机IP
            target_port (int): 目标主机端口
            buffer_size (int, optional): 缓冲区大小. Defaults to args.buffer.
            timeout (int, optional): 超时时间. Defaults to args.timeout.
            seq_size (int, optional): 序列号范围. Defaults to 10.
        """
        self.__source_socket = source_socket
        self.__target = (target_host, target_port)
        self.__buffer_size = buffer_size
        self.__timeout = timeout
        self.__seq_size = seq_size

    @property
    def seq_size(self) -> int:
        return self.__seq_size

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

    def send(self, data_path: str, lock=None) -> None:
        """使用SW协议向目的主机发送数据

        Args:
            data_path (str): 需要发送的文件路径
        """
        if lock:
            lock.acquire()
        # 初始化发送机
        seq = 0  # 将要发送的包的序列号
        last_data: Data = None  # 上一次发送的数据包
        f = open(data_path, "r")

        # 开始发送
        while True:
            line = f.readline().strip()
            if not line:
                break

            # 这里模拟发送初始的数据包
            last_data = Data(line, seq % self.seq_size)
            # 准备发送下一个数据包
            seq += 1

            ack = -1
            clock = 0  # 此处使用相对时钟而不是实际时钟

            while ack != last_data.seq:
                if clock == self.timeout:
                    # 若超时, 则重传上一个数据包, 并重置计时器
                    print("time out, try to resend")
                    self.source_socket.sendto(
                        encapsulate(last_data.seq, last_data.message).encode(),
                        self.target,
                    )
                    clock = 0

                # 停止发送, 等待接收方回复
                readable_list, _, _ = select.select([self.__source_socket], [], [], 1)
                if len(readable_list) > 0:
                    try:
                        ack, _ = self.source_socket.recvfrom(self.buffer)
                        ack = int(ack.decode())
                    except:
                        print("Error: ACK receive failed")

                # 什么消息都没收到, 等待并且增加计时器
                clock += 1

        # 结束发送
        f.close()
        self.source_socket.close()
        if lock:
            lock.release()

    def recv(self) -> List[str]:
        """使用SW协议从目的主机接收数据

        Returns:
            List[str]: 收到的数据列表
        """
        ret = []

        while True:
            readable_list, _, _ = select.select([self.source_socket], [], [], 1)

            if len(readable_list) > 0:
                buffer, _ = self.source_socket.recvfrom(self.buffer)
                buffer = buffer.decode()
                body = json.loads(buffer)
                # 解码并获得序列号
                ack_seq = body["seq"]
                message = body["message"]

                if random() > LOST_RATE:
                    # 随机成功收到包
                    self.source_socket.sendto(str(ack_seq).encode(), self.target)

                    if message == "<EOF>":
                        # 收到终止包
                        self.source_socket.close()
                        return ret
                    fmt_print(body)
                    ret.append(buffer.split(" ")[1])
