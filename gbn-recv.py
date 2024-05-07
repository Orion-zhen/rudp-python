import socket
import random
import threading
from utils.common import de_pkt


if __name__ == "__main__":
    recver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recver.bind(("127.0.0.1", 9999))
    
    recv_data = []
    recved_seq = -1
    expect_seq = recved_seq + 1
    f = open("recv.png", "wb")
    while True:
        buffer, addr = recver.recvfrom(2048)
        recved_seq, checksum, eof_flag, payload = de_pkt(buffer)
        if random.random() < 0.1:
            print("丢包")
            continue
        if eof_flag:
            print("EOF!")
            break
        print(f"{addr}: {recved_seq}")
        
        # 是正确顺序的报文
        if recved_seq == expect_seq:
            expect_seq += 1
            f.write(payload)
            recv_data.append(payload)
        
        recver.sendto(str(expect_seq).encode(), addr)
        
    # with open("recv.png", "wb") as f:
    #     for data in recv_data:
    #         f.write(data)