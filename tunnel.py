'''
Created on Dec 20, 2019

@author: dmitri
'''
import asyncore
import socket
import threading
import action
from socket import EWOULDBLOCK
from errno import EALREADY, EINPROGRESS, EINVAL,\
    EISCONN, errorcode, EBADF, ENOTCONN
import os
from asyncore import _DISCONNECTED
import time

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
    def remove(clz,num):
        del clz.tunnels[num] 
    
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
    
        if use_poll and hasattr(select, 'poll'):
            poll_fun = asyncore.poll2
        else:
            poll_fun = asyncore.poll
    
        if count is None:
            while map:
                #print("pooooooooool")
                keys = list(clz.keys())
                for c in keys:
                    #print("pool #"+str(c))
                    tunnel = clz.get(c)
                    #if tunnel.initialized and tunnel.checkalive:
                    #    tunnel.handle_read()
                    #if tunnel.initialized and tunnel.checkalive:
                    #    tunnel.check_alive()
                #try:    
                poll_fun(timeout, map)
                #except:
                    
                    
                #time.sleep(0.)
    
        else:
            while map and count > 0:
                poll_fun(timeout, map)
                count = count - 1    
        
        print("EXIT POOL")
        #create new map
        #keys = list(clz.keys())
        #for c in keys:
            #tunnel = clz.get(c)
            #map[tunnel._fileno]=tunnel
            #tunnel.reconnect(restartPool = False)
        clz.restartPool()                
        
        
    
class Tunnel(asyncore.dispatcher):
    
    def __init__(self,id):
        #asyncore.dispatcher_with_send.__init__(self)
        asyncore.dispatcher.__init__(self)
        self.id=id
        self.initialized = False
        
        self.checkalive = True
    
    def init(self,vchannel,host,port):
        self.host = host
        self.port = port
 
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )  
        self.vchannel=vchannel
        self.initialized = True
        TunnelManager.restartPool()
        
    def write(self,data):
        if self.socket ==None:
            asyncore.dispatcher.__init__(self)
            self.init(self.vchannel, self.host, self.port)

        try:
            self.send(data)
        except OSError as e:
            if e.winerror==10038: #socks closed. reconnect first
                self.close()
                asyncore.dispatcher.__init__(self)
                self.init(self.vchannel, self.host, self.port)

                print("!222")
                self.reconnect()
                print("!333")
                #asyncore.dispatcher_with_send.__init__(self)
                self.send(data)
                print("!444")
            else:
                raise e
        #self.handle_read()
    def reconnect(self,restartPool = True):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (self.host, self.port) )
        if  restartPool:
            TunnelManager.restartPool()
                  
    
    def handle_connect(self):
        pass

    def handle_close(self):
        TunnelManager.remove(self.id)
        self.close()

    def handle_read(self):
        data=self.recv(8192)
        if data:
            self.vchannel.Write(self.id,action.R2TCMD_DATA,data)

            
    def check_alive(self):
        print("check alive #"+str(self.id))
    #def handle_write(self):
    #    sent = self.send(self.buffer)

    