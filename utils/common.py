import json


def encapsulate(seq: int, message: str):
    return json.dumps({"seq": seq, "message": message})

def fmt_print(data: dict):
    print(f"seq: {data["seq"]} message: {data["message"]}")