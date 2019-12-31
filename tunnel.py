
'''
Created on Dec 20, 2019

@author: dmitri
'''
import asyncore
import socket
import threading
import action
import os
import struct
import time
import sys
from socket import EBADF
from errno import ENOTCONN

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
        if clz.poolThread != None:
            if clz.poolThread.isAlive():
                return
        clz.poolThread = threading.Thread(target=clz.loop, args=())
        clz.poolThread.start()
            
    
    @classmethod        
    def keys(clz):
        return clz.tunnels.keys()
    
    @classmethod     
    def loop(clz,timeout=30.0, use_poll=False, map=None, count=None):
        if map is None:
            map = asyncore.socket_map
    
        if use_poll and hasattr(select, 'poll'):  # @UndefinedVariable
            poll_fun = asyncore.poll2
        else:
            poll_fun = asyncore.poll
    
        if count is None:
            while map:
                print("pooooooooool")
                keys = list(clz.keys())
                for c in keys:
                    print("pool #"+str(c))
                    tunnel = clz.get(c)
                    #if tunnel.initialized and tunnel.checkalive:
                    #    tunnel.check_alive()
                poll_fun(timeout, map)
    
        else:
            while map and count > 0:
                poll_fun(timeout, map)
                count = count - 1    
        
        print("EXIT POOL")
        #create new map
        keys = list(clz.keys())
        for c in keys:
            tunnel = clz.get(c)
            map[tunnel._fileno]=tunnel
            #tunnel.reconnect(restartPool = False)
        #clz.restartPool()                
        
    
class Tunnel(asyncore.dispatcher_with_send):
    
    def __init__(self,id):
        asyncore.dispatcher_with_send.__init__(self)
        self.id=id
        self.initialized = False
        self.keepalive = True
        self.checkalive =True
    
    def init(self,vchannel,host,port):
        self.host = host
        self.port = port
        self.ip = socket.gethostbyname(self.host)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        #self.socks.setsockopt(socks.IPPROTO_TCP, socks.TCP_KEEPIDLE, 10)
        #self.socks.setsockopt(socks.IPPROTO_TCP, socks.TCP_KEEPINTVL, 10)
        #self.socks.setsockopt(socks.IPPROTO_TCP, socks.TCP_KEEPCNT, 6)
        self.socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 3000))  # @UndefinedVariable
        self.connect( (host, port) )  
        
        
        
        self.vchannel=vchannel
        self.initialized = True
        TunnelManager.restartPool()
        
    def write(self,data):
        #if self.checkalive:
        #    self.recv(0)
        try:
            TunnelManager.restartPool()
            #print("!111")
            self.send(data)
        except OSError as e:
            if e.winerror==10038: #socks closed. reconnect first
                print("!222")
                self.reconnect()
                print("!333")
                self.send(data)
                print("!444")
            else:
                raise e
    def reconnect(self,restartPool = True):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (self.host, self.port) )
        if  restartPool:
            TunnelManager.restartPool()
                  
    
    def handle_connect(self):
        pass

    def handle_close(self):
        print("HANDLE CLOSE!")
        if not self.keepalive:
            self.close()
            return
        #raise Exception("Asdasd1")
        #return
        print("HANDLE CLOSING!!!!!!!!!!!!")
        try:
            self.socket.close()
        except socket.error as why:
            if why.args[0] not in (ENOTCONN, EBADF):
                raise
        self.reconnect(restartPool=False)
        print("reconnected")            

    def handle_read(self):
        data=self.recv(8192)
        if data:
            self.vchannel.Write(self.id,action.R2TCMD_DATA,data)

            
    def check_alive(self):
        print("check alive #"+str(self.id))
    
    def close(self):
        print("CLOSED!!!!!!!!!!!!!!!")
        super().close()
    #def handle_write(self):
    #    sent = self.send(self.buffer)
    #    self.buffer = self.buffer[sent:]    