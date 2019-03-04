import socket
from socketserver import ThreadingTCPServer, BaseRequestHandler
from threading import Thread, Lock

lock = Lock()
total_part = 200
recv_size = 2048
global part


class request_handler(BaseRequestHandler):
    def handle(self):
        while True:
            global part
            lock.acquire()
            if part < total_part:
                part += 1
                req = self.request.recv(recv_size).decode()
                print("receive request from %s: %s" % (self.client_address, req))
                self.request.send(str(part / total_part).encode())
            else:
                self.request.send(b"finish")
                lock.release()
                break
            lock.release()

    def finish(self):
        print("%s finish the process of data" % str(self.client_address))


if __name__ == "__main__":
    global part
    part = 1
    server = ThreadingTCPServer(("localhost", ), request_handler)
    server.serve_forever()

