import socket
import argparse
import threading
from utils.args import parser


args = parser.parse_args()

if __name__ == "__main__":
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    recver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if args.remote:
        sender.bind(("0.0.0.0", 9998))
        target = ("127.0.0.1", 9999) # 本端口由frp映射
        recver.bind(("0.0.0.0", 10000))
    elif args.local:
        sender.bind(("127.0.0.1", 9998))
        target = ("123.56.42.16", 10000)
        recver.bind(("0.0.0.0", 9999))
    else:
        print("请输入正确的参数")
        exit()
        
    if args.proto == "sr":
        from protocol.sr import SR
        instance = SR(args.file, sender, target, recver, args.window_size, args.timeout)
    elif args.proto == "gbn":
        from protocol.gbn import GBN
        instance = GBN(args.file, sender, target, recver, args.window_size, args.timeout)
        
    th_send = threading.Thread(target=instance.send)
    th_recv = threading.Thread(target=instance.recv)
    th_send.start()
    th_recv.start()
