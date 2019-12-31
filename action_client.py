'''
Created on Dec 31, 2019

@author: dmitri
'''
from action import R2TCMD_PING,\
    TUNAF_IPV4, R2TCMD_CONN,R2TCMD_PINGECHO
from action import BaseAction
import struct
from logging1 import debug,trace
from tunnel import TunnelManager
import socket

class PingAction(BaseAction):##CLIENT
    def __init__(self,tid=0,server=True):
        super(PingAction, self).__init__(tid=tid,command=R2TCMD_PING,server=server)
        
    def Ack(self,vchannel):
        vchannel.Write(self.tunnelId,R2TCMD_PINGECHO,None)

    def Execute(self,vchannel):
        if not vchannel.connected: 
            vchannel.connected=True
            vchannel.onConnect()
        
    
class ConnectAction(BaseAction):##CLIENT
    def Ack(self,vchannel):
        error=0
        tokens=self.ip.split(".")
        ip1=int(tokens[0])
        ip2=int(tokens[1])
        ip3=int(tokens[2])
        ip4=int(tokens[3])
        ret = struct.pack(">BBHBBBB",error,TUNAF_IPV4,self.port,ip1,ip2,ip3,ip4)
        
        #print(ret)
        vchannel.Write(self.tunnelId,R2TCMD_CONN,ret)
        #vchannel.Write(self.tunnelId,R2TCMD_CONN,b'\0')
        #vchannel.Write(self.tunnelId,R2TCMD_PING,None)
    
    def Execute(self,vchannel):
        trace(self.tid,"execute for action"+str(self),server=self.server)
        tunnel=TunnelManager.get(self.tunnelId)
        tunnel.init(vchannel,self.host,self.port)

    def Parse(self, msgBuffer):
        BaseAction.Parse(self, msgBuffer)
        self.port = struct.unpack(">H",msgBuffer[0:2])[0]
        self.host = msgBuffer[3:-1]
        self.ip = socket.gethostbyname(self.host)
    
class CloseAction(BaseAction):##CLIENT
    def Ack(self,vchannel):
        trace(self.tid,"ack for action"+str(self),server=self.server)
        #vchannel.Write(self.tunnelId,R2TCMD_CLOSE,None)
    
    def Execute(self,vchannel):
        trace(self.tid,"execute for action"+str(self),server=self.server)
        tunnel=TunnelManager.get(self.tunnelId)  
        #tunnel.handle_close()  
        tunnel.close()
        
class DataAction(BaseAction):##CLIENT
    def Ack(self,vchannel):
        #print("ack for action"+str(self))
        #vchannel.Write(self.tunnelId,R2TCMD_CLOSE,None)
        pass
    
    def Execute(self,vchannel):
        trace(self.tid,"execute for action"+str(self),server=self.server)
        tunnel=TunnelManager.get(self.tunnelId)  
        