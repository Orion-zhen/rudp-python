import _thread
from utils.args import args
from utils.device import Device


if __name__ == "__main__":
    send_device = Device(
        args.server_send_port, args.client_host, args.client_recv_port, args.protocol
    )
    recv_device = Device(
        args.server_recv_port, args.client_host, args.client_send_port, args.protocol
    )

    lock = _thread.allocate_lock()

    _thread.start_new_thread(
        send_device.send, (args.data_path + "/server_data.txt", lock)
    )
    recv_device.recv()

    while lock.locked():
        pass
