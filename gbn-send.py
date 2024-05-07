import socket
from utils.common import make_pkt

WD_SIZE = 10


if __name__ == "__main__":
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sender.bind(("127.0.0.1", 9998))
    target = ("127.0.0.1", 9999)
    data_list = []
    with open("./mirror.png", "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            data_list.append(data)
    print(f"数据包数量: {len(data_list)}")
    
    seq_to_send = 0
    base_seq = 0
    last_ack = -1
    ack_seq = -1
    state = ["NOT SEND"] * len(data_list)
    print(len(state))
    while True:
        if all(s == "ACKED" for s in state):
            break
        
        # 当窗口未满时, 试图填充窗口
        while seq_to_send < min(base_seq + WD_SIZE, len(data_list)):
            pkt = make_pkt(seq_to_send, data_list[seq_to_send])
            sender.sendto(pkt, target)
            print(f"send {seq_to_send}")
            # state[seq_to_send] = "SENT"
            seq_to_send += 1
        
        # 开始从接收方接收信息
        ack_seq, _ = sender.recvfrom(1024)
        ack_seq = int(ack_seq.decode())
        # 如果和上一次确认号相同, 则说明发生丢包, 此时应回退整个窗口
        if ack_seq == last_ack:
            print(f"duplicate ack {ack_seq}")
            seq_to_send = last_ack
            base_seq = last_ack
            for i in range(base_seq, min(base_seq + WD_SIZE, len(data_list))):
                state[i] = "NOT SEND"
            continue
        last_ack = ack_seq
        # 认为收到确认号之前的数据包已经收到
        for i in range(base_seq, ack_seq):
            state[i] = "ACKED"
            
        # 向后滑动窗口
        base_seq = ack_seq
        print(f"recv ack {ack_seq}")
    eof_pkt = make_pkt(len(data_list), "".encode(), True)
    sender.sendto(eof_pkt, target)