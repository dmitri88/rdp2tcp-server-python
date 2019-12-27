'''
Created on Dec 20, 2019

@author: dmitri
'''
#rdp2tcp commands
import struct
import socket
from tunnel import TunnelManager
R2TCMD_CONN=0
R2TCMD_CLOSE=1
R2TCMD_DATA=2
R2TCMD_PING=3
R2TCMD_BIND=4
R2TCMD_RCONN=5
R2TCMD_MAX=6

TUNAF_ANY=0
TUNAF_IPV4=1
TUNAF_IPV6=2

class BaseAction():    
    def __init__(self,tid=None,command=None, data=None):
        self.data = data
        if tid!=None:
            self.tunnelId = int(tid)
        else:
            self.tunnelId = None
        if command != None:
            self.command = int(command)
        else:
            self.command = None
        if self.command<0 or self.command>R2TCMD_MAX:
            raise Exception("invalid tid #"+str(self.tunnelId)+" command "+str(self.command)+" data:"+str(self.data))
        
        
        self.__parse(data)
    
    def Ack(self,vchannel):
        print("ack for action"+str(self))
        pass
    
    def Execute(self,vchannel):
        print("execute for action"+str(self))
        pass
    
    def Parse(self,msgBuffer):
        pass
    
    def __parse(self,msgBuffer):
        if self.command==0:
            self.__class__=ConnectAction
        elif self.command==1:
            self.__class__=CloseAction
        elif self.command==3:
            self.__class__=PingAction
        elif self.command==2:
            self.__class__=DataAction
        else:
            raise Exception("unknown command "+str(self.command)+" data:"+str(self.data))
        self.Parse(msgBuffer)
    
        
    def __str__(self):
        return str(self.__class__)+": tun:"+str(self.tunnelId)+" cmd:"+str(self.command)+" data:"+str(self.data)
    
class PingAction(BaseAction):
    def __init__(self,tid=0):
        super(PingAction, self).__init__(tid=0,command=R2TCMD_PING)
        
    def Ack(self,vchannel):
        vchannel.PingRaw()    
        pass
    def Execute(self,vchannel):
        pass    
        
class ConnectAction(BaseAction):
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
        print("execute for action"+str(self))
        tunnel=TunnelManager.get(self.tunnelId)
        tunnel.init(vchannel,self.host,self.port)

    def Parse(self, msgBuffer):
        BaseAction.Parse(self, msgBuffer)
        self.port = struct.unpack(">H",msgBuffer[0:2])[0]
        self.host = msgBuffer[3:-1]
        self.ip = socket.gethostbyname(self.host)
    
class CloseAction(BaseAction):
    def Ack(self,vchannel):
        print("ack for action"+str(self))
        #vchannel.Write(self.tunnelId,R2TCMD_CLOSE,None)
    
    def Execute(self,vchannel):
        print("execute for action"+str(self))
        tunnel=TunnelManager.get(self.tunnelId)  
        tunnel.handle_close()  
        #tunnel.close()
        
class DataAction(BaseAction):
    def Ack(self,vchannel):
        #print("ack for action"+str(self))
        #vchannel.Write(self.tunnelId,R2TCMD_CLOSE,None)
        pass
    
    def Execute(self,vchannel):
        print("execute for action"+str(self))
        tunnel=TunnelManager.get(self.tunnelId)  
        tunnel.write(self.data)         
