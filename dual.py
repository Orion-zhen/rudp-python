import socket
import argparse
import threading
from utils.args import parser


args = parser.parse_args()

if __name__ == "__main__":
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sender.bind(("0.0.0.0", int(args.send_port)))

    recver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if args.remote:
        target = (str(args.target_host), int(args.target_port)) # 本端口由frp映射
        recver.bind(("0.0.0.0", 10009))
    elif args.local:
        args.target_host = "123.56.42.16"
        target = (str(args.target_host), 10009)
        recver.bind(("0.0.0.0", args.recv_port))
    else:
        print("请输入正确的参数")
        exit()
        
    if args.proto == "sr":
        from protocol.sr import SR
        instance_send = SR(args.file, sender, target, recver, args.window_size, args.timeout)
        instance_recv = SR(args.file, sender, target, recver, args.window_size, args.timeout)
    elif args.proto == "gbn":
        from protocol.gbn import GBN
        instance_send = GBN(args.file, sender, target, recver, args.window_size, args.timeout)
        instance_recv = GBN(args.file, sender, target, recver, args.window_size, args.timeout)
        
    th_send = threading.Thread(target=instance_send.send)
    th_recv = threading.Thread(target=instance_recv.recv)
    th_send.start()
    th_recv.start()
