import socket
from utils.args import parser


if __name__ == "__main__":
    args = parser.parse_args()
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sender.bind(("0.0.0.0", args.send_port))
    
    recver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # recver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # recver.bind(("0.0.0.0", args.recv_port))
    
    target = (str(args.target_host), int(args.target_port))
    
    if args.proto == "sr":
        from protocol.sr import SR
        instance = SR(args.file, sender, target, recver, args.window_size, args.timeout)
    elif args.proto == "gbn":
        from protocol.gbn import GBN
        instance = GBN(args.file, sender, target, recver, args.window_size, args.timeout)
    
    instance.send()