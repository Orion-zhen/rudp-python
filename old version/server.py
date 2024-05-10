import os
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
    ret = recv_device.recv()
    
    if not os.path.exists("./recv/"):
        os.makedirs("./recv/")
    with open("./recv/server.txt", "w") as f:
        for msg in ret:
            f.writelines(msg)

    while lock.locked():
        pass
