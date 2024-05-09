import argparse

parser = argparse.ArgumentParser(description="RUDP Server/Client configs")

parser.add_argument("--send-port", "-s", type=int, default=9998, help="发送方端口")

parser.add_argument("--target-host", "-th", type=str, default="127.0.0.1", help="发送目标的IP")

parser.add_argument("--target-port", "-tp", type=int, default=9999, help="发送目标的端口")

parser.add_argument("--recv-port", "-r", type=int, default=9999, help="接收方端口")

parser.add_argument("--proto", "-p", choices=["sr", "gbn"], default="gbn", help="差错处理策略")

parser.add_argument("--window-size", "-ws", type=int, default=10, help="窗口大小")

parser.add_argument("--timeout", "-to", type=float, default=3, help="超时时间")

parser.add_argument("--file", "-f", type=str, default="./send/mirror.jpg", help="发送文件的路径")

parser.add_argument("--remote", "-rm", default=False, action="store_true", help="在云服务器上选这个")

parser.add_argument("--local", "-l", default=False, action="store_true", help="在本地运行")
