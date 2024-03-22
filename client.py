import threading
from utils.args import args
from utils.device import Device


if __name__ == "__main__":
    send_device = Device(
        args.client_send_port, args.server_host, args.server_recv_port, args.protocol
    )
    recv_device = Device(
        args.client_recv_port, args.server_host, args.server_send_port, args.protocol
    )

    send_thread = threading.Thread(
        target=send_device.send, args=(args.data_path + "/client_data.txt",)
    )
    recv_thread = threading.Thread(target=recv_device.recv(), args=())

    send_thread.start()
    recv_thread.start()
    send_thread.join()
    recv_thread.join()
