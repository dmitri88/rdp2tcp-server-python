'''
Created on Dec 20, 2019

@author: dmitri
'''
import asyncore
import socket
import threading
import action

x = threading.Thread(target=asyncore.loop, args=())
x.start()
class TunnelManager:
    
    tunnels = {}
    poolThread = None
    
    @classmethod
    def get(clz,num):
        if not num in clz.tunnels:
            print("Registered new tunnel #"+str(num))
            clz.tunnels[num] = Tunnel(num)
        return clz.tunnels[num]
    
    @classmethod
    def restartPool(clz):
        if clz.poolThread == None:
            clz.poolThread = threading.Thread(target=asyncore.loop, args=())
            clz.poolThread.start()
        
    
class Tunnel(asyncore.dispatcher_with_send):
    
    def __init__(self,id):
        asyncore.dispatcher_with_send.__init__(self)
        self.id=id
    
    def init(self,vchannel,host,port):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )  
        self.vchannel=vchannel
        TunnelManager.restartPool()
        
    def write(self,data):
        self.send(data)
                  
    
    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        data=self.recv(8192)
        if data:
            self.vchannel.Write(self.id,action.R2TCMD_DATA,data)

    #def handle_write(self):
    #    sent = self.send(self.buffer)
    #    self.buffer = self.buffer[sent:]    