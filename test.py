'''
Created on Dec 27, 2019

@author: dmitri
'''
import threading
from client import Client
from server import start_server
from channel import VirtualChannel as OrigVirtualChannel
import channel
import tempfile
import os
import socket
import time
import io

#tempRead, tempWrite = os.pipe()
#tempRead = tempfile.TemporaryFile() #2
#tempWrite = tempfile.TemporaryFile() #2
# HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
# 
# def connection(PORT):
#     print(PORT)
#     
#     
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind((HOST, PORT))
#         s.listen()
#         conn, addr = s.accept()
#         with conn:
#             print('Connected by', addr)
#             return conn
# 
# PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
# #tempRead = connection(PORT)
# #tempWrite = connection(PORT+1)
# clientThread = threading.Thread(target=connection, args=(PORT,))
# clientThread.start()
# clientThread = threading.Thread(target=connection, args=(PORT+1,))
# clientThread.start()
# 
# 
# time.sleep(1)
# tempRead = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tempRead.connect((HOST, PORT))
# 
# tempWrite=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tempWrite.connect((HOST, PORT+1))


class MemoryStream(io.BytesIO): 
    mutex = threading.Lock()
    def sendall(self,data):
        MemoryStream.mutex.acquire()
        self.seek(0,2)
        ret = self.write(data)
        self.flush()
        MemoryStream.mutex.release()
        return ret
    def recv(self,num):
        MemoryStream.mutex.acquire()
        self.seek(0)
        data = self.read(num)
        if data==None or len(data)<1:
            MemoryStream.mutex.release()
            return None
        buffer=self.getvalue()
        self.seek(0)
        self.truncate(0)
        self.write(buffer[len(data):])    
        #tempRead.write(buffer) 
        MemoryStream.mutex.release()
        return data
        

tempRead=MemoryStream()
tempWrite=MemoryStream()

#tempRead.sendall('dat2'.encode('ascii'))
#tempRead.sendall('dat1'.encode('ascii'))

# print(tempRead.recv(4))
# print(tempRead.getvalue())
# print("-----------")
# tempRead.sendall('dat3'.encode('ascii'))
# print(tempRead.recv(4))
# print(tempRead.getvalue())
# print("-----------")
# print(tempRead.recv(4))
# print(tempRead.getvalue())
# print("-----------")

class TestClient(Client):
    def ReadRaw(self,size=0):
        return tempWrite.recv(size)
    def WriteRaw(self,data):
        if data==None:
            return 
        if type(data)==str:
            data=data.encode('ascii')
        tempRead.sendall(data)
        return True

class VirtualChannel(OrigVirtualChannel):
    def loadLibrary(self):
        pass
    def Open(self):
        self._handle = 1
        
    def WriteRaw(self, messageBuffer):
        tempWrite.sendall(messageBuffer)
        return True
    def ReadRaw(self, size=0,timeout=100):
        return tempRead.recv(size)
    
    def Close(self):
        pass
channel.VirtualChannel=VirtualChannel




if __name__ == "__main__":
    print("starting client")
    clientThread = threading.Thread(target=TestClient().loop, args=())
    clientThread.start()

    print("starting server")    
    serverThread = threading.Thread(target=start_server, args=())
    serverThread.start()
    