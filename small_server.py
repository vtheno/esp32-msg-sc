import socket
import threading
from pack import pack, unpack, data_pack, data_unpack, auto_pack


class Server(object):
    def __init__(self):
        self.clients = {}

    def send(self, client, id, message):
        resp_length, resp_data = data_pack(message)
        resp_header = pack(resp_length, id)
        try:
            client.sendall(resp_header)
            client.sendall(resp_data)
            return id
        except OSError:
            self.clients[client]["loop"] = False
            return

    def recv(self, client):
        while self.clients[client]["loop"]:
            try:
                header = client.recv(68)
                header_maps = unpack(header)
                resp_id = header_maps["id"]
                resp_length = header_maps["length"]
                data = ""
                if resp_length > 0:
                    buff = client.recv(resp_length)
                    data = data_unpack(buff)
                self.clients[client]["recv_map"][resp_id] = data
            except Exception as e:
                self.clients[client]["loop"] = False
                break

    def handler(self, id, message):
        if message.startswith("notify"):
            try:
                msg = message.split(" ")[1]
                for c in self.clients.keys():
                    self.send(c, id, msg)
                return
            except Exception as e:
                return
        return "server recv: {}".format(message)

    def resp(self, client):
        while self.clients[client]["loop"]:
            for id in list(self.clients[client]["recv_map"].keys()):
                message = self.clients[client]["recv_map"].pop(id)
                print("Message:", message)
                message = self.handler(id, message)
                if message:
                    if not self.send(client, id, message):
                        self.clients[client]["loop"] = False
                        break

    def __call__(self, tup):
        client, addr = tup
        with client:
            self.clients[client] = {"loop": True, "recv_map": {}}
            msg_thread = threading.Thread(target=self.recv, args=(client,), daemon=True)
            resp_thread = threading.Thread(
                target=self.resp, args=(client,), daemon=True
            )
            print("client counts:", len(self.clients))
            msg_thread.start()
            resp_thread.start()
            msg_thread.join()
            resp_thread.join()
            self.clients.pop(client)
            print("client counts:", len(self.clients))

    def listen(self, host="0.0.0.0", port=8686, worker=10240):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.setblocking(False)
            sock.settimeout(0.002)
            sock.listen(worker)
            while 1:
                try:
                    threading.Thread(
                        target=self, args=(sock.accept(),), daemon=True
                    ).start()
                except socket.timeout:
                    # esp32 OSError e.args = (110, )
                    continue
                except KeyboardInterrupt:
                    break


s = Server()
s.listen()
