import os
import random
import socket
import threading
from utils.common import make_pkt, de_pkt


class SR(object):
    def __init__(
        self, file_path, sender, target, recver, window_size=10, timeout=3, buffer_size=2048
    ) -> None:
        self.data_list = []
        try:
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.data_list.append(data)
        except Exception as e:
            print(e)
            exit(1)
        self.file_name = os.path.basename(file_path)
        self.sender = sender
        self.target = target
        self.recver = recver
        self.wd_size = window_size
        self.timeout = timeout
        self.buffer_size = buffer_size

    def send(self):
        seq_to_send = 0
        base_seq = 0
        last_ack = -1
        ack_seq = -1
        state = ["NOT SENT"] * len(self.data_list)
        timer_list = [None] * len(self.data_list)

        # 发送体
        while True:
            if all(s == "ACKED" for s in state):
                break

            # 当窗口未满时, 试图填充窗口
            while seq_to_send < min(base_seq + self.wd_size, len(self.data_list)):
                pkt = make_pkt(seq_to_send, self.data_list[seq_to_send])
                self.sender.sendto(pkt, self.target)
                print(f"send {seq_to_send}")
                state[seq_to_send] = "SENT"
                # 开启对应包的定时器
                # if timer_list[seq_to_send].is_alive():
                #     timer_list[seq_to_send].cancel()
                # timer_list[ack_seq] = start_timer(ack_seq, TIMEOUT)
                # timer_list[seq_to_send].start()
                seq_to_send += 1

            # 开始从接收方接收信息
            ack_seq, _ = self.sender.recvfrom(1024)
            ack_seq = int(ack_seq.decode())
            # 如果和上一次确认号相同, 则说明发生丢包, 此时应重传这个包
            if ack_seq == last_ack:
                print(f"duplicate ack {ack_seq}")
                resend_pkt = make_pkt(ack_seq, self.data_list[ack_seq])
                self.sender.sendto(resend_pkt, self.target)
                # 重启定时器
                # if timer_list[ack_seq].is_alive():
                #     timer_list[ack_seq].cancel()
                # timer_list[ack_seq] = start_timer(ack_seq, TIMEOUT)
                # timer_list[ack_seq].start()
                continue

            last_ack = ack_seq
            # 认为收到确认号之前的数据包已经收到
            for i in range(base_seq, ack_seq):
                state[i] = "ACKED"
                if timer_list[i].is_alive():
                    timer_list[i].cancel()
            # 向后滑动窗口
            base_seq = ack_seq
            print(f"recv ack {ack_seq}")

        eof_pkt = make_pkt(len(self.data_list), "".encode(), True)
        self.sender.sendto(eof_pkt, self.target)

    def recv(self):
        # 是否收到对应的包
        state = [False] * len(self.data_list)
        recved_data = [None] * len(self.data_list)
        while not all(s == True for s in state):
            buffer, addr = self.recver.recvfrom(self.buffer_size)
            recved_seq, checksum, eof_flag, payload = de_pkt(buffer)
            if eof_flag:
                print("Received EOF")
                break
            if random.random() < 0.1:
                print("丢包")
                continue
            print(f"{addr}: {recved_seq}")
            state[recved_seq] = True
            recved_data[recved_seq] = payload
            
            for i, s in enumerate(state):
                if not s:
                    # 第一个未收到的包
                    self.recver.sendto(str(i).encode(), addr)
                    break
        
        # 告知服务器成功接收
        self.recver.sendto(str(len(state)).encode(), addr)
                
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "recv")):
            os.path.makedirs(os.path.join(os.path.dirname(__file__), "recv"))
        with open(os.path.join(os.path.dirname(__file__), "recv", self.file_name), "wb") as f:
            for data in self.data_list:
                f.write(data)
                

if __name__ == "__main__":
    recver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recver.bind(("127.0.0.1", 9999))
    
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    instance = SR("./mirror.png", sender, ("127.0.0.1", 9998), recver)
    
    instance.recv()