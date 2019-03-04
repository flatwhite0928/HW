import socket
import time

recv_buffer = 

client = socket.socket()
client.connect(("localhost", ))

while True:
    time.sleep(0.5)
    client.send(b"require for data")
    resp = client.recv(recv_buffer).decode()
    if str(resp) == "finish":
        client.close()
    else:
        print("process data part %.3f" % float(resp))
