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

    def send(self, data_path: str, lock=None) -> None:
        """使用GBN协议向目的主机发送数据

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
                # 超时, 将整个窗口视为未发送(GBN)
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
                        (str(data.seq) + " " + data.message).encode(), self.target
                    )
                    data.switch("SENT_NOT_ACKED")

            # 接收应答
            readable_list, _, _ = select.select([self.source_socket], [], [], 1)
            if len(readable_list) > 0:
                try:
                    ack, _ = self.source_socket.recvfrom(self.buffer)
                    ack = int(ack.decode())
                    if ack == -1:
                        print("receive NACK, reset window")
                        clock = 0
                        for data in window:
                            data.switch("NOT_SENT")
                    else:
                        for i in range(len(window)):
                            if window[i].seq == ack:
                                # 认为这个ACK之前的包都已经确认收到
                                clock = 0
                                window = window[i + 1 :]
                                break
                except:
                    print("Error: ACK receive failed")
            else:
                clock += 1

        f.close()
        self.source_socket.close()
        if lock:
            lock.release()

    def recv(self) -> List[str]:
        """使用GBN协议从目的主机接收数据

        Returns:
            List[str]: 收到的数据列表
        """
        last_ack = self.seq_size - 1
        window = []
        ret = []

        while True:
            readable_list, _, _ = select.select([self.source_socket], [], [], 10)
            if len(readable_list) > 0:
                data, addr = self.source_socket.recvfrom(self.buffer)
                data = data.decode()
                ack_seq = int(data.split(" ")[0])
                if (ack_seq - 1) % self.seq_size == last_ack:
                    # ACK序号正确
                    if random() < LOST_RATE:
                        continue
                    # 随机成功收包
                    self.source_socket.sendto(
                        str(ack_seq).encode(), self.target
                    )
                    last_ack = ack_seq

                    if ack_seq not in window:
                        window.append(ack_seq)

                        if data.split(" ")[1] == "<EOF>":
                            self.source_socket.close()
                            return ret

                        print(data)
                        ret.append(data.split(" ")[1])

                    while len(window) > self.window_size:
                        window.pop(0)
                else:
                    # 重复ACK
                    self.source_socket.sendto(str(last_ack).encode(), addr)
