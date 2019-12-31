'''
Created on Dec 20, 2019

@author: dmitri
'''
#rdp2tcp commands
import struct
import socket
from tunnel import TunnelManager
from logging1 import debug,trace
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
 

class BaseAction:    
    def __init__(self,tid=None,command=None, data=None, server=True):
        self.data = data
        self.server=server
        import client_action
        import server_action
        if server:
            self.actions = server_action
        else:
            self.actions = client_action
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
        debug(self.tid,"ack for action"+str(self))
        pass
    
    def Execute(self,vchannel):
        trace(self.tid,"execute for action"+str(self))
        pass
    
    def Parse(self,msgBuffer):
        pass
    
    def __parse(self,msgBuffer):
        if self.command==0:
            self.__class__=self.actions.ConnectAction
        elif self.command==1:
            self.__class__=self.actions.CloseAction
        elif self.command==3:
            self.__class__=self.actions.PingAction
        elif self.command==2:
            self.__class__=self.actions.DataAction
        else:
            raise Exception("unknown command "+str(self.command)+" data:"+str(self.data))
        self.Parse(msgBuffer)
    
        
    def __str__(self):
        return str(self.__class__)+": tun:"+str(self.tunnelId)+" cmd:"+str(self.command)+" data:"+str(self.data)
       
