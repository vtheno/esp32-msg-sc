import socket
import sys

isESP32 = sys.platform == "esp32"
if isESP32:
    # just support pyboard and esp32
    import _thread as threading

    start_new_thread = threading.start_new_thread
else:
    import threading

    start_new_thread = threading._start_new_thread


from pack import auto_pack, pack, unpack, data_pack, data_unpack


class Client(object):
    def __init__(self):
        self.sendeds = set()
        self.connected = False
        self.recv_map = {}

    def show(self):
        print(self.recv_map)

    def recv(self):
        while self.connected:
            try:
                header = self.sock.recv(68)
                header_maps = unpack(header)
                resp_id = header_maps["id"]
                resp_length = header_maps["length"]
                data = ""
                if resp_length > 0:
                    buff = self.sock.recv(resp_length)
                    data = data_unpack(buff)
                self.recv_map[resp_id] = data
            except Exception as e:
                self.connected = False

    def send(self, message):
        if self.connected:
            try:
                id, header, data = auto_pack(message)
                self.sendeds.add(id)
                self.sock.sendall(header)
                self.sock.sendall(data)
                return id
            except OSError:
                self.connected = False
                return
        return

    def start(self, host="192.168.0.6", port=8686):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # keepalive
        self.sock.connect((host, port))
        self.connected = True
        # threading.Thread(target=self.recv, args=(), daemon=True).start()
        start_new_thread(self.recv, ())

    def close(self):
        self.connected = False
        self.sock.close()


def start_client():
    s = Client()
    s.start()

    while 1:
        cmd = input("=> ")
        if cmd == "flush":
            s.show()
        elif cmd == "clear":
            s.recv_map = {}
        elif cmd == "quit":
            s.close()
            break
        else:
            s.send(cmd)
