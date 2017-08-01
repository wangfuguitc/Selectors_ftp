#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import selectors
import os
import sys
import json

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from conf import setting

sel = selectors.DefaultSelector()
Get_size = {}
Put_data = {}

def accept(sock, mask):
    conn, addr = sock.accept()
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, mask):
    #执行下载和上次操作
    global Get_size
    global Put_data
    try:
        data = conn.recv(4096)
        if conn in Put_data.keys():
            file_name = Put_data[conn]['name']
            with open(os.path.join(setting.HOME_PATH, file_name), 'ab') as file:
                file.write(data)
            if os.path.isfile(os.path.join(setting.HOME_PATH, file_name)):
                received_size = os.path.getsize(os.path.join(setting.HOME_PATH, file_name))
                if received_size >= Put_data[conn]['size']:
                    Put_data.pop(conn)
        else:
            handle = data.decode()
            if handle.split()[0] == 'get':
                if os.path.isfile(os.path.join(setting.HOME_PATH, handle.split()[1])):
                    file_path = os.path.join(setting.HOME_PATH, handle.split()[1])
                    size = os.path.getsize(file_path)
                    base_data = {'size': size}
                    conn.send(json.dumps(base_data).encode())
                    Get_size[conn] = [file_path,0,size]
                    with open(file_path, 'rb')as file:
                        data = file.read(2048)
                        conn.sendall(data)
                        Get_size[conn][1] += len(data)
                else:
                    conn.send(b'non-existent')
            elif handle == 'continue':
                if Get_size[conn][1] < Get_size[conn][2]:
                    with open(Get_size[conn][0], 'rb')as file:
                        file.seek(Get_size[conn][1])
                        data = file.read(2048)
                        conn.sendall(data)
                        Get_size[conn][1] += len(data)
                else:
                    Get_size.pop(conn)
            else:
                Put_data[conn] = json.loads(handle)
    except ConnectionResetError:
        sel.unregister(conn)
        conn.close()

sock = socket.socket()
sock.bind((setting.ADDRESS, setting.PORT))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

def main():
    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
