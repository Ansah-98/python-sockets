from audioop import add
from select import select
import selectors 
import sys 
import types
import socket

host = sys.argv[1]
port = int(sys.argv[2])

sel = selectors.DefaultSelector()

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
s.bind((host,port))
s.listen()
s.setblocking(False)
sel.register(s,selectors.EVENT_READ, data= None)


def accept_wrapper(sock):
    conn,addr = sock.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr,inb=b'' ,outb=b'')
    events = selectors.EVENT_READ |selectors.EVENT_WRITE
    sel.register(conn,events,data=data)


def service_connection(key,mask):
    sock = key.fileobj
    data = key.data 
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

try :
    while True:
        events = sel.select(timeout=None)
        for key , mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key,mask)
except KeyboardInterrupt:
    print(f'caught the keyboard interrupt,exiting')
finally:
    sel.close