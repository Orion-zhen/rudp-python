import json
import select
from typing import List
from typing import Tuple
from random import random
from copy import deepcopy
from utils.args import args
from utils.data import Data
from utils.common import encapsulate, fmt_print

LOST_RATE = args.lost_rate


class SR(object):
    def __init__(
        self,
        source_socket,
        target_host: str,
        target_port: int,
        buffer_size: int = args.buffer,
        timeout: int = args.timeout,
        window_size=10,
        seq_size=16,
    ) -> None:
        """初始化传输协议

        Args:
            source_socket (socket.socket): 本机用于通信的socket
            target_host (str): 目标主机IP
            target_port (int): 目标主机端口
            buffer_size (int, optional): 缓冲区大小. Defaults to args.buffer.
            timeout (int, optional): 超时时间. Defaults to args.timeout.
            window_size (int, optional): 窗口长度. Defaults to 10.
            seq_size (int, optional): 序列号范围. Defaults to 16.
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

    def send(self, data_path: str, lock=None):
        """使用SR协议向目的主机发送数据

        Args:
            data_path (str): 需要发送的文件路径
        """
        if lock:
            lock.acquire()
        seq = 0
        clock = 0
        window: List[Data] = []
        f = open(data_path, "r")

        while True:
            if clock > self.timeout:
                # 超时, 将整个窗口视为未发送
                print("time out, reset window")
                clock = 0
                for data in window:
                    data.switch("NOT_SENT")

            # 试图充满整个窗口
            while len(window) < self.window_size:
                line = f.readline().strip()
                if not line:
                    break
                window.append(Data(line, seq % self.seq_size))
                seq += 1

            # 传输完毕
            if not window:
                break

            # 开始传输
            for data in window:
                if data.state == "NOT_SENT":
                    self.source_socket.sendto(
                        encapsulate(data.seq, data.message).encode(), self.target
                    )
                    data.switch("SENT_NOT_ACKED")

            # 接收应答
            readable_list, _, _ = select.select([self.source_socket], [], [], 1)
            if len(readable_list) > 0:
                try:
                    ack, _ = self.source_socket.recvfrom(self.buffer)
                    ack = int(ack.decode())

                    for data in window:
                        if ack == data.seq:
                            # 确认窗口中的一个包
                            data.switch("ACKED")
                            clock = 0
                            break
                except:
                    print("Error: ACK receive failed")
            else:
                clock += 1

            # 尝试向后滑动窗口
            while len(window) > 0 and window[0].state == "ACKED":
                window.pop(0)

        # 值得注意的是, 在SR中, 即使传输完了最后一个包, 也不意味着传输过程结束. 为了显式地结束传输, 需要再发送一个传输终止包
        # 此处约定 -1 <EOF> 为终止包
        seq = 0
        clock = 0
        while seq == 0:
            if clock == 0:
                self.source_socket.sendto(encapsulate(-1, "<EOF>").encode(), self.target)

            # 接收传输应答
            readable_list, _, _ = select.select([self.source_socket], [], [], 1)
            if len(readable_list) > 0:
                try:
                    ack, _ = self.source_socket.recvfrom(self.buffer)
                    seq = int(ack.decode())
                except:
                    print("Error: ACK receive failed")
            else:
                clock += 1

        # 最后结束传输
        f.close()
        self.source_socket.close()
        if lock:
            lock.release()

    def recv(self) -> List[str]:
        """使用SR协议从目的主机接收数据

        Returns:
            List[str]: 收到的数据列表
        """
        window = [None] * self.seq_size
        current_ack = 0
        ret = []

        while True:
            readable_list, _, _ = select.select([self.source_socket], [], [], 1)
            if len(readable_list) > 0:
                buffer, _ = self.source_socket.recvfrom(self.buffer)
                buffer = buffer.decode()
                body = json.loads(buffer)
                ack_seq = body["seq"]
                message = body["message"]

                if random() < LOST_RATE:
                    continue
                self.source_socket.sendto(str(ack_seq).encode(), self.target)
                if ack_seq == -1:
                    # 收到终止包
                    self.source_socket.close()
                    return ret
                elif message != "<EOF>":
                    window[ack_seq] = deepcopy(message)
                    fmt_print(body)

                    # 更新当前期待的包序号
                    while window[current_ack] is not None:
                        ret.append(window[current_ack])
                        # 取走数据
                        window[current_ack] = None
                        current_ack = (current_ack + 1) % self.seq_size
