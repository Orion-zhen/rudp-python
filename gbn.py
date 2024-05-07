import socket
import struct
import select
import threading
from typing import List
from typing import Tuple
from random import random
from utils.common import make_pkt, de_pkt, get_checksum


class GBN(object):
    def __init__(
        self,
        source_socket,
        recv_socket,
        target_host,
        target_port,
        data_list,
        buffer_size=2048,
        timeout=3,
        window_size=10,
    ) -> None:
        self.send_socket = source_socket
        self.recv_socket = recv_socket
        self.target = (target_host, target_port)
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.payloads = data_list
        self.window_size = window_size
        self.state = ["NOT_SENT"] * len(self.payloads)
        # 窗口开始序号
        self.base_seq = 0
        
    
    def send(self):
        # 当前发送的包序号
        seq = 0
        clock = 0
        
        while True:
            if clock > self.timeout:
                # 超时, 将整个窗口视为未发送
                print("Timeout, reset the window")
                clock = 0
                for i in range(self.base_seq, self.base_seq + self.window_size):
                    self.state[i] = "NOT_SENT"
            
            # 全部数据包都已确认
            if all(s == "ACKED" for s in self.state):
                print("发送完成, 退出")
                eof = make_pkt(len(self.state), b"", 0, True)
                self.send_socket.sendto(eof, self.target)
                break
            
            # 试图填满整个窗口
            while seq < self.base_seq + self.window_size:
                if self.state[seq] == "NOT_SENT":
                    print(f"发送序列号{seq}")
                    pkt = make_pkt(seq, self.payloads[seq])
                    self.send_socket.sendto(pkt, self.target)
                    self.state[seq] = "SENT"
                seq += 1
                
            # 接收应答
            readable_list, _, _ = select.select([self.send_socket], [], [], self.timeout)
            if readable_list:
                ack_seq, _ = self.send_socket.recvfrom(self.buffer_size)
                ack_seq = int(ack_seq)
                print(f"收到应答{ack_seq}")
                # 认为该ack之前的包都已确认收到
                for i in range(self.base_seq, ack_seq + 1):
                    self.state[i] = "ACKED"
                # 移动窗口
                self.base_seq = ack_seq + 1
            else:
                clock += 1
        
        self.send_socket.close()
        
    def recv(self):
        recved_seq = 0
        expect_seq = recved_seq
        while True:
            readable_list, _, _ = select.select([self.recv_socket], [], [], self.timeout)
            if readable_list:
                buffer, addr = self.recv_socket.recvfrom(self.buffer_size)
                recved_seq, rm_checksum, eof_flag, data = de_pkt(buffer)
                
                if eof_flag:
                    break
                
                local_checksum = get_checksum(data)
                if local_checksum != rm_checksum:
                    print("checksum error")
                    continue
                
                if recved_seq == expect_seq:
                    print(f"recv {recved_seq}")
                    self.recv_socket.sendto(str(recved_seq).encode(), addr)
        
if __name__ == "__main__":
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    target_host = "127.0.0.1"
    target_port = 9999
    sender.bind(("127.0.0.1", 9998))
    recver.bind(("127.0.0.1", 9999))
    
    data_list = []
    with open("./mirror.png", "rb") as f:
        while True:
            data = f.read(512)
            if not data:
                break
            data_list.append(data)
    print(f"数据包数量: {len(data_list)}")
    instance = GBN(sender, recver, target_host, target_port, data_list)
    
    th1 = threading.Thread(target=instance.send, daemon=True)
    th2 = threading.Thread(target=instance.recv, daemon=True)
    
    th1.start()
    th2.start()
