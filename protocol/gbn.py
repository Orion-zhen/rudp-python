import os
import socket
import random
from utils.common import make_pkt, de_pkt


class GBN(object):
    def __init__(self, file_path, sender, target, recver, window_size=10, timeout=3, buffer_size=2048) -> None:
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
        state = ["NOT SEND"] * len(self.data_list)
        
        # 发送体
        while True:
            if all(s == "ACKED" for s in state):
                break
            
            # 当窗口未满时, 试图填充窗口
            while seq_to_send < min(base_seq + self.wd_size, len(self.data_list)):
                pkt = make_pkt(seq_to_send, self.data_list[seq_to_send])
                self.sender.sendto(pkt, self.target)
                seq_to_send += 1
                print(f"send {seq_to_send}")
                
            # 开始从接收方接收信息
            ack_seq, _ = self.sender.recvfrom(self.buffer_size)
            ack_seq = int(ack_seq.decode())
            # 如果和上一次确认号相同, 则说明发生丢包, 此时应回退整个窗口
            if ack_seq == last_ack:
                print(f"duplicate ack {ack_seq}")
                seq_to_send = last_ack
                base_seq = last_ack
                for i in range(base_seq, min(base_seq + self.wd_size, len(self.data_list))):
                    state[i] = "NOT SEND"
                continue
            
            # 认为收到确认号之前的数据包已经收到
            for i in range(base_seq, ack_seq):
                state[i] = "ACKED"
                
            # 向后滑动窗口
            base_seq = ack_seq
            print(f"recv ack {ack_seq}")
            
        # 传输结束, 发送中止包
        eof_pkt = make_pkt(base_seq, "".encode(), stop=True)
        self.sender.sendto(eof_pkt, self.target)
        
    def recv(self):
        if not os.path.exists(os.path.join(os.getcwd(), "recv")):
            os.path.makedirs(os.path.join(os.getcwd(), "recv"))
        f = open(os.path.join(os.getcwd(), "recv", self.file_name), "wb")
        
        recved_seq = -1
        expect_seq = recved_seq + 1
        
        # 接收体
        while True:
            buffer, addr = self.recver.recvfrom(self.buffer_size)
            recved_seq, checksum, eof_flag, payload = de_pkt(buffer)
            # if random.random() < 0.1:
            #     print("丢包")
            #     continue
            if eof_flag:
                print("EOF!")
                break
            
            # 是正确顺序的报文
            if recved_seq == expect_seq:
                print(f"ack {recved_seq}. length: {len(payload)}")
                expect_seq += 1
                f.write(payload)
        
            self.recver.sendto(str(expect_seq).encode(), addr)
            