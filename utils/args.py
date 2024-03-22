import argparse

parser = argparse.ArgumentParser(description="RUDP Server/Client configs")

parser.add_argument(
    "--server-host", "-sh", type=str, default="127.0.0.1", help="Server host"
)
parser.add_argument(
    "--client-host", "-ch", type=str, default="127.0.0.1", help="Client host"
)

parser.add_argument(
    "server-send-port", "-ssp", type=int, default=50001, help="Server send port"
)
parser.add_argument(
    "server-recv-port", "-srp", type=int, default=50002, help="Server receive port"
)
parser.add_argument(
    "client-send-port", "-csp", type=int, default=50003, help="Client send port"
)
parser.add_argument(
    "client-recv-port", "-crp", type=int, default=50004, help="Client receive port"
)

parser.add_argument("--buffer", "-b", type=int, default=1024, help="Buffer size")
parser.add_argument("--timeout", "-t", type=int, default=3, help="Timeout in seconds")
parser.add_argument(
    "--lost-rate", "-lr", type=float, default=0.0, help="Packeges lost rate"
)

parser.add_argument(
    "--protocol",
    "--proto",
    "-p",
    type=str,
    default="SR",
    choices=["SR", "GBN", "SW"],
    help="RUDP protocol (Selective Repeat, Go Back N, Stop and Wait)",
)

parser.add_argument(
    "--data-dir", "-d", type=str, default="./data", help="Data directory"
)

args = parser.parse_args()
