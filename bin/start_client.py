#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import os
import json

class Ftp_client():
    def connect(self):
        #与服务端建立连接
        while True:
            self.client=socket.socket()
            address = input('请输入ftp服务器地址:')
            port = input('请输入ftp服务器端口号:')
            if len(address)>20 or len(port)>20:
                print('输入不能大于20个字符')
                continue
            if address and port.isdigit():
                try:
                    self.client.connect((address,int(port)))
                except :
                    print('连接失败,请重新输入')
                    continue
                else:
                    print('连接成功')
            else:
                print('输入格式不对,请重新输入')
                continue
            break

    def handle(self):
        #解析用户输入的命令并执行相应动作
        while True:
            command = input('请输入命令')
            if len(command)>100:
                print('输入不能大于100个字符')
                continue
            if not command:
                print('不能为空')
                continue
            if command == 'quit':
                self.client.close()
                print('连接关闭')
                break
            elif hasattr(self,command.split()[0]):
                if len(command.split()) < 2:
                    print('请输入文件或目录')
                    continue
                getattr(self, command.split()[0])(command)
            else :
                print('命令不存在')

    def get(self,command):
        #执行下载操作
        self.client.send(command.encode())
        signal = self.client.recv(1024)
        if signal.decode() == 'non-existent':
            print('文件不存在')
            return
        else:
            data_dict = json.loads(signal.decode())
            with open(command.split()[1].split('\\')[-1],'wb') as file:
                received_size = 0
                while received_size < data_dict['size']:
                    data = self.client.recv(4096)
                    self.client.send(b'continue')
                    file.write(data)
                    received_size += len(data)
                    num = int(received_size / data_dict['size'] * 100)
                    print('\r [%-100s]%d%%' % ('=' * num, num),end='')
                else:
                    print('\nget完成')

    def put(self,command):
        #执行上传操作
        if os.path.isfile(command.split()[1]):
            file_name = command.split()[1].split('\\').pop()
            size = os.path.getsize(command.split()[1])
            base_data = {'size': size,'name':file_name}
            self.client.send(json.dumps(base_data).encode())
            with open(command.split()[1],'rb')as file:
                send_size = 0
                for line in file:
                    self.client.send(line)
                    total_size = size
                    send_size += len(line)
                    num = int(send_size / total_size * 100)
                    print('\r [%-100s]%d%%' % ('=' * num, num), end='')
            print('\nput完成')
        else:
            print('文件不存在')


if __name__ == '__main__':
    ftp = Ftp_client()
    ftp.connect()
    ftp.handle()