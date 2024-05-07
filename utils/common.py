import struct


def get_checksum(data):
    return sum(data) & 0xFFFFFFFF

def make_pkt(seq_num, payload,stop=False):
    flag = 1 if stop else 0
    checksum = get_checksum(payload)
    return (
        struct.pack("I", seq_num)
        + struct.pack("I", checksum)
        + struct.pack("I", flag)
        + payload
    )


def de_pkt(pkt):
    seq_num = struct.unpack("I", pkt[:4])[0]
    checksum = struct.unpack("I", pkt[4:8])[0]
    flag = struct.unpack("I", pkt[8:12])[0]
    payload = pkt[12:]
    return seq_num, checksum, flag, payload


def fmt_print(data: dict):
    print(f"seq: {data['seq']} message: {data['message']}")
